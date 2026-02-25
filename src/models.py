"""
Domain dataclasses used across the application.
"""

from dataclasses import dataclass
from typing import Optional, Set


@dataclass
class AccessContext:
    """Represents the authenticated user's identity and scope."""
    user_id: int
    display_name: str
    role: str                  # "doctor", "pharmacy", or "admin"
    doctor_id: Optional[int]   # scope for doctor role
    pharmacy_id: Optional[int] # scope for pharmacy role


@dataclass
class Policy:
    """RBAC policy derived from an AccessContext."""
    role: str
    scope_filter_hint: str
    required_filter_column: Optional[str]
    required_filter_value: Optional[int]
    blocked_patient_columns: Set[str]
    notes: str
