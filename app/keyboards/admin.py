from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.enums import OrderStatus


def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🍔 Taomlar", callback_data="admin:foods")],
            [InlineKeyboardButton(text="📂 Kategoriyalar", callback_data="admin:categories")],
            [InlineKeyboardButton(text="🎁 Promokodlar", callback_data="admin:promos")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
            [InlineKeyboardButton(text="🚴 Kuryerlar", callback_data="admin:couriers")],
            [InlineKeyboardButton(text="📦 Aktiv buyurtmalar", callback_data="admin:active_orders")],
            [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin:settings")],
        ]
    )


def admin_order_actions_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвержден", callback_data=f"order:set:{order_id}:{OrderStatus.CONFIRMED.value}"),
                InlineKeyboardButton(text="🍳 Готовится", callback_data=f"order:set:{order_id}:{OrderStatus.COOKING.value}"),
            ],
            [InlineKeyboardButton(text="🚴 Курьер", callback_data=f"order:courier_menu:{order_id}")],
            [InlineKeyboardButton(text="❌ Отменен", callback_data=f"order:set:{order_id}:{OrderStatus.CANCELED.value}")],
        ]
    )
