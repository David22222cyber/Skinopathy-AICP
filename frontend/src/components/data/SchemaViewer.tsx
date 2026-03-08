import { useEffect, useState, useCallback } from 'react';
import {
  Paper, Typography, Box, Chip, CircularProgress, Alert,
  IconButton, Tooltip, TextField, InputAdornment,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import StorageIcon from '@mui/icons-material/Storage';
import { getSchema } from '../../services/queryService';
import type { SchemaResponse } from '../../types';

export default function SchemaViewer() {
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  const fetchSchema = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getSchema();
      setSchema(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load schema');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchSchema(); }, [fetchSchema]);

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

  if (!schema) return null;

  const lines = schema.schema.split('\n');
  const filteredLines = search
    ? lines.filter((line) => line.toLowerCase().includes(search.toLowerCase()))
    : lines;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <StorageIcon color="primary" />
          <Typography variant="h5">Database Schema</Typography>
          <Chip label={`Role: ${schema.role}`} size="small" color="primary" variant="outlined" />
        </Box>
        <Tooltip title="Refresh schema">
          <IconButton onClick={fetchSchema} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {schema.policy_notes && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {schema.policy_notes}
        </Alert>
      )}

      <TextField
        fullWidth
        size="small"
        placeholder="Filter schema text..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        sx={{ mb: 3 }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          },
        }}
      />

      <Paper
        variant="outlined"
        sx={{
          p: 2,
          maxHeight: '70vh',
          overflow: 'auto',
          bgcolor: 'grey.50',
        }}
      >
        <Typography
          component="pre"
          sx={{
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            m: 0,
          }}
        >
          {filteredLines.join('\n')}
        </Typography>
      </Paper>
    </Box>
  );
}
