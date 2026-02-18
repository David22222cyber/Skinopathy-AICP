"""
AICP Research Portal - REST API Server
Flask-based API wrapper for natural language to SQL query system with RBAC.
"""

import os
import sys
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt

# Import core functionality from main.py
from main import (
    init_engine,
    init_llm,
    build_schema_summary,
    load_access_context,
    build_policy,
    generate_sql,
    compute_basic_analysis,
    compute_advanced_analysis,
    summarize_result,
    AccessContext,
    Policy,
)

# ---------------- CONFIG ----------------

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Session configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
TOKEN_EXPIRY_HOURS = 24
MAX_RESULTS_RETURN = 1000  # Limit rows returned to frontend

# Global resources (initialized once on startup)
engine = None
llm = None
schema_text = None

# In-memory session store (use Redis in production)
# Structure: {token: {"ctx": AccessContext, "policy": Policy, "created_at": datetime}}
sessions: Dict[str, Dict[str, Any]] = {}


# ---------------- INITIALIZATION ----------------

def initialize_app():
    """Initialize database connection and LLM on startup."""
    global engine, llm, schema_text
    
    try:
        print("[init] Initializing database connection...")
        engine = init_engine()
        
        print("[init] Initializing LLM...")
        llm = init_llm()
        
        print("[init] Building schema summary...")
        schema_text = build_schema_summary(engine)
        
        print("[init] ✓ API server ready")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}", file=sys.stderr)
        traceback.print_exc()
        return False


# ---------------- AUTH HELPERS ----------------

