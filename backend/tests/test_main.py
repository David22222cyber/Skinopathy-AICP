import types
import pytest
import pandas as pd

import main as app


# -----------------------
# Helpers / Fakes
# -----------------------

class FakeLLMResponse:
    def __init__(self, content: str):
        self.content = content

class FakeLLM:
    """A tiny fake that returns whatever content we configure."""
    def __init__(self, content: str):
        self._content = content

    def invoke(self, messages):
        return FakeLLMResponse(self._content)


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


# -----------------------
# Unit tests: env
# -----------------------

def test_get_env_ok(monkeypatch):
    monkeypatch.setenv("X", "123")
    assert app.get_env("X") == "123"

def test_get_env_missing_exits(monkeypatch, capsys):
    monkeypatch.delenv("MISSING_ENV", raising=False)
    with pytest.raises(SystemExit) as e:
        app.get_env("MISSING_ENV")
    assert e.value.code == 1
    err = capsys.readouterr().err
    assert "ERROR: env var MISSING_ENV is not set" in err


# -----------------------
# Unit tests: RBAC context + policy
# -----------------------

def test_load_access_context_doctor_ok():
    engine = FakeEngine({
        "id": 1,
        "display_name": "Dr A",
        "role": "doctor",
        "doctor_id": 7,
        "pharmacy_id": None,
    })
    ctx = app.load_access_context(engine, api_key="k")
    assert ctx.role == "doctor"
    assert ctx.doctor_id == 7
    assert ctx.pharmacy_id is None

def test_load_access_context_invalid_key():
    engine = FakeEngine(None)
    with pytest.raises(ValueError) as e:
        app.load_access_context(engine, api_key="bad")
    assert "Invalid key" in str(e.value)

def test_load_access_context_unsupported_role():
    engine = FakeEngine({
        "id": 2,
        "display_name": "X",
        "role": "nurse",
        "doctor_id": None,
        "pharmacy_id": None,
    })
    with pytest.raises(ValueError) as e:
        app.load_access_context(engine, api_key="k")
    assert "Unsupported role" in str(e.value)

def test_build_policy_doctor_requires_doctor_id():
    ctx = app.AccessContext(user_id=1, display_name="Dr", role="doctor", doctor_id=None, pharmacy_id=None)
    with pytest.raises(ValueError) as e:
        app.build_policy(ctx)
    assert "must have doctor_id" in str(e.value)

def test_build_policy_pharmacy_requires_pharmacy_id():
    ctx = app.AccessContext(user_id=1, display_name="Pharm", role="pharmacy", doctor_id=None, pharmacy_id=None)
    with pytest.raises(ValueError) as e:
        app.build_policy(ctx)
    assert "must have pharmacy_id" in str(e.value)

def test_build_policy_admin_ok():
    ctx = app.AccessContext(user_id=9, display_name="Admin", role="admin", doctor_id=None, pharmacy_id=None)
    policy = app.build_policy(ctx)
    assert policy.role == "admin"
    assert policy.required_filter_column is None
    assert policy.required_filter_value is None


# -----------------------
# Unit tests: SQL parsing/safety helpers
# -----------------------

def test_extract_dbo_tables_basic():
    sql = "SELECT * FROM dbo.patients p JOIN dbo.patient_notes n ON p.id=n.patient_id"
    tables = app.extract_dbo_tables(sql)
    assert tables == {"patients", "patient_notes"}

def test_contains_required_scope_filter_true_literal():
    sql = "SELECT * FROM dbo.patients WHERE family_dr_id = 12"
    assert app.contains_required_scope_filter(sql, "family_dr_id", 12) is True

def test_contains_required_scope_filter_false():
    sql = "SELECT * FROM dbo.patients WHERE family_dr_id = 13"
    assert app.contains_required_scope_filter(sql, "family_dr_id", 12) is False

def test_blocks_pii_for_pharmacy_detects_column():
    sql = "SELECT first_name, last_name FROM dbo.patients"
    bad = app.blocks_pii_for_pharmacy(sql, {"first_name", "email"})
    assert bad == "first_name"

def test_blocks_pii_for_pharmacy_none_when_clean():
    sql = "SELECT COUNT(*) AS n FROM dbo.patients"
    bad = app.blocks_pii_for_pharmacy(sql, {"first_name", "email"})
    assert bad is None


# -----------------------
# Unit tests: generate_sql
# -----------------------

