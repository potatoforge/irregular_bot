from uuid import UUID
from services.shared.database.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger


class IrregularVerbGameScoreDB(Base):
    __tablename__ = "irregular_verb_game_score"
    __table_args__ = ({"schema": "game"},)

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(BigInteger, default=0)

    repr_cols_num = 2
