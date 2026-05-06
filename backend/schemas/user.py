from enum import Enum

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    administrador = "administrador"
    editor = "editor"
    viewer = "viewer"


class UserResponse(BaseModel):
    id: str          # UUID serializado como str
    nombre: str
    email: EmailStr
    rol: UserRole
    activo: bool
    creado_en: str   # ISO 8601
