"""
Role-Based Access Control – loading user context and building policies.
"""

from sqlalchemy import text

from src.config import SENSITIVE_PATIENT_COLUMNS
from src.models import AccessContext, Policy


def load_access_context(engine, api_key: str) -> AccessContext:
    """Look up a user by API key and return their AccessContext."""
    sql = text("""
        SELECT TOP 1 id, display_name, role, doctor_id, pharmacy_id
        FROM dbo.portal_users
        WHERE api_key = :k AND is_active = 1
    """)
    with engine.connect() as conn:
        row = conn.execute(sql, {"k": api_key}).mappings().first()

    if not row:
        raise ValueError("Invalid key or user inactive (no match in dbo.portal_users).")

    role = str(row["role"]).strip().lower()
    if role not in {"doctor", "pharmacy", "admin"}:
        raise ValueError(f"Unsupported role '{row['role']}' in dbo.portal_users.")

    return AccessContext(
        user_id=int(row["id"]),
        display_name=str(row["display_name"]),
        role=role,
        doctor_id=int(row["doctor_id"]) if row["doctor_id"] is not None else None,
        pharmacy_id=int(row["pharmacy_id"]) if row["pharmacy_id"] is not None else None,
    )


def build_policy(ctx: AccessContext) -> Policy:
    """Derive an RBAC Policy from an AccessContext."""

    if ctx.role == "doctor":
        if ctx.doctor_id is None:
            raise ValueError("Doctor user must have doctor_id set in dbo.portal_users.")
        return Policy(
            role="doctor",
            scope_filter_hint=(
                f"Row-level rule: Only include patients where dbo.patients.family_dr_id = {ctx.doctor_id}.\n"
                "If querying other tables with patient_id, JOIN to dbo.patients and apply that filter."
            ),
            required_filter_column="family_dr_id",
            required_filter_value=ctx.doctor_id,
            blocked_patient_columns=set(),
            notes="Doctor can access patient-level data, but only within their family_dr_id scope.",
        )

    if ctx.role == "pharmacy":
        if ctx.pharmacy_id is None:
            raise ValueError("Pharmacy user must have pharmacy_id set in dbo.portal_users.")
        return Policy(
            role="pharmacy",
            scope_filter_hint=(
                f"Row-level rule: Only include patients where dbo.patients.pharmacy_id = {ctx.pharmacy_id}.\n"
                "If querying other tables with patient_id, JOIN to dbo.patients and apply that filter.\n"
                "Column-level rule: Do NOT select patient PII (names, address, phones, email, health card, birth date)."
            ),
            required_filter_column="pharmacy_id",
            required_filter_value=ctx.pharmacy_id,
            blocked_patient_columns=set(SENSITIVE_PATIENT_COLUMNS),
            notes="Pharmacy should primarily analyze clinical/utilization info. Patient PII is blocked.",
        )

    if ctx.role == "admin":
        return Policy(
            role="admin",
            scope_filter_hint=(
                "Admin rule: Full access to all tables and rows. "
                "No row-level scope filters required."
            ),
            required_filter_column=None,
            required_filter_value=None,
            blocked_patient_columns=set(),
            notes="Admin can access all data (including patient-level and PII).",
        )

    raise ValueError(f"Unknown role: {ctx.role}")
