import api from './api';
import type { QueryRequest, QueryResponse, SchemaResponse, HealthResponse } from '../types';

export async function executeQuery(data: QueryRequest): Promise<QueryResponse> {
  const response = await api.post<QueryResponse>('/api/query', data);
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

export const queryService = { executeQuery, getSchema, getHealth };
