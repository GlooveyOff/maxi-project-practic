from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Brigade, BrigadeStatus, MaintenanceRequest, RequestStatus, User
from app.schemas import BrigadeCreate, BrigadeOut, BrigadeUpdate

router = APIRouter(prefix="/brigades", tags=["brigades"])


def _active_counts(db: Session) -> dict[int, int]:
    rows = (
        db.query(MaintenanceRequest.brigade_id, func.count(MaintenanceRequest.id))
        .filter(MaintenanceRequest.brigade_id.isnot(None))
        .filter(MaintenanceRequest.status.in_([RequestStatus.new, RequestStatus.in_progress]))
        .group_by(MaintenanceRequest.brigade_id)
        .all()
    )
    return {bid: cnt for bid, cnt in rows}


def _to_out(brigade: Brigade, counts: dict[int, int]) -> BrigadeOut:
    data = BrigadeOut.model_validate(brigade)
    data.active_requests = counts.get(brigade.id, 0)
    return data


@router.get("", response_model=list[BrigadeOut])
def list_brigades(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Brigade)
    if status_filter:
        try:
            query = query.filter(Brigade.status == BrigadeStatus(status_filter))
        except ValueError:
            return []
    brigades = query.order_by(Brigade.name).all()
    counts = _active_counts(db)
    return [_to_out(b, counts) for b in brigades]


@router.get("/{brigade_id}", response_model=BrigadeOut)
def get_brigade(
    brigade_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    brigade = db.get(Brigade, brigade_id)
    if not brigade:
        raise HTTPException(status_code=404, detail="Бригада не найдена")
    return _to_out(brigade, _active_counts(db))


@router.post("", response_model=BrigadeOut, status_code=status.HTTP_201_CREATED)
def create_brigade(
    payload: BrigadeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(Brigade).filter(Brigade.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Бригада с таким названием уже есть")
    brigade = Brigade(**payload.model_dump())
    db.add(brigade)
    db.commit()
    db.refresh(brigade)
    return _to_out(brigade, {})


@router.patch("/{brigade_id}", response_model=BrigadeOut)
def update_brigade(
    brigade_id: int,
    payload: BrigadeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    brigade = db.get(Brigade, brigade_id)
    if not brigade:
        raise HTTPException(status_code=404, detail="Бригада не найдена")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(brigade, key, value)
    db.commit()
    db.refresh(brigade)
    return _to_out(brigade, _active_counts(db))


@router.delete("/{brigade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brigade(
    brigade_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    brigade = db.get(Brigade, brigade_id)
    if not brigade:
        raise HTTPException(status_code=404, detail="Бригада не найдена")
    db.delete(brigade)
    db.commit()
    return None
