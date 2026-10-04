"""Reusable logging setup for local project development."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from app.config import ROOT_DIR, VALID_LOG_LEVELS

DEFAULT_LOG_DIR = ROOT_DIR / "logs"


def setup_logging(
    log_level: str | None = None,
    log_dir: str | Path | None = None,
) -> logging.Logger:
    """Create a console and file logger with consistent formatting."""
    configured_level = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()
    if configured_level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"LOG_LEVEL must be one of: {', '.join(sorted(VALID_LOG_LEVELS))}"
        )

    target_dir = Path(log_dir) if log_dir is not None else DEFAULT_LOG_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("loan_processing_ai_poc")
    logger.setLevel(configured_level)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(configured_level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(target_dir / "application.log", encoding="utf-8")
    file_handler.setLevel(configured_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logging initialized for the Intelligent Loan Underwriting Assistant foundation.")
    return logger
