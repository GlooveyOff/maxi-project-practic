from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import MaintenanceRequest, User, UserRole, Well
from app.schemas import RequestCreate, RequestOut, RequestUpdate

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("", response_model=list[RequestOut])
def list_requests(
    well_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(MaintenanceRequest)
    if well_id is not None:
        query = query.filter(MaintenanceRequest.well_id == well_id)
    if status_filter:
        query = query.filter(MaintenanceRequest.status == status_filter)
    return query.order_by(MaintenanceRequest.created_at.desc()).all()


@router.post("", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.get(Well, payload.well_id):
        raise HTTPException(status_code=400, detail="Скважина не найдена")
    req = MaintenanceRequest(
        well_id=payload.well_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        author_id=current_user.id,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.patch("/{request_id}", response_model=RequestOut)
def update_request(
    request_id: int,
    payload: RequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = db.get(MaintenanceRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if current_user.role != UserRole.admin and req.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на изменение заявки")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(req, key, value)
    db.commit()
    db.refresh(req)
    return req


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = db.get(MaintenanceRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if current_user.role != UserRole.admin and req.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление заявки")
    db.delete(req)
    db.commit()
    return None
