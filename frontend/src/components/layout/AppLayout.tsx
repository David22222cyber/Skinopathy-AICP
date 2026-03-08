import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Avatar, Menu, MenuItem,
  Box, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText,
  Divider, Chip, useMediaQuery, useTheme, Container,
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard, Search, Analytics, Storage,
  Person, Logout, HealthAndSafety,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '../../hooks/useStore';
import { logout } from '../../store/slices/authSlice';
import { APP_NAME } from '../../config';

const ROLE_COLORS: Record<string, 'primary' | 'secondary' | 'success'> = {
  admin: 'success',
  doctor: 'primary',
  pharmacy: 'secondary',
};

export default function AppLayout() {
  const { user } = useAppSelector((s) => s.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = async () => {
    setAnchorEl(null);
    await dispatch(logout());
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
    { label: 'Query', path: '/query', icon: <Search /> },
    { label: 'Analytics', path: '/analytics', icon: <Analytics /> },
    { label: 'Schema', path: '/schema', icon: <Storage /> },
    { label: 'Health', path: '/health', icon: <HealthAndSafety /> },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'white', color: 'text.primary', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Toolbar sx={{ px: { xs: 2, md: 3 } }}>
          {isMobile && (
            <IconButton edge="start" onClick={() => setDrawerOpen(true)} sx={{ mr: 1 }}>
              <MenuIcon />
            </IconButton>
          )}
          <Typography
            variant="h6"
            sx={{ cursor: 'pointer', color: 'primary.main', fontWeight: 700, mr: 4, whiteSpace: 'nowrap' }}
            onClick={() => navigate('/dashboard')}
          >
            {APP_NAME}
          </Typography>

          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 0.5, flexGrow: 1 }}>
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  startIcon={item.icon}
                  onClick={() => navigate(item.path)}
                  size="small"
                  sx={{
                    color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                    bgcolor: isActive(item.path) ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                    fontWeight: isActive(item.path) ? 600 : 500,
                    '&:hover': { bgcolor: 'rgba(25, 118, 210, 0.04)' },
                    px: 1.5,
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}

          <Box sx={{ flexGrow: isMobile ? 1 : 0 }} />

          {user && (
            <>
              <Chip
                label={user.role}
                size="small"
                color={ROLE_COLORS[user.role] || 'primary'}
                sx={{ mr: 1.5, textTransform: 'capitalize', fontWeight: 600 }}
              />
              <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} size="small">
                <Avatar sx={{ width: 34, height: 34, bgcolor: 'primary.main', fontSize: 15, fontWeight: 600 }}>
                  {user.display_name.charAt(0).toUpperCase()}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                slotProps={{ paper: { sx: { minWidth: 180, mt: 1 } } }}
              >
                <Box sx={{ px: 2, py: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600}>{user.display_name}</Typography>
                  <Typography variant="caption" color="text.secondary">{user.role}</Typography>
                </Box>
                <Divider />
                <MenuItem onClick={() => { setAnchorEl(null); navigate('/profile'); }}>
                  <ListItemIcon><Person fontSize="small" /></ListItemIcon>
                  Profile
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
                  Logout
                </MenuItem>
              </Menu>
            </>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 280, pt: 2 }}>
          <Typography variant="h6" sx={{ px: 2, pb: 1.5, color: 'primary.main', fontWeight: 700 }}>
            {APP_NAME}
          </Typography>
          <Divider />
          <List sx={{ px: 1, pt: 1 }}>
            {navItems.map((item) => (
              <ListItem
                key={item.path}
                onClick={() => { navigate(item.path); setDrawerOpen(false); }}
                sx={{
                  cursor: 'pointer',
                  bgcolor: isActive(item.path) ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                  borderRadius: 2,
                  mb: 0.5,
                  '&:hover': { bgcolor: 'rgba(25, 118, 210, 0.04)' },
                }}
              >
                <ListItemIcon sx={{ color: isActive(item.path) ? 'primary.main' : 'text.secondary', minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: isActive(item.path) ? 600 : 400,
                    color: isActive(item.path) ? 'primary.main' : 'text.primary',
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
        <Container maxWidth="xl" sx={{ py: { xs: 3, md: 4 }, px: { xs: 2, md: 3 } }}>
          <Outlet />
        </Container>
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2, px: 3,
          bgcolor: 'white',
          borderTop: '1px solid',
          borderColor: 'divider',
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          &copy; {new Date().getFullYear()} Skinopathy Research Portal. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
}
