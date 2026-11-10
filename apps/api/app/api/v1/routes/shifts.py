import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_id
from app.core.db import get_db
from app.models import Shift
from app.models.operations import ShiftStatus
from app.schemas.shift import ShiftCreate, ShiftOut

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.get("", response_model=list[ShiftOut])
def list_shifts(
    tenant_id: uuid.UUID = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[Shift]:
    stmt = select(Shift).where(Shift.tenant_id == tenant_id).order_by(Shift.starts_at)
    return list(db.scalars(stmt))


@router.post("", response_model=ShiftOut, status_code=201)
def create_shift(
    data: ShiftCreate, tenant_id: uuid.UUID = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> Shift:
    if data.ends_at <= data.starts_at:
        raise HTTPException(status_code=422, detail="ends_at doit être après starts_at")
    shift = Shift(
        tenant_id=tenant_id,
        **data.model_dump(),
        status=ShiftStatus.ASSIGNED if data.agent_id else ShiftStatus.OPEN,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift
