from uuid import UUID
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IrregularVerbGameScore:
    user_id: UUID
    score: int
