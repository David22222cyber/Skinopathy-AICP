import { Box, Container, Typography, AppBar, Toolbar, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import { APP_NAME } from '../config';

export default function LoginPage() {
  const navigate = useNavigate();

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8fafc' }}>
      {/* Public Nav */}
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'white', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar sx={{ px: { xs: 2, md: 4 } }}>
          <Typography
            variant="h6"
            sx={{ color: 'primary.main', fontWeight: 700, flexGrow: 1, cursor: 'pointer' }}
            onClick={() => navigate('/')}
          >
            {APP_NAME}
          </Typography>
          <Button variant="outlined" onClick={() => navigate('/')}>
            Back to Home
          </Button>
        </Toolbar>
      </AppBar>

      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 'calc(100vh - 64px)',
          py: 4,
        }}
      >
        <Container maxWidth="sm">
          <LoginForm />
        </Container>
      </Box>
    </Box>
  );
}
