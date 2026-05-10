from schemas.auth import TokenResponse
from services.token_service import refresh_access_token, revoke_refresh_token


def refresh_tokens(refresh_token: str) -> TokenResponse:
    """
    Rota el par de tokens a partir de un refresh token válido.

    Delega toda la lógica de validación, comparación de hash y rotación a
    token_service.refresh_access_token, que implementa SEGURIDAD-PENTEST 2.5.

    Args:
        refresh_token: Token leído desde la cookie httpOnly del cliente.

    Returns:
        TokenResponse con nuevo access_token y nuevo refresh_token.

    Raises:
        AppError: UNAUTHORIZED 401 si el token es inválido o no existe en DB.
    """
    result = refresh_access_token(refresh_token)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
    )


def logout(user_id: str) -> dict:
    """
    Revoca todos los refresh tokens del usuario y confirma el cierre de sesión.

    Borra los tokens de DB para que no puedan reutilizarse aunque el cliente
    los conserve (SEGURIDAD-PENTEST 2.5).

    Args:
        user_id: UUID del usuario autenticado, extraído del JWT por el middleware.

    Returns:
        Dict con mensaje de confirmación.
    """
    revoke_refresh_token(user_id)
    return {"message": "Sesión cerrada correctamente."}
