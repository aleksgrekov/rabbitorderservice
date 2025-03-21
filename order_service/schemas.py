from typing import List

from pydantic import BaseModel, Field


class OrderSchema(BaseModel):
    """
    Схема для данных заказа.
    """

    user_id: int = Field(
        ..., ge=1, description="ID пользователя, должно быть больше или равно 1"
    )
    items: List[str] = Field(..., min_length=1, description="Список наименований товаров в заказе")
    total: float = Field(
        ..., ge=0, description="Общая сумма заказа, должна быть неотрицательной"
    )


class OrderResponseSchema(BaseModel):
    """
    Схема для ответа при создании заказа.
    """

    message: str = "Заказ принят в обработку"
    order: OrderSchema
