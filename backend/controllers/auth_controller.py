from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserResponse
from services.auth_service import (
    authenticate_user,
    create_access_token,
    get_user_profile,
)
from services.token_service import create_refresh_token


async def login(payload: LoginRequest) -> TokenResponse:
    """
    Autentica un usuario y devuelve sus tokens de acceso.

    Delega la verificación de credenciales a auth_service.authenticate_user().
    Los errores de autenticación propagan con mensaje genérico (SEGURIDAD 2.3).

    Args:
        payload: Credenciales validadas por Pydantic.

    Returns:
        TokenResponse con access_token y refresh_token.
    """
    user = await authenticate_user(payload.username, payload.password)
    return TokenResponse(
        access_token=create_access_token(user["id"], user["rol"]),
        refresh_token=await create_refresh_token(user["id"]),
    )


async def get_me(user_id: str) -> UserResponse:
    """
    Retorna el perfil completo del usuario autenticado.

    Args:
        user_id: UUID del usuario extraído del payload JWT.

    Returns:
        UserResponse con los datos actuales del usuario en DB.
    """
    user = await get_user_profile(user_id)
    return UserResponse(
        id=str(user["id"]),
        nombre=user["nombre"],
        email=user["email"],
        rol=user["rol"],
        activo=user.get("activo", True),
        creado_en=user.get("created_at", user.get("creado_en", "")),
    )
