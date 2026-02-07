from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.handlers.admin.panel import is_admin
from app.fsm.states import CourierCreate
from app.models import Courier

router = Router()


@router.message(F.text == "/admin_couriers")
async def cour_help(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🚴 Kuryerlar:\n/courier_list\n/courier_add\n/courier_disable <id>")


@router.message(F.text == "/courier_list")
async def cour_list(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    cs = (await session.execute(select(Courier).order_by(Courier.id.desc()).limit(50))).scalars().all()
    if not cs:
        await message.answer("No couriers")
        return
    await message.answer("\n".join([f"id={c.id} | {c.name} | chat_id={c.chat_id} | active={c.is_active}" for c in cs]))


@router.message(F.text == "/courier_add")
async def cour_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(CourierCreate.chat_id)
    await message.answer("Courier chat_id?")


@router.message(CourierCreate.chat_id)
async def cour_chat(message: Message, state: FSMContext):
    await state.update_data(chat_id=int(message.text.strip()))
    await state.set_state(CourierCreate.name)
    await message.answer("Courier name?")


@router.message(CourierCreate.name)
async def cour_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(CourierCreate.is_active)
    await message.answer("Is active? (yes/no)")


@router.message(CourierCreate.is_active)
async def cour_active(message: Message, state: FSMContext, session: AsyncSession):
    active = message.text.strip().lower() in ("yes", "y", "ha", "true", "1")
    data = await state.get_data()
    c = Courier(chat_id=data["chat_id"], name=data["name"], is_active=active)
    session.add(c)
    await state.clear()
    await message.answer("✅ Courier added")
