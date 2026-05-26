from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    extracted_skills: list[str]
    fit_score: int = Field(ge=0, le=100)
    missing_keywords: list[str]
    suggestion: str
    raw_resume_text: str
