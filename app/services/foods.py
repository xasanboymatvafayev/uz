from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from app.models import Food, Category


async def list_categories(session: AsyncSession):
    q = select(Category).where(Category.is_active == True).order_by(Category.name.asc())
    return (await session.execute(q)).scalars().all()


async def list_foods(session: AsyncSession, category_id: int | None = None, sort: str | None = None, search: str | None = None):
    q = select(Food).where(Food.is_active == True)

    if category_id:
        q = q.where(Food.category_id == category_id)
    if search:
        q = q.where(Food.name.ilike(f"%{search}%"))

    if sort == "rating_desc":
        q = q.order_by(desc(Food.rating))
    elif sort == "new_desc":
        q = q.order_by(desc(Food.created_at))
    elif sort == "price_asc":
        q = q.order_by(asc(Food.price))
    elif sort == "price_desc":
        q = q.order_by(desc(Food.price))
    else:
        q = q.order_by(desc(Food.is_new), Food.name.asc())

    return (await session.execute(q)).scalars().all()


async def get_food(session: AsyncSession, food_id: int) -> Food | None:
    q = select(Food).where(Food.id == food_id)
    return (await session.execute(q)).scalar_one_or_none()
