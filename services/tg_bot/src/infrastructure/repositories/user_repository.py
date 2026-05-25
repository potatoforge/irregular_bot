import logging
from sqlalchemy import select

from services.shared.database.base_repository import BaseRepository
from services.tg_bot.src.infrastructure.db.sqlalchemy.user import UserDB
from services.tg_bot.src.domain.user import User

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        async with self._session() as session:
            stmt = select(UserDB).where(UserDB.tg_id == tg_id)
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()

            logger.debug(
                f"Queried user with tg_id={tg_id}, found: {user_db is not None}"
            )
            logger.debug(f"User query result: {user_db}")

            if user_db is None:
                return None

            return User(
                id=user_db.id,
                tg_id=user_db.tg_id,
                username=user_db.username,
                first_name=user_db.first_name,
                last_name=user_db.last_name,
            )

    async def create_user(self, user: User) -> None:
        async with self._session() as session:
            user_db = UserDB(
                id=user.id,
                tg_id=user.tg_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            session.add(user_db)
            logging.info(f"User with tg_id={user.tg_id} created")
