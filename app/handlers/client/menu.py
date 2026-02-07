from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.keyboards.client import shop_inline_kb
from app.services.orders import list_user_orders
from app.services.referral import referral_stats, ensure_referral_reward_promo
from app.config import settings
from app.utils.enums import STATUS_LABEL, OrderStatus

router = Router()

ABOUT_TEXT = """🌟 Добро Пожаловать в FIESTA !
📍 Наш адрес:Хорезмская область, г.Хива, махаллинский сход граждан Гиламчи
🏢﻿ Ориентир: Школа №12 Оруджева
📞 Контактный номер: +998 91 420 15 15
🕙﻿ Рабочие часы: 24/7
📷 Мы в Instagram: fiesta.khiva (https://www.instagram.com/fiesta.khiva?igsh=Z3VoMzE0eGx0ZTVo)
🔗 Найти нас на карте: Место расположение (https://maps.app.goo.gl/dpBVHBWX1K7NTYVR7)"""


@router.message(F.text == "ℹ️ Информация о нас")
async def about(message: Message, session: AsyncSession):
    await message.answer(ABOUT_TEXT, disable_web_page_preview=True)


@router.message(F.text == "/shop")
async def shop_cmd(message: Message, session: AsyncSession):
    await message.answer("Чтобы открыть наш магазин, нажмите кнопку ниже", reply_markup=shop_inline_kb())


@router.message(F.text == "📦 Мои заказы")
async def my_orders(message: Message, session: AsyncSession):
    tg_id = message.from_user.id
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    orders = await list_user_orders(session, user.id, limit=10)
    if not orders:
        await message.answer(
            "В данный момент у вас нет активных заказов в нашем магазине.\n"
            "Чтобы открыть магазин, введите команду — /shop"
        )
        return

    lines = []
    for o in orders:
        st = STATUS_LABEL.get(OrderStatus(o.status), o.status)
        lines.append(f"🆔 Заказ №{o.order_number} | {o.created_at:%Y-%m-%d %H:%M} | 💰 {o.total} | 📦 {st}")
        for it in o.items:
            lines.append(f"  • {it.name_snapshot} x{it.qty} = {it.line_total}")
        lines.append("")

    await message.answer("\n".join(lines).strip())


@router.message(F.text == "👥 Пригласить друга")
async def invite(message: Message, session: AsyncSession):
    tg_id = message.from_user.id
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    ref_count, orders_count, delivered_count = await referral_stats(session, user)
    promo = await ensure_referral_reward_promo(session, user)

    text = (
        "За приглашение друга, вы можете получить промо-код от нас\n"
        f"👥 Вы пригласили {ref_count} человек\n"
        f"🛒 Оформили заказов: {orders_count}\n"
        f"💰 Оплатили заказов: {delivered_count}\n"
        f"👤 Ваша реферальная ссылка: https://t.me/{settings.BOT_USERNAME}?start={user.tg_id}\n"
        "Пригласите трех человек и вы получите от нас промо-код со скидкой 15%"
    )
    await message.answer(text, disable_web_page_preview=True)

    if promo:
        await message.answer(f"🎁 Ваш промо-код на 15%: `{promo.code}`", parse_mode="Markdown")
