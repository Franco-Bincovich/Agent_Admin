from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from config.settings import get_settings
from repositories import token_repo
from repositories.user_repo import find_by_id as _find_user
from services.auth_service import ALGORITHM, create_access_token, verify_token
from utils.errors import AppError, ErrorCode

_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_token(token: str) -> str:
    """Hashea un token con bcrypt antes de guardarlo en DB."""
    return _PWD_CONTEXT.hash(token)


def create_refresh_token(user_id: str) -> str:
    """Genera un JWT de refresco, hashea con bcrypt y persiste el hash en DB. El texto plano nunca se almacena (SEGURIDAD-PENTEST 2.5)."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expiration_days
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    token_repo.save(user_id, hash_token(token), expire)
    return token


def refresh_access_token(refresh_token: str) -> dict:
    """Verifica un refresh token, rota el par y retorna nuevos tokens. Implementa SEGURIDAD-PENTEST 2.5."""
    _INVALID = AppError("No autorizado", ErrorCode.UNAUTHORIZED, 401)

    payload = verify_token(refresh_token)
    if payload.get("type") != "refresh":
        raise _INVALID

    user_id = payload["sub"]
    stored = token_repo.find_by_user(user_id)
    if not stored or not _PWD_CONTEXT.verify(refresh_token, stored["token_hash"]):
        raise _INVALID

    # Rotar: eliminar el viejo antes de generar el nuevo
    token_repo.delete(stored["id"])

    user = _find_user(user_id)
    if not user:
        raise _INVALID

    new_access = create_access_token(user["id"], user["rol"])
    new_refresh = create_refresh_token(user["id"])  # persiste en DB internamente

    return {"access_token": new_access, "refresh_token": new_refresh}


def revoke_refresh_token(user_id: str) -> None:
    """Revoca todos los refresh tokens del usuario en DB. Llamar en logout (SEGURIDAD-PENTEST 2.5)."""
    token_repo.delete_all_by_user(user_id)
