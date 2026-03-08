import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authService } from '../../services/authService';
import { TOKEN_KEY, EXPIRY_KEY } from '../../config';
import type { User, Policy, LoginRequest } from '../../types';

export interface AuthState {
  user: User | null;
  policy: Policy | null;
  token: string | null;
  expiresAt: string | null;
  session: { created_at: string; last_activity: string } | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
}

const initialState: AuthState = {
  user: null,
  policy: null,
  token: localStorage.getItem(TOKEN_KEY),
  expiresAt: localStorage.getItem(EXPIRY_KEY),
  session: null,
  loading: false,
  error: null,
  initialized: !localStorage.getItem(TOKEN_KEY),
};

export const login = createAsyncThunk(
  'auth/login',
  async (data: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authService.login(data);
      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(EXPIRY_KEY, response.expires_at);
      return response;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      return rejectWithValue(error.response?.data?.error || 'Login failed');
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    await authService.logout();
  } finally {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXPIRY_KEY);
  }
});

export const fetchProfile = createAsyncThunk(
  'auth/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      return await authService.getProfile();
    } catch (err: unknown) {
      localStorage.removeItem(TOKEN_KEY);
      const error = err as { response?: { data?: { error?: string } } };
      return rejectWithValue(error.response?.data?.error || 'Session expired');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError(state) {
      state.error = null;
    },
    forceLogout(state) {
      state.user = null;
      state.policy = null;
      state.token = null;
      state.expiresAt = null;
      state.session = null;
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(EXPIRY_KEY);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.initialized = true;
        state.user = action.payload.user;
        state.policy = action.payload.policy;
        state.token = action.payload.token;
        state.expiresAt = action.payload.expires_at;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.policy = null;
        state.token = null;
        state.expiresAt = null;
        state.session = null;
      })
      .addCase(fetchProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.initialized = true;
        state.user = action.payload.user;
        state.policy = action.payload.policy;
        state.session = action.payload.session;
      })
      .addCase(fetchProfile.rejected, (state) => {
        state.loading = false;
        state.initialized = true;
        state.user = null;
        state.policy = null;
        state.token = null;
        state.expiresAt = null;
        state.session = null;
      });
  },
});

export const { clearError, forceLogout } = authSlice.actions;
export default authSlice.reducer;
