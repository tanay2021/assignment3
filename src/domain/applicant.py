"""Applicant contract (synthetic data only)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import Field

from src.domain.base import DomainModel
from src.domain.enums import EmploymentStatus


class Applicant(DomainModel):
    """A loan applicant (synthetic data only)."""

    applicant_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    date_of_birth: Optional[date] = None
    employment_status: Optional[EmploymentStatus] = None
    employer: Optional[str] = None
    annual_income: Optional[Decimal] = Field(default=None, ge=0)
    other_income: Optional[Decimal] = Field(default=None, ge=0, description="Annual income from other sources.")
    existing_liabilities: Optional[Decimal] = Field(
        default=None, ge=0, description="Total monthly debt obligations."
    )
