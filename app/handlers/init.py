from aiogram import Router
from app.handlers.client.start import router as client_start
from app.handlers.client.menu import router as client_menu
from app.handlers.client.webapp_data import router as client_webapp

from app.handlers.admin.panel import router as admin_panel
from app.handlers.admin.orders import router as admin_orders
from app.handlers.admin.foods import router as admin_foods
from app.handlers.admin.categories import router as admin_categories
from app.handlers.admin.promos import router as admin_promos
from app.handlers.admin.couriers import router as admin_couriers
from app.handlers.admin.settings import router as admin_settings
from app.handlers.admin.stats import router as admin_stats

from app.handlers.courier.actions import router as courier_actions


def build_router() -> Router:
    r = Router()
    r.include_router(client_start)
    r.include_router(client_menu)
    r.include_router(client_webapp)

    r.include_router(admin_panel)
    r.include_router(admin_orders)
    r.include_router(admin_foods)
    r.include_router(admin_categories)
    r.include_router(admin_promos)
    r.include_router(admin_couriers)
    r.include_router(admin_settings)
    r.include_router(admin_stats)

    r.include_router(courier_actions)
    return r
