"""
Flask route handlers for the REST API.
"""

import os
import sys
import traceback
from datetime import datetime, timedelta

import pandas as pd
from flask import request, jsonify

from src.config import TOKEN_EXPIRY_HOURS, MAX_RESULTS_RETURN
from src.rbac import load_access_context, build_policy
from src.sql_generator import generate_sql
from src.analysis import compute_basic_analysis, compute_advanced_analysis, summarize_result
from src.api.auth import (
    sessions,
    generate_token,
    token_required,
)


def register_routes(app, engine, llm, schema_text):
    """Register all API routes on the Flask *app*."""

    # ── Health / info ────────────────────────────────────────────────

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "AICP Research Portal API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "auth": "/api/auth/login",
                "query": "/api/query",
                "schema": "/api/schema",
                "logout": "/api/auth/logout",
                "health": "/health",
            },
        })

    @app.route("/health", methods=["GET"])
    def health():
        from sqlalchemy import text as sa_text

        checks = {"database": False, "llm": False, "schema": False}
        try:
            if engine:
                with engine.connect() as conn:
                    conn.execute(sa_text("SELECT 1"))
                checks["database"] = True
        except Exception:
            pass

        checks["llm"] = llm is not None
        checks["schema"] = schema_text is not None
        all_healthy = all(checks.values())

        return jsonify({
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "active_sessions": len(sessions),
        }), 200 if all_healthy else 503

    # ── Auth ─────────────────────────────────────────────────────────

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.json
        api_key = data.get("api_key", "").strip()
        if not api_key:
            return jsonify({"error": "api_key is required"}), 400

        try:
            ctx = load_access_context(engine, api_key)
            policy = build_policy(ctx)
            token = generate_token(ctx)

            sessions[token] = {
                "ctx": ctx,
                "policy": policy,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
            }

            return jsonify({
                "success": True,
                "token": token,
                "user": {
                    "id": ctx.user_id,
                    "display_name": ctx.display_name,
                    "role": ctx.role,
                    "doctor_id": ctx.doctor_id,
                    "pharmacy_id": ctx.pharmacy_id,
                },
                "policy": {
                    "role": policy.role,
                    "notes": policy.notes,
                    "scope_filter_hint": policy.scope_filter_hint,
                },
                "expires_at": (datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat(),
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
        token = request.token
        if token in sessions:
            del sessions[token]
        return jsonify({"success": True, "message": "Logged out successfully"}), 200

    # ── Query ────────────────────────────────────────────────────────

    @app.route("/api/query", methods=["POST"])
    @token_required
    def execute_query():
        start_time = datetime.utcnow()

        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.json
        question = data.get("question", "").strip()
        include_sql = data.get("include_sql", True)
        max_rows = min(data.get("max_rows", MAX_RESULTS_RETURN), MAX_RESULTS_RETURN)

        if not question:
            return jsonify({"error": "question is required"}), 400

        session_data = request.session_data
        ctx = session_data["ctx"]
        policy = session_data["policy"]
        session_data["last_activity"] = datetime.utcnow()

        try:
            sql = generate_sql(llm, schema_text, policy, question)

            with engine.connect() as conn:
                df = pd.read_sql_query(sql, conn)

            df_limited = df.head(max_rows) if len(df) > max_rows else df

            numeric_summary, cat_summary = compute_basic_analysis(df_limited)
            advanced_summary = compute_advanced_analysis(df_limited)

            try:
                ai_summary = summarize_result(
                    llm, question, sql, df_limited,
                    numeric_summary, cat_summary, advanced_summary,
                )
            except Exception as e:
                print(f"[WARN] AI summary generation failed: {e}", file=sys.stderr)
                ai_summary = "AI summary unavailable."

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

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
                    "ai_summary": ai_summary,
                },
                "execution_time_ms": round(execution_time, 2),
                "truncated": len(df) > max_rows,
            }
            if include_sql:
                response["sql"] = sql
            return jsonify(response), 200

        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Query validation failed",
                "details": str(e),
                "question": question,
            }), 403
        except Exception as e:
            print(f"[ERROR] Query execution error: {e}", file=sys.stderr)
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": "Query execution failed",
                "details": str(e),
                "question": question,
            }), 500

    # ── Schema / profile ─────────────────────────────────────────────

    @app.route("/api/schema", methods=["GET"])
    @token_required
    def get_schema():
        session_data = request.session_data
        policy = session_data["policy"]
        return jsonify({
            "success": True,
            "schema": schema_text,
            "policy_notes": policy.notes,
            "role": policy.role,
        }), 200

    @app.route("/api/user/profile", methods=["GET"])
    @token_required
    def get_profile():
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
                "pharmacy_id": ctx.pharmacy_id,
            },
            "policy": {
                "role": policy.role,
                "notes": policy.notes,
            },
            "session": {
                "created_at": session_data["created_at"].isoformat(),
                "last_activity": session_data["last_activity"].isoformat(),
            },
        }), 200

    @app.route("/api/sessions", methods=["GET"])
    def get_sessions_info():
        if os.getenv("FLASK_ENV") != "development":
            return jsonify({"error": "Not available in production"}), 403

        sessions_info = []
        for _token, data in sessions.items():
            ctx = data["ctx"]
            sessions_info.append({
                "user_id": ctx.user_id,
                "display_name": ctx.display_name,
                "role": ctx.role,
                "created_at": data["created_at"].isoformat(),
                "last_activity": data["last_activity"].isoformat(),
            })
        return jsonify({
            "active_sessions": len(sessions),
            "sessions": sessions_info,
        }), 200

    # ── Error handlers ───────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found", "message": str(e)}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "message": str(e)}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
