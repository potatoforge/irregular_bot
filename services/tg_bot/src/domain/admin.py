from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True, slots=True)
class Admin:
    id: UUID
    tg_id: int
    username: str
    first_name: str
    last_name: str
