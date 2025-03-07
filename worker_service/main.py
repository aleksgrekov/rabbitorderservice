import asyncio
import aio_pika
from pydantic import BaseModel


class Order(BaseModel):
    user_id: int
    items: list[str]
    total: float


async def process_order():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("orders_queue", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                order = Order.parse_raw(message.body)
                print(f"Processing order: {order}")

                # Имитация обработки заказа
                await asyncio.sleep(2)

                # Отправка в notifications_queue
                notification_queue = await channel.declare_queue(
                    "notifications_queue", durable=True
                )
                await channel.default_exchange.publish(
                    aio_pika.Message(body=order.json().encode()),
                    routing_key=notification_queue.name,
                )
                print(
                    f"Order {order.user_id} processed and sent to notifications_queue"
                )


if __name__ == "__main__":
    asyncio.run(process_order())
