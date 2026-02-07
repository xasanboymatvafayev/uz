from aiogram.fsm.state import State, StatesGroup


class FoodCreate(StatesGroup):
    name = State()
    category_id = State()
    description = State()
    price = State()
    rating = State()
    is_new = State()
    is_active = State()
    image_url = State()


class CategoryCreate(StatesGroup):
    name = State()
    is_active = State()


class PromoCreate(StatesGroup):
    code = State()
    discount_percent = State()
    expires_at = State()
    usage_limit = State()
    is_active = State()


class CourierCreate(StatesGroup):
    chat_id = State()
    name = State()
    is_active = State()


class SettingsEdit(StatesGroup):
    shop_channel_id = State()
    courier_channel_id = State()
