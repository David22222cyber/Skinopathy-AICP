"""
JWT authentication helpers and middleware for the Flask API.
"""

import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional

import jwt
from flask import request, jsonify

from src.config import SECRET_KEY, TOKEN_EXPIRY_HOURS
from src.models import AccessContext

# In-memory session store (use Redis in production)
# Structure: {token: {"ctx": AccessContext, "policy": Policy, "created_at": datetime, ...}}
sessions: Dict[str, Dict[str, Any]] = {}


def generate_token(ctx: AccessContext) -> str:
    """Generate a JWT token for an authenticated user."""
    payload = {
        "user_id": ctx.user_id,
        "role": ctx.role,
        "display_name": ctx.display_name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return the decoded payload (or None)."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator that protects endpoints with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check Authorization header (Bearer token)
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401

        # Fallback: check token in JSON body or query params
        if not token:
            token = request.json.get("token") if request.is_json else None
        if not token:
            token = request.args.get("token")

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        if token not in sessions:
            return jsonify({"error": "Session not found. Please login again."}), 401

        # Attach session data to the request context
        request.session_data = sessions[token]
        request.token = token

        return f(*args, **kwargs)

    return decorated


def cleanup_expired_sessions():
    """Remove sessions that have been inactive beyond TOKEN_EXPIRY_HOURS."""
    now = datetime.utcnow()
    expired = [
        tok for tok, data in sessions.items()
        if (now - data["last_activity"]).total_seconds() > TOKEN_EXPIRY_HOURS * 3600
    ]
    for tok in expired:
        del sessions[tok]
    if expired:
        print(f"[cleanup] Removed {len(expired)} expired sessions")
