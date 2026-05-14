from pydantic import BaseModel, Field


class GeneratedQuestion(BaseModel):
    type: str = Field(default="adaptive_scenario")
    content: str
    focus_groups: list[str] = Field(default_factory=list)

    # Dùng để debug, chống lặp, và tăng đa dạng câu hỏi
    context: str | None = None
    question_style: str | None = None


class FinalReportResult(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)

    suitable_career_groups: list[str] = Field(default_factory=list)
    recommended_majors: list[str] = Field(default_factory=list)
    suitable_roles: list[str] = Field(default_factory=list)
    learning_suggestions: list[str] = Field(default_factory=list)

    career_advice: list[str] = Field(default_factory=list)


class AnswerQualityResult(BaseModel):
    is_valid: bool
    reason: str
    warning_message: str | None = None