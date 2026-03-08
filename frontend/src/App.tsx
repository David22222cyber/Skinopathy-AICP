import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, CssBaseline, Box, CircularProgress, Typography } from '@mui/material';
import { store } from './store';
import theme from './config/theme';
import AppLayout from './components/layout/AppLayout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import QueryPage from './pages/QueryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SchemaPage from './pages/SchemaPage';
import HealthPage from './pages/HealthPage';
import ProfilePage from './pages/ProfilePage';
import { useAppDispatch, useAppSelector } from './hooks/useStore';
import { fetchProfile, forceLogout } from './store/slices/authSlice';

function AuthInitializer({ children }: { children: React.ReactNode }) {
  const dispatch = useAppDispatch();
  const { token, initialized, expiresAt } = useAppSelector((s) => s.auth);

  useEffect(() => {
    if (token && !initialized) {
      if (expiresAt && new Date(expiresAt) <= new Date()) {
        dispatch(forceLogout());
      } else {
        dispatch(fetchProfile());
      }
    }
  }, [token, initialized, expiresAt, dispatch]);

  // Periodic expiry check every 60 seconds
  useEffect(() => {
    if (!token || !expiresAt) return;
    const interval = setInterval(() => {
      if (new Date(expiresAt) <= new Date()) {
        dispatch(forceLogout());
      }
    }, 60_000);
    return () => clearInterval(interval);
  }, [token, expiresAt, dispatch]);

  if (token && !initialized) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: 2 }}>
        <CircularProgress />
        <Typography color="text.secondary">Restoring session...</Typography>
      </Box>
    );
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />

      {/* Protected */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/query" element={<QueryPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/schema" element={<SchemaPage />} />
          <Route path="/health" element={<HealthPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <AuthInitializer>
            <AppRoutes />
          </AuthInitializer>
        </BrowserRouter>
      </ThemeProvider>
    </Provider>
  );
}
