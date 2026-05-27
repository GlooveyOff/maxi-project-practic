from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Brigade, MaintenanceRequest, RequestStatus, User, UserRole, Well
from app.schemas import RequestCreate, RequestOut, RequestUpdate

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("", response_model=list[RequestOut])
def list_requests(
    well_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(MaintenanceRequest)
    if well_id is not None:
        query = query.filter(MaintenanceRequest.well_id == well_id)
    if status_filter:
        query = query.filter(MaintenanceRequest.status == status_filter)
    if priority:
        query = query.filter(MaintenanceRequest.priority == priority)
    return query.order_by(MaintenanceRequest.created_at.desc()).all()


@router.post("", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.get(Well, payload.well_id):
        raise HTTPException(status_code=400, detail="Скважина не найдена")
    if payload.brigade_id is not None and not db.get(Brigade, payload.brigade_id):
        raise HTTPException(status_code=400, detail="Бригада не найдена")
    req = MaintenanceRequest(
        well_id=payload.well_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        brigade_id=payload.brigade_id,
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
    updates = payload.model_dump(exclude_unset=True)
    if "brigade_id" in updates and updates["brigade_id"] is not None:
        if not db.get(Brigade, updates["brigade_id"]):
            raise HTTPException(status_code=400, detail="Бригада не найдена")
    for key, value in updates.items():
        setattr(req, key, value)
    if req.status == RequestStatus.done and req.closed_at is None:
        req.closed_at = datetime.now(timezone.utc)
    elif req.status != RequestStatus.done:
        req.closed_at = None
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
