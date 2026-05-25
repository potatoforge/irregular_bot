import dotenv

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = dotenv.find_dotenv()


class PostgresSettings(BaseModel):
    protocol: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 5432
    user: str = "123"
    password: str = "postgres"
    db: str = "main"

    @property
    def dsn(self) -> str:
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def dsn_safe(self) -> str:
        return f"{self.protocol}://{self.user}:****@{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    postgresql: PostgresSettings = PostgresSettings()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
        env_file_encoding="utf-8",
    )


def _get_setting() -> Settings:
    return Settings()


settings = _get_setting()
