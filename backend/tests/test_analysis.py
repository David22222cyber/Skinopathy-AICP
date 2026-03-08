"""
Unit tests for basic and advanced analysis functions.
"""

import pandas as pd

from src.analysis import compute_basic_analysis, compute_advanced_analysis, summarize_result


# ── Helpers ──────────────────────────────────────────────────────────

class FakeLLMResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, content: str):
        self._content = content

    def invoke(self, messages):
        return FakeLLMResponse(self._content)


# ── Tests: compute_basic_analysis ────────────────────────────────────

def test_compute_basic_analysis_empty_df():
    df = pd.DataFrame()
    n, c = compute_basic_analysis(df)
    assert "no rows" in n.lower()
    assert "no rows" in c.lower()


def test_compute_basic_analysis_numeric_and_categorical():
    df = pd.DataFrame({
        "age": [10, 20, 30, 40],
        "sex": ["M", "F", "M", "M"],
        "big_cat": list("abcd"),
    })
    n, c = compute_basic_analysis(df)
    assert "age" in n
    assert "Column: sex" in c
    assert "Column: big_cat" in c


# ── Tests: compute_advanced_analysis ─────────────────────────────────

def test_compute_advanced_analysis_no_rows():
    df = pd.DataFrame(columns=["x"])
    out = compute_advanced_analysis(df)
    assert "no rows" in out.lower()


def test_compute_advanced_analysis_no_numeric():
    df = pd.DataFrame({"x": ["a", "b"]})
    out = compute_advanced_analysis(df)
    assert "no numeric columns" in out.lower()


def test_compute_advanced_analysis_detects_primary_metric_and_corr():
    df = pd.DataFrame({
        "metric": [1, 2, 3, 4, 5],
        "other": [2, 4, 6, 8, 10],
    })
    out = compute_advanced_analysis(df)
    assert "primary metric" in out.lower()
    assert "correlation" in out.lower()
    assert "r = 1.00" in out or "r = 0.99" in out


# ── Tests: summarize_result ──────────────────────────────────────────

def test_summarize_result_calls_llm_and_returns_text():
    llm = FakeLLM("Here is a 3–7 sentence summary.")
    df = pd.DataFrame({"a": [1, 2]})
    out = summarize_result(
        llm=llm, question="What is X?", sql="SELECT 1",
        df=df, numeric_summary="num", cat_summary="cat",
        advanced_summary="adv",
    )
    assert "summary" in out.lower()
