import { useMemo } from 'react';
import { Paper, Typography, Box, Tabs, Tab } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  ScatterChart, Scatter, LineChart, Line,
} from 'recharts';
import { useState } from 'react';
import { useAppSelector } from '../../hooks/useStore';

const COLORS = ['#1976d2', '#9c27b0', '#4caf50', '#ff9800', '#f44336', '#00bcd4', '#795548', '#607d8b'];

export default function DataVisualizer() {
  const { result } = useAppSelector((s) => s.query);
  const [tab, setTab] = useState(0);

  const { numericCols, categoricalCols, chartData } = useMemo(() => {
    if (!result?.data?.length) return { numericCols: [], categoricalCols: [], chartData: [] };

    const numCols: string[] = [];
    const catCols: string[] = [];
    const first = result.data[0];

    for (const col of result.columns) {
      if (typeof first[col] === 'number') numCols.push(col);
      else catCols.push(col);
    }

    return { numericCols: numCols, categoricalCols: catCols, chartData: result.data };
  }, [result]);

  if (!result?.data?.length) return null;

  const pieData = useMemo(() => {
    if (!categoricalCols.length) return [];
    const col = categoricalCols[0];
    const counts: Record<string, number> = {};
    for (const row of chartData) {
      const key = String(row[col] ?? 'N/A');
      counts[key] = (counts[key] || 0) + 1;
    }
    return Object.entries(counts)
      .slice(0, 10)
      .map(([name, value]) => ({ name, value }));
  }, [chartData, categoricalCols]);

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Visualizations
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        {numericCols.length > 0 && <Tab label="Bar Chart" />}
        {pieData.length > 0 && <Tab label="Pie Chart" />}
        {numericCols.length >= 2 && <Tab label="Scatter Plot" />}
        {numericCols.length > 0 && <Tab label="Line Chart" />}
      </Tabs>

      <Box sx={{ height: 400 }}>
        {/* Bar Chart */}
        {tab === 0 && numericCols.length > 0 && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData.slice(0, 50)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey={categoricalCols[0] || numericCols[0]}
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {numericCols.slice(0, 4).map((col, i) => (
                <Bar key={col} dataKey={col} fill={COLORS[i % COLORS.length]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )}

        {/* Pie Chart */}
        {tab === 1 && pieData.length > 0 && (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={140}
                label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
                dataKey="value"
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}

        {/* Scatter Plot */}
        {tab === 2 && numericCols.length >= 2 && (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={numericCols[0]} name={numericCols[0]} tick={{ fontSize: 12 }} />
              <YAxis dataKey={numericCols[1]} name={numericCols[1]} tick={{ fontSize: 12 }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={chartData.slice(0, 200)} fill={COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        )}

        {/* Line Chart */}
        {tab === 3 && numericCols.length > 0 && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData.slice(0, 100)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={categoricalCols[0] || numericCols[0]} tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {numericCols.slice(0, 4).map((col, i) => (
                <Line
                  key={col}
                  type="monotone"
                  dataKey={col}
                  stroke={COLORS[i % COLORS.length]}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </Box>
    </Paper>
  );
}
