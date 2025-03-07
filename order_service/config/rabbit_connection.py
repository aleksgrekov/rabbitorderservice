import aio_pika

from config.base import base_config
from logger import configure_logging

logger = configure_logging(__name__)


async def create_connection_and_channel():
    try:
        connection = await aio_pika.connect_robust(base_config.rabbit_url)
        channel = await connection.channel()
        return connection, channel
    except Exception as e:
        logger.exception(f"Failed to create connection or channel: {e}")
        raise
