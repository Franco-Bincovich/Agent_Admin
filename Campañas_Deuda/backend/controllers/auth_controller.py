from schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from utils.errors import AppError


async def register_user(request: RegisterRequest) -> TokenResponse:
    """
    Orquesta el registro de un nuevo usuario.

    Valida que el email no esté duplicado, hashea la contraseña,
    persiste el usuario y emite un par de tokens JWT.

    Args:
        request: Datos de registro (email, password, nombre).

    Returns:
        TokenResponse con access_token y refresh_token.

    Raises:
        AppError: "DUPLICATE_EMAIL" (409) si el email ya existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def login_user(request: LoginRequest) -> TokenResponse:
    """
    Orquesta el login con email y contraseña.

    Verifica credenciales, genera tokens y registra el evento.

    Args:
        request: Credenciales de login.

    Returns:
        TokenResponse con access_token y refresh_token.

    Raises:
        AppError: "UNAUTHORIZED" (401) si las credenciales son incorrectas.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def refresh_tokens(request: RefreshRequest) -> TokenResponse:
    """
    Rota el refresh token y emite nuevos tokens.

    Invalida el token anterior (rotación obligatoria).

    Args:
        request: refresh_token actual.

    Returns:
        Nuevo par de tokens.

    Raises:
        AppError: "UNAUTHORIZED" (401) si el token es inválido o ya fue rotado.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def logout_user(request: RefreshRequest) -> None:
    """
    Invalida el refresh token del usuario.

    Args:
        request: refresh_token a invalidar.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
