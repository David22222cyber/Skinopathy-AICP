"""
Data analysis utilities – basic summaries, advanced analytics, and AI narrative.
"""

from typing import List, Tuple

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import MAX_CATEGORY_UNIQUE


# ── Basic analysis ───────────────────────────────────────────────────

def compute_basic_analysis(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Basic numeric + categorical summaries.
    Returns (numeric_summary_str, categorical_summary_str).
    """
    if df.empty:
        return "(no numeric summary – no rows)", "(no categorical summary – no rows)"

    numeric_summary = "(no numeric columns)"
    cat_summary = "(no small categorical columns)"

    num_cols = df.select_dtypes(include="number")
    if not num_cols.empty:
        desc = num_cols.describe().T
        numeric_summary = desc.to_markdown()

    cat_frames = []
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        is_categorical = (
            df[col].dtype == "object"
            or dtype_str.startswith("category")
            or dtype_str in ("str", "string", "String")
            or hasattr(df[col].dtype, "na_value")  # pandas StringDtype
        )
        if is_categorical:
            vals = df[col].dropna()
            n_unique = vals.nunique()
            if 0 < n_unique <= MAX_CATEGORY_UNIQUE:
                vc = vals.value_counts().reset_index()
                vc.columns = [col, "count"]
                cat_frames.append(vc)

    if cat_frames:
        pieces = []
        for vc in cat_frames:
            col_name = vc.columns[0]
            pieces.append(f"Column: {col_name}\n" + vc.to_markdown(index=False))
        cat_summary = "\n\n".join(pieces)

    return numeric_summary, cat_summary


# ── Advanced analysis ────────────────────────────────────────────────

def compute_advanced_analysis(df: pd.DataFrame) -> str:
    """
    Next-level analysis: primary metric selection, tier segmentation,
    outlier detection, and numeric correlations.
    """
    if df.empty:
        return "No advanced analysis: result has no rows."

    numeric = df.select_dtypes(include="number").copy()
    numeric = numeric.dropna(axis=1, how="all")

    if numeric.empty:
        return "No advanced analysis: result has no numeric columns."

    lines: List[str] = []

    # Identify ID-like columns to skip
    id_cols = [
        c for c in numeric.columns
        if "id" in c.lower() or c.lower().endswith("_id")
    ]
    metric_candidates = [c for c in numeric.columns if c not in id_cols]
    primary_metric = metric_candidates[0] if metric_candidates else numeric.columns[0]
    s = numeric[primary_metric].dropna()

    lines.append(f"Primary metric used for deeper analysis: {primary_metric}")

    if s.nunique() > 1:
        q1, q2, q3 = s.quantile([0.25, 0.5, 0.75])
        lines.append(
            f"{primary_metric}: median={q2:.2f}, IQR=[{q1:.2f}, {q3:.2f}], "
            f"min={s.min():.2f}, max={s.max():.2f}."
        )

        # Quantile-based 3-tier segmentation
        try:
            tiers = pd.qcut(s, 3, labels=["low", "medium", "high"])
            seg_counts = tiers.value_counts().sort_index()
            total = len(s)
            lines.append("Quantile-based tiers for primary metric:")
            for level, count in seg_counts.items():
                pct = count * 100.0 / total
                lines.append(f"  - {level}: {count} rows ({pct:.1f}%)")
        except ValueError:
            lines.append("Not enough distinct values to build quantile-based tiers.")

        # Z-score outlier detection (> 2.5σ)
        mean = s.mean()
        std = s.std()
        if std and std > 0:
            z = (s - mean) / std
            outliers = s[abs(z) > 2.5]
            n_out = len(outliers)
            if n_out > 0:
                frac = n_out * 100.0 / len(s)
                lines.append(
                    f"Detected {n_out} potential outliers (> 2.5σ) "
                    f"for {primary_metric}, representing {frac:.1f}% of rows."
                )
            else:
                lines.append(f"No strong outliers (> 2.5σ) detected for {primary_metric}.")
        else:
            lines.append(f"Standard deviation is zero or undefined for {primary_metric}.")

    # Correlation analysis
    if numeric.shape[1] >= 2:
        corr = numeric.corr()
        pairs = []
        cols = list(corr.columns)
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                r = corr.iloc[i, j]
                pairs.append((cols[i], cols[j], r, abs(r)))

        strong_pairs = [p for p in pairs if p[3] >= 0.3]
        strong_pairs.sort(key=lambda x: x[3], reverse=True)
        if strong_pairs:
            lines.append("Top numeric correlations (|r| ≥ 0.30):")
            for col_a, col_b, r, _ in strong_pairs[:5]:
                lines.append(f"  - {col_a} vs {col_b}: r = {r:.2f}")
        else:
            lines.append("No strong numeric correlations (|r| ≥ 0.30) found.")
    else:
        lines.append("Correlation analysis skipped: only one numeric column present.")

    return "\n".join(lines)


# ── AI narrative summary ─────────────────────────────────────────────

def summarize_result(
    llm: ChatOpenAI,
    question: str,
    sql: str,
    df: pd.DataFrame,
    numeric_summary: str,
    cat_summary: str,
    advanced_summary: str,
) -> str:
    """Ask the LLM to produce a concise analytical summary."""
    preview = df.head(10).to_markdown(index=False) if not df.empty else "(no rows)"

    system = SystemMessage(
        content=(
            "You are a senior data analyst for a clinical research portal.\n"
            "You will see:\n"
            "1) The user's question\n"
            "2) The SQL query that was run\n"
            "3) A small preview of the result table\n"
            "4) A numeric summary (pandas describe)\n"
            "5) Simple categorical summaries (value counts)\n"
            "6) An automatic advanced analysis (tiers, outliers, correlations)\n\n"
            "Using all of that, provide a concise but insightful analysis:\n"
            "- Directly answer the question.\n"
            "- Mention key numbers (totals, averages, ranges, outliers).\n"
            "- Highlight any obvious patterns or imbalances.\n"
            "- Optionally comment on correlations or tiers if they matter.\n"
            "- If there are no rows, clearly say so.\n"
            "Write 3–7 sentences, no SQL and no markdown."
        )
    )
    human = HumanMessage(
        content=(
            f"User question:\n{question}\n\n"
            f"SQL query executed:\n{sql}\n\n"
            f"Result preview (first rows):\n{preview}\n\n"
            f"Numeric summary (describe()):\n{numeric_summary}\n\n"
            f"Categorical summary (value_counts):\n{cat_summary}\n\n"
            f"Advanced analysis (tiers, outliers, correlations):\n{advanced_summary}\n"
        )
    )
    resp = llm.invoke([system, human])
    return resp.content.strip()
