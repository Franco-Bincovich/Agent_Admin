import re
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


class UserRole(str, Enum):
    administrador = "administrador"
    editor = "editor"
    viewer = "viewer"
    usuario = "usuario"


class UserResponse(BaseModel):
    id: str
    nombre: str
    email: str
    rol: UserRole
    activo: bool
    creado_en: str


class ProfileResponse(BaseModel):
    id: str
    nombre: str
    email: str
    username: Optional[str] = None
    rol: UserRole
    activo: bool
    creado_en: str


class UpdateProfileRequest(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    username: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return re.sub(r"[<>\"']", "", v).strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not _EMAIL_RE.match(v):
            raise ValueError("Email inválido")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def sanitize_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not re.fullmatch(r"[a-zA-Z0-9_.\-]+", v):
            raise ValueError("Solo letras, números, puntos, guiones y guiones bajos.")
        return v


class ChangePasswordRequest(BaseModel):
    password_actual: str = Field(min_length=1)
    password_nueva: str = Field(min_length=8, max_length=128)
    confirmar_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordRequest":
        if self.password_nueva != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden.")
        return self


class CreateUserRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=200)
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    rol: Literal["administrador", "usuario"]

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        return re.sub(r"[<>\"']", "", v).strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Email inválido")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.fullmatch(r"[a-zA-Z0-9_.\-]+", v):
            raise ValueError("Solo letras, números, puntos, guiones y guiones bajos.")
        return v
