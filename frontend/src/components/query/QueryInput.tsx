import { useState } from 'react';
import {
  Box, TextField, Button, Paper, Typography, Slider,
  FormControlLabel, Switch, CircularProgress, Alert, InputAdornment,
} from '@mui/material';
import { Send, Search } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { executeQuery } from '../../store/slices/querySlice';

export default function QueryInput() {
  const [question, setQuestion] = useState('');
  const [includeSql, setIncludeSql] = useState(true);
  const [maxRows, setMaxRows] = useState(100);
  const dispatch = useAppDispatch();
  const { loading, error } = useAppSelector((s) => s.query);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;
    dispatch(executeQuery({ question: question.trim(), include_sql: includeSql, max_rows: maxRows }));
  };

  return (
    <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        <Search sx={{ mr: 1, verticalAlign: 'middle' }} />
        Ask a Question
      </Typography>

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          multiline
          minRows={2}
          maxRows={5}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question in natural language, e.g. 'How many patients do I have with diabetes?'"
          sx={{ mb: 2 }}
          slotProps={{
            input: {
              endAdornment: (
                <InputAdornment position="end">
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading || !question.trim()}
                    startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <Send />}
                    sx={{ borderRadius: 2 }}
                  >
                    {loading ? 'Running...' : 'Ask'}
                  </Button>
                </InputAdornment>
              ),
            },
          }}
        />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
          <FormControlLabel
            control={<Switch checked={includeSql} onChange={(_, v) => setIncludeSql(v)} />}
            label="Show SQL"
          />
          <Box sx={{ width: 200 }}>
            <Typography variant="caption" color="text.secondary">
              Max rows: {maxRows}
            </Typography>
            <Slider
              value={maxRows}
              onChange={(_, v) => setMaxRows(v as number)}
              min={10}
              max={1000}
              step={10}
              size="small"
            />
          </Box>
        </Box>
      </form>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Paper>
  );
}
