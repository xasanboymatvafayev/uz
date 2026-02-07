from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Promo


async def validate_promo(session: AsyncSession, code: str) -> Promo | None:
    code = code.strip().upper()
    q = select(Promo).where(Promo.code == code, Promo.is_active == True)
    promo = (await session.execute(q)).scalar_one_or_none()
    if not promo:
        return None

    now = datetime.now(timezone.utc)
    if promo.expires_at and promo.expires_at < now:
        return None
    if promo.usage_limit and promo.used_count >= promo.usage_limit:
        return None
    return promo


async def apply_discount(total: int, promo: Promo) -> int:
    discounted = total - (total * promo.discount_percent // 100)
    return max(discounted, 0)


async def mark_used(session: AsyncSession, promo: Promo) -> None:
    promo.used_count += 1
    await session.flush()
