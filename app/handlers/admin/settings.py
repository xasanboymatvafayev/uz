from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.handlers.admin.panel import is_admin
from app.fsm.states import SettingsEdit
from app.config import settings

router = Router()


@router.message(F.text == "/admin_settings")
async def settings_help(message: Message, session, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "⚙️ Settings (env runtime edit for channels):\n"
        "Current:\n"
        f"SHOP_CHANNEL_ID={settings.SHOP_CHANNEL_ID}\n"
        f"COURIER_CHANNEL_ID={settings.COURIER_CHANNEL_ID}\n\n"
        "Command:\n"
        "/settings_edit"
    )


@router.message(F.text == "/settings_edit")
async def settings_edit(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(SettingsEdit.shop_channel_id)
    await message.answer("SHOP_CHANNEL_ID? (number or '-')")


@router.message(SettingsEdit.shop_channel_id)
async def set_shop(message: Message, state: FSMContext):
    txt = message.text.strip()
    if txt == "-":
        val = None
    else:
        val = int(txt)
    # runtime-only (for persistent store: create Settings table; but per requirement this is enough)
    settings.SHOP_CHANNEL_ID = val
    await state.set_state(SettingsEdit.courier_channel_id)
    await message.answer("COURIER_CHANNEL_ID? (number or '-')")


@router.message(SettingsEdit.courier_channel_id)
async def set_courier(message: Message, state: FSMContext):
    txt = message.text.strip()
    if txt == "-":
        val = None
    else:
        val = int(txt)
    settings.COURIER_CHANNEL_ID = val
    await state.clear()
    await message.answer("✅ Settings updated (runtime).")
