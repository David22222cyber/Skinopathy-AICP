# AICP Research Portal

Natural-language → SQL query system with role-based access control (RBAC) for the Skinopathy/AICP clinical research database.

## Features

- **NL → SQL** – Ask questions in plain English; the LLM generates safe, read-only T-SQL
- **RBAC** – Doctor / Pharmacy / Admin roles with row-level and column-level enforcement
- **Automated Analytics** – Numeric summaries, categorical breakdowns, tier segmentation, outlier detection, correlations
- **AI Narrative** – LLM-generated insight summaries for every query result
- **REST API** – Flask-based API with JWT authentication for frontend integration
- **Interactive CLI** – Terminal-based assistant for quick ad-hoc queries

## Project Structure

```
├── src/                        # Application source code
│   ├── config.py               #   Configuration constants & env helpers
│   ├── models.py               #   AccessContext & Policy dataclasses
│   ├── database.py             #   SQLAlchemy engine & schema introspection
│   ├── llm.py                  #   LLM (ChatOpenAI) initialisation
│   ├── rbac.py                 #   User context loading & policy building
│   ├── sql_generator.py        #   SQL generation with safety checks
│   ├── analysis.py             #   Basic, advanced & AI summary analysis
│   ├── cli.py                  #   Interactive CLI entry-point
│   └── api/                    #   REST API sub-package
│       ├── app.py              #     Flask app factory & server start
│       ├── auth.py             #     JWT helpers & token_required middleware
│       └── routes.py           #     All API route handlers
│
├── tests/                      # Automated tests (pytest)
│   ├── test_rbac.py            #   RBAC & policy tests
│   ├── test_sql_generator.py   #   SQL generation & safety tests
│   ├── test_analysis.py        #   Analysis function tests
│   └── test_api.py             #   API integration tests
│
├── scripts/                    # Utility & setup scripts
│   ├── generate_api_key.py     #   Generate API keys for portal_users
│   ├── generate_secret_key.py  #   Generate JWT secret for .env
│   ├── seed_data.py            #   Seed mock data into the database
│   └── schema.sql              #   Database table creation DDL
│
├── docs/                       # Documentation
│   ├── README.md               #   Detailed backend documentation
│   ├── API_DOCUMENTATION.md    #   REST API endpoint reference
│   ├── backend_testing_documentation.md
│   └── ...
│
├── postman/                    # Postman collection for API testing
│   └── AICP_API.postman_collection.json
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── run_api.py                  # Entry point: start the REST API
├── run_cli.py                  # Entry point: start the CLI
├── run.sh                      # Shell script: activate venv & start API
└── run.bat                     # Windows batch: start CLI
```

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env – fill in OPENAI_API_KEY, DB_URI, JWT_SECRET_KEY

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
python run_api.py
# or
bash run.sh
```

### 3. Run the Interactive CLI

```bash
python run_cli.py
```

### 4. Run Tests

```bash
pytest tests/ -v
```

## Roles

| Role       | Row Scope                          | PII Access | Notes                          |
|------------|-------------------------------------|------------|--------------------------------|
| `doctor`   | `family_dr_id = <doctor_id>`       | ✓          | Patient-level data in scope    |
| `pharmacy` | `pharmacy_id = <pharmacy_id>`      | ✗          | Aggregates only, PII blocked   |
| `admin`    | All rows                           | ✓          | Full access                    |

## API Endpoints

| Method | Endpoint              | Auth     | Description                |
|--------|-----------------------|----------|----------------------------|
| POST   | `/api/auth/login`     | —        | Authenticate with API key  |
| POST   | `/api/auth/logout`    | Bearer   | Invalidate session         |
| POST   | `/api/query`          | Bearer   | Execute NL query           |
| GET    | `/api/schema`         | Bearer   | Get database schema info   |
| GET    | `/api/user/profile`   | Bearer   | Get current user profile   |
| GET    | `/health`             | —        | Health check               |

See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for full details.
