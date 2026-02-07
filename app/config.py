from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    ADMIN_IDS: str

    DB_URL: str
    REDIS_URL: str

    SHOP_CHANNEL_ID: Optional[int] = None
    COURIER_CHANNEL_ID: Optional[int] = None

    WEBAPP_URL: str
    API_BASE_URL: str

    BOT_USERNAME: str
    LOG_LEVEL: str = "INFO"

    @field_validator("ADMIN_IDS")
    @classmethod
    def _admins(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("ADMIN_IDS empty")
        return v

    def admin_id_list(self) -> List[int]:
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]


settings = Settings()
