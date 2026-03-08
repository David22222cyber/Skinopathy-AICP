import {
  Paper, Typography, Box, Chip, Divider, IconButton, Tooltip,
} from '@mui/material';
import { ContentCopy, Code } from '@mui/icons-material';
import { useAppSelector } from '../../hooks/useStore';

export default function QueryResult() {
  const { result } = useAppSelector((s) => s.query);
  if (!result) return null;

  const handleCopySql = () => {
    if (result.sql) navigator.clipboard.writeText(result.sql);
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="h6">Results</Typography>
        <Chip label={`${result.row_count} rows`} size="small" color="primary" />
        <Chip label={`${result.column_count} cols`} size="small" variant="outlined" />
        <Chip label={`${result.execution_time_ms.toFixed(0)}ms`} size="small" variant="outlined" />
        {result.truncated && <Chip label="Truncated" size="small" color="warning" />}
      </Box>

      {/* AI Summary */}
      {result.analysis?.ai_summary && (
        <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.50', borderRadius: 2, border: '1px solid', borderColor: 'primary.100' }}>
          <Typography variant="subtitle2" color="primary.main" sx={{ mb: 1 }}>
            AI Analysis
          </Typography>
          <Typography variant="body2">{result.analysis.ai_summary}</Typography>
        </Box>
      )}

      {/* SQL */}
      {result.sql && (
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Code sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
            <Typography variant="subtitle2" color="text.secondary">
              Generated SQL
            </Typography>
            <Tooltip title="Copy SQL">
              <IconButton size="small" onClick={handleCopySql} sx={{ ml: 'auto' }}>
                <ContentCopy fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <Box
            sx={{
              p: 2, bgcolor: '#1e1e1e', borderRadius: 2,
              overflow: 'auto', maxHeight: 200,
            }}
          >
            <Typography
              component="pre"
              sx={{ color: '#d4d4d4', fontFamily: 'monospace', fontSize: 13, m: 0, whiteSpace: 'pre-wrap' }}
            >
              {result.sql}
            </Typography>
          </Box>
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Data Table */}
      <Box sx={{ overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr>
              {result.columns.map((col) => (
                <th
                  key={col}
                  style={{
                    padding: '10px 12px', textAlign: 'left',
                    borderBottom: '2px solid #e0e0e0', fontWeight: 600,
                    whiteSpace: 'nowrap', backgroundColor: '#fafafa',
                  }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.data.map((row, i) => (
              <tr key={i} style={{ backgroundColor: i % 2 ? '#fafafa' : 'white' }}>
                {result.columns.map((col) => (
                  <td
                    key={col}
                    style={{
                      padding: '8px 12px',
                      borderBottom: '1px solid #f0f0f0',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {row[col] != null ? String(row[col]) : '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Box>

      {/* Analysis sections */}
      {result.analysis && (
        <Box sx={{ mt: 3 }}>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Statistical Summary
          </Typography>

          {result.analysis.numeric_summary && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Numeric Summary
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1,
                  overflow: 'auto', fontSize: 12, fontFamily: 'monospace',
                }}
              >
                {result.analysis.numeric_summary}
              </Box>
            </Box>
          )}

          {result.analysis.categorical_summary && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Categorical Summary
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1,
                  overflow: 'auto', fontSize: 12, fontFamily: 'monospace',
                }}
              >
                {result.analysis.categorical_summary}
              </Box>
            </Box>
          )}

          {result.analysis.advanced_summary && (
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Advanced Analysis
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 1.5, bgcolor: '#f5f5f5', borderRadius: 1,
                  overflow: 'auto', fontSize: 12, fontFamily: 'monospace',
                }}
              >
                {result.analysis.advanced_summary}
              </Box>
            </Box>
          )}
        </Box>
      )}
    </Paper>
  );
}
