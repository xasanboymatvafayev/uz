from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.handlers.admin.panel import is_admin
from app.services.stats import stats_today_week_month

router = Router()


@router.message(F.text == "/admin_stats")
async def stats_cmd(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    s = await stats_today_week_month(session)

    def fmt(key: str):
        orders_count, delivered_count, revenue_sum, top = s[key]
        top_lines = "\n".join([f"• {name}: {qty}" for name, qty in top]) or "-"
        return (
            f"== {key.upper()} ==\n"
            f"orders_count: {orders_count}\n"
            f"delivered_count: {delivered_count}\n"
            f"revenue_sum: {revenue_sum}\n"
            f"top foods:\n{top_lines}\n"
        )

    await message.answer(fmt("today") + "\n" + fmt("week") + "\n" + fmt("month"))
