import uuid
from sqlalchemy.types import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from services.shared.database.base_model import Base


class IrregularVerbGameScoreDB(Base):
    __tablename__ = "irregular_verb_game_score"
    __table_args__ = {"schema": "game"}

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(BigInteger, default=0)

    repr_cols_num = 2
