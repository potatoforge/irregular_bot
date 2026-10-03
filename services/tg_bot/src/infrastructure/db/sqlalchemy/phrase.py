from services.shared.database.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column


class IdiomPhraseDB(Base):
    __tablename__ = "idiom_phrase"
    __table_args__ = ({"schema": "eng"},)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="identifier")
    idiom: Mapped[str] = mapped_column(unique=True, nullable=False, comment="idiom phrase")
    translation: Mapped[str] = mapped_column(comment="translation to russian")
    meaning: Mapped[str] = mapped_column(comment="meaning of idiom phrase")
    context: Mapped[str] = mapped_column(comment="context of usage for idiom phrase")
    source: Mapped[str] = mapped_column(comment="source of knowledge")
