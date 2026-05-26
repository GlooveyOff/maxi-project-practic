from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import OilField, User
from app.schemas import FieldCreate, FieldOut, FieldUpdate

router = APIRouter(prefix="/fields", tags=["fields"])


def _to_out(field: OilField) -> FieldOut:
    data = FieldOut.model_validate(field)
    data.wells_count = len(field.wells)
    return data


@router.get("", response_model=list[FieldOut])
def list_fields(
    q: str | None = Query(default=None, description="Поиск по названию"),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(OilField)
    if q:
        query = query.filter(OilField.name.ilike(f"%{q}%"))
    if status_filter:
        query = query.filter(OilField.status == status_filter)
    return [_to_out(f) for f in query.order_by(OilField.name).all()]


@router.get("/{field_id}", response_model=FieldOut)
def get_field(field_id: int, db: Session = Depends(get_db)):
    field = db.get(OilField, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Месторождение не найдено")
    return _to_out(field)


@router.post("", response_model=FieldOut, status_code=status.HTTP_201_CREATED)
def create_field(
    payload: FieldCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(OilField).filter(OilField.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Месторождение с таким названием уже есть")
    field = OilField(**payload.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return _to_out(field)


@router.put("/{field_id}", response_model=FieldOut)
def update_field(
    field_id: int,
    payload: FieldUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    field = db.get(OilField, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Месторождение не найдено")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(field, key, value)
    db.commit()
    db.refresh(field)
    return _to_out(field)


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    field = db.get(OilField, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Месторождение не найдено")
    db.delete(field)
    db.commit()
    return None
