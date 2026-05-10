from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config.settings import get_settings
from repositories.user_mutations_repo import create as create_user_record
from repositories.user_repo import find_by_email, find_by_id, find_by_username
from schemas.auth import RegisterRequest
from utils.errors import AppError, ErrorCode
from utils.logger import log

ALGORITHM = "HS256"
_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano con bcrypt."""
    return _PWD_CONTEXT.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica que una contraseña en texto plano coincide con su hash bcrypt."""
    return _PWD_CONTEXT.verify(plain[:72], hashed)


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


def register_user(payload: RegisterRequest) -> dict:
    """
    Registra un usuario nuevo verificando unicidad de email.

    Verifica que el email no esté en uso antes de crear. Nunca almacena
    la contraseña en texto plano — delega el hash a hash_password.

    Args:
        payload: Datos de registro validados por Pydantic.

    Returns:
        Dict con los datos del usuario creado.

    Raises:
        AppError: code 'USER_ALREADY_EXISTS', status 409 si el email ya existe.
    """
    if find_by_email(payload.email):
        raise AppError("El email ya está registrado.", ErrorCode.USER_ALREADY_EXISTS, 409)
    user = create_user_record(
        email=payload.email,
        nombre=payload.nombre,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    log.info("Usuario registrado", extra={"user_id": str(user["id"])})
    return user


def authenticate_user(username: str, password: str) -> dict:
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
    user = find_by_username(username)
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


def get_user_profile(user_id: str) -> dict:
    """
    Retorna el perfil del usuario autenticado.

    Args:
        user_id: UUID del usuario extraído del payload JWT.

    Returns:
        Dict con los datos del usuario en DB.

    Raises:
        AppError: code 'UNAUTHORIZED', status 401 si el usuario no existe.
    """
    user = find_by_id(user_id)
    if not user:
        raise AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)
    return user
