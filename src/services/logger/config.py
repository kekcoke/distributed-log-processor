# config.py

import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path

# =========================
# Core Settings (edit here)
# =========================
LOG_DIR = Path("/app/logs")
LOG_FILE = LOG_DIR / "app.log"

LOG_LEVEL_CONSOLE = "INFO"
LOG_LEVEL_FILE = "DEBUG"

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Rotation settings (size-based)
LOG_MAX_BYTES = 1 * 1024 * 1024  # 1MB
LOG_BACKUP_COUNT = 5


# =========================
# Setup
# =========================
LOG_DIR.mkdir(exist_ok=True)


def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "standard": {
                "format": LOG_FORMAT,
                "datefmt": LOG_DATE_FORMAT,
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": LOG_LEVEL_CONSOLE,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": LOG_LEVEL_FILE,
                "formatter": "standard",
                "filename": str(LOG_FILE),
                "maxBytes": LOG_MAX_BYTES,
                "backupCount": LOG_BACKUP_COUNT,
                "encoding": "utf-8",
            },
        },

        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    }

    logging.config.dictConfig(logging_config)


# Initialize once
setup_logging()
logger = logging.getLogger(__name__)