import logging


from services.tg_bot.src.domain.phrase import Idiom
from services.tg_bot.src.infrastructure.repositories.phrase_repository import PhraseRepository

logger = logging.getLogger(__name__)


class IdiomsService:
    def __init__(self, idioms_repository: PhraseRepository):
        self.repository = idioms_repository

    async def get_idiom(self) -> Idiom:
        return await self.repository.fetch_random_idiom()
