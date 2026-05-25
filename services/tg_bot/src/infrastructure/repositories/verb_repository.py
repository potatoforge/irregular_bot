import logging
from sqlalchemy import func, select

from services.shared.database.base_repository import BaseRepository
from services.tg_bot.src.infrastructure.db.sqlalchemy.verbs import IrregularVerbDB
from services.tg_bot.src.domain.verb import IrregularVerb

logger = logging.getLogger(__name__)


class VerbRepository(BaseRepository):
    async def get_random_irregular_verb(self) -> IrregularVerb:
        async with self._session() as session:
            stmt = select(IrregularVerbDB).order_by(func.random()).limit(1)
            result = await session.execute(stmt)
            verb_db = result.scalar_one()

            logger.debug(f"Queried random irregular verb, found: {verb_db is not None}")
            logger.debug(f"Random irregular verb query result: {verb_db}")

            return IrregularVerb(
                id=verb_db.id,
                base_form=verb_db.base_form,
                past_simple=verb_db.past_simple,
                past_participle=verb_db.past_participle,
                translation=verb_db.translation,
            )

    async def get_irregular_verb_by_id(self, verb_id: int) -> IrregularVerb:
        async with self._session() as session:
            stmt = select(IrregularVerbDB).where(IrregularVerbDB.id == verb_id)
            result = await session.execute(stmt)
            verb_db = result.scalar_one()

            logger.debug(
                f"Queried irregular verb by id={verb_id}, found: {verb_db is not None}"
            )
            logger.debug(f"Irregular verb by id={verb_id} query result: {verb_db}")

            return IrregularVerb(
                id=verb_db.id,
                base_form=verb_db.base_form,
                past_simple=verb_db.past_simple,
                past_participle=verb_db.past_participle,
                translation=verb_db.translation,
            )
