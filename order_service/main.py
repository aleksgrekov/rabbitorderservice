from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from logger import configure_logging
from rabbit_connection import rabbit_connection
from schemas import OrderResponseSchema, OrderSchema

logger = configure_logging(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Управляет жизненным циклом приложения:
    - Устанавливает соединение с брокером сообщений при запуске.
    - Закрывает соединение при завершении работы сервиса.
    """
    logger.info("Подключение к RabbitMQ...")
    await rabbit_connection.connect()
    yield
    logger.info("Завершение работы с RabbitMQ...")
    await rabbit_connection.disconnect()


app = FastAPI(
    title="Order Service",
    description="Сервис для отправки заказов через брокер сообщений",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post(
    "/order",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ",
    description="Принимает данные заказа, отправляет их в брокер сообщений и возвращает подтверждение.",
    response_description="Возвращает созданный заказ.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Заказ принят в обработку",
            "model": OrderResponseSchema,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Не удалось отправить заказ в брокер",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации данных заказа",
        },
    },
)
async def create_order(order: OrderSchema) -> OrderResponseSchema:
    """
    Создает заказ и отправляет его в брокер сообщений.

    - **order**: Данные заказа.
    - **Возвращает**: Подтверждение с данными заказа.
    - **Ошибки**:
        - 500: Если не удалось отправить заказ в брокер.
    """
    try:
        await rabbit_connection.send_messages(order)
        logger.info("Заказ отправлен успешно: %s", order)
    except Exception as e:
        logger.error("Ошибка при отправке заказа: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to send order"
        )

    return OrderResponseSchema(order=order)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")
