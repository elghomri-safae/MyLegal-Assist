"""Application-wide logging configuration."""

import logging
import sys

from backend.config.settings import get_settings


def configure_logging() -> None:
    """Configure the root logger according to the current application settings."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
