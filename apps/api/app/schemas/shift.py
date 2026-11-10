import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.operations import ShiftStatus


class ShiftCreate(BaseModel):
    site_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    agent_id: uuid.UUID | None = None


class ShiftOut(ShiftCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ShiftStatus
