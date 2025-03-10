import asyncio
import json

from aio_pika.abc import AbstractIncomingMessage
from aio_pika import connect_robust
from database.models.order_model import Order
from database.schemas import OrderSchema
from database.service import DBSession
from logger import configure_logging
from order_config import rabbit_config

logger = configure_logging(__name__)


async def process_message(message: AbstractIncomingMessage):
    async with message.process():
        order = OrderSchema.model_validate(json.loads(message.body.decode()))
        logger.info(f"Processing order: {order}")
        await Order.add_order(order=order, session=DBSession)
        await asyncio.sleep(2)
        logger.info(f"Order {order} processed and sent to notifications_queue")


async def main() -> None:
    queue_key = rabbit_config.ORDERS_RABBITMQ_QUEUE

    connection = await connect_robust(rabbit_config.url)
    channel = await connection.channel(publisher_confirms=False)
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(queue_key)

    await queue.bind(queue_key)
    await queue.consume(process_message)
    try:
        await asyncio.Future()
    finally:
        await connection.close()
