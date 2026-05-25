from dataclasses import dataclass
from functools import cached_property

from services.tg_bot.src.config.settings import Settings
from services.shared.database.pg_connector import PostgresqlConnector
from services.tg_bot.src.infrastructure.repositories.user_repository import (
    UserRepository,
)
from services.tg_bot.src.infrastructure.repositories.verb_repository import (
    VerbRepository,
)


@dataclass
class Container:
    settings: Settings

    @classmethod
    def build(cls, settings: Settings) -> "Container":
        container = cls(settings=settings)
        # Force initialization of all cached properties
        _ = container.pg_connector
        _ = container.user_repository
        _ = container.verb_repository
        return container

    @cached_property
    def pg_connector(self) -> PostgresqlConnector:
        return PostgresqlConnector(config=self.settings.postgresql)

    @cached_property
    def user_repository(self) -> UserRepository:
        return UserRepository(connector=self.pg_connector)

    @cached_property
    def verb_repository(self) -> VerbRepository:
        return VerbRepository(connector=self.pg_connector)
