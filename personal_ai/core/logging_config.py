"""Structured logging helpers for Personal AI."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from .config import SETTINGS

_LOGGING_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    """Simple JSON-line formatter for machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return (
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"message":"%(message)s"}'
        ) % {
            "asctime": self.formatTime(record, self.datefmt),
            "levelname": record.levelname,
            "name": record.name,
            "message": message.replace('"', "'"),
        }


def configure_logging() -> None:
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    SETTINGS.log_file.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(getattr(logging, SETTINGS.log_level.upper(), logging.INFO))

    formatter = JsonFormatter()

    info_handler = RotatingFileHandler(SETTINGS.log_file, maxBytes=1_000_000, backupCount=3)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(SETTINGS.error_log_file, maxBytes=1_000_000, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    root.addHandler(info_handler)
    root.addHandler(error_handler)
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
