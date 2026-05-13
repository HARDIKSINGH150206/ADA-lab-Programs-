"""Tests for schema validators and models."""
from datetime import datetime, timezone

import pytest

from app.schemas.auth import PhoneFieldValidator
from app.schemas.users import UserAdminUpdateRequest
from app.schemas.cases import CaseStepResponse
from app.schemas.evidence import EvidenceMetadataResponse, EvidenceResponse


def test_phone_validator_strips_non_digits():
    assert PhoneFieldValidator.validate_phone("+91 98765-43210") == "+919876543210"


def test_phone_validator_rejects_malformed_input():
    with pytest.raises(ValueError):
        PhoneFieldValidator.validate_phone("abc")


def test_user_admin_update_phone_validation():
    request = UserAdminUpdateRequest(phone_number="(+91) 98765 43210")
    assert request.phone_number == "+919876543210"


def test_case_step_response_allows_updated_at():
    step = CaseStepResponse(
        id="1",
        case_id="2",
        step_number="1",
        title="Review",
        description=None,
        status="pending",
        created_at=datetime.now(timezone.utc),
        updated_at=None,
    )
    assert step.status == "pending"


def test_evidence_metadata_response_includes_optional_fields():
    evidence = EvidenceResponse(
        id="1",
        case_id="2",
        file_name="salary.pdf",
        file_url="/uploads/evidence/salary.pdf",
        file_size="1234",
        mime_type="application/pdf",
        category="wage_slip",
        confidence_score="0.9",
        auto_tags=["wage", "salary"],
        extracted_text="Monthly salary slip",
        ai_summary="Salary slip showing unpaid wages",
        user_description=None,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
    )
    response = EvidenceMetadataResponse(
        evidence=evidence,
        extracted_text="Monthly salary slip",
        auto_tags=["wage", "salary"],
        ai_summary="Salary slip showing unpaid wages",
    )
    assert response.evidence.category == "wage_slip"
    assert response.auto_tags == ["wage", "salary"]
