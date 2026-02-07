from __future__ import annotations
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.utils.time import utcnow
from app.utils.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    customer_name: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(String(255), default="")

    total: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default=OrderStatus.NEW.value)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), default=utcnow)
    delivered_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)

    location_lat: Mapped[str] = mapped_column(String(32))
    location_lng: Mapped[str] = mapped_column(String(32))

    courier_id: Mapped[int | None] = mapped_column(ForeignKey("couriers.id"), nullable=True)
    admin_channel_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    user: Mapped["User"] = relationship(lazy="selectin")
    courier: Mapped["Courier | None"] = relationship(lazy="selectin")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )
