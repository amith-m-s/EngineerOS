"""Logging configuration with structured logging support."""

import json
import logging
import logging.config
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger

from .config import get_settings

settings = get_settings()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log records."""
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(UTC).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def setup_logging():
    """Setup structured logging configuration."""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "()": CustomJsonFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "json" if settings.environment != "development" else "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"],
        },
        "loggers": {
            "fastapi": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
    return logging.getLogger(__name__)
