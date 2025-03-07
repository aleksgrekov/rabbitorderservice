import asyncio
import aio_pika
from pydantic import BaseModel


class Order(BaseModel):
    user_id: int
    items: list[str]
    total: float


async def listen_notifications():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("notifications_queue", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                order = Order.parse_raw(message.body)
                print(f"Заказ №{order.user_id} обработан и уведомление отправлено")


if __name__ == "__main__":
    asyncio.run(listen_notifications())
