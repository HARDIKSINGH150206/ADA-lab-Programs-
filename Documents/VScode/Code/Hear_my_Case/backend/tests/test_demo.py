"""Tests for demo bootstrap helpers."""
import pytest

from app.services.demo import (
    DEMO_ADMIN_PASSWORD,
    DEMO_ADMIN_PHONE,
    DEMO_LAWYER_PASSWORD,
    DEMO_LAWYER_PHONE,
    DEMO_WORKER_PASSWORD,
    DEMO_WORKER_PHONE,
    seed_demo_data,
)


class _DummyScalarResult:
    def first(self):
        return None


class _DummyResult:
    def scalars(self):
        return _DummyScalarResult()


class _DummySession:
    def __init__(self):
        self.data = []

    async def execute(self, *args, **kwargs):
        return _DummyResult()

    def add_all(self, items):
        self.data.extend(items)

    def add(self, item):
        self.data.append(item)

    async def flush(self):
        return None

    async def commit(self):
        return None


@pytest.mark.asyncio
async def test_seed_demo_data_returns_credentials_when_not_seeded(monkeypatch):
    session = _DummySession()

    async def fake_generate_case_analysis(_data):
        return {
            "case_summary": "Demo summary",
            "applicable_laws": "Demo law",
            "what_should_happen": "Demo outcome",
            "next_steps": ["Step 1", "Step 2"],
        }

    monkeypatch.setattr("app.services.demo.generate_case_analysis", fake_generate_case_analysis)
    monkeypatch.setattr("app.services.demo.store_upload", lambda *args, **kwargs: "/uploads/demo/collective-notice.txt")
    result = await seed_demo_data(session)

    assert result["seeded"] is True
    assert result["credentials"]["worker_phone"] == DEMO_WORKER_PHONE
    assert result["credentials"]["admin_phone"] == DEMO_ADMIN_PHONE
    assert result["credentials"]["lawyer_phone"] == DEMO_LAWYER_PHONE


def test_demo_constants_exist():
    assert DEMO_WORKER_PASSWORD
    assert DEMO_ADMIN_PASSWORD
    assert DEMO_LAWYER_PASSWORD
