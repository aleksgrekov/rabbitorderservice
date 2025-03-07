from config.base import base_config
from typing import TYPE_CHECKING
from aio_pika import Message, DeliveryMode

from config.rabbit_connection import create_connection_and_channel
from logger import configure_logging

if TYPE_CHECKING:
    from aio_pika import Channel
    from schemas import OrderSchema

logger = configure_logging(__name__)


async def send_to_queue(order: OrderSchema, channel: Channel):
    try:
        queue = await channel.declare_queue(base_config.RABBITMQ_QUEUE, durable=True)

        await channel.default_exchange.publish(
            Message(
                body=order.model_dump_json().encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )
        logger.info(f"Order sent to queue: {order}")
    except Exception as e:
        logger.exception(f"Failed to send message to queue: {e}")
        raise


async def process_order(order: OrderSchema):
    connection, channel = await create_connection_and_channel()
    try:
        await send_to_queue(order, channel)
    finally:
        await connection.close()
