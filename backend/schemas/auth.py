import re

from pydantic import BaseModel, EmailStr, Field, field_validator

_VALID_ROLES = {"administrador", "editor", "viewer"}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nombre: str = Field(min_length=2, max_length=100)
    rol: str = Field(default="editor")

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r"[<>\"']", "", v)
        return v.strip()

    @field_validator("rol")
    @classmethod
    def validate_rol(cls, v: str) -> str:
        if v not in _VALID_ROLES:
            raise ValueError(f"Rol inválido. Valores permitidos: {', '.join(_VALID_ROLES)}.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
