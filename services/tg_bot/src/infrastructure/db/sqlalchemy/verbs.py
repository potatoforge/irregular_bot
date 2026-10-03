from services.shared.database.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column


class IrregularVerbDB(Base):
    __tablename__ = "irregular_verb"
    __table_args__ = ({"schema": "eng"},)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="identifier")
    base_form: Mapped[str] = mapped_column(
        unique=True, nullable=False, comment="base form of irregular verb"
    )
    past_simple: Mapped[str] = mapped_column(nullable=False, comment="past simple form")
    past_participle: Mapped[str] = mapped_column(nullable=False, comment="past participle form")
    translation: Mapped[str] = mapped_column(nullable=False, comment="translation to russian")
