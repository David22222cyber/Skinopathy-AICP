"""
Centralised configuration constants and environment helpers.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────
MODEL_NAME = "gpt-4.1-mini"

# ── Schema / preview limits ──────────────────────────────────────────
MAX_SCHEMA_CHARS = 4500
MAX_PREVIEW_ROWS = 20
MAX_CATEGORY_UNIQUE = 10

# ── PII columns (blocked for pharmacy role) ──────────────────────────
SENSITIVE_PATIENT_COLUMNS = {
    "first_name", "last_name", "street_address", "street_address_2",
    "city", "province", "postal", "health_card_number", "home_phone",
    "cell_phone", "email", "birth", "health_card_expiry_date",
}

# If pharmacy should only see aggregates (not individual rows), set True.
PHARMACY_AGGREGATES_ONLY = False

# ── API server ───────────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
TOKEN_EXPIRY_HOURS = 24
MAX_RESULTS_RETURN = 1000


def get_env(name: str) -> str:
    """Return an environment variable or exit with an error message."""
    value = os.getenv(name)
    if not value:
        print(f"ERROR: env var {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value
