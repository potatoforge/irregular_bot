import logging

from services.shared.database.base_repository import BaseRepository
from services.tg_bot.src.domain.phrase import Idiom
from services.tg_bot.src.infrastructure.db.sqlalchemy.phrase import IdiomPhraseDB
from sqlalchemy import func, select

logger = logging.getLogger(__name__)


class PhraseRepository(BaseRepository):
    async def fetch_random_idiom(self) -> Idiom:
        stmt = select(IdiomPhraseDB).order_by(func.random()).limit(1)
        async with self._session() as session:
            result = await session.execute(stmt)
        idiom_db = result.scalar_one()
        logger.info("Queried random idiom, idiom found", extra={"idiom": idiom_db})

        return Idiom(
            id=idiom_db.id,
            idiom=idiom_db.idiom,
            translation=idiom_db.translation,
            meaning=idiom_db.meaning,
            context=idiom_db.context,
            source=idiom_db.source,
        )
