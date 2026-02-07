from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.config import settings
from app.logging_conf import setup_logging
from app.handlers import build_router
print(build_router)
from app.middlewares.db import DbSessionMiddleware


async def main():
    setup_logging()

    bot = Bot(settings.BOT_TOKEN)
    redis = Redis.from_url(settings.REDIS_URL)
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(storage=storage)
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(build_router())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
