import { useEffect, useState, useCallback } from 'react';
import {
  Paper, Typography, Box, Chip, CircularProgress, Alert,
  Grid, Card, CardContent, IconButton, Tooltip, LinearProgress,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { getHealth } from '../../services/queryService';
import type { HealthResponse } from '../../types';

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to check health');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchHealth(); }, [fetchHealth]);

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
          <Typography variant="h5">System Health</Typography>
          <Chip
            icon={isHealthy ? <CheckCircleIcon /> : <ErrorIcon />}
            label={health.status.toUpperCase()}
            color={isHealthy ? 'success' : 'error'}
          />
        </Box>
        <Tooltip title="Refresh health status">
          <IconButton onClick={fetchHealth} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Overall Status */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: isHealthy ? 'success.50' : 'error.50' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          {isHealthy ? (
            <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
          ) : (
            <ErrorIcon color="error" sx={{ fontSize: 40 }} />
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
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Paper>

      {/* Service Cards */}
      <Grid container spacing={3}>
        {services.map((svc) => {
          return (
            <Grid size={{ xs: 12, md: 6 }} key={svc.label}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {svc.icon}
                      <Typography variant="h6">{svc.label}</Typography>
                    </Box>
                    <Chip
                      label={svc.status ? 'ONLINE' : 'OFFLINE'}
                      color={svc.status ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {svc.description}
                  </Typography>
                  <Typography
                    variant="body2"
                    fontFamily="monospace"
                    sx={{
                      p: 1,
                      bgcolor: 'grey.100',
                      borderRadius: 1,
                    }}
                  >
                    Status: {svc.status ? 'Connected' : 'Disconnected'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
