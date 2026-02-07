from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.handlers.admin.panel import is_admin
from app.fsm.states import FoodCreate
from app.models import Food, Category

router = Router()


@router.message(F.text == "/admin_foods")
async def foods_help(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🍔 Taomlar:\n"
        "/food_list\n"
        "/food_add\n"
        "/food_del <food_id>\n"
    )


@router.message(F.text == "/food_list")
async def food_list(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    foods = (await session.execute(select(Food).order_by(Food.id.desc()).limit(50))).scalars().all()
    if not foods:
        await message.answer("No foods")
        return
    lines = []
    for f in foods:
        lines.append(f"id={f.id} | {f.name} | {f.price} | cat={f.category_id} | active={f.is_active} | new={f.is_new}")
    await message.answer("\n".join(lines))


@router.message(F.text == "/food_add")
async def food_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(FoodCreate.name)
    await message.answer("Food name?")


@router.message(FoodCreate.name)
async def food_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(FoodCreate.category_id)
    await message.answer("Category id? (see /cat_list)")


@router.message(FoodCreate.category_id)
async def food_cat(message: Message, state: FSMContext, session: AsyncSession):
    cid = int(message.text.strip())
    cat = (await session.execute(select(Category).where(Category.id == cid))).scalar_one_or_none()
    if not cat:
        await message.answer("Invalid category id. Try again.")
        return
    await state.update_data(category_id=cid)
    await state.set_state(FoodCreate.description)
    await message.answer("Description?")


@router.message(FoodCreate.description)
async def food_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(FoodCreate.price)
    await message.answer("Price (int сум)?")


@router.message(FoodCreate.price)
async def food_price(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text.strip()))
    await state.set_state(FoodCreate.rating)
    await message.answer("Rating (1-5)?")


@router.message(FoodCreate.rating)
async def food_rating(message: Message, state: FSMContext):
    await state.update_data(rating=int(message.text.strip()))
    await state.set_state(FoodCreate.is_new)
    await message.answer("Is new? (yes/no)")


@router.message(FoodCreate.is_new)
async def food_is_new(message: Message, state: FSMContext):
    v = message.text.strip().lower() in ("yes", "y", "ha", "true", "1")
    await state.update_data(is_new=v)
    await state.set_state(FoodCreate.is_active)
    await message.answer("Is active? (yes/no)")


@router.message(FoodCreate.is_active)
async def food_is_active(message: Message, state: FSMContext):
    v = message.text.strip().lower() in ("yes", "y", "ha", "true", "1")
    await state.update_data(is_active=v)
    await state.set_state(FoodCreate.image_url)
    await message.answer("Image URL? (or '-' to skip)")


@router.message(FoodCreate.image_url)
async def food_image(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    image_url = message.text.strip()
    if image_url == "-" or not image_url:
        image_url = None

    food = Food(
        category_id=data["category_id"],
        name=data["name"],
        description=data["description"],
        price=data["price"],
        rating=data["rating"],
        is_new=data["is_new"],
        is_active=data["is_active"],
        image_url=image_url,
    )
    session.add(food)
    await state.clear()
    await message.answer(f"✅ Food added id={food.id} (after commit)")
