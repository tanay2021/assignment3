"""Application use cases for applicants and loan applications."""

from __future__ import annotations

import logging

from src.common.exceptions import NotFoundError
from src.data.repositories import ApplicantRepository, LoanApplicationRepository
from src.domain import Applicant, LoanApplication
from src.services._validation import require_id, require_model

logger = logging.getLogger("loan_processing_ai_poc.services.loan_application")


class LoanApplicationService:
    """Registers applicants and applications. Holds no approval logic."""

    def __init__(
        self, applicants: ApplicantRepository, applications: LoanApplicationRepository
    ) -> None:
        self._applicants = applicants
        self._applications = applications

    def register_applicant(self, applicant: Applicant) -> Applicant:
        require_model(applicant, Applicant, "applicant")
        self._applicants.save(applicant)
        logger.info("Registered applicant %s", applicant.applicant_id)
        return applicant

    def get_applicant(self, applicant_id: str) -> Applicant:
        applicant_id = require_id(applicant_id, "applicant_id")
        applicant = self._applicants.get(applicant_id)
        if applicant is None:
            raise NotFoundError(f"Applicant {applicant_id} was not found.")
        return applicant

    def submit_application(self, application: LoanApplication) -> LoanApplication:
        require_model(application, LoanApplication, "application")
        self.get_applicant(application.applicant_id)
        self._applications.save(application)
        logger.info("Stored application %s", application.application_id)
        return application

    def get_application(self, application_id: str) -> LoanApplication:
        application_id = require_id(application_id, "application_id")
        application = self._applications.get(application_id)
        if application is None:
            raise NotFoundError(f"Application {application_id} was not found.")
        return application

    def list_applications(self, applicant_id: str) -> list[LoanApplication]:
        applicant_id = require_id(applicant_id, "applicant_id")
        return self._applications.list_by_applicant(applicant_id)
