"""
Database engine initialisation and schema introspection.
"""

import sys
from typing import List

from sqlalchemy import create_engine, inspect, text

from src.config import get_env, MAX_SCHEMA_CHARS


def init_engine():
    """Create a SQLAlchemy engine and verify the connection."""
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
