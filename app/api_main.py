from __future__ import annotations
from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import SessionLocal
from app.utils.telegram_initdata import verify_init_data
from app.services.foods import list_categories, list_foods
from app.services.promo import validate_promo

app = FastAPI(title="Fiesta API", version="1.0.0")


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


def verify_webapp(telegram_init_data: str = Header(..., alias="X-Telegram-InitData")):
    try:
        data = verify_init_data(telegram_init_data, settings.BOT_TOKEN)
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid initData")


@app.get("/api/categories")
async def api_categories(
    _init=Depends(verify_webapp),
    session: AsyncSession = Depends(get_session),
):
    cats = await list_categories(session)
    return [{"id": c.id, "name": c.name} for c in cats]


@app.get("/api/foods")
async def api_foods(
    category_id: int | None = None,
    sort: str | None = None,
    search: str | None = None,
    _init=Depends(verify_webapp),
    session: AsyncSession = Depends(get_session),
):
    foods = await list_foods(session, category_id=category_id, sort=sort, search=search)
    return [
        {
            "id": f.id,
            "category_id": f.category_id,
            "name": f.name,
            "description": f.description,
            "price": f.price,
            "rating": f.rating,
            "is_new": f.is_new,
            "image_url": f.image_url,
        }
        for f in foods
    ]


@app.get("/api/promo/validate")
async def api_promo_validate(
    code: str,
    _init=Depends(verify_webapp),
    session: AsyncSession = Depends(get_session),
):
    promo = await validate_promo(session, code)
    if not promo:
        return {"valid": False}
    return {"valid": True, "discount_percent": promo.discount_percent}
