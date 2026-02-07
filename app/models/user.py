from __future__ import annotations
from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.utils.time import utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    joined_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), default=utcnow)

    ref_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    ref_by_user: Mapped["User | None"] = relationship(remote_side=[id], lazy="selectin")
    
