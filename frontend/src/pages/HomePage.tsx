import { Box, Typography, Button, Grid, Card, CardContent, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const features = [
  {
    icon: <SmartToyIcon sx={{ fontSize: 48 }} color="primary" />,
    title: 'AI-Powered Queries',
    desc: 'Ask questions in plain English and get instant SQL results powered by GPT-4.',
  },
  {
    icon: <SecurityIcon sx={{ fontSize: 48 }} color="secondary" />,
    title: 'Role-Based Access',
    desc: 'Secure RBAC ensures doctors, pharmacies, and admins see only what they should.',
  },
  {
    icon: <QueryStatsIcon sx={{ fontSize: 48 }} color="success" />,
    title: 'Smart Analytics',
    desc: 'Automatic statistical analysis and visualizations on your query results.',
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 48 }} color="warning" />,
    title: 'Real-Time Results',
    desc: 'Fast query execution with interactive data tables and export options.',
  },
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <Box>
      {/* Hero */}
      <Box
        sx={{
          py: 10,
          textAlign: 'center',
          background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
          color: 'white',
          borderRadius: 3,
          mb: 6,
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" fontWeight={700} gutterBottom>
            Skinopathy AICP
          </Typography>
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
            AI-Powered Clinical Intelligence Platform
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, maxWidth: 600, mx: 'auto', opacity: 0.85 }}>
            Transform natural language questions into powerful database queries.
            Get instant insights with AI-driven analysis and smart visualizations.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/login')}
            sx={{
              bgcolor: 'white',
              color: 'primary.main',
              px: 5,
              py: 1.5,
              fontSize: '1.1rem',
              '&:hover': { bgcolor: 'grey.100' },
            }}
          >
            Get Started
          </Button>
        </Container>
      </Box>

      {/* Features */}
      <Container maxWidth="lg">
        <Typography variant="h4" textAlign="center" fontWeight={600} sx={{ mb: 5 }}>
          Platform Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((f) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={f.title}>
              <Card
                sx={{
                  height: '100%',
                  textAlign: 'center',
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 },
                }}
              >
                <CardContent sx={{ py: 4 }}>
                  <Box sx={{ mb: 2 }}>{f.icon}</Box>
                  <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                    {f.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {f.desc}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}
