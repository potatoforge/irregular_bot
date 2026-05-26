import logging
from uuid import UUID

from sqlalchemy import select

from services.shared.database.base_repository import BaseRepository
from services.tg_bot.src.infrastructure.db.sqlalchemy.user import UserDB
from services.tg_bot.src.infrastructure.db.sqlalchemy.game import (
    IrregularVerbGameScoreDB,
)
from services.tg_bot.src.domain.irregular_game import IrregularVerbGameScore

logger = logging.getLogger(__name__)


class IrregularGameRepository(BaseRepository):
    async def get_user_score_by_id(self, user_id: UUID) -> IrregularVerbGameScore:
        async with self._session() as session:
            stmt = select(IrregularVerbGameScoreDB).where(
                IrregularVerbGameScoreDB.user_id == user_id
            )
            result = await session.execute(stmt)
            score_db = result.scalar_one_or_none()

            logger.debug(
                f"Queried game score for user_id={user_id}, found: {score_db is not None}"
            )
            logger.debug(f"Game score query result: {score_db}")

            if score_db is None:
                score_db = IrregularVerbGameScoreDB(
                    user_id=user_id,
                )
                session.add(score_db)
                await session.flush()

            return IrregularVerbGameScore(
                user_id=score_db.user_id,
                score=score_db.score,
            )

    async def increment_user_score(self, user_id: UUID) -> IrregularVerbGameScore:
        async with self._session() as session:
            stmt = select(IrregularVerbGameScoreDB).where(
                IrregularVerbGameScoreDB.user_id == user_id
            )
            result = await session.execute(stmt)
            score_db = result.scalar_one()

            logger.debug(
                f"Queried game score for incrementing score for user_id={user_id}, found: {score_db is not None}"
            )
            logger.debug(f"Game score for incrementing query result: {score_db}")

            score_db.score += 1
            await session.flush()
            return IrregularVerbGameScore(
                user_id=score_db.user_id,
                score=score_db.score,
            )
