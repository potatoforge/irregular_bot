from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.shared.database.pg_connector import PostgresqlConnector


class BaseRepository:
    def __init__(self, connector: PostgresqlConnector) -> None:
        self.connector = connector

    @asynccontextmanager
    async def _session(self, *, commit_on_exit: bool = True) -> AsyncGenerator[AsyncSession]:
        async with self.connector.session(commit_on_exit=commit_on_exit) as session:
            yield session
