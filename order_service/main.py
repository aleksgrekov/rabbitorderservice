from fastapi import FastAPI

from publisher import process_order
from schemas import OrderSchema, OrderResponseSchema

app = FastAPI()


@app.post("/order")
async def create_order(order: OrderSchema):
    await process_order(order)
    return OrderResponseSchema(order=order)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
