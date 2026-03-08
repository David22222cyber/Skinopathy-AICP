import { useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import DashboardOverview from '../components/dashboard/DashboardOverview';
import { useAppDispatch, useAppSelector } from '../hooks/useStore';
import { fetchProfile } from '../store/slices/authSlice';

export default function DashboardPage() {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((s) => s.auth);

  useEffect(() => {
    if (!user) dispatch(fetchProfile());
  }, [dispatch, user]);

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        Dashboard
      </Typography>
      <DashboardOverview />
    </Box>
  );
}
