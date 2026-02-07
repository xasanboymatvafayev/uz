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
    router = Router()

    # client
    router.include_router(client_start)
    router.include_router(client_menu)
    router.include_router(client_webapp)

    # admin
    router.include_router(admin_panel)
    router.include_router(admin_orders)
    router.include_router(admin_foods)
    router.include_router(admin_categories)
    router.include_router(admin_promos)
    router.include_router(admin_couriers)
    router.include_router(admin_settings)
    router.include_router(admin_stats)

    # courier
    router.include_router(courier_actions)

    return router
