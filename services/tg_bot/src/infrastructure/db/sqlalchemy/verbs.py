from sqlalchemy.orm import Mapped, mapped_column
from services.shared.database.base_model import Base


class IrregularVerbDB(Base):
    __tablename__ = "irregular_verb"
    __table_args__ = {"schema": "eng"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base_form: Mapped[str] = mapped_column(unique=True, nullable=False)
    past_simple: Mapped[str] = mapped_column(nullable=False)
    past_participle: Mapped[str] = mapped_column(nullable=False)
    translation: Mapped[str] = mapped_column(nullable=False)
