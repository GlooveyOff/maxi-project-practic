from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import (
    BrigadeStatus,
    FieldStatus,
    RequestPriority,
    RequestStatus,
    UserRole,
    WellStatus,
)


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class FieldBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    location: str = Field(min_length=2, max_length=200)
    reserves_tons: float = Field(ge=0)
    discovered_year: int = Field(ge=1900, le=2100)
    status: FieldStatus = FieldStatus.exploration
    description: str | None = None


class FieldCreate(FieldBase):
    pass


class FieldUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    location: str | None = None
    reserves_tons: float | None = Field(default=None, ge=0)
    discovered_year: int | None = Field(default=None, ge=1900, le=2100)
    status: FieldStatus | None = None
    description: str | None = None


class FieldOut(FieldBase):
    id: int
    created_at: datetime
    wells_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class WellBase(BaseModel):
    field_id: int
    name: str = Field(min_length=1, max_length=100)
    depth_m: float = Field(gt=0)
    daily_output_tons: float = Field(ge=0, default=0)
    status: WellStatus = WellStatus.drilling
    drilled_at: datetime | None = None


class WellCreate(WellBase):
    pass


class WellUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    depth_m: float | None = Field(default=None, gt=0)
    daily_output_tons: float | None = Field(default=None, ge=0)
    status: WellStatus | None = None
    drilled_at: datetime | None = None


class WellOut(WellBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrigadeBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    foreman: str = Field(min_length=2, max_length=150)
    members_count: int = Field(ge=1, le=50, default=1)
    phone: str | None = Field(default=None, max_length=40)
    status: BrigadeStatus = BrigadeStatus.available


class BrigadeCreate(BrigadeBase):
    pass


class BrigadeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    foreman: str | None = Field(default=None, min_length=2, max_length=150)
    members_count: int | None = Field(default=None, ge=1, le=50)
    phone: str | None = Field(default=None, max_length=40)
    status: BrigadeStatus | None = None


class BrigadeOut(BrigadeBase):
    id: int
    created_at: datetime
    active_requests: int = 0

    model_config = ConfigDict(from_attributes=True)


class RequestBase(BaseModel):
    well_id: int
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    priority: RequestPriority = RequestPriority.medium
    brigade_id: int | None = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    status: RequestStatus | None = None
    priority: RequestPriority | None = None
    brigade_id: int | None = None


class RequestOut(RequestBase):
    id: int
    status: RequestStatus
    author_id: int | None
    closed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
