from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def courier_actions_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qabul qildim", callback_data=f"courier:accept:{order_id}")],
            [InlineKeyboardButton(text="📦 Yetkazildi", callback_data=f"courier:delivered:{order_id}")],
        ]
    )


def courier_pick_kb(order_id: int, couriers: list[tuple[int, str]]):
    rows = []
    for cid, name in couriers:
        rows.append([InlineKeyboardButton(text=f"🚴 {name}", callback_data=f"order:assign:{order_id}:{cid}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
