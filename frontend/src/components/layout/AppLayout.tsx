import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Avatar, Menu, MenuItem,
  Box, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText,
  Divider, Chip, useMediaQuery, useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard, Search, Analytics, Storage,
  Person, Logout, HealthAndSafety, Home,
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
    { label: 'Home', path: '/', icon: <Home /> },
    ...(user
      ? [
          { label: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
          { label: 'Query', path: '/query', icon: <Search /> },
          { label: 'Analytics', path: '/analytics', icon: <Analytics /> },
          { label: 'Schema', path: '/schema', icon: <Storage /> },
          { label: 'Health', path: '/health', icon: <HealthAndSafety /> },
        ]
      : []),
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="sticky" elevation={1} sx={{ bgcolor: 'white', color: 'text.primary' }}>
        <Toolbar>
          {isMobile && (
            <IconButton edge="start" onClick={() => setDrawerOpen(true)} sx={{ mr: 1 }}>
              <MenuIcon />
            </IconButton>
          )}
          <Typography
            variant="h6"
            sx={{ cursor: 'pointer', color: 'primary.main', fontWeight: 700, mr: 4 }}
            onClick={() => navigate('/')}
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
                  sx={{
                    color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                    bgcolor: isActive(item.path) ? 'primary.50' : 'transparent',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}

          <Box sx={{ flexGrow: isMobile ? 1 : 0 }} />

          {user ? (
            <>
              <Chip
                label={user.role}
                size="small"
                color={ROLE_COLORS[user.role] || 'primary'}
                sx={{ mr: 1, textTransform: 'capitalize' }}
              />
              <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
                <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main', fontSize: 16 }}>
                  {user.display_name.charAt(0)}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <MenuItem disabled>
                  <Typography variant="body2" fontWeight={600}>
                    {user.display_name}
                  </Typography>
                </MenuItem>
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
          ) : (
            <Button variant="contained" onClick={() => navigate('/login')}>
              Login
            </Button>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box sx={{ width: 260, pt: 2 }}>
          <Typography variant="h6" sx={{ px: 2, pb: 1, color: 'primary.main', fontWeight: 700 }}>
            {APP_NAME}
          </Typography>
          <Divider />
          <List>
            {navItems.map((item) => (
              <ListItem
                key={item.path}
                onClick={() => { navigate(item.path); setDrawerOpen(false); }}
                sx={{
                  cursor: 'pointer',
                  bgcolor: isActive(item.path) ? 'action.selected' : 'transparent',
                  borderRadius: 1,
                  mx: 1, my: 0.5,
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main content */}
      <Box component="main" sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
        <Outlet />
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
