from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IrregularVerb:
    id: int
    base_form: str
    past_simple: str
    past_participle: str
    translation: str
