from contextlib import asynccontextmanager

from fastapi import FastAPI

from rabbit_connection import rabbit_connection
from schemas import OrderResponseSchema, OrderSchema


@asynccontextmanager
async def lifespan(_: FastAPI):
    await rabbit_connection.connect()
    yield
    await rabbit_connection.disconnect()


app = FastAPI(lifespan=lifespan)


@app.post("/order")
async def create_order(order: OrderSchema):
    await rabbit_connection.send_messages(order)
    return OrderResponseSchema(order=order)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
