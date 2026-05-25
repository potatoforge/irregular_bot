import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    tg_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    id: uuid.UUID = uuid.uuid4()
