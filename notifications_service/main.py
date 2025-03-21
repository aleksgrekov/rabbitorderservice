import asyncio
import signal

from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection, AbstractChannel
from logger import configure_logging
from notification_config import rabbit_config

logger = configure_logging(__name__)

stop_event = asyncio.Event()


async def send_notification(message: AbstractIncomingMessage, channel: AbstractChannel) -> None:
    """
    Обрабатывает входящие сообщения и логирует уведомление о заказе.

    :param message: Сообщение, полученное из очереди RabbitMQ.
    :param channel: Канал для отправки сообщений.
    """
    retries = message.headers.get(rabbit_config.X_RETRIES_HEADER, rabbit_config.CRITICAL_ATTEMPTS_VALUE)
    try:
        logger.info(
            "Заказ № %s обработан и уведомление отправлено",
            message.body.decode(),
        )
        await message.ack()
    except Exception as exc:
        retries -= 1
        logger.error(f"Ошибка при обработке заказа: %s", exc)
        await handle_error(message, retries, channel)


async def handle_error(message: AbstractIncomingMessage, retries: int, channel: AbstractChannel) -> None:
    """
    Обрабатывает ошибку, пытается повторить обработку или отклоняет сообщение.

    :param message: Сообщение, полученное из очереди RabbitMQ.
    :param retries: Количество оставшихся попыток для повторной обработки.
    :param channel: Канал для отправки сообщений.
    """
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
    Главная функция, которая инициализирует соединение с RabbitMQ,
    подписывается на очередь уведомлений и обрабатывает сообщения.
    """
    logger.info("Запуск сервиса уведомлений")

    queue_key = rabbit_config.NOTIFICATION_RABBITMQ_QUEUE
    connection: AbstractRobustConnection | None = None

    try:
        connection = await connect_robust(rabbit_config.url)
        channel = await connection.channel(publisher_confirms=False)

        queue = await channel.declare_queue(queue_key, durable=True)
        logger.info(f"Очередь {queue_key} объявлена и готова к приему сообщений.")

        await queue.consume(lambda message: send_notification(message, channel))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Обработка сигналов завершения
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown)

        await stop_event.wait()
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        logger.info("Остановка сервиса")
        if connection and not connection.is_closed:
            await connection.close()


if __name__ == "__main__":
    try:
        # Запуск основного процесса
        asyncio.run(main())
    except KeyboardInterrupt:
        # Логирование остановки сервиса
        logger.info("Сервис был остановлен!")
