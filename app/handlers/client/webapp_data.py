from __future__ import annotations
import json
from aiogram import Router, F, Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User
from app.services.orders import create_order
from app.services.promo import validate_promo, apply_discount, mark_used
from app.services.telegram_notify import send_admin_order_post
from app.keyboards.admin import admin_order_actions_kb
from app.utils.enums import STATUS_LABEL, OrderStatus

router = Router()

MIN_TOTAL = 50_000


def _fmt_items(items: list[dict]) -> str:
    out = []
    for it in items:
        name = it["name"]
        qty = int(it["qty"])
        price = int(it["price"])
        out.append(f"{name} x{qty} = {qty*price}")
    return "\n".join(out)


@router.message(F.web_app_data)
async def webapp_order(message: Message, bot: Bot, session: AsyncSession):
    raw = message.web_app_data.data
    try:
        payload = json.loads(raw)
    except Exception:
        await message.answer("❌ Ошибка данных заказа")
        return

    if payload.get("type") != "order_create":
        return

    items = payload.get("items") or []
    total = int(payload.get("total") or 0)
    if total < MIN_TOTAL:
        await message.answer(f"❌ Минимальная сумма заказа: {MIN_TOTAL}")
        return

    loc = payload.get("location") or {}
    lat = loc.get("lat")
    lng = loc.get("lng")
    if lat is None or lng is None:
        await message.answer("❌ Локация обязательна")
        return

    tg_id = message.from_user.id
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if not user:
        await message.answer("Сначала нажмите /start")
        return

    customer_name = str(payload.get("customer_name") or user.full_name)
    phone = str(payload.get("phone") or "").strip()
    comment = str(payload.get("comment") or "").strip()

    promo_code = (payload.get("promo") or "").strip()
    if promo_code:
        promo = await validate_promo(session, promo_code)
        if not promo:
            await message.answer("❌ Промокод недействителен или истёк")
            return
        total = await apply_discount(total, promo)
        await mark_used(session, promo)

    order = await create_order(
        session=session,
        user=user,
        customer_name=customer_name,
        phone=phone,
        comment=comment,
        location_lat=str(lat),
        location_lng=str(lng),
        items=items,
        total=total,
    )

    user_text = (
        "Ваш заказ принят ✅\n"
        f"🆔 Заказ №{order.order_number}\n"
        f"💰 Сумма: {order.total} сум\n"
        f"📦 Статус: {STATUS_LABEL[OrderStatus.NEW]}"
    )
    await message.answer(user_text)

    admin_text = (
        f"🆕 Новый заказ №{order.order_number}\n"
        f"👤 Пользователь: {user.full_name} (@{user.username or '-'})\n"
        f"📞 Телефон: {phone}\n"
        f"💰 Сумма: {order.total}\n"
        f"🕒 Время: {order.created_at:%Y-%m-%d %H:%M:%S}\n"
        f"📍 Локация: {lat},{lng}\n"
        f"🔗 Карта: https://maps.google.com/?q={lat},{lng}\n"
        "🍽️ Заказ:\n"
        f"{_fmt_items(items)}"
    )
    kb = admin_order_actions_kb(order.id)
    msg_id = await send_admin_order_post(bot, admin_text, kb)
    order.admin_channel_message_id = msg_id
