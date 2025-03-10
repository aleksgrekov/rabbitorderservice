import asyncio

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage

from logger import configure_logging
from notification_config import rabbit_config

logger = configure_logging(__name__)


async def send_notification(message: AbstractIncomingMessage):
    async with message.process():
        logger.info(
            "Заказ № %s обработан и уведомление отправлено", message.body.decode()
        )


async def main() -> None:
    logger.info("Starting notification service")
    queue_key = rabbit_config.NOTIFICATION_RABBITMQ_QUEUE

    connection = await connect_robust(rabbit_config.url)
    channel = await connection.channel(publisher_confirms=False)
    queue = await channel.declare_queue(queue_key, durable=True)

    # await queue.consume(process_message)
    await queue.consume(send_notification)
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service was stopped!")
