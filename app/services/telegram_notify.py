from __future__ import annotations
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from app.config import settings


async def notify_user(bot: Bot, tg_id: int, text: str) -> None:
    try:
        await bot.send_message(tg_id, text)
    except Exception:
        # don't crash production flow
        pass


async def send_admin_order_post(
    bot: Bot,
    text: str,
    kb: InlineKeyboardMarkup | None,
) -> int | None:
    if not settings.SHOP_CHANNEL_ID:
        return None
    msg = await bot.send_message(settings.SHOP_CHANNEL_ID, text, reply_markup=kb, disable_web_page_preview=True)
    return msg.message_id


async def edit_admin_order_post(
    bot: Bot,
    message_id: int,
    text: str,
    kb: InlineKeyboardMarkup | None,
) -> None:
    if not settings.SHOP_CHANNEL_ID:
        return
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=settings.SHOP_CHANNEL_ID,
            message_id=message_id,
            reply_markup=kb,
            disable_web_page_preview=True,
        )
    except Exception:
        # if can't edit, ignore
        pass
