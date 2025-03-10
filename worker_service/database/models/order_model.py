from database.models.base_model import Base
from database.models.order_item_model import OrderItem
from database.service import SessionFactory
from logger import configure_logging
from schemas import OrderSchema
from sqlalchemy import Numeric
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship

logger = configure_logging(__name__)


class Order(Base):
    """
    Модель для заказа.

    Связана с таблицей "orders", которая хранит информацию о заказах.
    Включает поле `user_id` (идентификатор пользователя), поле `total` (сумма заказа)
    и связь с элементами заказа (модель OrderItem).
    """

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
    async def add_order(order: OrderSchema) -> int:
        """
        Добавляет новый заказ в базу данных.

        :param order: Схема заказа, содержащая данные о заказе и его элементах.
        :return: Идентификатор нового заказа.
        :raises SQLAlchemyError: Ошибка базы данных при добавлении заказа.
        """
        async with SessionFactory() as session:
            try:
                new_order = Order(user_id=order.user_id, total=order.total)
                new_order.items = [OrderItem(item_name=item) for item in order.items]

                session.add(new_order)
                await session.commit()

                return new_order.id
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Ошибка при добавлении заказа: {e}")
                raise

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total})>"
