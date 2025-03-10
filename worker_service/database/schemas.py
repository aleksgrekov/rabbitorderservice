from typing import Annotated, List

from annotated_types import Ge
from pydantic import BaseModel, Field


class OrderSchema(BaseModel):
    """
    Схема для данных заказа.
    """

    user_id: int = Field(
        ..., ge=1, description="ID пользователя, должно быть больше или равно 1"
    )
    items: List[str] = Field(..., description="Список наименований товаров в заказе")
    total: float = Field(
        ..., ge=0, description="Общая сумма заказа, должна быть неотрицательной"
    )
