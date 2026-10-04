"""Starter entry point for the loan underwriting POC foundation."""

from __future__ import annotations

import argparse

from app.config import load_settings
from app.healthcheck import main as healthcheck_main
from app.logging_config import setup_logging


def main() -> None:
    """Start the local application scaffold.

    The project is intentionally minimal at this stage; the future AI and loan
    workflows will be added in subsequent prompts without reworking the foundation.
    """
    parser = argparse.ArgumentParser(description="Intelligent Loan Underwriting Assistant foundation")
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run the lightweight environment health check.",
    )
    args = parser.parse_args()

    if args.health_check:
        raise SystemExit(healthcheck_main())

    settings = load_settings()
    logger = setup_logging(settings.log_level)
    logger.info("Application foundation initialized successfully.")
    print("Application foundation initialized successfully.")
    print("This stage establishes the engineering foundation.")
    print("AI functionality will be implemented incrementally in subsequent development stages.")


if __name__ == "__main__":
    main()
