from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.database.pg_connector import PostgresqlConnector


class BaseRepository:
    def __init__(self, connector: PostgresqlConnector) -> None:
        self.connector = connector

    @asynccontextmanager
    async def _session(
        self, *, commit_on_exit: bool = True
    ) -> AsyncIterator[AsyncSession]:
        async with self.connector.session(commit_on_exit=commit_on_exit) as session:
            yield session
