from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Courier


async def list_active_couriers(session: AsyncSession):
    q = select(Courier).where(Courier.is_active == True).order_by(Courier.name.asc())
    return (await session.execute(q)).scalars().all()


async def get_courier(session: AsyncSession, courier_id: int) -> Courier | None:
    q = select(Courier).where(Courier.id == courier_id)
    return (await session.execute(q)).scalar_one_or_none()


async def get_courier_by_chat(session: AsyncSession, chat_id: int) -> Courier | None:
    q = select(Courier).where(Courier.chat_id == chat_id, Courier.is_active == True)
    return (await session.execute(q)).scalar_one_or_none()
