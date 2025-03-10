from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base_model import Base
from database.models.order_item_model import OrderItem
from schemas import OrderSchema


class Order(Base):
    __tablename__ = "orders"

    user_id: Mapped[int]
    total: Mapped[float] = mapped_column(Numeric(10, 2))

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete",
        passive_deletes=True,
    )

    @staticmethod
    async def add_order(session, order: OrderSchema):
        new_order = Order(user_id=order.user_id, total=order.total)
        new_order.items = [OrderItem(item_name=item) for item in order.items]
        session.add(new_order)
        await session.commit()
