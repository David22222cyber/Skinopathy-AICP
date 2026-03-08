import { Box, Typography, Alert, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Search } from '@mui/icons-material';
import DataVisualizer from '../components/analytics/DataVisualizer';
import { useAppSelector } from '../hooks/useStore';

export default function AnalyticsPage() {
  const { result } = useAppSelector((s) => s.query);
  const navigate = useNavigate();

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        Analytics
      </Typography>

      {!result?.data?.length ? (
        <Alert
          severity="info"
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" startIcon={<Search />} onClick={() => navigate('/query')}>
              Go to Query
            </Button>
          }
        >
          Run a query first from the Query Workspace to see analytics and visualizations here.
        </Alert>
      ) : (
        <>
          <Alert severity="success" sx={{ mb: 3 }}>
            Showing analytics for the last query result ({result.data.length} rows, {result.columns.length} columns).
          </Alert>
          <DataVisualizer />
        </>
      )}
    </Box>
  );
}
