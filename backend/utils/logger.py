import logging
import sys
from typing import Any


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("agent_admin")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


log = _build_logger()


# ── Eventos de negocio (únicos llamadores permitidos fuera de este módulo) ───

def log_generation_started(user_id: str, generation_id: str, template: str) -> None:
    log.info(f"generation.started | user={user_id} gen={generation_id} template={template}")


def log_generation_completed(user_id: str, generation_id: str) -> None:
    log.info(f"generation.completed | user={user_id} gen={generation_id}")


def log_generation_failed(user_id: str, generation_id: str, reason: str) -> None:
    log.error(f"generation.failed | user={user_id} gen={generation_id} reason={reason}")


def log_user_registered(user_id: str, email: str) -> None:
    log.info(f"user.registered | user={user_id} email={email}")


def log_pipeline_step(step: str, detail: Any = None) -> None:
    log.debug(f"pipeline.step | step={step} detail={detail}")
