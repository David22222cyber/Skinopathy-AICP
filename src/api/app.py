"""
Flask application factory and server entry-point.
"""

import os
import sys
import traceback

from flask import Flask
from flask_cors import CORS

from src.config import TOKEN_EXPIRY_HOURS
from src.database import init_engine, build_schema_summary
from src.llm import init_llm
from src.api.routes import register_routes


def create_app():
    """Build and return a fully configured Flask application."""
    app = Flask(__name__)
    CORS(app)

    # ── Initialise shared resources ──────────────────────────────────
    try:
        print("[init] Initializing database connection...")
        engine = init_engine()

        print("[init] Initializing LLM...")
        llm = init_llm()

        print("[init] Building schema summary...")
        schema_text = build_schema_summary(engine)

        print("[init] ✓ API server ready")
    except Exception as e:
        print(f"[FATAL] Failed to initialize: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    # ── Register routes ──────────────────────────────────────────────
    register_routes(app, engine, llm, schema_text)

    return app


def main():
    """Run the development server."""
    print("=" * 60)
    print("AICP Research Portal – REST API Server")
    print("=" * 60)

    app = create_app()

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

    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    main()
