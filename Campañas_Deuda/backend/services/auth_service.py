from schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from utils.errors import AppError


async def register_user(request: RegisterRequest) -> TokenResponse:
    """
    Lógica de negocio del registro de usuario.

    Hashea la contraseña con bcrypt, persiste en DB vía user_repo,
    emite access_token + refresh_token. El refresh se almacena hasheado.

    Args:
        request: Datos de registro validados por Pydantic.

    Returns:
        TokenResponse con el par de tokens.

    Raises:
        AppError: "DUPLICATE_EMAIL" (409) si el email ya existe.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def login_user(request: LoginRequest) -> TokenResponse:
    """
    Verifica credenciales y emite tokens.

    El mensaje de error es siempre genérico para no revelar si el usuario
    existe (principio de mínima información — SEGURIDAD-PENTEST §2.3).

    Args:
        request: Credenciales de login.

    Returns:
        TokenResponse con el par de tokens.

    Raises:
        AppError: "UNAUTHORIZED" (401) si las credenciales son incorrectas.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def refresh_tokens(refresh_token: str) -> TokenResponse:
    """
    Rota el refresh token con rotación obligatoria.

    Verifica que el token esté en DB, lo invalida e iemite un nuevo par.

    Args:
        refresh_token: Token de refresco actual.

    Returns:
        Nuevo TokenResponse.

    Raises:
        AppError: "UNAUTHORIZED" (401) si el token no existe o fue rotado.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def logout_user(refresh_token: str) -> None:
    """
    Elimina el refresh token de la DB (el cliente descarta el access_token).

    Args:
        refresh_token: Token a invalidar.

    Raises:
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 3.
    """
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
