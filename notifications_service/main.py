import asyncio

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from logger import configure_logging
from notification_config import rabbit_config

logger = configure_logging(__name__)


async def send_notification(message: AbstractIncomingMessage) -> None:
    """
    Обрабатывает входящие сообщения и логирует уведомление о заказе.

    :param message: Сообщение, полученное из очереди RabbitMQ.
    """
    async with message.process():
        logger.info(
            "Заказ № %s обработан и уведомление отправлено", message.body.decode()
        )


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

        await queue.consume(send_notification)

        await asyncio.Future()
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
