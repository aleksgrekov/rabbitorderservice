from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection

from order_config import rabbit_config
from schemas import OrderSchema
from logger import configure_logging

logger = configure_logging(__name__)


class RabbitConnection:
    """
    Класс для работы с RabbitMQ: подключение, отключение и отправка сообщений.
    """

    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None

    async def disconnect(self) -> None:
        """
        Отключение от RabbitMQ и закрытие канала и соединения.
        """
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

        self._connection = None
        self._channel = None
        logger.info("Отключение от RabbitMQ.")

    async def connect(self) -> None:
        """
        Подключение к RabbitMQ и создание канала.
        """
        try:
            self._connection = await connect_robust(rabbit_config.url)
            self._channel = await self._connection.channel(publisher_confirms=False)
            logger.info("Подключение к RabbitMQ.")
        except Exception as e:
            logger.exception("При подключении к RabbitMQ произошла ошибка: %s", e)
            await self.disconnect()

    async def send_messages(
        self,
        message: OrderSchema,
        queue_key: str = rabbit_config.ORDERS_RABBITMQ_QUEUE,
    ) -> None:
        """
        Отправка сообщений в RabbitMQ.

        :param message: Сообщение для отправки, которое соответствует схеме OrderSchema.
        :param queue_key: Очередь, в которую будет отправлено сообщение.
        """
        if self._channel is None or self._channel.is_closed:
            logger.error("Невозможно отправить сообщение. Канал закрыт.")
            return

        body = message.model_dump_json().encode()
        try:
            await self._channel.default_exchange.publish(
                Message(body=body), routing_key=queue_key
            )
            logger.info(f"Отправка сообщения в очередь: {queue_key}")
        except Exception as e:
            logger.exception("Ошибка при отправке сообщения в RabbitMQ: %s", e)
