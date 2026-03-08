import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { queryService } from '../../services/queryService';
import { HISTORY_KEY } from '../../config';
import type { QueryRequest, QueryResponse, QueryHistoryItem } from '../../types';

function loadHistory(): QueryHistoryItem[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(history: QueryHistoryItem[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

interface QueryState {
  result: QueryResponse | null;
  loading: boolean;
  error: string | null;
  history: QueryHistoryItem[];
}

const initialState: QueryState = {
  result: null,
  loading: false,
  error: null,
  history: loadHistory(),
};

export const executeQuery = createAsyncThunk(
  'query/execute',
  async (data: QueryRequest, { rejectWithValue }) => {
    try {
      return await queryService.executeQuery(data);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string; details?: string } } };
      return rejectWithValue(
        error.response?.data?.details || error.response?.data?.error || 'Query failed'
      );
    }
  }
);

const querySlice = createSlice({
  name: 'query',
  initialState,
  reducers: {
    clearResult(state) {
      state.result = null;
      state.error = null;
    },
    clearHistory(state) {
      state.history = [];
      saveHistory([]);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(executeQuery.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(executeQuery.fulfilled, (state, action) => {
        state.loading = false;
        state.result = action.payload;
        state.history.unshift({
          id: crypto.randomUUID(),
          question: action.payload.question,
          timestamp: new Date().toISOString(),
          rowCount: action.payload.row_count,
          executionTime: action.payload.execution_time_ms,
        });
        if (state.history.length > 50) state.history.pop();
        saveHistory(state.history);
      })
      .addCase(executeQuery.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearResult, clearHistory } = querySlice.actions;
export default querySlice.reducer;
