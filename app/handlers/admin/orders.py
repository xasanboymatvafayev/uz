from __future__ import annotations
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.admin.panel import is_admin
from app.services.orders import list_active_orders, get_order, set_status, assign_courier
from app.services.courier import list_active_couriers, get_courier
from app.services.telegram_notify import edit_admin_order_post, notify_user
from app.keyboards.admin import admin_order_actions_kb
from app.keyboards.courier import courier_pick_kb, courier_actions_kb
from app.utils.enums import OrderStatus, STATUS_LABEL
from app.config import settings

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


@router.message(F.text == "/admin_orders")
async def admin_orders(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    orders = await list_active_orders(session)
    if not orders:
        await message.answer("Активных заказов нет.")
        return

    lines = ["Активные заказы:"]
    for o in orders[:30]:
        lines.append(f"• #{o.order_number} | {STATUS_LABEL[OrderStatus(o.status)]} | {o.total} сум | id={o.id}")
    await message.answer("\n".join(lines))


@router.callback_query(F.data.startswith("order:set:"))
async def order_set_status(call: CallbackQuery, bot: Bot, session: AsyncSession):
    if not is_admin(call.from_user.id):
        await call.answer("No access", show_alert=True)
        return

    _, _, order_id, status = call.data.split(":", 3)
    order = await get_order(session, int(order_id))
    if not order:
        await call.answer("Order not found", show_alert=True)
        return

    new_status = OrderStatus(status)
    await set_status(session, order, new_status)

    # notify user
    if new_status in (OrderStatus.CONFIRMED, OrderStatus.COOKING, OrderStatus.CANCELED):
        await notify_user(
            bot,
            order.user.tg_id,
            f"📦 Статус заказа №{order.order_number}: {STATUS_LABEL[new_status]}",
        )

    # edit admin post
    if order.admin_channel_message_id:
        kb = admin_order_actions_kb(order.id) if new_status not in (OrderStatus.DELIVERED, OrderStatus.CANCELED) else None
        await edit_admin_order_post(bot, order.admin_channel_message_id, _admin_post_text(order), kb)

    await call.answer("OK")


@router.callback_query(F.data.startswith("order:courier_menu:"))
async def courier_menu(call: CallbackQuery, session: AsyncSession):
    if not is_admin(call.from_user.id):
        await call.answer("No access", show_alert=True)
        return
    order_id = int(call.data.split(":")[-1])
    couriers = await list_active_couriers(session)
    if not couriers:
        await call.answer("No couriers", show_alert=True)
        return

    kb = courier_pick_kb(order_id, [(c.id, c.name) for c in couriers])
    await call.message.reply(f"Выберите курьера для заказа id={order_id}", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("order:assign:"))
async def assign(call: CallbackQuery, bot: Bot, session: AsyncSession):
    if not is_admin(call.from_user.id):
        await call.answer("No access", show_alert=True)
        return

    _, _, order_id, courier_id = call.data.split(":")
    order = await get_order(session, int(order_id))
    courier = await get_courier(session, int(courier_id))
    if not order or not courier:
        await call.answer("Not found", show_alert=True)
        return

    await assign_courier(session, order, courier)
    await set_status(session, order, OrderStatus.COURIER_ASSIGNED)

    # send to courier channel or courier private
    lat, lng = order.location_lat, order.location_lng
    items = "\n".join([f"{it.name_snapshot} x{it.qty}" for it in order.items])
    courier_text = (
        f"🚴 Новый заказ №{order.order_number}\n"
        f"👤 Клиент: {order.customer_name}\n"
        f"📞 Телефон: {order.phone}\n"
        f"💰 Сумма: {order.total}\n"
        f"📍 Локация: https://maps.google.com/?q={lat},{lng}\n"
        f"🍽️ Список:\n{items}"
    )
    target_chat = settings.COURIER_CHANNEL_ID or courier.chat_id
    await bot.send_message(target_chat, courier_text, reply_markup=courier_actions_kb(order.id), disable_web_page_preview=True)

    # update admin post
    if order.admin_channel_message_id:
        await edit_admin_order_post(bot, order.admin_channel_message_id, _admin_post_text(order), admin_order_actions_kb(order.id))

    await notify_user(bot, order.user.tg_id, f"🚴 Курьер назначен на заказ №{order.order_number}")
    await call.answer("Courier assigned")
