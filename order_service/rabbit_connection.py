from aio_pika import connect_robust, Message
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel,
)

from order_config import rabbit_config
from logger import configure_logging
from schemas import OrderSchema

logger = configure_logging(__name__)


class RabbitConnection:
    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None

    async def disconnect(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None

    async def connect(self) -> None:
        try:
            self._connection = await connect_robust(rabbit_config.url)
            self._channel = await self._connection.channel(publisher_confirms=False)
        except Exception as e:
            logger.exception("Произошла ошибка при подключении к RabbitMQ: %s", e)
            await self.disconnect()

    async def send_messages(
        self,
        message: OrderSchema,
        routing_key: str = rabbit_config.ORDERS_RABBITMQ_QUEUE,
    ) -> None:
        body = message.model_dump_json().encode()
        await self._channel.default_exchange.publish(
            Message(body=body), routing_key=routing_key
        )


rabbit_connection = RabbitConnection()
