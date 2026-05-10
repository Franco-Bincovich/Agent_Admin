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
