# AICP Research Portal - API Documentation

## Overview

REST API for natural language to SQL query system with role-based access control (RBAC).

**Base URL**: `http://localhost:8000`  
**Authentication**: JWT Bearer token  
**Content-Type**: `application/json`

---

## Authentication Flow

### 1. Login

**Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "api_key": "user-api-key-from-portal_users-table"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "display_name": "Dr. John Smith",
    "role": "doctor",
    "doctor_id": 5,
    "pharmacy_id": null
  },
  "policy": {
    "role": "doctor",
    "notes": "Doctor can access patient-level data, but only within their family_dr_id scope.",
    "scope_filter_hint": "Row-level rule: Only include patients where dbo.patients.family_dr_id = 5..."
  },
  "expires_at": "2026-01-26T10:30:00"
}
```

**Error Response** (401 Unauthorized):
```json
{
  "error": "Authentication failed: Invalid key or user inactive (no match in dbo.portal_users)."
}
```

### 2. Using the Token

Include the token in subsequent requests using the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Logout

**Endpoint**: `POST /api/auth/logout`

**Headers**: 
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Core Endpoints

### Execute Query

**Endpoint**: `POST /api/query`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request**:
```json
{
  "question": "How many patients do I have with diabetes?",
  "include_sql": true,
  "max_rows": 100
}
```

**Parameters**:
- `question` (required): Natural language question
- `include_sql` (optional): Include generated SQL in response (default: `true`)
- `max_rows` (optional): Maximum rows to return (default: 1000, max: 1000)

**Response** (200 OK):
```json
{
  "success": true,
  "question": "How many patients do I have with diabetes?",
  "sql": "SELECT COUNT(*) as patient_count FROM dbo.patients WHERE family_dr_id = 5 AND diagnosis LIKE '%diabetes%'",
  "row_count": 1,
  "column_count": 1,
  "columns": ["patient_count"],
  "data": [
    {"patient_count": 45}
  ],
  "preview": [
    {"patient_count": 45}
  ],
  "analysis": {
    "numeric_summary": "...",
    "categorical_summary": "...",
    "advanced_summary": "Primary metric used for deeper analysis: patient_count...",
    "ai_summary": "Based on the query results, you have 45 patients diagnosed with diabetes. This represents a significant portion of your patient base..."
  },
  "execution_time_ms": 234.56,
  "truncated": false
}
```

**Error Response** (403 Forbidden):
```json
{
  "success": false,
  "error": "Query validation failed",
  "details": "RBAC block: query references dbo.patients but missing required scope filter family_dr_id = 5.",
  "question": "How many patients do I have with diabetes?"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "success": false,
  "error": "Query execution failed",
  "details": "Syntax error near 'FROM'",
  "question": "Invalid question"
}
```

### Get Database Schema

**Endpoint**: `GET /api/schema`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "schema": "Table dbo.patients(id int, first_name varchar, ...)\nTable dbo.appointments(...)",
  "policy_notes": "Doctor can access patient-level data, but only within their family_dr_id scope.",
  "role": "doctor"
}
```

### Get User Profile

**Endpoint**: `GET /api/user/profile`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "display_name": "Dr. John Smith",
    "role": "doctor",
    "doctor_id": 5,
    "pharmacy_id": null
  },
  "policy": {
    "role": "doctor",
    "notes": "Doctor can access patient-level data, but only within their family_dr_id scope."
  },
  "session": {
    "created_at": "2026-01-25T10:30:00",
    "last_activity": "2026-01-25T12:45:00"
  }
}
```

---

## Utility Endpoints

### Health Check

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "llm": true,
    "schema": true
  },
  "active_sessions": 3
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "checks": {
    "database": false,
    "llm": true,
    "schema": true
  },
  "active_sessions": 0
}
```

### API Info

**Endpoint**: `GET /`

**Response** (200 OK):
```json
{
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
}
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format or missing parameters |
| 401 | Unauthorized | Missing, invalid, or expired token |
| 403 | Forbidden | RBAC violation or permission denied |
| 404 | Not Found | Endpoint doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service not healthy |

---

## RBAC (Role-Based Access Control)

### Doctor Role
- **Access**: Patient-level data for their assigned patients only
- **Filter**: Automatic `family_dr_id = <doctor_id>` filter applied
- **PII**: Full access to patient information
- **Queries**: Must include proper scope filter

### Pharmacy Role
- **Access**: Patient data for their pharmacy only
- **Filter**: Automatic `pharmacy_id = <pharmacy_id>` filter applied
- **PII**: Blocked from personal identifiers (names, addresses, phone, email, health card, DOB)
- **Queries**: Prefer aggregated results

### Admin Role
- **Access**: Full access to all data
- **Filter**: None required
- **PII**: Full access

---

## Example Usage

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"api_key": "doctor-api-key-123"}'
```

### Query
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "question": "How many patients visited last month?",
    "max_rows": 50
  }'
```

### Get Schema
```bash
curl -X GET http://localhost:8000/api/schema \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---
