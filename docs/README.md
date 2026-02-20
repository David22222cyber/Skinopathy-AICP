# AICP Research Portal – NL → SQL Assistant (Backend Prototype)

This repo contains a working backend prototype for the Skinopathy/AICP research portal.  
It supports:
- Natural-language questions → SQL generation → execution (read-only recommended)
- Tabular previews + basic numeric summaries
- Optional “advanced analysis” layer (distribution notes, outliers, tiering, etc.)
- Role-based access control (RBAC) using API keys:
  - **doctor**: can access patient-level data **only for their scope**
  - **pharmacy**: can access scoped patient rows but **PII is blocked**
  - **admin**: full access (including PII)

The database has been migrated from AWS (RDS) to **Microsoft Azure SQL** due to AWS free credit limitations.

---

## 1) High-level Architecture

**User flow:**
1. User asks a question in natural language
2. Backend builds a policy based on the user API key (role + scope)
3. LLM generates SQL with guardrails + scope filter hints
4. SQL executes against Azure SQL
5. Results preview (top N rows)
6. Analytics summary (optional, automated)

**Key design choice:**  
We implement RBAC primarily **in the application layer**, not in database permissions, to keep it simple and scalable for a student prototype. We store user identity/scope in the database so the backend can enforce access.

---

## 2) Database Setup

### Core Tables Used by RBAC

#### `dbo.portal_users` (NEW)
Stores API keys and role scopes.

Recommended columns:
- `id` (PK)
- `display_name`
- `api_key` (unique)
- `role` (`doctor`, `pharmacy`, `admin`)
- `doctor_id` (nullable, for doctor role)
- `pharmacy_id` (nullable, for pharmacy role)
- `is_active` (bit)
- `created_at`

**Role scopes:**
- `doctor`: must have `doctor_id` set  
  scope = patients where `dbo.patients.family_dr_id = doctor_id`
- `pharmacy`: must have `pharmacy_id` set  
  scope = patients where `dbo.patients.pharmacy_id = pharmacy_id`
- `admin`: no scope restriction

### Important Columns in Existing Tables
In `dbo.patients`, we rely on:
- `family_dr_id`
- `pharmacy_id`

These are the backbone of row-level access enforcement.

---

## 3) Roles and Access Rules

### Role: Doctor
- Row-level access: only patients where `patients.family_dr_id = ctx.doctor_id`
- Can view patient details (PII allowed)
- Designed for physician workflows and patient-specific analysis

### Role: Pharmacy
- Row-level access: only patients where `patients.pharmacy_id = ctx.pharmacy_id`
- **PII is blocked** (names, address, phone, email, birth date, health card, etc.)
- Designed mainly for utilization/clinical summaries (counts, meds, outcomes, etc.)

### Role: Admin
- Full access to all tables and rows
- Can view PII

---

## 4) How RBAC Works in Code

### Authentication
Requests provide an API key (from `dbo.portal_users.api_key`).

Backend:
1. Loads user from `dbo.portal_users` (must be `is_active = 1`)
2. Builds `AccessContext`
3. Calls `build_policy(ctx)` to produce a `Policy`

### Policy Object (concept)
A policy contains:
- `role`
- `required_filter_column` (ex: `family_dr_id` or `pharmacy_id`)
- `required_filter_value` (ex: doctor_id or pharmacy_id)
- `blocked_patient_columns` (for pharmacy role)
- a `scope_filter_hint` used to steer SQL generation

### Enforced Restrictions
- **Row-level**: query must include the required scope filter  
  For non-patient tables that reference `patient_id`, SQL must **JOIN to dbo.patients** and apply scope filter there.
- **Column-level**: pharmacy role cannot select sensitive PII columns from patients.

---

## 5) Example Questions Supported

### Basic count queries
- “How many patients are in the database?”
- “Show the number of patients by province.”

### Aggregations + analysis
- “Show total bill amount per patient and analyze the distribution.”
- “Show how many appointments each doctor has and analyze the pattern.”

### Pharmacy-safe analytics
- “Show number of prescriptions filled by month for my pharmacy.”
- “Show average medication cost for my pharmacy’s patients (no names).”

---

## 6) Running the Backend

