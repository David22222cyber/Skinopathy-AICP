import { Box, Typography, Grid } from '@mui/material';
import QueryInput from '../components/query/QueryInput';
import QueryResult from '../components/query/QueryResult';
import QueryHistory from '../components/query/QueryHistory';
import DataVisualizer from '../components/analytics/DataVisualizer';

export default function QueryPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        Query Workspace
      </Typography>

      <Grid container spacing={3}>
        {/* Left column: Input + Results */}
        <Grid size={{ xs: 12, md: 8 }}>
          <QueryInput />
          <QueryResult />
          <DataVisualizer />
        </Grid>

        {/* Right column: History */}
        <Grid size={{ xs: 12, md: 4 }}>
          <QueryHistory />
        </Grid>
      </Grid>
    </Box>
  );
}
