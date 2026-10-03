from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True, slots=True)
class IrregularVerbGameScore:
    user_id: UUID
    score: int
