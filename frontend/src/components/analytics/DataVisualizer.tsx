import { useMemo, useState } from 'react';
import { Paper, Typography, Box, Tabs, Tab } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  ScatterChart, Scatter, LineChart, Line,
} from 'recharts';
import { useAppSelector } from '../../hooks/useStore';

const COLORS = ['#1976d2', '#7c3aed', '#16a34a', '#ea580c', '#dc2626', '#0891b2', '#78716c', '#475569'];

type ChartType = 'bar' | 'pie' | 'scatter' | 'line';

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

  const pieData = useMemo(() => {
    if (!categoricalCols.length) return [];
    const col = categoricalCols[0];
    const counts: Record<string, number> = {};
    for (const row of chartData) {
      const key = String(row[col] ?? 'N/A');
      counts[key] = (counts[key] || 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name, value]) => ({ name, value }));
  }, [chartData, categoricalCols]);

  const availableTabs = useMemo(() => {
    const tabs: { label: string; type: ChartType }[] = [];
    if (numericCols.length > 0) tabs.push({ label: 'Bar Chart', type: 'bar' });
    if (pieData.length > 0) tabs.push({ label: 'Pie Chart', type: 'pie' });
    if (numericCols.length >= 2) tabs.push({ label: 'Scatter Plot', type: 'scatter' });
    if (numericCols.length > 0) tabs.push({ label: 'Line Chart', type: 'line' });
    return tabs;
  }, [numericCols, pieData]);

  if (!result?.data?.length || availableTabs.length === 0) return null;

  const safeTab = Math.min(tab, availableTabs.length - 1);
  const activeChart = availableTabs[safeTab]?.type;

  return (
    <Paper variant="outlined" sx={{ p: 3, mt: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Visualizations
      </Typography>

      <Tabs
        value={safeTab}
        onChange={(_, v) => setTab(v)}
        sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
      >
        {availableTabs.map((t) => (
          <Tab key={t.type} label={t.label} />
        ))}
      </Tabs>

      <Box sx={{ height: 400 }}>
        {activeChart === 'bar' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData.slice(0, 50)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey={categoricalCols[0] || numericCols[0]}
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              {numericCols.slice(0, 4).map((col, i) => (
                <Bar key={col} dataKey={col} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )}

        {activeChart === 'pie' && (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={140}
                innerRadius={60}
                label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
                dataKey="value"
                paddingAngle={2}
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

        {activeChart === 'scatter' && (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey={numericCols[0]} name={numericCols[0]} tick={{ fontSize: 12 }} />
              <YAxis dataKey={numericCols[1]} name={numericCols[1]} tick={{ fontSize: 12 }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={chartData.slice(0, 200)} fill={COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        )}

        {activeChart === 'line' && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData.slice(0, 100)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
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
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </Box>
    </Paper>
  );
}
