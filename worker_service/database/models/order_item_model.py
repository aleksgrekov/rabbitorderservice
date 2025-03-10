from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base_model import Base


class OrderItem(Base):
    """
    Модель для элемента заказа.

    Связана с таблицей "order_items", которая хранит информацию об элементах заказа.
    Включает поле `item_name` (название товара) и `order_id` (идентификатор заказа),
    а также связь с заказом.
    """

    __tablename__ = "order_items"

    item_name: Mapped[str] = mapped_column(String(30))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))

    order = relationship("Order", back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, item_name={self.item_name}, order_id={self.order_id})>"
