import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    guest = "guest"
    employee = "employee"
    admin = "admin"


class FieldStatus(str, enum.Enum):
    exploration = "exploration"
    active = "active"
    suspended = "suspended"
    depleted = "depleted"


class WellStatus(str, enum.Enum):
    drilling = "drilling"
    operating = "operating"
    maintenance = "maintenance"
    closed = "closed"


class RequestStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    rejected = "rejected"


class RequestPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.employee, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requests: Mapped[list["MaintenanceRequest"]] = relationship(back_populates="author")


class OilField(Base):
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    reserves_tons: Mapped[float] = mapped_column(Float, nullable=False)
    discovered_year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[FieldStatus] = mapped_column(Enum(FieldStatus), default=FieldStatus.exploration, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    wells: Mapped[list["Well"]] = relationship(
        back_populates="field", cascade="all, delete-orphan"
    )


class Well(Base):
    __tablename__ = "wells"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    depth_m: Mapped[float] = mapped_column(Float, nullable=False)
    daily_output_tons: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[WellStatus] = mapped_column(Enum(WellStatus), default=WellStatus.drilling, nullable=False)
    drilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    field: Mapped["OilField"] = relationship(back_populates="wells")
    requests: Mapped[list["MaintenanceRequest"]] = relationship(
        back_populates="well", cascade="all, delete-orphan"
    )


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.new, nullable=False)
    priority: Mapped[RequestPriority] = mapped_column(Enum(RequestPriority), default=RequestPriority.medium, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    well: Mapped["Well"] = relationship(back_populates="requests")
    author: Mapped["User"] = relationship(back_populates="requests")