def generate_token(ctx: AccessContext) -> str:
    """Generate JWT token for authenticated user."""
    payload = {
        "user_id": ctx.user_id,
        "role": ctx.role,
        "display_name": ctx.display_name,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to protect endpoints with token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check Authorization header (Bearer token)
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>"
            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Fallback: check token in JSON body or query params
        if not token:
            token = request.json.get("token") if request.is_json else None
        if not token:
            token = request.args.get("token")
        
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Check if session exists
        if token not in sessions:
            return jsonify({"error": "Session not found. Please login again."}), 401
        
        # Attach session data to request
        request.session_data = sessions[token]
        request.token = token
        
        return f(*args, **kwargs)
    
    return decorated


# ---------------- API ENDPOINTS ----------------

@app.route("/", methods=["GET"])
def index():
    """Health check endpoint."""
    return jsonify({
        "service": "AICP Research Portal API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth/login",
            "query": "/api/query",
            "schema": "/api/schema",
            "logout": "/api/auth/logout",
            "health": "/health"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Detailed health check."""
    checks = {
        "database": False,
        "llm": False,
        "schema": False
    }
    
    try:
        if engine:
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            checks["database"] = True
    except:
        pass
    
    checks["llm"] = llm is not None
    checks["schema"] = schema_text is not None
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return jsonify({
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "active_sessions": len(sessions)
    }), status_code


@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    Authenticate user with API key.
    
    Request body:
    {
        "api_key": "user-api-key"
    }
    
    Response:
    {
        "token": "jwt-token",
        "user": {
            "id": 1,
            "display_name": "Dr. Smith",
            "role": "doctor"
        },
        "policy": {
            "role": "doctor",
            "notes": "..."
        },
        "expires_at": "ISO datetime"
    }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.json
    api_key = data.get("api_key", "").strip()
    
    if not api_key:
        return jsonify({"error": "api_key is required"}), 400
    
    try:
        # Load user context from database
        ctx = load_access_context(engine, api_key)
        
        # Build access policy
        policy = build_policy(ctx)
        
        # Generate JWT token
        token = generate_token(ctx)
        
        # Store session
        sessions[token] = {
            "ctx": ctx,
            "policy": policy,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": ctx.user_id,
                "display_name": ctx.display_name,
                "role": ctx.role,
                "doctor_id": ctx.doctor_id,
                "pharmacy_id": ctx.pharmacy_id
            },
            "policy": {
                "role": policy.role,
                "notes": policy.notes,
                "scope_filter_hint": policy.scope_filter_hint
            },
            "expires_at": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 401
    except Exception as e:
        print(f"[ERROR] Login error: {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({"error": "Internal server error during login"}), 500


@app.route("/api/auth/logout", methods=["POST"])
@token_required
def logout():
    """
    Logout and invalidate session token.
    Requires: Authorization header with Bearer token
    """
    token = request.token
    
    if token in sessions:
        del sessions[token]
    
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200


@app.route("/api/query", methods=["POST"])
@token_required
def execute_query():
    """
    Execute a natural language query.
    
    Request body:
    {
        "question": "How many patients do I have?",
        "include_sql": true,  # optional, default true
        "max_rows": 100       # optional, default 1000
    }
    
    Response:
    {
        "success": true,
        "question": "...",
        "sql": "...",
        "data": [...],
        "row_count": 42,
        "column_count": 5,
        "preview": [...],  # first 20 rows
        "analysis": {
            "numeric_summary": "...",
            "categorical_summary": "...",
            "advanced_summary": "...",
            "ai_summary": "..."
        },
        "execution_time_ms": 1234
    }
    """
    start_time = datetime.utcnow()
    
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.json
    question = data.get("question", "").strip()
    include_sql = data.get("include_sql", True)
    max_rows = min(data.get("max_rows", MAX_RESULTS_RETURN), MAX_RESULTS_RETURN)
    
    if not question:
        return jsonify({"error": "question is required"}), 400
    
    # Get session data
    session_data = request.session_data
    ctx = session_data["ctx"]
    policy = session_data["policy"]
    
    # Update last activity
    session_data["last_activity"] = datetime.utcnow()
    
    try:
        # Step 1: Generate SQL
        sql = generate_sql(llm, schema_text, policy, question)
        
        # Step 2: Execute query
        with engine.connect() as conn:
            df = pd.read_sql_query(sql, conn)
        
        # Limit rows if needed
        df_limited = df.head(max_rows) if len(df) > max_rows else df
        
        # Step 3: Compute analyses
        numeric_summary, cat_summary = compute_basic_analysis(df_limited)
        advanced_summary = compute_advanced_analysis(df_limited)
        
        # Step 4: Generate AI summary
        try:
            ai_summary = summarize_result(
                llm, question, sql, df_limited,
                numeric_summary, cat_summary, advanced_summary
            )
        except Exception as e:
            print(f"[WARN] AI summary generation failed: {e}", file=sys.stderr)
            ai_summary = "AI summary unavailable."
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Build response
        response = {
            "success": True,
            "question": question,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "data": df_limited.to_dict(orient="records"),
            "preview": df_limited.head(20).to_dict(orient="records"),
            "analysis": {
                "numeric_summary": numeric_summary,
                "categorical_summary": cat_summary,
                "advanced_summary": advanced_summary,
                "ai_summary": ai_summary
            },
            "execution_time_ms": round(execution_time, 2),
            "truncated": len(df) > max_rows
        }
        
        if include_sql:
            response["sql"] = sql
        
        return jsonify(response), 200
        
    except ValueError as e:
        # RBAC or validation error
        return jsonify({
            "success": False,
            "error": "Query validation failed",
            "details": str(e),
            "question": question
        }), 403
        
    except Exception as e:
        print(f"[ERROR] Query execution error: {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Query execution failed",
            "details": str(e),
            "question": question
        }), 500


@app.route("/api/schema", methods=["GET"])
@token_required
def get_schema():
    """
    Get database schema information.
    Useful for frontend to show available tables/columns.
    """
    session_data = request.session_data
    policy = session_data["policy"]
    
    return jsonify({
        "success": True,
        "schema": schema_text,
        "policy_notes": policy.notes,
        "role": policy.role
    }), 200


@app.route("/api/user/profile", methods=["GET"])
@token_required
def get_profile():
    """Get current user profile and session info."""
    session_data = request.session_data
    ctx = session_data["ctx"]
    policy = session_data["policy"]
    
    return jsonify({
        "success": True,
        "user": {
            "id": ctx.user_id,
            "display_name": ctx.display_name,
            "role": ctx.role,
            "doctor_id": ctx.doctor_id,
            "pharmacy_id": ctx.pharmacy_id
        },
        "policy": {
            "role": policy.role,
            "notes": policy.notes
        },
        "session": {
            "created_at": session_data["created_at"].isoformat(),
            "last_activity": session_data["last_activity"].isoformat()
        }
    }), 200


@app.route("/api/sessions", methods=["GET"])
def get_sessions_info():
    """
    Development endpoint to see active sessions.
    Should be removed or protected in production.
    """
    if os.getenv("FLASK_ENV") != "development":
        return jsonify({"error": "Not available in production"}), 403
    
    sessions_info = []
    for token, data in sessions.items():
        ctx = data["ctx"]
        sessions_info.append({
            "user_id": ctx.user_id,
            "display_name": ctx.display_name,
            "role": ctx.role,
            "created_at": data["created_at"].isoformat(),
            "last_activity": data["last_activity"].isoformat()
        })
    
    return jsonify({
        "active_sessions": len(sessions),
        "sessions": sessions_info
    }), 200


# ---------------- ERROR HANDLERS ----------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "message": str(e)
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": "Method not allowed",
        "message": str(e)
    }), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


# ---------------- SESSION CLEANUP ----------------

def cleanup_expired_sessions():
    """Remove expired sessions (called periodically)."""
    now = datetime.utcnow()
    expired = []
    
    for token, data in sessions.items():
        # Remove sessions inactive for more than TOKEN_EXPIRY_HOURS
        if (now - data["last_activity"]).total_seconds() > TOKEN_EXPIRY_HOURS * 3600:
            expired.append(token)
    
    for token in expired:
        del sessions[token]
    
    if expired:
        print(f"[cleanup] Removed {len(expired)} expired sessions")


# ---------------- MAIN ----------------

if __name__ == "__main__":
    print("=" * 60)
    print("AICP Research Portal - REST API Server")
    print("=" * 60)
    
    # Initialize resources
    if not initialize_app():
        print("[FATAL] Failed to initialize. Exiting.", file=sys.stderr)
        sys.exit(1)
    
    # Get configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("FLASK_ENV") == "development"
    
    print(f"\n[server] Starting Flask API on {host}:{port}")
    print(f"[server] Debug mode: {debug}")
    print(f"[server] CORS enabled: True")
    print(f"[server] Session expiry: {TOKEN_EXPIRY_HOURS} hours")
    print("\nAPI Endpoints:")
    print(f"  - POST http://{host}:{port}/api/auth/login")
    print(f"  - POST http://{host}:{port}/api/query")
    print(f"  - GET  http://{host}:{port}/api/schema")
    print(f"  - GET  http://{host}:{port}/api/user/profile")
    print(f"  - POST http://{host}:{port}/api/auth/logout")
    print(f"  - GET  http://{host}:{port}/health")
    print("\n" + "=" * 60)
    
    # Run Flask app
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
