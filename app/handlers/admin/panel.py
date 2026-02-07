from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.keyboards.admin import admin_panel_kb

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_list()


@router.message(F.text == "/admin")
async def admin_cmd(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Admin panel:", reply_markup=admin_panel_kb())


@router.callback_query(F.data.startswith("admin:"))
async def admin_nav(call: CallbackQuery, session: AsyncSession):
    if not is_admin(call.from_user.id):
        await call.answer("No access", show_alert=True)
        return

    key = call.data.split(":", 1)[1]
    await call.answer()

    if key == "foods":
        await call.message.edit_text("🍔 Taomlar: /admin_foods", reply_markup=admin_panel_kb())
    elif key == "categories":
        await call.message.edit_text("📂 Kategoriyalar: /admin_categories", reply_markup=admin_panel_kb())
    elif key == "promos":
        await call.message.edit_text("🎁 Promokodlar: /admin_promos", reply_markup=admin_panel_kb())
    elif key == "stats":
        await call.message.edit_text("📊 Statistika: /admin_stats", reply_markup=admin_panel_kb())
    elif key == "couriers":
        await call.message.edit_text("🚴 Kuryerlar: /admin_couriers", reply_markup=admin_panel_kb())
    elif key == "active_orders":
        await call.message.edit_text("📦 Aktiv buyurtmalar: /admin_orders", reply_markup=admin_panel_kb())
    elif key == "settings":
        await call.message.edit_text("⚙️ Sozlamalar: /admin_settings", reply_markup=admin_panel_kb())
