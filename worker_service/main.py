import asyncio
import json

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel

from database.models.order_model import Order
from database.schemas import OrderSchema
from logger import configure_logging
from worker_config import rabbit_config

logger = configure_logging(__name__)


async def process_message(
    message: AbstractIncomingMessage, channel: AbstractRobustChannel
):
    async with message.process():
        order = OrderSchema.model_validate(json.loads(message.body.decode()))
        logger.info(f"Processing order: {order}")
        order_id = await Order.add_order(order=order)
        await asyncio.sleep(2)
        logger.info(f"Order {order} processed and sent to notifications_queue")

        await channel.default_exchange.publish(
            Message(body=f"{order_id}_{order.user_id}_{len(order.items)}".encode()),
            routing_key=rabbit_config.NOTIFICATION_RABBITMQ_QUEUE,
        )


async def main() -> None:
    logger.info("Starting worker service")
    queue_key = rabbit_config.ORDERS_RABBITMQ_QUEUE

    connection = await connect_robust(rabbit_config.url)
    channel = await connection.channel(publisher_confirms=False)
    queue = await channel.declare_queue(queue_key, durable=True)

    # await queue.consume(process_message)
    await queue.consume(lambda message: process_message(message, channel))
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service was stopped!")