### Requirements
- Python 3.10+ (tested with 3.11)
- `pyodbc`
- `sqlalchemy`
- ODBC Driver 18 for SQL Server installed
- LLM key configured (depends on your backend implementation)

### Connection String (Azure SQL)
Your SQLAlchemy URL typically looks like:

`mssql+pyodbc://USER:PASSWORD@SERVER/DATABASE?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes`

> Tip: If your password contains special characters, URL-encode it.

---

## 7) Mock Data Generation (Updated)

### Script
`Data Generator UPDATED.py` generates:
- doctors
- pharmacies
- patients (with `family_dr_id` and `pharmacy_id`)
- dependent tables
- RBAC demo users in `dbo.portal_users`:
  - 1 admin user
  - N doctor users
  - N pharmacy users

### Expected Output
You should see logs like:
- Seeding doctors...
- Seeding pharmacies...
- Seeding auth users (RBAC demo) into dbo.portal_users...
- Seeding patients...
- Seeding dependent tables...

### Important: Running Generator Multiple Times
Some tables (ex: `promo_codes`) may have **unique constraints**.  
If you re-run the generator without clearing tables, you may hit errors like:

> Violation of UNIQUE KEY constraint ... Cannot insert duplicate key ...

**Solutions:**
1. (Recommended) truncate tables before re-seeding
2. or adjust generators to avoid collisions by using globally unique IDs
3. or change seed logic to “upsert” style (more complex)

---

## 8) Common Issues and Fixes

### Issue A: `NameError: DB_SCHEMA is not defined`
Cause: functions reference `DB_SCHEMA` before definition or wrong scope.

Fix:
- Define `DB_SCHEMA = "dbo"` near the top of the file
- Avoid referencing it in default function args if editing caused ordering issues

### Issue B: `try_load_auth_table() missing required positional argument: schema`
Cause: function signature requires `schema` but call site didn’t pass it.

Fix:
- Pass schema explicitly at call: `try_load_auth_table(engine, metadata, schema=DB_SCHEMA)`
- Or set a default parameter in the function signature

### Issue C: Duplicate inserts due to unique constraints
Fix:
- TRUNCATE affected table(s) first
- Or make generated values guaranteed unique (UUID, suffix, etc.)

---

## 9) Mapping portal_users to Real Doctors/Pharmacies

### Problem
If `portal_users.display_name` is “Doctor 1”, it may not match real doctor names in `dbo.doctors`.

### Correct Approach (Recommended)
When creating portal users:
- Set `doctor_id` to a real `dbo.doctors.id`
- Set `display_name` by querying `dbo.doctors.first_name + last_name`

Similarly for pharmacies:
- set `pharmacy_id` to a real pharmacy record
- set `display_name` = actual pharmacy name

This ensures the UI/terminal demo shows realistic names, not placeholders.

---

## 10) Next Steps

### (A) Frontend Integration
Expose backend as an API:
- `/auth` or `/whoami`
- `/query` for NL→SQL execution
- return structured JSON:
  - SQL generated
  - preview rows
  - summaries
  - warnings (policy and safety)

### (B) Harder Security Improvements (Optional)
- Rotate API keys
- Hash API keys (store only hashed keys)
- Add audit logs: user_id, query text, generated SQL, timestamp
- Add query allowlist for high-risk operations (e.g., block `DELETE/UPDATE/INSERT`)

### (C) Role Expansion
To add new roles, update:
- `dbo.portal_users.role` allowed values
- `build_policy(ctx)` logic
- blocked columns lists / scope logic
- tests + generator

Example new roles:
- “researcher” = de-identified data only
- “ops” = aggregated stats only

---

## 11) Quick RBAC Demo Checklist (Terminal)
1. Pick an API key from `dbo.portal_users`
2. Run backend
3. Ask:
   - “Show the patients in my scope”
   - “Show total bills per patient”
4. Pharmacy role should NOT be able to retrieve PII columns
5. Doctor role should see patient info but only for patients under `family_dr_id`
6. Admin should see everything

---

## Contact / Notes
This is a student prototype for AICP/Skinopathy.  
Backend focuses on correctness, clarity, and iterative expansion rather than full enterprise security.
