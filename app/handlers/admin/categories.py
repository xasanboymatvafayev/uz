from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.handlers.admin.panel import is_admin
from app.fsm.states import CategoryCreate
from app.models import Category

router = Router()


@router.message(F.text == "/admin_categories")
async def cat_help(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await message.answer("📂 Kategoriyalar:\n/cat_list\n/cat_add\n/cat_del <id>")


@router.message(F.text == "/cat_list")
async def cat_list(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    cats = (await session.execute(select(Category).order_by(Category.id.asc()))).scalars().all()
    if not cats:
        await message.answer("No categories")
        return
    await message.answer("\n".join([f"id={c.id} | {c.name} | active={c.is_active}" for c in cats]))


@router.message(F.text == "/cat_add")
async def cat_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(CategoryCreate.name)
    await message.answer("Category name?")


@router.message(CategoryCreate.name)
async def cat_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(CategoryCreate.is_active)
    await message.answer("Is active? (yes/no)")


@router.message(CategoryCreate.is_active)
async def cat_active(message: Message, state: FSMContext, session: AsyncSession):
    active = message.text.strip().lower() in ("yes", "y", "ha", "true", "1")
    data = await state.get_data()
    cat = Category(name=data["name"], is_active=active)
    session.add(cat)
    await state.clear()
    await message.answer("✅ Category added")
