from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.utils.time import utcnow


class ReferralPromoIssued(Base):
    __tablename__ = "referral_promo_issued"
    __table_args__ = (UniqueConstraint("user_id", name="uq_referral_promo_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    promo_id: Mapped[int] = mapped_column(ForeignKey("promos.id"), index=True)
    issued_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), default=utcnow)
