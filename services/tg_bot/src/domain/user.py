import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class User:
    tg_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
