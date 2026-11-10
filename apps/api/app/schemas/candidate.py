import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.workforce import CandidateStatus


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str
    full_name: str | None
    city: str | None
    score: int | None
    status: CandidateStatus
    created_at: datetime


class CandidateExtraction(BaseModel):
    """Format attendu en sortie du LLM après lecture des messages du candidat."""

    full_name: str | None = None
    age: int | None = None
    city: str | None = None
    experience_years: float | None = None
    has_pro_card: bool | None = None
    availability: str | None = None  # ex. "nuit", "week-end", "immédiate"
    languages: list[str] = []
    summary: str | None = None
