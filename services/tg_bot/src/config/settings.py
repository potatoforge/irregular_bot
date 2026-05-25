import os

import dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()

LOGGING_LEVEL = os.environ.get("SERVICE_LOGGING_LEVEL", "debug").upper()


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s  %(name)s:  %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOGGING_LEVEL,
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "telethon": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


class PostgresSettings(BaseModel):
    protocol: str = "postgresql+asyncpg"

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    db: str = "main"

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: float = 5.0
    db_pool_recycle: int = 3600  # 1 hour
    db_pool_pre_ping: bool = True
    db_echo: bool = False

    @property
    def dsn(self) -> str:
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def dsn_safe(self) -> str:
        return f"{self.protocol}://{self.user}:***@{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):

    postgresql: PostgresSettings = PostgresSettings()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
        env_file_encoding="utf-8",
    )


def _get_config() -> Settings:
    return Settings()


settings = _get_config()
