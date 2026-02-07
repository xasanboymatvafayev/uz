from __future__ import annotations
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import User, Order, Promo, ReferralPromoIssued
from app.utils.enums import OrderStatus
from app.utils.time import utcnow


def _gen_promo_code(prefix: str = "FIESTA15") -> str:
    rnd = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}-{rnd}"


async def apply_referral_if_needed(session: AsyncSession, user: User, ref_tg_id: int | None):
    if not ref_tg_id:
        return
    if user.ref_by_user_id is not None:
        return
    if user.tg_id == ref_tg_id:
        return

    q = select(User).where(User.tg_id == ref_tg_id)
    ref_user = (await session.execute(q)).scalar_one_or_none()
    if not ref_user:
        return

    user.ref_by_user_id = ref_user.id
    await session.flush()


async def referral_stats(session: AsyncSession, user: User):
    # ref_count: users who ref_by_user_id == user.id
    q_ref = select(func.count(User.id)).where(User.ref_by_user_id == user.id)
    ref_count = (await session.execute(q_ref)).scalar_one()

    q_orders = select(func.count(Order.id)).where(Order.user_id == user.id)
    orders_count = (await session.execute(q_orders)).scalar_one()

    q_paid = select(func.count(Order.id)).where(Order.user_id == user.id, Order.status == OrderStatus.DELIVERED.value)
    delivered_count = (await session.execute(q_paid)).scalar_one()

    return int(ref_count), int(orders_count), int(delivered_count)


async def ensure_referral_reward_promo(session: AsyncSession, user: User) -> Promo | None:
    ref_count, _, _ = await referral_stats(session, user)
    if ref_count < 3:
        return None

    already_q = select(ReferralPromoIssued).where(ReferralPromoIssued.user_id == user.id)
    already = (await session.execute(already_q)).scalar_one_or_none()
    if already:
        return None

    promo = Promo(
        code=_gen_promo_code(),
        discount_percent=15,
        expires_at=None,
        usage_limit=1,
        used_count=0,
        is_active=True,
        created_at=utcnow(),
    )
    session.add(promo)
    await session.flush()

    issued = ReferralPromoIssued(user_id=user.id, promo_id=promo.id, issued_at=utcnow())
    session.add(issued)
    await session.flush()
    return promo
