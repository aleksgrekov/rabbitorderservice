import asyncio
import json
import signal
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage
from database.models.order_model import Order
from logger import configure_logging
from schemas import OrderSchema
from worker_config import rabbit_config

logger = configure_logging(__name__)

stop_event = asyncio.Event()


async def process_message(message: AbstractIncomingMessage, channel: AbstractChannel) -> None:
    """
    Обрабатывает сообщение из очереди RabbitMQ, десериализует его, добавляет заказ в базу данных,
    подтверждает успешную обработку сообщения и отправляет информацию в очередь уведомлений.
    При ошибке сообщение отклоняется и помещается обратно в очередь для повторной обработки.

    :param message: Сообщение из очереди RabbitMQ.
    :param channel: Канал для отправки сообщений.
    """
    retries = message.headers.get(rabbit_config.X_RETRIES_HEADER, rabbit_config.CRITICAL_ATTEMPTS_VALUE)
    try:
        order = OrderSchema.model_validate(json.loads(message.body.decode()))
        logger.info(f"Обработка заказа: {order}")

        # Добавление заказа в базу данных
        order_id = await Order.add_order(order)
        if order_id:
            logger.info(f"Заказ {order_id} успешно добавлен в базу данных")
            await send_notification(order_id, order, channel)

        await message.ack()
    except Exception as exc:
        retries -= 1
        logger.error(f"Ошибка при обработке заказа: %s", exc)
        await handle_error(message, retries, channel)


async def send_notification(order_id: int, order: OrderSchema, channel: AbstractChannel) -> None:
    """Отправляет уведомление о заказе в очередь уведомлений."""
    await asyncio.sleep(2)  # Пример задержки
    notification_message = f"{order_id}_{order.user_id}_{len(order.items)}".encode()
    await channel.default_exchange.publish(
        Message(body=notification_message),
        routing_key=rabbit_config.NOTIFICATION_RABBITMQ_QUEUE,
    )
    logger.info(f"Заказ {order_id} отправлен в очередь уведомлений")


async def handle_error(message: AbstractIncomingMessage, retries: int, channel: AbstractChannel) -> None:
    """Обрабатывает ошибку, пытается повторить обработку или отклоняет сообщение."""
    x_retries_header = rabbit_config.X_RETRIES_HEADER
    if retries != rabbit_config.CRITICAL_ATTEMPTS_VALUE:
        await channel.default_exchange.publish(
            Message(
                body=message.body,
                headers={x_retries_header: retries},
            ),
            routing_key=message.routing_key,
        )
        logger.info(f"Сообщение повторно поставлено в очередь, попытка {retries}")
    else:
        await message.reject(requeue=False)
        logger.error(f"Сообщение отклонено после {retries} попыток")


def shutdown() -> None:
    """Обработчик завершения работы по сигналу"""
    logger.info("Получен сигнал завершения, останавливаем сервис")
    stop_event.set()


async def main() -> None:
    """
    Основная функция для запуска воркер-сервиса. Устанавливает соединение с RabbitMQ,
    подписывается на очередь и начинает обработку сообщений.
    """
    connection: AbstractConnection | None = None
    try:
        logger.info("Запуск воркер-сервиса")
        queue_key = rabbit_config.ORDERS_RABBITMQ_QUEUE

        connection = await connect_robust(rabbit_config.url)
        channel = await connection.channel(publisher_confirms=False)
        queue = await channel.declare_queue(queue_key, durable=True)

        logger.info(f"Очередь {queue_key} объявлена и готова к приему сообщений.")
        await queue.consume(lambda message: process_message(message, channel))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Обработка сигналов завершения
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown)

        await stop_event.wait()

    except Exception as e:
        logger.error(f"Ошибка при запуске воркер-сервиса: {e}")
    finally:
        logger.info("Остановка воркер-сервиса")
        if connection:
            await connection.close()


if __name__ == "__main__":
    """Запускает основной процесс воркер-сервиса."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Сервис был остановлен вручную!")
