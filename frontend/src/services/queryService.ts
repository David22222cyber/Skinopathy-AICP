import api from './api';
import { QUERY_TIMEOUT_MS } from '../config';
import type { QueryRequest, QueryResponse, SchemaResponse, HealthResponse, ApiInfoResponse, SessionsResponse } from '../types';

export async function executeQuery(data: QueryRequest, signal?: AbortSignal): Promise<QueryResponse> {
  const response = await api.post<QueryResponse>('/api/query', data, {
    timeout: QUERY_TIMEOUT_MS,
    signal,
  });
  return response.data;
}

export async function getSchema(): Promise<SchemaResponse> {
  const response = await api.get<SchemaResponse>('/api/schema');
  return response.data;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>('/health');
  return response.data;
}

export async function getApiInfo(): Promise<ApiInfoResponse> {
  const response = await api.get<ApiInfoResponse>('/');
  return response.data;
}

export async function getActiveSessions(): Promise<SessionsResponse> {
  const response = await api.get<SessionsResponse>('/api/sessions');
  return response.data;
}

export const queryService = { executeQuery, getSchema, getHealth, getApiInfo, getActiveSessions };
