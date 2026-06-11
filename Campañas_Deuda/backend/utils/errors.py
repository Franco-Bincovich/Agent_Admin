class AppError(Exception):
    """
    Error tipado de la aplicación.

    Todos los módulos lanzan AppError — nunca excepciones genéricas.
    El handler global en middleware/error_handler.py lo captura y devuelve
    siempre el mismo formato JSON: { error, message, code }.

    Args:
        message: Descripción legible para el usuario.
        code: Código interno en SNAKE_CASE (ej. "USER_NOT_FOUND").
        status_code: HTTP status a devolver. Default 500.
    """

    def __init__(self, message: str, code: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
