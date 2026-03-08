import { Box, Typography } from '@mui/material';
import SchemaViewer from '../components/data/SchemaViewer';

export default function SchemaPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} sx={{ mb: 3 }}>
        Database Schema
      </Typography>
      <SchemaViewer />
    </Box>
  );
}
