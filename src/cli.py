"""
Interactive CLI for the AICP Research Portal.
Ask natural-language questions against the database with RBAC enforcement.
"""

import pandas as pd

from src.config import MAX_PREVIEW_ROWS
from src.database import init_engine, build_schema_summary
from src.llm import init_llm
from src.rbac import load_access_context, build_policy
from src.sql_generator import generate_sql
from src.analysis import compute_basic_analysis, compute_advanced_analysis, summarize_result


def main():
    print("=== AICP Research Portal: NL → SQL Assistant (RBAC + Next-Level Analysis) ===\n")

    engine = init_engine()
    schema_text = build_schema_summary(engine)
    llm = init_llm()

    # ── Login ────────────────────────────────────────────────────────
    try:
        api_key = input("Enter access key (or 'quit'): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        return

    if not api_key or api_key.lower() in {"quit", "exit"}:
        print("Goodbye.")
        return

    try:
        ctx = load_access_context(engine, api_key)
        policy = build_policy(ctx)
    except Exception as e:
        print("\n[ERROR] Login failed.")
        print("Details:", e)
        return

    print(f"\n[auth] Logged in as: {ctx.display_name} (role={ctx.role})")
    print(f"[auth] Policy: {policy.notes}")

    # ── REPL ─────────────────────────────────────────────────────────
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
            sql = generate_sql(llm, schema_text, policy, q)
        except Exception as e:
            print("\n[RBAC/SQL ERROR] Could not generate an allowed SQL query.")
            print("Details:", e)
            continue

        print("\n[SQL generated]")
        print(sql)

        # 2) Execute
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(sql, conn)
        except Exception as e:
            print("\n[DB ERROR] Database error while running the query.")
            print("Details:", e)
            continue

        # 3) Preview
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

        # 5) Advanced analysis
        advanced_summary = compute_advanced_analysis(df)
        print("\n[Advanced analysis (automatic)]")
        print(advanced_summary)

        # 6) AI narrative
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
