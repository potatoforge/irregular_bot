from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Idiom:
    id: int
    idiom: str
    translation: str
    meaning: str
    context: str
    source: str
