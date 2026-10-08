"""Starter entry point for the loan underwriting POC foundation."""

from __future__ import annotations

import argparse

from app.bootstrap import initialize_application
from app.healthcheck import main as healthcheck_main


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

    context = initialize_application()
    context.services.database.close()
    print("Application foundation initialized successfully.")
    print("This stage establishes the engineering foundation.")
    print("AI functionality will be implemented incrementally in subsequent development stages.")


if __name__ == "__main__":
    main()
