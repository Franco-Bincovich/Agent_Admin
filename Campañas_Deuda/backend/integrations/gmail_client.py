"""
Wrapper de la Gmail API.

Maneja el flujo OAuth por usuario (tokens almacenados en DB hasheados).
Los destinatarios reciben el informe en CC — nunca a deudores individuales.
Sin conexión real hasta Sesión 19.
"""

from config.settings import settings
from utils.errors import AppError
from utils.logger import logger


async def get_authorization_url(user_id: str) -> str:
    """
    Genera la URL de autorización OAuth de Gmail para el usuario.

    Args:
        user_id: UUID del usuario que autoriza Gmail.

    Returns:
        URL de autorización de Google para redirigir al usuario.

    Raises:
        AppError: "GMAIL_NOT_CONFIGURED" (503) si las credenciales no están configuradas.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 19.
    """
    if not settings.gmail_client_id:
        raise AppError("Gmail OAuth no configurado", "GMAIL_NOT_CONFIGURED", 503)
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)


async def send_report(
    user_id: str,
    recipients_cc: list[str],
    subject: str,
    body: str,
    attachment_path: str,
) -> bool:
    """
    Envía el informe ejecutivo vía Gmail del usuario autenticado, en CC.

    Los destinatarios reciben el informe como copia — el sistema no contacta
    deudores individuales en ningún caso.

    Args:
        user_id: UUID del usuario remitente (para obtener sus tokens).
        recipients_cc: Lista de emails que reciben en CC.
        subject: Asunto del correo.
        body: Cuerpo del correo (texto plano).
        attachment_path: Ruta local del archivo .docx o .pdf a adjuntar.

    Returns:
        True si el envío fue exitoso.

    Raises:
        AppError: "GMAIL_UNAUTHORIZED" (401) si el token expiró o fue revocado.
        AppError: "GMAIL_SEND_FAILED" (503) si el envío falla.
        AppError: "NOT_IMPLEMENTED" (501) hasta Sesión 20.
    """
    logger.info(
        "Envío de informe vía Gmail (stub)",
        extra={"user_id": user_id, "recipients_count": len(recipients_cc)},
    )
    raise AppError("NOT_IMPLEMENTED", "NOT_IMPLEMENTED", 501)
