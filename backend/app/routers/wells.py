from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import OilField, User, Well
from app.schemas import WellCreate, WellOut, WellUpdate

router = APIRouter(prefix="/wells", tags=["wells"])


@router.get("", response_model=list[WellOut])
def list_wells(
    field_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(Well)
    if field_id is not None:
        query = query.filter(Well.field_id == field_id)
    if status_filter:
        query = query.filter(Well.status == status_filter)
    return query.order_by(Well.field_id, Well.name).all()


@router.get("/{well_id}", response_model=WellOut)
def get_well(well_id: int, db: Session = Depends(get_db)):
    well = db.get(Well, well_id)
    if not well:
        raise HTTPException(status_code=404, detail="Скважина не найдена")
    return well


@router.post("", response_model=WellOut, status_code=status.HTTP_201_CREATED)
def create_well(
    payload: WellCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if not db.get(OilField, payload.field_id):
        raise HTTPException(status_code=400, detail="Месторождение не найдено")
    well = Well(**payload.model_dump())
    db.add(well)
    db.commit()
    db.refresh(well)
    return well


@router.put("/{well_id}", response_model=WellOut)
def update_well(
    well_id: int,
    payload: WellUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    well = db.get(Well, well_id)
    if not well:
        raise HTTPException(status_code=404, detail="Скважина не найдена")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(well, key, value)
    db.commit()
    db.refresh(well)
    return well


@router.delete("/{well_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_well(
    well_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    well = db.get(Well, well_id)
    if not well:
        raise HTTPException(status_code=404, detail="Скважина не найдена")
    db.delete(well)
    db.commit()
    return None
