from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base_model import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    item_name: Mapped[str] = mapped_column(String(30))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))

    order = relationship("Order", back_populates="items")
