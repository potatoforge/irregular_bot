from functools import cached_property

from services.shared.database.pg_connector import PostgresqlConnector
from services.tg_bot.src.infrastructure.repositories.game_repository import IrregularGameRepository
from services.tg_bot.src.infrastructure.repositories.user_repository import UserRepository
from services.tg_bot.src.infrastructure.repositories.verb_repository import VerbRepository
from services.tg_bot.src.infrastructure.repositories.phrase_repository import PhraseRepository
from services.tg_bot.src.application.phrases.idioms_service import IdiomsService
from services.tg_bot.src.config.settings import Settings


class Container:
    instance: Container | None = None

    def __new__(cls, *args, **kwargs) -> Container:  # noqa: ANN002, ANN003, ARG004
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @classmethod
    def build(cls, settings: Settings) -> Container:
        container = cls(settings=settings)
        # Force initialization of all cached properties
        _ = container.pg_connector
        _ = container.user_repository
        _ = container.verb_repository
        _ = container.irregular_game_repository
        _ = container.phrase_repository
        _ = container.idiom_service
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

    @cached_property
    def irregular_game_repository(self) -> IrregularGameRepository:
        return IrregularGameRepository(connector=self.pg_connector)

    @cached_property
    def phrase_repository(self) -> PhraseRepository:
        return PhraseRepository(connector=self.pg_connector)

    @cached_property
    def idiom_service(self) -> IdiomsService:
        return IdiomsService(self.phrase_repository)
