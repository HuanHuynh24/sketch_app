from pydantic import BaseModel, Field


class RiasecScore(BaseModel):
    R: float = 0
    I: float = 0
    A: float = 0
    S: float = 0
    E: float = 0
    C: float = 0


class RiasecScoringResult(BaseModel):
    scores: RiasecScore
    confidence: RiasecScore
    reasoning: str
    detected_traits: list[str] = Field(default_factory=list)


class NextQuestion(BaseModel):
    type: str
    content: str
    focus_groups: list[str] = Field(default_factory=list)
