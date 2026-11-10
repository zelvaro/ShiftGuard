import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_id
from app.core.db import get_db
from app.models import Candidate
from app.schemas.candidate import CandidateOut

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateOut])
def list_candidates(
    tenant_id: uuid.UUID = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[Candidate]:
    stmt = (
        select(Candidate)
        .where(Candidate.tenant_id == tenant_id)
        .order_by(Candidate.score.desc().nulls_last(), Candidate.created_at.desc())
    )
    return list(db.scalars(stmt))
