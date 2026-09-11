from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class IrregularVerbGameScore:
    user_id: UUID
    score: int
