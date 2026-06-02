import json
import logging
from datetime import UTC, datetime

# Campos estándar del LogRecord que no deben propagarse como "extra"
_STANDARD_FIELDS = frozenset(
    {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "exc_info",
        "exc_text",
        "message",
        "taskName",
    }
)


class _JSONFormatter(logging.Formatter):
    """Formateador de logs en JSON estructurado para facilitar el parseo en producción."""

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        log_data: dict = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.message,
            "module": record.module,
        }
        # Campos extra pasados con logger.info("...", extra={...})
        extra = {k: v for k, v in record.__dict__.items() if k not in _STANDARD_FIELDS}
        log_data.update(extra)
        return json.dumps(log_data, ensure_ascii=False, default=str)


def _build_logger() -> logging.Logger:
    log = logging.getLogger("app")
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_JSONFormatter())
        log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log


logger = _build_logger()
