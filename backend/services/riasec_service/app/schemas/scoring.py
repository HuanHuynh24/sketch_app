from pydantic import BaseModel


class RiasecScore(BaseModel):
    R: float
    I: float
    A: float
    S: float
    E: float
    C: float


class RiasecEvidence(BaseModel):
    group: str
    quote: str | None
    strength: float
    confidence: float


class RiasecScoringResult(BaseModel):
    scores: RiasecScore
    confidence: RiasecScore
    reasoning: str
    detected_traits: list[str]
    primary_groups: list[str]
    evidence: list[RiasecEvidence]


class NextQuestion(BaseModel):
    type: str
    content: str
    focus_groups: list[str]
