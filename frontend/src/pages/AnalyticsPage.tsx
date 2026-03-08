import { Box, Typography, Alert } from '@mui/material';
import DataVisualizer from '../components/analytics/DataVisualizer';
import { useAppSelector } from '../hooks/useStore';

export default function AnalyticsPage() {
  const { result } = useAppSelector((s) => s.query);

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        Analytics
      </Typography>

      {!result?.data?.length ? (
        <Alert severity="info" sx={{ mb: 3 }}>
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
