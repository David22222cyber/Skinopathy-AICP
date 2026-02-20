# Backend Test Coverage (Unit Tests)

This document describes what is covered by the current **unit test suite** (24 tests). The suite is designed to validate core backend logic **offline**, without requiring a real database or real LLM/API calls.

---

## How the tests run

### Offline-by-design
- **Database access** is mocked using fake `Engine/Connection/Result` objects.
- **LLM calls** are mocked using a fake LLM object that returns deterministic responses.

This ensures the test suite is:
- fast,
- deterministic,
- runnable on any machine without external dependencies.

---

## 1) Environment Configuration

### `get_env(name: str) -> str`
**Verified behaviors**
- Returns the value of an environment variable when it exists.
- Exits with `SystemExit(1)` when the variable is missing.
- Prints a clear error message to `stderr` when missing.

---

## 2) Authentication & Access Context Loading (RBAC)

### `load_access_context(engine, api_key: str) -> AccessContext`
**Verified behaviors**
- With a valid API key and a returned user row:
  - Returns `AccessContext` populated with:
    - `user_id`
    - `display_name`
    - normalized `role` (lowercased)
    - role-dependent identifiers (`doctor_id` / `pharmacy_id`)
- With an invalid API key (no row returned):
  - Raises `ValueError` indicating the key is invalid.
- With an unsupported role:
  - Raises `ValueError` indicating the role is not supported.

---

## 3) Policy Construction (Authorization Rules)

### `build_policy(ctx: AccessContext) -> Policy`
**Verified behaviors**
- **Doctor**:
  - Requires `ctx.doctor_id`; otherwise raises `ValueError`.
  - Produces a policy enforcing a required doctor scope filter.
- **Pharmacy**:
  - Requires `ctx.pharmacy_id`; otherwise raises `ValueError`.
  - Produces a policy enforcing a required pharmacy scope filter.
  - Produces a policy containing a blocked column set for patient PII fields.
- **Admin**:
  - Produces a policy with no required scope filter (`required_filter_column/value` are `None`).

---

## 4) SQL Parsing & Safety Helpers

### `extract_dbo_tables(sql: str) -> set[str]`
**Verified behaviors**
- Extracts `dbo.<table>` references from common SQL patterns:
  - `FROM dbo.table`
  - `JOIN dbo.table`
- Returns a de-duplicated set of table names.

### `contains_required_scope_filter(sql: str, column: str, value: int) -> bool`
**Verified behaviors**
- Returns `True` if the SQL contains the expected scope constraint (e.g., `column = value`).
- Returns `False` if the scope constraint is missing or mismatched.

### `blocks_pii_for_pharmacy(sql: str, sensitive_cols: set[str]) -> str | None`
**Verified behaviors**
- Detects whether a SQL query references blocked patient fields.
- Returns the first blocked column detected when present.
- Returns `None` when the query contains no blocked columns.

---

## 5) SQL Generation Safety & RBAC Enforcement

### `generate_sql(llm, schema_text: str, policy: Policy, question: str) -> str`
**Verified behaviors**

#### Output cleanup
- Strips markdown fences from LLM output (e.g., ```sql ... ```), returning clean SQL.

#### Statement safety
- Rejects non-`SELECT` SQL (e.g., `DELETE`, `UPDATE`, `INSERT`) by raising an error.
- Rejects SQL containing dangerous keywords or multi-statement injection patterns (e.g., `SELECT ...; DROP TABLE ...`).

#### RBAC scope enforcement
- When `dbo.patients` is referenced:
  - Requires the policy’s scope filter to be present (role-dependent).
  - Raises an error when the required scope filter is missing.

#### PII protection for pharmacy role
- Blocks patient PII columns defined by the policy (e.g., `first_name`, `email`, etc.).
- Raises an error when blocked columns appear in the SQL.

---

## 6) Basic Data Analysis Output

### `compute_basic_analysis(df: pd.DataFrame) -> tuple[str, str]`
**Verified behaviors**
- If the dataframe has **0 rows**:
  - Returns “no rows” summaries for both numeric and categorical outputs.
- Numeric summary:
  - Produces a `describe()`-style summary (markdown) for numeric columns.
- Categorical summary:
  - Produces `value_counts()` tables (markdown) for low-cardinality categorical columns.
- Output contains expected column references and section formatting.

---

## 7) Advanced Data Analysis Output

### `compute_advanced_analysis(df: pd.DataFrame) -> str`
**Verified behaviors**
- If the dataframe has **0 rows**:
  - Returns a “no rows” message.
- If there are **no numeric columns**:
  - Returns a “no numeric columns” message.
- For numeric data:
  - Identifies a “primary metric” (based on the function’s heuristic).
  - Computes and reports correlation insights between numeric columns.
  - Output includes correlation-related text.

---

## 8) LLM-Based Result Summarization

### `summarize_result(llm, question: str, sql: str, df: pd.DataFrame, numeric_summary: str, cat_summary: str, advanced_summary: str) -> str`
**Verified behaviors**
- Calls the LLM interface (`invoke`) with a composed prompt/messages.
- Returns the model’s `.content` as the final summary text.
- Tested using a deterministic fake LLM (no network calls).

---

## Notes / Non-goals of this test suite
- The suite does **not** test database seeding or any mock-data generator.
- The suite does **not** require a real SQL Server instance.
- The suite does **not** call real OpenAI/LLM APIs.

---

## Running the tests

From the project root:

```bash
python -m pytest -q
