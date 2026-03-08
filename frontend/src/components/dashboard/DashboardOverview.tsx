import {
  Box, Typography, Grid, Card, CardContent, Chip, Paper, Button,
} from '@mui/material';
import {
  Person, Security, AccessTime, QueryStats, ArrowForward,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../../hooks/useStore';

export default function DashboardOverview() {
  const { user, policy } = useAppSelector((s) => s.auth);
  const { history } = useAppSelector((s) => s.query);
  const navigate = useNavigate();

  if (!user) return null;

  const stats = [
    {
      label: 'Queries Run',
      value: history.length,
      icon: <QueryStats sx={{ fontSize: 36, color: '#1976d2' }} />,
      color: '#e3f2fd',
    },
    {
      label: 'Role',
      value: user.role,
      icon: <Security sx={{ fontSize: 36, color: '#7c3aed' }} />,
      color: '#f3e8ff',
    },
    {
      label: 'Session',
      value: 'Active',
      icon: <AccessTime sx={{ fontSize: 36, color: '#16a34a' }} />,
      color: '#dcfce7',
    },
    {
      label: 'User ID',
      value: `#${user.id}`,
      icon: <Person sx={{ fontSize: 36, color: '#ea580c' }} />,
      color: '#fff7ed',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Welcome, {user.display_name}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Your research dashboard at a glance
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={stat.label}>
            <Card variant="outlined">
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2.5, '&:last-child': { pb: 2.5 } }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: stat.color, display: 'flex' }}>
                  {stat.icon}
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary" fontWeight={500}>
                    {stat.label}
                  </Typography>
                  <Typography variant="h5" fontWeight={700} sx={{ textTransform: 'capitalize' }}>
                    {stat.value}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper variant="outlined" sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Access Policy
            </Typography>
            <Chip
              label={policy?.role || user.role}
              color="primary"
              size="small"
              sx={{ mb: 2, textTransform: 'capitalize' }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
              {policy?.notes || 'No specific policy notes.'}
            </Typography>
            {user.doctor_id && (
              <Typography variant="body2" sx={{ mt: 1.5 }}>
                Doctor ID: <strong>{user.doctor_id}</strong>
              </Typography>
            )}
            {user.pharmacy_id && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Pharmacy ID: <strong>{user.pharmacy_id}</strong>
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper variant="outlined" sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Recent Queries</Typography>
              {history.length > 0 && (
                <Button size="small" endIcon={<ArrowForward />} onClick={() => navigate('/query')}>
                  View all
                </Button>
              )}
            </Box>
            {history.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  No queries yet. Get started with your first query.
                </Typography>
                <Button variant="outlined" size="small" onClick={() => navigate('/query')} startIcon={<ArrowForward />}>
                  Go to Query
                </Button>
              </Box>
            ) : (
              history.slice(0, 5).map((item) => (
                <Box
                  key={item.id}
                  sx={{
                    py: 1.5,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    '&:last-child': { borderBottom: 'none' },
                  }}
                >
                  <Typography variant="body2" fontWeight={500} noWrap>
                    {item.question}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.rowCount} rows &bull; {item.executionTime.toFixed(0)}ms &bull;{' '}
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </Typography>
                </Box>
              ))
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
