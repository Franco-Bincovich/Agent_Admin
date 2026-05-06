from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config.settings import get_settings
from utils.errors import AppError, ErrorCode

ALGORITHM = "HS256"
_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hashea una contraseña en texto plano con bcrypt."""
    return _PWD_CONTEXT.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica que una contraseña en texto plano coincide con su hash bcrypt."""
    return _PWD_CONTEXT.verify(plain, hashed)


def create_access_token(user_id: str, role: str) -> str:
    """
    Genera un JWT de acceso de corta duración.

    Args:
        user_id: ID del usuario (UUID como str).
        role: Rol del usuario. Valores: 'administrador' | 'editor' | 'viewer'.

    Returns:
        Token JWT firmado con HS256.
    """
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


def create_refresh_token(user_id: str) -> str:
    """
    Genera un JWT de refresco de larga duración.

    Incluye únicamente sub y type. No contiene rol ni permisos.
    Al usarlo, el token anterior debe invalidarse (rotación obligatoria).

    Args:
        user_id: ID del usuario (UUID como str).

    Returns:
        Token JWT firmado con HS256.
    """
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
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un JWT firmado con la secret del entorno.

    No valida el campo 'type' — el llamador es responsable de esa verificación.
    Ante cualquier error de decodificación lanza AppError con mensaje genérico
    para no revelar información interna (SEGURIDAD-PENTEST 2.3).

    Args:
        token: JWT en formato string.

    Returns:
        Payload decodificado como dict.

    Raises:
        AppError: code 'UNAUTHORIZED', status 401 si el token es inválido o expiró.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Mensaje genérico — no informar si expiró, si la firma es incorrecta, etc.
        raise AppError("No autorizado", ErrorCode.UNAUTHORIZED, 401)
