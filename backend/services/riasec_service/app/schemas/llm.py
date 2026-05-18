from pydantic import BaseModel


class GeneratedQuestion(BaseModel):
    type: str
    content: str
    focus_groups: list[str]
    context: str
    question_style: str
    expected_signals: dict[str, list[str]] | None = None
    scoring_rubric: dict[str, str] | None = None


class FinalReportResult(BaseModel):
    summary: str
    strengths: list[str]
    suitable_career_groups: list[str]
    recommended_majors: list[str]
    suitable_roles: list[str]
    learning_suggestions: list[str]
    career_advice: list[str]


class AnswerQualityResult(BaseModel):
    is_valid: bool
    reason: str
    warning_message: str | None
