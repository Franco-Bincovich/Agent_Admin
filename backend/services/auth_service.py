from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from config.settings import get_settings
from repositories.user_repo import find_by_id, find_by_username
from utils.errors import AppError, ErrorCode
from utils.logger import log

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano con bcrypt."""
    return bcrypt.hashpw(
        password.encode("utf-8")[:72],
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica que una contraseña en texto plano coincide con su hash bcrypt."""
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8")[:72],
            hashed.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(user_id: str, role: str) -> str:
    """Genera un JWT de acceso de corta duración firmado con HS256."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verifica y decodifica un JWT; lanza UNAUTHORIZED 401 ante cualquier fallo (SEGURIDAD-PENTEST 2.3)."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Mensaje genérico — no informar si expiró, si la firma es incorrecta, etc.
        raise AppError("No autorizado", ErrorCode.UNAUTHORIZED, 401)


async def authenticate_user(username: str, password: str) -> dict:
    """
    Verifica credenciales y retorna el usuario si son válidas.

    Los errores siempre usan mensaje genérico para no revelar si el username
    existe o si la contraseña es incorrecta (SEGURIDAD-PENTEST 2.3).

    Args:
        username: Nombre de usuario del candidato.
        password: Contraseña en texto plano a verificar.

    Returns:
        Dict con los datos del usuario autenticado.

    Raises:
        AppError: code 'UNAUTHORIZED', status 401 ante cualquier fallo de auth.
    """
    _INVALID = AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)
    user = await find_by_username(username)
    if not user:
        log.warning("Intento de login fallido", extra={"username": username})
        raise _INVALID
    if not verify_password(password, user.get("password_hash", "")):
        log.warning("Intento de login fallido", extra={"username": username})
        raise _INVALID
    if not user.get("activo", False):
        log.warning("Intento de login fallido", extra={"username": username})
        raise _INVALID
    log.info("Login exitoso", extra={"user_id": str(user["id"])})
    return user


async def get_user_profile(user_id: str) -> dict:
    """
    Retorna el perfil del usuario autenticado.

    Args:
        user_id: UUID del usuario extraído del payload JWT.

    Returns:
        Dict con los datos del usuario en DB.

    Raises:
        AppError: code 'UNAUTHORIZED', status 401 si el usuario no existe.
    """
    user = await find_by_id(user_id)
    if not user:
        raise AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)
    return user
