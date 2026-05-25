import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Protocol

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


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
        self._config = config
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            logger.info("Creating new AsyncEngine for PostgreSQL")
            self._engine = create_async_engine(
                url=self._config.dsn,
                echo=self._config.db_echo,
                echo_pool=self._config.db_echo,
                pool_size=self._config.db_pool_size,
                max_overflow=self._config.db_max_overflow,
                pool_timeout=self._config.db_pool_timeout,
                pool_recycle=self._config.db_pool_recycle,
                pool_pre_ping=self._config.db_pool_pre_ping,
                future=True,
            )
        return self._engine

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            logger.info("Creating new async_sessionmaker for PostgreSQL")
            self._sessionmaker = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
            )
        return self._sessionmaker

    async def connect(self):
        if self._engine is None:
            self._engine = self.engine
            logger.info("PostgreSQL AsyncEngine connected")
        if self._sessionmaker is None:
            self._sessionmaker = self.sessionmaker
            logger.info("PostgreSQL async_sessionmaker created")

    async def disconnect(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("PostgreSQL AsyncEngine disconnected")

    @asynccontextmanager
    async def session(
        self, *, commit_on_exit: bool = True
    ) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            self._sessionmaker = self.sessionmaker

        async with self._sessionmaker() as session:
            try:
                yield session
                if commit_on_exit:
                    await session.commit()
            except Exception:
                await session.rollback()
                raise
