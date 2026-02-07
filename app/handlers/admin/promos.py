from __future__ import annotations
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.handlers.admin.panel import is_admin
from app.fsm.states import PromoCreate
from app.models import Promo

router = Router()


@router.message(F.text == "/admin_promos")
async def promo_help(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🎁 Promokodlar:\n/promo_list\n/promo_add\n/promo_disable <id>")


@router.message(F.text == "/promo_list")
async def promo_list(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    promos = (await session.execute(select(Promo).order_by(Promo.id.desc()).limit(50))).scalars().all()
    if not promos:
        await message.answer("No promos")
        return
    lines = []
    for p in promos:
        lines.append(f"id={p.id} | {p.code} | {p.discount_percent}% | used={p.used_count}/{p.usage_limit} | active={p.is_active}")
    await message.answer("\n".join(lines))


@router.message(F.text == "/promo_add")
async def promo_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(PromoCreate.code)
    await message.answer("Promo code? (will be uppercased)")


@router.message(PromoCreate.code)
async def promo_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text.strip().upper())
    await state.set_state(PromoCreate.discount_percent)
    await message.answer("Discount percent (1-90)?")


@router.message(PromoCreate.discount_percent)
async def promo_disc(message: Message, state: FSMContext):
    await state.update_data(discount_percent=int(message.text.strip()))
    await state.set_state(PromoCreate.expires_at)
    await message.answer("Expires at? (YYYY-MM-DD) or '-' for none")


@router.message(PromoCreate.expires_at)
async def promo_exp(message: Message, state: FSMContext):
    txt = message.text.strip()
    if txt == "-":
        exp = None
    else:
        dt = datetime.strptime(txt, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        exp = dt
    await state.update_data(expires_at=exp)
    await state.set_state(PromoCreate.usage_limit)
    await message.answer("Usage limit? (0=unlimited)")


@router.message(PromoCreate.usage_limit)
async def promo_lim(message: Message, state: FSMContext):
    await state.update_data(usage_limit=int(message.text.strip()))
    await state.set_state(PromoCreate.is_active)
    await message.answer("Is active? (yes/no)")


@router.message(PromoCreate.is_active)
async def promo_active(message: Message, state: FSMContext, session: AsyncSession):
    active = message.text.strip().lower() in ("yes", "y", "ha", "true", "1")
    data = await state.get_data()
    promo = Promo(
        code=data["code"],
        discount_percent=data["discount_percent"],
        expires_at=data["expires_at"],
        usage_limit=data["usage_limit"],
        used_count=0,
        is_active=active,
    )
    session.add(promo)
    await state.clear()
    await message.answer("✅ Promo created")
