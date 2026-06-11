from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nombre: str = Field(min_length=2, max_length=100)
    rol: str = Field(default="analista", pattern="^(admin|analista)$")


class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    activo: bool | None = None
    rol: str | None = Field(default=None, pattern="^(admin|analista)$")


class UserResponse(BaseModel):
    id: UUID
    email: str
    nombre: str
    rol: str
    activo: bool
    created_at: datetime
