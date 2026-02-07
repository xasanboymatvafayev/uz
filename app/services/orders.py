from __future__ import annotations
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Order, OrderItem, User, Food, Courier
from app.utils.enums import OrderStatus
from app.utils.time import utcnow


def _gen_order_number() -> str:
    # short unique-ish: FST-8 chars
    rnd = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"FST-{rnd}"


async def create_order(
    session: AsyncSession,
    user: User,
    customer_name: str,
    phone: str,
    comment: str,
    location_lat: str,
    location_lng: str,
    items: list[dict],
    total: int,
) -> Order:
    order = Order(
        order_number=_gen_order_number(),
        user_id=user.id,
        customer_name=customer_name,
        phone=phone,
        comment=comment or "",
        total=total,
        status=OrderStatus.NEW.value,
        created_at=utcnow(),
        updated_at=utcnow(),
        location_lat=str(location_lat),
        location_lng=str(location_lng),
    )
    session.add(order)
    await session.flush()  # get order.id

    for it in items:
        # snapshot
        food_id = int(it["food_id"])
        name = str(it["name"])
        qty = int(it["qty"])
        price = int(it["price"])
        line_total = qty * price

        oi = OrderItem(
            order_id=order.id,
            food_id=food_id,
            name_snapshot=name,
            price_snapshot=price,
            qty=qty,
            line_total=line_total,
        )
        session.add(oi)

    await session.flush()
    return order


async def list_user_orders(session: AsyncSession, user_id: int, limit: int = 10):
    q = select(Order).where(Order.user_id == user_id).order_by(desc(Order.created_at)).limit(limit)
    return (await session.execute(q)).scalars().all()


async def list_active_orders(session: AsyncSession):
    active = [
        OrderStatus.NEW.value,
        OrderStatus.CONFIRMED.value,
        OrderStatus.COOKING.value,
        OrderStatus.COURIER_ASSIGNED.value,
        OrderStatus.OUT_FOR_DELIVERY.value,
    ]
    q = select(Order).where(Order.status.in_(active)).order_by(desc(Order.created_at))
    return (await session.execute(q)).scalars().all()


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    q = select(Order).where(Order.id == order_id)
    return (await session.execute(q)).scalar_one_or_none()


async def set_status(session: AsyncSession, order: Order, status: OrderStatus) -> None:
    order.status = status.value
    order.updated_at = utcnow()
    await session.flush()


async def assign_courier(session: AsyncSession, order: Order, courier: Courier) -> None:
    order.courier_id = courier.id
    order.updated_at = utcnow()
    await session.flush()
