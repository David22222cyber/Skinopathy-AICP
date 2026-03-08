import {
  Paper, Typography, List, ListItem, ListItemText,
  IconButton, Box, Chip,
} from '@mui/material';
import { Replay, Delete } from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '../../hooks/useStore';
import { executeQuery, clearHistory } from '../../store/slices/querySlice';

export default function QueryHistory() {
  const { history } = useAppSelector((s) => s.query);
  const dispatch = useAppDispatch();

  if (history.length === 0) return null;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Query History</Typography>
        <IconButton size="small" sx={{ ml: 'auto' }} onClick={() => dispatch(clearHistory())}>
          <Delete fontSize="small" />
        </IconButton>
      </Box>

      <List dense disablePadding>
        {history.map((item) => (
          <ListItem
            key={item.id}
            sx={{
              borderBottom: '1px solid',
              borderColor: 'divider',
              '&:last-child': { borderBottom: 'none' },
            }}
            secondaryAction={
              <IconButton
                edge="end"
                size="small"
                onClick={() =>
                  dispatch(executeQuery({ question: item.question, include_sql: true, max_rows: 100 }))
                }
              >
                <Replay fontSize="small" />
              </IconButton>
            }
          >
            <ListItemText
              primary={item.question}
              secondary={
                <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                  <Chip label={`${item.rowCount} rows`} size="small" variant="outlined" />
                  <Chip label={`${item.executionTime.toFixed(0)}ms`} size="small" variant="outlined" />
                  <Typography variant="caption" color="text.secondary">
                    {new Date(item.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              }
              primaryTypographyProps={{ noWrap: true, variant: 'body2', fontWeight: 500 }}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}
