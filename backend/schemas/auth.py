import re

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=200)
    password: str = Field(min_length=8, max_length=128)
    nombre: str = Field(min_length=2, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Email inválido")
        return v.lower().strip()

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: str) -> str:
        v = re.sub(r"[<>\"']", "", v)
        return v.strip()


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

