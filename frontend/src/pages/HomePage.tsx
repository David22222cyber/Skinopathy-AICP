import {
  Box, Typography, Button, Grid, Card, CardContent, Container,
  AppBar, Toolbar,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { useAppSelector } from '../hooks/useStore';
import { APP_NAME } from '../config';

const features = [
  {
    icon: <SmartToyIcon sx={{ fontSize: 44 }} />,
    title: 'AI-Powered Queries',
    desc: 'Ask questions in plain English and get instant SQL results powered by GPT-4.',
    color: '#e3f2fd',
    iconColor: '#1976d2',
  },
  {
    icon: <SecurityIcon sx={{ fontSize: 44 }} />,
    title: 'Role-Based Access',
    desc: 'Secure RBAC ensures doctors, pharmacies, and admins see only what they should.',
    color: '#f3e8ff',
    iconColor: '#7c3aed',
  },
  {
    icon: <QueryStatsIcon sx={{ fontSize: 44 }} />,
    title: 'Smart Analytics',
    desc: 'Automatic statistical analysis and visualizations on your query results.',
    color: '#dcfce7',
    iconColor: '#16a34a',
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 44 }} />,
    title: 'Real-Time Results',
    desc: 'Fast query execution with interactive data tables and charts.',
    color: '#fff7ed',
    iconColor: '#ea580c',
  },
];

export default function HomePage() {
  const navigate = useNavigate();
  const { token } = useAppSelector((s) => s.auth);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc' }}>
      {/* Public Nav */}
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'white', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar sx={{ px: { xs: 2, md: 4 } }}>
          <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 700, flexGrow: 1 }}>
            {APP_NAME}
          </Typography>
          {token ? (
            <Button variant="contained" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
            </Button>
          ) : (
            <Button variant="contained" onClick={() => navigate('/login')}>
              Sign In
            </Button>
          )}
        </Toolbar>
      </AppBar>

      {/* Hero */}
      <Box
        sx={{
          py: { xs: 8, md: 12 },
          textAlign: 'center',
          background: 'linear-gradient(135deg, #1976d2 0%, #7c3aed 100%)',
          color: 'white',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" fontWeight={700} gutterBottom sx={{ fontSize: { xs: '2rem', md: '3.5rem' } }}>
            Skinopathy AICP
          </Typography>
          <Typography variant="h5" sx={{ mb: 3, opacity: 0.92, fontSize: { xs: '1.1rem', md: '1.5rem' } }}>
            AI-Powered Clinical Intelligence Platform
          </Typography>
          <Typography variant="body1" sx={{ mb: 5, maxWidth: 560, mx: 'auto', opacity: 0.85, lineHeight: 1.7 }}>
            Transform natural language questions into powerful database queries.
            Get instant insights with AI-driven analysis and smart visualizations.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate(token ? '/dashboard' : '/login')}
            sx={{
              bgcolor: 'white',
              color: 'primary.main',
              px: 5,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 600,
              '&:hover': { bgcolor: 'grey.100' },
            }}
          >
            {token ? 'Go to Dashboard' : 'Get Started'}
          </Button>
        </Container>
      </Box>

      {/* Features */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Typography variant="h4" textAlign="center" fontWeight={700} sx={{ mb: 1 }}>
          Platform Features
        </Typography>
        <Typography variant="body1" textAlign="center" color="text.secondary" sx={{ mb: 6, maxWidth: 500, mx: 'auto' }}>
          Everything you need for clinical data intelligence in one platform.
        </Typography>
        <Grid container spacing={3}>
          {features.map((f) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={f.title}>
              <Card
                variant="outlined"
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  transition: 'all 0.2s ease',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 8px 24px rgba(0,0,0,0.08)' },
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ mb: 2, p: 1.5, borderRadius: 3, bgcolor: f.color, display: 'inline-flex', color: f.iconColor }}>
                    {f.icon}
                  </Box>
                  <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                    {f.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                    {f.desc}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Footer */}
      <Box sx={{ py: 4, textAlign: 'center', borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary">
          &copy; {new Date().getFullYear()} Skinopathy Research Portal. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
}
