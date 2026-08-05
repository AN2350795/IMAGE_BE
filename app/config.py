from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # 실행 위치와 무관하게 저장소 루트의 .env 를 찾도록 절대 경로로 지정한다.
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    sql_echo: bool = Field(default=False, alias="SQL_ECHO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
