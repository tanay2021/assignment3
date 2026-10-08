"""Loan application contract."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import Field

from src.domain.base import DomainModel
from src.domain.enums import LoanStatus, LoanType


class LoanApplication(DomainModel):
    """A loan application. It holds no AI or automated decision fields."""

    application_id: str = Field(min_length=1)
    applicant_id: str = Field(min_length=1)
    loan_type: LoanType
    requested_amount: Decimal = Field(gt=0)
    property_value: Optional[Decimal] = Field(default=None, gt=0)
    application_date: date
    status: LoanStatus = LoanStatus.SUBMITTED
