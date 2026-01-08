# AICP Research Portal - NL → SQL Assistant (RBAC + Analysis)

## What this does
A terminal-based prototype that:
1) Prompts user for an access key
2) Determines role + scope (doctor vs pharmacy)
3) Converts natural-language questions into safe SELECT-only SQL
4) Enforces row-level scope (family_dr_id or pharmacy_id)
5) Blocks pharmacy from selecting patient PII columns
6) Executes query and returns:
   - result preview
   - basic numeric/categorical summaries
   - advanced analysis (tiers/outliers/correlations)
   - short LLM narrative analysis

## Setup

### 1) Install dependencies
```bash
pip install -U pandas python-dotenv sqlalchemy pyodbc langchain-openai langchain-core tabulate
