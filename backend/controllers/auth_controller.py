from repositories.user_mutations_repo import create
from repositories.user_repo import find_by_email, find_by_id, find_by_username
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from schemas.user import UserResponse
from services.auth_service import create_access_token, hash_password, verify_password
from services.token_service import create_refresh_token
from utils.errors import AppError, ErrorCode
from utils.logger import log


def register(payload: RegisterRequest) -> TokenResponse:
    """
    Registra un usuario nuevo y devuelve sus tokens de acceso.

    Verifica que el email no esté en uso antes de crear. Nunca almacena
    la contraseña en texto plano — delega el hash a auth_service.

    Args:
        payload: Datos de registro validados por Pydantic.

    Returns:
        TokenResponse con access_token y refresh_token.

    Raises:
        AppError: code 'USER_ALREADY_EXISTS', status 409 si el email ya existe.
    """
    if find_by_email(payload.email):
        raise AppError("El email ya está registrado.", ErrorCode.USER_ALREADY_EXISTS, 409)

    user = create(
        email=payload.email,
        nombre=payload.nombre,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    return TokenResponse(
        access_token=create_access_token(user["id"], user["rol"]),
        refresh_token=create_refresh_token(user["id"]),
    )


def login(payload: LoginRequest) -> TokenResponse:
    """
    Autentica un usuario y devuelve sus tokens de acceso.

    Los errores siempre usan mensaje genérico para no revelar si el email
    existe o si la contraseña es incorrecta (SEGURIDAD-PENTEST 2.3).

    Args:
        payload: Credenciales validadas por Pydantic.

    Returns:
        TokenResponse con access_token y refresh_token.

    Raises:
        AppError: code 'UNAUTHORIZED', status 401 ante cualquier fallo de auth.
    """
    _INVALID = AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)

    user = find_by_username(payload.username)
    if not user:
        raise _INVALID
    pwd_ok = verify_password(payload.password, user.get("password_hash", ""))
    if not pwd_ok:
        raise _INVALID
    if not user.get("activo", False):
        raise _INVALID

    return TokenResponse(
        access_token=create_access_token(user["id"], user["rol"]),
        refresh_token=create_refresh_token(user["id"]),
    )


def get_me(user_id: str) -> UserResponse:
    """
    Retorna el perfil completo del usuario autenticado.

    Args:
        user_id: UUID del usuario extraído del payload JWT.

    Returns:
        UserResponse con los datos actuales del usuario en DB.

    Raises:
        AppError: code 'UNAUTHORIZED', status 401 si el usuario no existe.
    """
    user = find_by_id(user_id)
    if not user:
        # 401 en lugar de 404 — no confirmar si el ID existe (SEGURIDAD 2.4)
        raise AppError("No autorizado.", ErrorCode.UNAUTHORIZED, 401)
    return UserResponse(
        id=str(user["id"]),
        nombre=user["nombre"],
        email=user["email"],
        rol=user["rol"],
        activo=user.get("activo", True),
        creado_en=user.get("created_at", user.get("creado_en", "")),
    )
