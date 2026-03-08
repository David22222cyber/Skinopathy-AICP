import { useEffect } from 'react';
import {
  Box, Typography, Paper, Grid, Card, CardContent, Chip,
  CircularProgress, Alert, Divider, Avatar,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import BadgeIcon from '@mui/icons-material/Badge';
import PolicyIcon from '@mui/icons-material/Policy';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import { useAppDispatch, useAppSelector } from '../hooks/useStore';
import { fetchProfile } from '../store/slices/authSlice';

export default function ProfilePage() {
  const dispatch = useAppDispatch();
  const { user, policy, session, loading, error } = useAppSelector((s) => s.auth);

  useEffect(() => {
    if (!user) dispatch(fetchProfile());
  }, [dispatch, user]);

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

  if (!user) return null;

  const roleColors: Record<string, 'primary' | 'secondary' | 'success'> = {
    admin: 'primary',
    doctor: 'success',
    pharmacy: 'secondary',
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        User Profile
      </Typography>

      {/* Profile Header */}
      <Paper variant="outlined" sx={{ p: 4, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Avatar sx={{ width: 72, height: 72, bgcolor: 'primary.main', fontSize: 32, fontWeight: 600 }}>
            {user.display_name?.charAt(0).toUpperCase() || 'U'}
          </Avatar>
          <Box>
            <Typography variant="h5" fontWeight={600}>
              {user.display_name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip
                label={user.role.toUpperCase()}
                color={roleColors[user.role] || 'default'}
                size="small"
                icon={<BadgeIcon />}
              />
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* Details Grid */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined">
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PersonIcon color="primary" />
                <Typography variant="h6">Account Details</Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">User ID</Typography>
                  <Typography variant="body2" fontFamily="monospace">{user.id}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Display Name</Typography>
                  <Typography variant="body2" fontWeight={500}>{user.display_name}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">Role</Typography>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>{user.role}</Typography>
                </Box>
                {user.doctor_id && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Doctor ID</Typography>
                    <Typography variant="body2" fontFamily="monospace">{user.doctor_id}</Typography>
                  </Box>
                )}
                {user.pharmacy_id && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Pharmacy ID</Typography>
                    <Typography variant="body2" fontFamily="monospace">{user.pharmacy_id}</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined">
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PolicyIcon color="secondary" />
                <Typography variant="h6">Access Policy</Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              {policy ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Role</Typography>
                    <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>{policy.role}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                      Policy Notes
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1, whiteSpace: 'pre-wrap', lineHeight: 1.7, border: '1px solid', borderColor: 'divider' }}
                    >
                      {policy.notes}
                    </Typography>
                  </Box>
                  {policy.scope_filter_hint && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Scope Filter</Typography>
                      <Typography variant="body2" fontFamily="monospace" sx={{ fontSize: 12 }}>
                        {policy.scope_filter_hint}
                      </Typography>
                    </Box>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No policy restrictions applied
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Session Info */}
        {session && (
          <Grid size={{ xs: 12 }}>
            <Card variant="outlined">
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <AccessTimeIcon color="primary" />
                  <Typography variant="h6">Session Information</Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>Session Created</Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {new Date(session.created_at).toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>Last Activity</Typography>
                    <Typography variant="body2" fontFamily="monospace">
                      {new Date(session.last_activity).toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
