"""
SQL generation from natural language, with safety checks and RBAC enforcement.
"""

import re
from typing import Optional, Set

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import PHARMACY_AGGREGATES_ONLY
from src.models import Policy


# ── Helper functions ─────────────────────────────────────────────────

def extract_dbo_tables(sql: str) -> Set[str]:
    """Return the set of dbo.* table names referenced in FROM / JOIN clauses."""
    hits = re.findall(r"(?is)\b(?:from|join)\s+dbo\.([a-zA-Z0-9_]+)\b", sql)
    return {h.lower() for h in hits}


def contains_required_scope_filter(sql: str, filter_col: str, filter_val: int) -> bool:
    """Check that the SQL contains the mandatory scope predicate."""
    s = sql.lower()
    if filter_col.lower() not in s:
        return False
    if re.search(rf"(?is)\b{re.escape(filter_col.lower())}\b\s*=\s*{filter_val}\b", s):
        return True
    return str(filter_val) in s


def blocks_pii_for_pharmacy(sql: str, blocked_cols: Set[str]) -> Optional[str]:
    """Return the first blocked PII column found in the SQL, or None."""
    s = sql.lower()
    for col in blocked_cols:
        if re.search(rf"(?is)\b{re.escape(col.lower())}\b", s):
            return col
    return None


# ── Main generation function ─────────────────────────────────────────

def generate_sql(llm: ChatOpenAI, schema_text: str, policy: Policy, question: str) -> str:
    """Ask the LLM to produce a safe, RBAC-compliant SQL SELECT query."""

    system = SystemMessage(
        content=(
            "You are an expert SQL assistant for a SQL Server (T-SQL) database.\n"
            "You have READ-ONLY access.\n\n"
            "CRITICAL SAFETY RULES:\n"
            "- Output exactly ONE SQL SELECT query.\n"
            "- Allowed clauses: SELECT, FROM, JOIN, WHERE, GROUP BY, ORDER BY, TOP.\n"
            "- Never use INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/MERGE.\n"
            "- Always use explicit dbo.<table> names.\n"
            "- ONLY use columns that exist in the provided schema. NEVER invent or assume column names.\n"
            "- If a column does not exist in the schema, you CANNOT use it in your query.\n\n"
            "PATIENT COUNT RULE:\n"
            "- When counting or identifying patients, ALWAYS use dbo.patients as the primary table.\n"
            "- Do NOT infer total patients from patient_notes, walkin_cases, or other auxiliary tables.\n\n"
            "DATA EXTRACTION RULES:\n"
            "- For diagnosis information: Search within the 'note' column of dbo.patient_notes using LIKE or string functions.\n"
            "- For unstructured data: Use WHERE note LIKE '%keyword%' or string analysis functions.\n"
            "- Do NOT assume structured columns exist if they are not in the schema.\n\n"
            f"ROLE-BASED ACCESS POLICY:\n{policy.scope_filter_hint}\n\n"
            "If the user asks something outside their permission, do NOT try to bypass it.\n"
            "Instead, write a query that returns an allowed aggregate or allowed subset.\n"
            "Return ONLY the SQL query, with no explanation and no markdown."
        )
    )

    role_hint = ""
    if policy.role == "pharmacy":
        role_hint = (
            "\nExtra guidance for pharmacy role:\n"
            "- Prefer aggregated outputs (counts, totals, distributions) over listing patient rows.\n"
            "- Avoid selecting any patient identity or contact information.\n"
        )

    human = HumanMessage(
        content=(
            f"Schema:\n{schema_text}\n\n"
            f"User question: {question}\n"
            f"{role_hint}\n"
            "Write the SQL query now."
        )
    )

    resp = llm.invoke([system, human])
    sql = resp.content.strip()

    # Strip markdown fences if present
    if sql.lower().startswith("```sql"):
        sql = sql.strip("`")
        sql = re.sub(r"^sql", "", sql, flags=re.IGNORECASE).strip()
    elif sql.startswith("```"):
        sql = sql.strip("`").strip()

    # ── Safety checks ────────────────────────────────────────────────
    if not re.match(r"(?is)^\s*select\b", sql):
        raise ValueError(f"LLM generated non-SELECT query, blocked: {sql[:160]}...")
    if re.search(r"\b(insert|update|delete|drop|alter|truncate|create|merge)\b", sql, re.IGNORECASE):
        raise ValueError(f"LLM generated potentially unsafe query, blocked: {sql[:160]}...")

    # ── RBAC enforcement ─────────────────────────────────────────────
    tables = extract_dbo_tables(sql)

    if "patients" in tables and policy.required_filter_column and policy.required_filter_value is not None:
        if not contains_required_scope_filter(sql, policy.required_filter_column, policy.required_filter_value):
            raise ValueError(
                f"RBAC block: query references dbo.patients but missing required scope filter "
                f"{policy.required_filter_column} = {policy.required_filter_value}."
            )

    if policy.role == "pharmacy":
        bad = blocks_pii_for_pharmacy(sql, policy.blocked_patient_columns)
        if bad:
            raise ValueError(f"RBAC block: pharmacy role query attempted to use PII column '{bad}'.")
        if PHARMACY_AGGREGATES_ONLY:
            pass  # optionally block patient_id selection here

    return sql
