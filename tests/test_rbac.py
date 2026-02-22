"""
Unit tests for RBAC – access context loading and policy building.
"""

import pytest

from src.config import get_env, SENSITIVE_PATIENT_COLUMNS
from src.models import AccessContext, Policy
from src.rbac import load_access_context, build_policy


# ── Helpers / Fakes ──────────────────────────────────────────────────

class FakeResult:
    """Mimic SQLAlchemy Result with .mappings().first()."""
    def __init__(self, row_dict_or_none):
        self._row = row_dict_or_none

    def mappings(self):
        return self

    def first(self):
        return self._row


class FakeConn:
    def __init__(self, row_dict_or_none=None):
        self._row = row_dict_or_none
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        return FakeResult(self._row)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeEngine:
    """Mimic engine.connect() context manager."""
    def __init__(self, row_dict_or_none=None):
        self._row = row_dict_or_none
        self.connect_calls = 0

    def connect(self):
        self.connect_calls += 1
        return FakeConn(self._row)


# ── Tests: get_env ───────────────────────────────────────────────────

def test_get_env_ok(monkeypatch):
    monkeypatch.setenv("X", "123")
    assert get_env("X") == "123"


def test_get_env_missing_exits(monkeypatch, capsys):
    monkeypatch.delenv("MISSING_ENV", raising=False)
    with pytest.raises(SystemExit) as e:
        get_env("MISSING_ENV")
    assert e.value.code == 1
    err = capsys.readouterr().err
    assert "ERROR: env var MISSING_ENV is not set" in err


# ── Tests: load_access_context ───────────────────────────────────────

def test_load_access_context_doctor_ok():
    engine = FakeEngine({
        "id": 1, "display_name": "Dr A", "role": "doctor",
        "doctor_id": 7, "pharmacy_id": None,
    })
    ctx = load_access_context(engine, api_key="k")
    assert ctx.role == "doctor"
    assert ctx.doctor_id == 7
    assert ctx.pharmacy_id is None


def test_load_access_context_invalid_key():
    engine = FakeEngine(None)
    with pytest.raises(ValueError, match="Invalid key"):
        load_access_context(engine, api_key="bad")


def test_load_access_context_unsupported_role():
    engine = FakeEngine({
        "id": 2, "display_name": "X", "role": "nurse",
        "doctor_id": None, "pharmacy_id": None,
    })
    with pytest.raises(ValueError, match="Unsupported role"):
        load_access_context(engine, api_key="k")


# ── Tests: build_policy ─────────────────────────────────────────────

def test_build_policy_doctor_requires_doctor_id():
    ctx = AccessContext(user_id=1, display_name="Dr", role="doctor",
                        doctor_id=None, pharmacy_id=None)
    with pytest.raises(ValueError, match="must have doctor_id"):
        build_policy(ctx)


def test_build_policy_pharmacy_requires_pharmacy_id():
    ctx = AccessContext(user_id=1, display_name="Pharm", role="pharmacy",
                        doctor_id=None, pharmacy_id=None)
    with pytest.raises(ValueError, match="must have pharmacy_id"):
        build_policy(ctx)


def test_build_policy_admin_ok():
    ctx = AccessContext(user_id=9, display_name="Admin", role="admin",
                        doctor_id=None, pharmacy_id=None)
    policy = build_policy(ctx)
    assert policy.role == "admin"
    assert policy.required_filter_column is None
    assert policy.required_filter_value is None
