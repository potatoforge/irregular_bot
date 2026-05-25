import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from services.shared.database.base_model import Base


class UserDB(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "tg"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column()
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()

    admin: Mapped["AdminDB"] = relationship(back_populates="user")

    repr_cols_num = 5


class AdminDB(Base):
    __tablename__ = "admin"
    __table_args__ = {"schema": "tg"}

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tg.user.id"), primary_key=True)
    user: Mapped[UserDB] = relationship(back_populates="admin")