def test_generate_sql_strips_markdown_and_allows_select():
    llm = FakeLLM("```sql\nSELECT TOP 5 * FROM dbo.patients WHERE family_dr_id = 7\n```")
    policy = app.Policy(
        role="doctor",
        scope_filter_hint="",
        required_filter_column="family_dr_id",
        required_filter_value=7,
        blocked_patient_columns=set(),
        notes="",
    )
    sql = app.generate_sql(llm, schema_text="(schema)", policy=policy, question="q")
    assert sql.lower().startswith("select")
    assert "```" not in sql
    assert "family_dr_id = 7" in sql.lower()

def test_generate_sql_blocks_non_select():
    llm = FakeLLM("DELETE FROM dbo.patients")
    policy = app.Policy("admin", "", None, None, set(), "")
    with pytest.raises(ValueError) as e:
        app.generate_sql(llm, "(schema)", policy, "q")
    assert "non-SELECT" in str(e.value) or "unsafe" in str(e.value)

def test_generate_sql_blocks_dangerous_verbs_even_if_select_like():
    llm = FakeLLM("SELECT 1; DROP TABLE dbo.patients;")
    policy = app.Policy("admin", "", None, None, set(), "")
    with pytest.raises(ValueError) as e:
        app.generate_sql(llm, "(schema)", policy, "q")
    assert "unsafe" in str(e.value).lower() or "potentially unsafe" in str(e.value).lower()

def test_generate_sql_enforces_scope_filter_when_patients_referenced():
    llm = FakeLLM("SELECT * FROM dbo.patients")  # missing family_dr_id filter
    policy = app.Policy("doctor", "", "family_dr_id", 7, set(), "")
    with pytest.raises(ValueError) as e:
        app.generate_sql(llm, "(schema)", policy, "q")
    assert "missing required scope filter" in str(e.value).lower()

def test_generate_sql_pharmacy_blocks_pii():
    llm = FakeLLM("SELECT first_name FROM dbo.patients WHERE pharmacy_id = 2")
    policy = app.Policy("pharmacy", "", "pharmacy_id", 2, set(app.SENSITIVE_PATIENT_COLUMNS), "")
    with pytest.raises(ValueError) as e:
        app.generate_sql(llm, "(schema)", policy, "q")
    assert "pii" in str(e.value).lower()


# -----------------------
# Unit tests: analysis functions
# -----------------------

def test_compute_basic_analysis_empty_df():
    df = pd.DataFrame()
    n, c = app.compute_basic_analysis(df)
    assert "no rows" in n.lower()
    assert "no rows" in c.lower()

def test_compute_basic_analysis_numeric_and_categorical():
    df = pd.DataFrame({
        "age": [10, 20, 30, 40],
        "sex": ["M", "F", "M", "M"],
        "big_cat": list("abcd"),  # 4 unique -> still <= MAX_CATEGORY_UNIQUE default 10
    })
    n, c = app.compute_basic_analysis(df)
    assert "age" in n
    assert "Column: sex" in c
    assert "Column: big_cat" in c

def test_compute_advanced_analysis_no_rows():
    df = pd.DataFrame(columns=["x"])
    out = app.compute_advanced_analysis(df)
    assert "no rows" in out.lower()

def test_compute_advanced_analysis_no_numeric():
    df = pd.DataFrame({"x": ["a", "b"]})
    out = app.compute_advanced_analysis(df)
    assert "no numeric columns" in out.lower()

def test_compute_advanced_analysis_detects_primary_metric_and_corr():
    df = pd.DataFrame({
        "metric": [1, 2, 3, 4, 5],
        "other":  [2, 4, 6, 8, 10],  # perfect correlation
    })
    out = app.compute_advanced_analysis(df)
    assert "primary metric" in out.lower()
    assert "correlation" in out.lower()
    assert "r = 1.00" in out or "r = 0.99" in out


# -----------------------
# Unit tests: summarize_result
# -----------------------

def test_summarize_result_calls_llm_and_returns_text():
    llm = FakeLLM("Here is a 3–7 sentence summary.")
    df = pd.DataFrame({"a": [1, 2]})
    out = app.summarize_result(
        llm=llm,
        question="What is X?",
        sql="SELECT 1",
        df=df,
        numeric_summary="num",
        cat_summary="cat",
        advanced_summary="adv",
    )
    assert "summary" in out.lower()