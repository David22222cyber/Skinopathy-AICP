import os
import sys
import re
from typing import List, Tuple

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# ---------------- CONFIG ----------------

load_dotenv()  # load .env in same folder

MODEL_NAME = "gpt-4.1-mini"
MAX_SCHEMA_CHARS = 4000          # max schema text sent to LLM
MAX_PREVIEW_ROWS = 20            # rows shown in console
MAX_CATEGORY_UNIQUE = 10         # <= this many uniques → treat as categorical


def get_env(name: str) -> str:
    """Get environment variable or exit with clear error."""
    v = os.getenv(name)
    if not v:
        print(f"ERROR: env var {name} is not set", file=sys.stderr)
        sys.exit(1)
    return v


# ---------------- DB SETUP ----------------

def init_engine():
    """Create SQLAlchemy engine and test connection."""
    db_uri = get_env("DB_URI")
    engine = create_engine(db_uri, echo=False, future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print("ERROR: could not connect to DB:", e, file=sys.stderr)
        sys.exit(1)
    print("[init] Connected to DB.")
    return engine


def build_schema_summary(engine) -> str:
    """Describe dbo tables/columns for the LLM, truncated to MAX_SCHEMA_CHARS."""
    insp = inspect(engine)
    tables: List[str] = insp.get_table_names(schema="dbo")
    lines = []
    for t in sorted(tables):
        cols = insp.get_columns(t, schema="dbo")
        col_desc = ", ".join(f"{c['name']} {str(c['type'])}" for c in cols)
        lines.append(f"Table dbo.{t}({col_desc})")
    schema_text = "\n".join(lines)
    if len(schema_text) > MAX_SCHEMA_CHARS:
        schema_text = schema_text[:MAX_SCHEMA_CHARS] + "\n... (schema truncated)"
    return schema_text


# ---------------- LLM SETUP ----------------

def init_llm() -> ChatOpenAI:
    _ = get_env("OPENAI_API_KEY")  # fail early if missing
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    print(f"[init] Using LLM model: {MODEL_NAME}")
    return llm


def generate_sql(llm: ChatOpenAI, schema_text: str, question: str) -> str:
    """Ask the LLM to write a single safe SELECT query for SQL Server."""
    system = SystemMessage(
        content=(
            "You are an expert SQL assistant for a SQL Server (T-SQL) database.\n"
            "You have READ-ONLY access.\n"
            "IMPORTANT TABLE RULES:\n"
            "- When counting or identifying patients, ALWAYS use dbo.patients as the primary table.\n"
            "- Do NOT infer total patients from patient_notes, walkin_cases, or other auxiliary tables.\n\n"
            "Task: Given a user question and the schema, write exactly ONE SQL SELECT query that answers it.\n"
            "Rules:\n"
            "- Only use SELECT, FROM, JOIN, WHERE, GROUP BY, ORDER BY, and TOP.\n"
            "- DO NOT use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or MERGE.\n"
            "- Use dbo.<table> names explicitly.\n"
            "- Return ONLY the SQL query, with no explanation and no backticks."
        )
    )
    human = HumanMessage(
        content=(
            f"Schema:\n{schema_text}\n\n"
            f"User question: {question}\n\n"
            "Write the SQL query now."
        )
    )

    resp = llm.invoke([system, human])
    sql = resp.content.strip()

    # Remove markdown fences if the model added them
    if sql.lower().startswith("```sql"):
        sql = sql.strip("`")
        sql = re.sub(r"^sql", "", sql, flags=re.IGNORECASE).strip()
    elif sql.startswith("```"):
        sql = sql.strip("`").strip()

    # Enforce SELECT-only and block dangerous verbs
    if not re.match(r"(?is)^\s*select\b", sql):
        raise ValueError(f"Llm generated non-SELECT query, blocked: {sql[:120]}...")
    if re.search(r"\b(insert|update|delete|drop|alter|truncate|create|merge)\b", sql, re.IGNORECASE):
        raise ValueError(f"Llm generated potentially unsafe query, blocked: {sql[:120]}...")

    return sql


# ---------------- BASIC ANALYSIS ----------------

def compute_basic_analysis(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Basic numeric + categorical summaries.
    Returns: (numeric_summary_str, categorical_summary_str)
    """
    if df.empty:
        return "(no numeric summary – no rows)", "(no categorical summary – no rows)"

    numeric_summary = "(no numeric columns)"
    cat_summary = "(no small categorical columns)"

    # numeric summary
    num_cols = df.select_dtypes(include="number")
    if not num_cols.empty:
        desc = num_cols.describe().T
        numeric_summary = desc.to_markdown()

    # categorical: small-unique columns
    cat_frames = []
    for col in df.columns:
        if df[col].dtype == "object" or str(df[col].dtype).startswith("category"):
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


# ---------------- NEXT-LEVEL ANALYSIS ----------------

def compute_advanced_analysis(df: pd.DataFrame) -> str:
    """
    Next-level analysis: choose a primary metric, segment into tiers,
    detect outliers, and compute numeric correlations.
    Returns: free-text technical summary (for the LLM + console).
    """
    if df.empty:
        return "No advanced analysis: result has no rows."

    numeric = df.select_dtypes(include="number").copy()
    numeric = numeric.dropna(axis=1, how="all")

    if numeric.empty:
        return "No advanced analysis: result has no numeric columns."

    lines: List[str] = []

    # Identify ID-like columns so we can focus on more meaningful metrics
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

        # Quantile-based 3-tier segmentation (low / medium / high)
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

        # Z-score outlier detection (> 2.5 standard deviations)
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

    # Correlation analysis among numeric columns
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


def summarize_result(
    llm: ChatOpenAI,
    question: str,
    sql: str,
    df: pd.DataFrame,
    numeric_summary: str,
    cat_summary: str,
    advanced_summary: str,
) -> str:
    """Ask LLM to provide a short analytical summary using all context."""
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


# ---------------- MAIN LOOP ----------------

def main():
    print("=== AICP Research Portal: NL → SQL Assistant (Next-Level Analysis) ===\n")

    engine = init_engine()
    schema_text = build_schema_summary(engine)
    llm = init_llm()

    while True:
        try:
            q = input("\nAsk a question about the database (or 'quit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not q:
            continue
        if q.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        print(f"\n[user] {q}")

        # 1) Generate SQL
        try:
            sql = generate_sql(llm, schema_text, q)
        except Exception as e:
            print("\n[ERROR] Could not generate a safe SQL query.")
            print("Details:", e)
            continue

        print("\n[SQL generated]")
        print(sql)

        # 2) Execute SQL safely
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(sql, conn)
        except Exception as e:
            print("\n[ERROR] Database error while running the query.")
            print("Details:", e)
            continue

        # 3) Show preview
        print("\n[Preview of results (up to 20 rows)]")
        if df.empty:
            print("(no rows returned)")
        else:
            print(df.head(MAX_PREVIEW_ROWS).to_string(index=False))

        # 4) Basic analysis
        numeric_summary, cat_summary = compute_basic_analysis(df)
        print("\n[Basic numeric summary]")
        print(numeric_summary)
        print("\n[Basic categorical summary]")
        print(cat_summary)

        # 5) Next-level analysis
        advanced_summary = compute_advanced_analysis(df)
        print("\n[Advanced analysis (automatic)]")
        print(advanced_summary)

        # 6) LLM narrative analysis
        try:
            summary = summarize_result(
                llm, q, sql, df, numeric_summary, cat_summary, advanced_summary
            )
            print("\n[AI Analysis]")
            print(summary)
        except Exception as e:
            print("\n[WARN] Failed to generate AI analysis; showing only raw data.")
            print("Details:", e)


if __name__ == "__main__":
    main()