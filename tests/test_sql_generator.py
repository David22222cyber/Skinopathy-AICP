"""
Unit tests for SQL generation and safety checks.
"""

import pytest

from src.config import SENSITIVE_PATIENT_COLUMNS
from src.models import Policy
from src.sql_generator import (
    extract_dbo_tables,
    contains_required_scope_filter,
    blocks_pii_for_pharmacy,
    generate_sql,
)


# ── Helpers ──────────────────────────────────────────────────────────

class FakeLLMResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, content: str):
        self._content = content

    def invoke(self, messages):
        return FakeLLMResponse(self._content)


# ── Tests: helper functions ──────────────────────────────────────────

def test_extract_dbo_tables_basic():
    sql = "SELECT * FROM dbo.patients p JOIN dbo.patient_notes n ON p.id=n.patient_id"
    assert extract_dbo_tables(sql) == {"patients", "patient_notes"}


def test_contains_required_scope_filter_true_literal():
    sql = "SELECT * FROM dbo.patients WHERE family_dr_id = 12"
    assert contains_required_scope_filter(sql, "family_dr_id", 12) is True


def test_contains_required_scope_filter_false():
    sql = "SELECT * FROM dbo.patients WHERE family_dr_id = 13"
    assert contains_required_scope_filter(sql, "family_dr_id", 12) is False


def test_blocks_pii_for_pharmacy_detects_column():
    sql = "SELECT first_name, last_name FROM dbo.patients"
    bad = blocks_pii_for_pharmacy(sql, {"first_name", "email"})
    assert bad == "first_name"


def test_blocks_pii_for_pharmacy_none_when_clean():
    sql = "SELECT COUNT(*) AS n FROM dbo.patients"
    bad = blocks_pii_for_pharmacy(sql, {"first_name", "email"})
    assert bad is None


# ── Tests: generate_sql ─────────────────────────────────────────────

def test_generate_sql_strips_markdown_and_allows_select():
    llm = FakeLLM("```sql\nSELECT TOP 5 * FROM dbo.patients WHERE family_dr_id = 7\n```")
    policy = Policy(
        role="doctor", scope_filter_hint="",
        required_filter_column="family_dr_id", required_filter_value=7,
        blocked_patient_columns=set(), notes="",
    )
    sql = generate_sql(llm, schema_text="(schema)", policy=policy, question="q")
    assert sql.lower().startswith("select")
    assert "```" not in sql
    assert "family_dr_id = 7" in sql.lower()


def test_generate_sql_blocks_non_select():
    llm = FakeLLM("DELETE FROM dbo.patients")
    policy = Policy("admin", "", None, None, set(), "")
    with pytest.raises(ValueError, match="non-SELECT|unsafe"):
        generate_sql(llm, "(schema)", policy, "q")


def test_generate_sql_blocks_dangerous_verbs():
    llm = FakeLLM("SELECT 1; DROP TABLE dbo.patients;")
    policy = Policy("admin", "", None, None, set(), "")
    with pytest.raises(ValueError, match="(?i)unsafe"):
        generate_sql(llm, "(schema)", policy, "q")


def test_generate_sql_enforces_scope_filter():
    llm = FakeLLM("SELECT * FROM dbo.patients")
    policy = Policy("doctor", "", "family_dr_id", 7, set(), "")
    with pytest.raises(ValueError, match="missing required scope filter"):
        generate_sql(llm, "(schema)", policy, "q")


def test_generate_sql_pharmacy_blocks_pii():
    llm = FakeLLM("SELECT first_name FROM dbo.patients WHERE pharmacy_id = 2")
    policy = Policy("pharmacy", "", "pharmacy_id", 2, set(SENSITIVE_PATIENT_COLUMNS), "")
    with pytest.raises(ValueError, match="(?i)pii"):
        generate_sql(llm, "(schema)", policy, "q")
