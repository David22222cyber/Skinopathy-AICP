import { Box, Typography } from '@mui/material';
import HealthStatus from '../components/common/HealthStatus';

export default function HealthPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        System Health
      </Typography>
      <HealthStatus />
    </Box>
  );
}
