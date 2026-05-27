from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Brigade,
    BrigadeStatus,
    FieldStatus,
    MaintenanceRequest,
    OilField,
    RequestStatus,
    User,
    Well,
    WellStatus,
)

router = APIRouter(prefix="/stats", tags=["stats"])


class Overview(BaseModel):
    fields_total: int
    fields_active: int
    wells_total: int
    wells_operating: int
    requests_open: int
    requests_done: int
    daily_output_tons: float
    brigades_available: int


@router.get("/overview", response_model=Overview)
def overview(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    fields_total = db.query(func.count(OilField.id)).scalar() or 0
    fields_active = (
        db.query(func.count(OilField.id)).filter(OilField.status == FieldStatus.active).scalar() or 0
    )
    wells_total = db.query(func.count(Well.id)).scalar() or 0
    wells_operating = (
        db.query(func.count(Well.id)).filter(Well.status == WellStatus.operating).scalar() or 0
    )
    daily_output = (
        db.query(func.coalesce(func.sum(Well.daily_output_tons), 0.0))
        .filter(Well.status == WellStatus.operating)
        .scalar()
        or 0.0
    )
    requests_open = (
        db.query(func.count(MaintenanceRequest.id))
        .filter(MaintenanceRequest.status.in_([RequestStatus.new, RequestStatus.in_progress]))
        .scalar()
        or 0
    )
    requests_done = (
        db.query(func.count(MaintenanceRequest.id))
        .filter(MaintenanceRequest.status == RequestStatus.done)
        .scalar()
        or 0
    )
    brigades_available = (
        db.query(func.count(Brigade.id))
        .filter(Brigade.status == BrigadeStatus.available)
        .scalar()
        or 0
    )

    return Overview(
        fields_total=fields_total,
        fields_active=fields_active,
        wells_total=wells_total,
        wells_operating=wells_operating,
        requests_open=requests_open,
        requests_done=requests_done,
        daily_output_tons=float(daily_output),
        brigades_available=brigades_available,
    )
