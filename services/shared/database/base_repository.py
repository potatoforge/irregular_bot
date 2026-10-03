import logging

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.shared.database.pg_connector import (
    PostgresqlConnector,
    IsolationLevelsEnum,
)

logger = logging.getLogger(__name__)


class BaseRepository:
    def __init__(self, connector: PostgresqlConnector) -> None:
        self.connector = connector

    @asynccontextmanager
    async def _session(
        self,
        isolation_level: IsolationLevelsEnum = IsolationLevelsEnum.READ_COMMITTED,
    ) -> AsyncGenerator[AsyncSession]:
        engine: async_sessionmaker[AsyncSession] = self.connector.get_engine()
        async with engine() as session:
            try:
                await session.connection(
                    execution_options={"isolation_level": isolation_level.value}
                )
                yield session
                await session.commit()
                logger.debug(
                    "DB transaction committed",
                    extra={"repository": self.__class__.__name__},
                )
            except Exception:
                await session.rollback()
                logger.debug(
                    "DB transaction rollback",
                    extra={"repository": self.__class__.__name__},
                )
                raise
