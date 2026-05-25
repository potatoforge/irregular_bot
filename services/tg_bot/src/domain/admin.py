from uuid import UUID
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Admin:
    id: UUID
    tg_id: int
    username: str
    first_name: str
    last_name: str
