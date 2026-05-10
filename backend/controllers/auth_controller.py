from schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from schemas.user import UserResponse
from services.auth_service import (
    authenticate_user,
    create_access_token,
    get_user_profile,
    register_user,
)
from services.token_service import create_refresh_token


def register(payload: RegisterRequest) -> TokenResponse:
    """
    Registra un usuario nuevo y devuelve sus tokens de acceso.

    Delega la validación de unicidad y creación a auth_service.register_user().
    Construye los tokens a partir del usuario creado.

    Args:
        payload: Datos de registro validados por Pydantic.

    Returns:
        TokenResponse con access_token y refresh_token.
    """
    user = register_user(payload)
    return TokenResponse(
        access_token=create_access_token(user["id"], user["rol"]),
        refresh_token=create_refresh_token(user["id"]),
    )


def login(payload: LoginRequest) -> TokenResponse:
    """
    Autentica un usuario y devuelve sus tokens de acceso.

    Delega la verificación de credenciales a auth_service.authenticate_user().
    Los errores de autenticación propagan con mensaje genérico (SEGURIDAD 2.3).

    Args:
        payload: Credenciales validadas por Pydantic.

    Returns:
        TokenResponse con access_token y refresh_token.
    """
    user = authenticate_user(payload.username, payload.password)
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
    """
    user = get_user_profile(user_id)
    return UserResponse(
        id=str(user["id"]),
        nombre=user["nombre"],
        email=user["email"],
        rol=user["rol"],
        activo=user.get("activo", True),
        creado_en=user.get("created_at", user.get("creado_en", "")),
    )
