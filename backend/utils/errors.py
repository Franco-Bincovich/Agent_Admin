from typing import Optional


class AppError(Exception):
    """Error de aplicación tipado. Usar siempre en lugar de excepciones genéricas."""

    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"error": True, "message": self.message, "code": self.code}


# ── Códigos estándar ─────────────────────────────────────────────────────────

class ErrorCode:
    # Auth
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Usuarios
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"

    # Generaciones
    GENERATION_NOT_FOUND = "GENERATION_NOT_FOUND"
    GENERATION_FAILED = "GENERATION_FAILED"

    # Archivos / extracción
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    EMPTY_FILE = "EMPTY_FILE"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"

    # Integraciones externas
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    PPTX_BUILD_ERROR = "PPTX_BUILD_ERROR"
    GAMMA_PUBLISH_ERROR = "GAMMA_PUBLISH_ERROR"

    # Genérico
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# ── Helpers de construcción rápida ───────────────────────────────────────────

def not_found(resource: str, identifier: Optional[str] = None) -> AppError:
    detail = f"{resource} '{identifier}' no encontrado." if identifier else f"{resource} no encontrado."
    return AppError(detail, ErrorCode.NOT_FOUND, 404)


def forbidden(action: str = "Acción no permitida para tu rol.") -> AppError:
    return AppError(action, ErrorCode.FORBIDDEN, 403)


def unauthorized(msg: str = "No autenticado.") -> AppError:
    return AppError(msg, ErrorCode.UNAUTHORIZED, 401)
