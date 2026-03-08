import {
  Box, Typography, Grid, Card, CardContent, Chip, Paper,
} from '@mui/material';
import {
  Person, Security, AccessTime, QueryStats,
} from '@mui/icons-material';
import { useAppSelector } from '../../hooks/useStore';

export default function DashboardOverview() {
  const { user, policy } = useAppSelector((s) => s.auth);
  const { history } = useAppSelector((s) => s.query);

  if (!user) return null;

  const stats = [
    {
      label: 'Queries Run',
      value: history.length,
      icon: <QueryStats sx={{ fontSize: 40, color: 'primary.main' }} />,
      color: '#e3f2fd',
    },
    {
      label: 'Role',
      value: user.role,
      icon: <Security sx={{ fontSize: 40, color: 'secondary.main' }} />,
      color: '#f3e5f5',
    },
    {
      label: 'Session',
      value: 'Active',
      icon: <AccessTime sx={{ fontSize: 40, color: 'success.main' }} />,
      color: '#e8f5e9',
    },
    {
      label: 'User ID',
      value: `#${user.id}`,
      icon: <Person sx={{ fontSize: 40, color: 'warning.main' }} />,
      color: '#fff3e0',
    },
  ];

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" sx={{ mb: 1 }}>
        Welcome, {user.display_name}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Your research dashboard at a glance
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={stat.label}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: stat.color }}>
                  {stat.icon}
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
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
        {/* Policy info */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Access Policy
            </Typography>
            <Chip
              label={policy?.role || user.role}
              color="primary"
              sx={{ mb: 2, textTransform: 'capitalize' }}
            />
            <Typography variant="body2" color="text.secondary">
              {policy?.notes || 'No specific policy notes.'}
            </Typography>
            {user.doctor_id && (
              <Typography variant="body2" sx={{ mt: 1 }}>
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

        {/* Recent queries */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Recent Queries
            </Typography>
            {history.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No queries yet. Go to the Query page to get started.
              </Typography>
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
