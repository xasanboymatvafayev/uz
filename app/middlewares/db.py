from __future__ import annotations
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with SessionLocal() as session:  # type: AsyncSession
            data["session"] = session
            result = await handler(event, data)
            await session.commit()
            return result
