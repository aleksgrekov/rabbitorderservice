from typing import Annotated, List

from annotated_types import Ge
from pydantic import BaseModel


class OrderSchema(BaseModel):
    user_id: Annotated[int, Ge(1)]
    items: List[str]
    total: float


class OrderResponseSchema(BaseModel):
    message: str = "Заказ принят в обработку"
    order: OrderSchema
