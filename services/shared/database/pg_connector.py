import asyncio
import logging
from enum import StrEnum
from typing import Protocol

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


class IsolationLevelsEnum(StrEnum):
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"
    READ_UNCOMMITTED = "READ UNCOMMITTED"


class PostgresSettings(Protocol):
    protocol: str = "postgresql+asyncpg"

    host: str
    port: int
    user: str
    password: str
    db: str

    db_pool_size: int
    db_max_overflow: int
    db_pool_timeout: float
    db_pool_recycle: int
    db_pool_pre_ping: bool
    db_echo: bool

    @property
    def dsn(self) -> str:
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def dsn_safe(self) -> str:
        return f"{self.protocol}://{self.user}:***@{self.host}:{self.port}/{self.db}"


class PostgresqlConnector:
    def __init__(self, config: PostgresSettings):
        self._config: PostgresSettings = config
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def connect(self) -> None:

        if self._engine is not None:
            return

        async with self._lock:
            if self._engine is not None:
                return

            logger.info("Creating new AsyncEngine for PostgreSQL")
            try:
                self._engine = create_async_engine(
                    url=self._config.dsn,
                    echo=self._config.db_echo,
                    echo_pool=self._config.db_echo,
                    pool_size=self._config.db_pool_size,
                    max_overflow=self._config.db_max_overflow,
                    pool_timeout=self._config.db_pool_timeout,
                    pool_recycle=self._config.db_pool_recycle,
                    pool_pre_ping=self._config.db_pool_pre_ping,
                )

                logger.info("Creating new async_sessionmaker for PostgreSQL")
                self._sessionmaker = async_sessionmaker(
                    bind=self._engine,
                    expire_on_commit=False,
                )

            except Exception:
                logger.exception(
                    "Failed to connect Postgresql", extra={"dsn": self._config.dsn_safe}
                )
                raise

    async def disconnect(self) -> None:
        async with self._lock:
            if self._engine is not None:
                logger.info("Disposing PostgresSQL connection pool...")
                await self._engine.dispose()
                self._engine = None
                self._sessionmaker = None
                logger.info("PostgreSQL AsyncEngine disconnected")

    def get_engine(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("PostgresqlConnector is not connected.")

        return self._sessionmaker
