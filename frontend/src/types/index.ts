export interface User {
  id: number;
  display_name: string;
  role: 'doctor' | 'pharmacy' | 'admin';
  doctor_id: number | null;
  pharmacy_id: number | null;
}

export interface Policy {
  role: string;
  notes: string;
  scope_filter_hint?: string;
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: User;
  policy: Policy;
  expires_at: string;
}

export interface LoginRequest {
  api_key: string;
}

export interface ProfileResponse {
  success: boolean;
  user: User;
  policy: Policy;
  session: {
    created_at: string;
    last_activity: string;
  };
}

export interface SchemaResponse {
  success: boolean;
  schema: string;
  policy_notes: string;
  role: string;
}

export interface QueryRequest {
  question: string;
  include_sql?: boolean;
  max_rows?: number;
}

export interface AnalysisData {
  numeric_summary: string;
  categorical_summary: string;
  advanced_summary: string;
  ai_summary: string;
}

export interface QueryResponse {
  success: boolean;
  question: string;
  sql?: string;
  row_count: number;
  column_count: number;
  columns: string[];
  data: Record<string, unknown>[];
  preview: Record<string, unknown>[];
  analysis: AnalysisData;
  execution_time_ms: number;
  truncated: boolean;
}

export interface QueryError {
  success: false;
  error: string;
  details?: string;
  question?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  checks: {
    database: boolean;
    llm: boolean;
    schema: boolean;
  };
  active_sessions: number;
}

export interface QueryHistoryItem {
  id: string;
  question: string;
  timestamp: string;
  rowCount: number;
  executionTime: number;
}
