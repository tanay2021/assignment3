"""Application initialization shared by every entry point (CLI, Streamlit, tests).

It loads configuration, sets up logging and wires the services. It needs no
OpenAI API key and imports no UI framework.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.config import Settings, load_settings
from app.logging_config import setup_logging
from src.services import Services, create_services


@dataclass(frozen=True)
class ApplicationContext:
    settings: Settings
    logger: logging.Logger
    services: Services


def initialize_application(settings: Optional[Settings] = None) -> ApplicationContext:
    """Create the application context. Safe to call more than once."""
    settings = settings or load_settings()
    logger = setup_logging(settings.log_level)
    services = create_services(settings.database_file)
    logger.info("Application initialized (environment=%s)", settings.app_env)
    return ApplicationContext(settings=settings, logger=logger, services=services)
