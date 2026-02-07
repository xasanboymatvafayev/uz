from __future__ import annotations
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.orders import get_order, set_status
from app.services.courier import get_courier_by_chat
from app.services.telegram_notify import edit_admin_order_post, notify_user
from app.keyboards.admin import admin_order_actions_kb
from app.utils.enums import OrderStatus, STATUS_LABEL

router = Router()


def _admin_post_text(order) -> str:
    lat, lng = order.location_lat, order.location_lng
    items = "\n".join([f"{it.name_snapshot} x{it.qty} = {it.line_total}" for it in order.items])
    return (
        f"🧾 Заказ №{order.order_number}\n"
        f"👤 Клиент: {order.customer_name}\n"
        f"📞 Телефон: {order.phone}\n"
        f"💰 Сумма: {order.total}\n"
        f"📦 Статус: {STATUS_LABEL[OrderStatus(order.status)]}\n"
        f"📍 Локация: {lat},{lng}\n"
        f"🔗 Карта: https://maps.google.com/?q={lat},{lng}\n"
        f"🍽️ Заказ:\n{items}"
    )


@router.callback_query(F.data.startswith("courier:accept:"))
async def courier_accept(call: CallbackQuery, bot: Bot, session: AsyncSession):
    order_id = int(call.data.split(":")[-1])
    courier = await get_courier_by_chat(session, call.from_user.id)
    if not courier:
        await call.answer("Вы не зарегистрированы как курьер", show_alert=True)
        return

    order = await get_order(session, order_id)
    if not order:
        await call.answer("Order not found", show_alert=True)
        return

    await set_status(session, order, OrderStatus.OUT_FOR_DELIVERY)

    # notify user + admin post edit
    await notify_user(bot, order.user.tg_id, f"Ваш заказ №{order.order_number} передан курьеру 🚴")
    if order.admin_channel_message_id:
        await edit_admin_order_post(bot, order.admin_channel_message_id, _admin_post_text(order), admin_order_actions_kb(order.id))

    await call.answer("OK")


@router.callback_query(F.data.startswith("courier:delivered:"))
async def courier_delivered(call: CallbackQuery, bot: Bot, session: AsyncSession):
    order_id = int(call.data.split(":")[-1])
    courier = await get_courier_by_chat(session, call.from_user.id)
    if not courier:
        await call.answer("Вы не зарегистрированы как курьер", show_alert=True)
        return

    order = await get_order(session, order_id)
    if not order:
        await call.answer("Order not found", show_alert=True)
        return

    await set_status(session, order, OrderStatus.DELIVERED)
    order.delivered_at = order.updated_at

    await notify_user(bot, order.user.tg_id, f"Ваш заказ №{order.order_number} успешно доставлен 🎉 Спасибо!")

    # admin post: mark delivered + remove inline
    if order.admin_channel_message_id:
        await edit_admin_order_post(bot, order.admin_channel_message_id, _admin_post_text(order) + "\n\n✅ Доставлен", None)

    # remove inline on courier msg
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await call.answer("Delivered")
