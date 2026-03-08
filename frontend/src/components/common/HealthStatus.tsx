import { useEffect, useState, useCallback } from 'react';
import {
  Paper, Typography, Box, Chip, CircularProgress, Alert,
  Grid, Card, CardContent, IconButton, Tooltip, LinearProgress,
  Divider, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import InfoIcon from '@mui/icons-material/Info';
import PeopleIcon from '@mui/icons-material/People';
import { getHealth, getApiInfo, getActiveSessions } from '../../services/queryService';
import type { HealthResponse, ApiInfoResponse, SessionsResponse } from '../../types';

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [apiInfo, setApiInfo] = useState<ApiInfoResponse | null>(null);
  const [sessions, setSessions] = useState<SessionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [healthData, infoData] = await Promise.all([getHealth(), getApiInfo()]);
      setHealth(healthData);
      setApiInfo(infoData);

      // Sessions endpoint is dev-only, so catch 403 silently
      try {
        const sessionsData = await getActiveSessions();
        setSessions(sessionsData);
      } catch {
        setSessions(null);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to check health');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!health) return null;

  const isHealthy = health.status === 'healthy';
  const schemaLoaded = health.checks.schema;
  const services = [
    {
      label: 'Database',
      status: health.checks.database,
      icon: <StorageIcon />,
      description: 'SQL Server connection',
    },
    {
      label: 'LLM Service',
      status: health.checks.llm,
      icon: <SmartToyIcon />,
      description: 'OpenAI GPT model availability',
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={isHealthy ? <CheckCircleIcon /> : <ErrorIcon />}
            label={health.status.toUpperCase()}
            color={isHealthy ? 'success' : 'error'}
            variant="outlined"
          />
          <Chip label={`${health.active_sessions} active sessions`} size="small" variant="outlined" />
          {schemaLoaded && <Chip label="Schema loaded" size="small" color="primary" variant="outlined" />}
        </Box>
        <Tooltip title="Refresh health status">
          <IconButton onClick={fetchAll} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Overall Status */}
      <Paper
        variant="outlined"
        sx={{ p: 3, mb: 3, bgcolor: isHealthy ? '#f0fdf4' : '#fef2f2' }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          {isHealthy ? (
            <CheckCircleIcon color="success" sx={{ fontSize: 36 }} />
          ) : (
            <ErrorIcon color="error" sx={{ fontSize: 36 }} />
          )}
          <Box>
            <Typography variant="h6">
              {isHealthy ? 'All Systems Operational' : 'System Issues Detected'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Last checked: {new Date().toLocaleTimeString()}
            </Typography>
          </Box>
        </Box>
        <LinearProgress
          variant="determinate"
          value={isHealthy ? 100 : 50}
          color={isHealthy ? 'success' : 'error'}
          sx={{ height: 6, borderRadius: 3 }}
        />
      </Paper>

      {/* Service Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {services.map((svc) => (
          <Grid size={{ xs: 12, md: 6 }} key={svc.label}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {svc.icon}
                    <Typography variant="subtitle1" fontWeight={600}>{svc.label}</Typography>
                  </Box>
                  <Chip
                    label={svc.status ? 'ONLINE' : 'OFFLINE'}
                    color={svc.status ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {svc.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* API Information */}
      {apiInfo && (
        <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <InfoIcon color="primary" />
            <Typography variant="h6">API Information</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Typography variant="caption" color="text.secondary">Service</Typography>
              <Typography variant="body2" fontWeight={500}>{apiInfo.service}</Typography>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Typography variant="caption" color="text.secondary">Version</Typography>
              <Typography variant="body2" fontWeight={500}>{apiInfo.version}</Typography>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Typography variant="caption" color="text.secondary">Status</Typography>
              <Typography variant="body2" fontWeight={500} sx={{ textTransform: 'capitalize' }}>{apiInfo.status}</Typography>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Typography variant="caption" color="text.secondary">Endpoints</Typography>
              <Typography variant="body2" fontWeight={500}>{Object.keys(apiInfo.endpoints).length} registered</Typography>
            </Grid>
          </Grid>
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>Available Endpoints</Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {Object.entries(apiInfo.endpoints).map(([name, path]) => (
                <Chip key={name} label={`${name}: ${path}`} size="small" variant="outlined" sx={{ fontFamily: 'monospace', fontSize: 12 }} />
              ))}
            </Box>
          </Box>
        </Paper>
      )}

      {/* Active Sessions (dev only) */}
      {sessions && (
        <Paper variant="outlined" sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <PeopleIcon color="primary" />
            <Typography variant="h6">Active Sessions</Typography>
            <Chip label={`${sessions.active_sessions} total`} size="small" color="primary" variant="outlined" />
          </Box>
          <Divider sx={{ mb: 2 }} />
          {sessions.sessions.length === 0 ? (
            <Typography variant="body2" color="text.secondary">No active sessions.</Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>User</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Last Activity</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sessions.sessions.map((s, i) => (
                    <TableRow key={i}>
                      <TableCell>{s.display_name}</TableCell>
                      <TableCell><Chip label={s.role} size="small" sx={{ textTransform: 'capitalize' }} /></TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{new Date(s.created_at).toLocaleString()}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: 12 }}>{new Date(s.last_activity).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      )}
    </Box>
  );
}
