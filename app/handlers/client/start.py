from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.keyboards.client import client_menu_kb
from app.services.referral import apply_referral_if_needed
from app.utils.time import utcnow

router = Router()


@router.message(F.text.startswith("/start"))
async def start_cmd(message: Message, session: AsyncSession):
    args = message.text.split(maxsplit=1)
    ref_tg_id = None
    if len(args) == 2:
        try:
            ref_tg_id = int(args[1].strip())
        except Exception:
            ref_tg_id = None

    tg_id = message.from_user.id
    username = message.from_user.username
    full_name = (message.from_user.full_name or "").strip() or "User"

    q = select(User).where(User.tg_id == tg_id)
    user = (await session.execute(q)).scalar_one_or_none()
    if not user:
        user = User(tg_id=tg_id, username=username, full_name=full_name, joined_at=utcnow())
        session.add(user)
        await session.flush()
    else:
        user.username = username
        user.full_name = full_name
        await session.flush()

    await apply_referral_if_needed(session, user, ref_tg_id)

    text = f"Добро пожаловать в FIESTA! {full_name}\nДля заказа перейдите по кнопке ➡️\n🛍 Заказать"
    await message.answer(text, reply_markup=client_menu_kb())
