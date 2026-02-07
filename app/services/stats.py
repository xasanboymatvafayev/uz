from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models import Order, OrderItem
from app.utils.enums import OrderStatus


async def stats_range(session: AsyncSession, since: datetime):
    delivered = OrderStatus.DELIVERED.value
    q_orders = select(func.count(Order.id)).where(Order.created_at >= since)
    q_deliv = select(func.count(Order.id)).where(Order.created_at >= since, Order.status == delivered)
    q_rev = select(func.coalesce(func.sum(Order.total), 0)).where(Order.created_at >= since, Order.status == delivered)

    orders_count = (await session.execute(q_orders)).scalar_one()
    delivered_count = (await session.execute(q_deliv)).scalar_one()
    revenue_sum = (await session.execute(q_rev)).scalar_one()

    top_q = (
        select(OrderItem.name_snapshot, func.sum(OrderItem.qty).label("qty_sum"))
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.created_at >= since, Order.status == delivered)
        .group_by(OrderItem.name_snapshot)
        .order_by(desc("qty_sum"))
        .limit(5)
    )
    top = (await session.execute(top_q)).all()
    return orders_count, delivered_count, int(revenue_sum or 0), top


async def stats_today_week_month(session: AsyncSession):
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = now - timedelta(days=7)
    month = now - timedelta(days=30)
    return {
        "today": await stats_range(session, today),
        "week": await stats_range(session, week),
        "month": await stats_range(session, month),
    }
