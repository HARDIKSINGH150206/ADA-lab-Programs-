"""Tests for AI helper behavior."""
import pytest

from app.services.ai import generate_case_analysis, infer_evidence_tags


@pytest.mark.asyncio
async def test_generate_case_analysis_falls_back_without_key(monkeypatch):
    monkeypatch.setattr("app.services.ai.settings.ANTHROPIC_API_KEY", "")
    result = await generate_case_analysis(
        {
            "case_type": "unpaid_wages",
            "employer_name": "ABC Manufacturing",
            "amount_owed": 50000,
        }
    )

    assert "case_summary" in result
    assert "next_steps" in result
    assert isinstance(result["next_steps"], list)


def test_infer_evidence_tags_from_filename():
    category, confidence, tags = infer_evidence_tags("salary_slip_april.pdf", "application/pdf")
    assert category == "wage_slip"
    assert confidence > 0.8
    assert "salary" in tags or "wage" in tags


def test_infer_evidence_tags_defaults_to_other():
    category, confidence, tags = infer_evidence_tags("random_file.bin", "application/octet-stream")
    assert category == "other"
    assert confidence == 0.5
    assert tags == ["other"]

