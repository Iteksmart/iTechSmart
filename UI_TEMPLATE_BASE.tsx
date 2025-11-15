/**
 * Base UI Template for iTechSmart Products
 * This template provides a consistent, professional interface
 * that can be customized for each product
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Chip,
  Avatar,
  IconButton,
  Badge,
  Divider,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';

import {
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Menu as MenuIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';

interface DashboardProps {
  productName: string;
  productIcon: React.ReactElement;
  primaryColor?: string;
  menuItems: MenuItem[];
  statsCards: StatsCard[];
  mainContent: React.ReactNode;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactElement;
  onClick?: () => void;
}

interface StatsCard {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactElement;
  color?: string;
}

const BaseDashboard: React.FC<DashboardProps> = ({
  productName,
  productIcon,
  primaryColor = '#1976d2',
  menuItems,
  statsCards,
  mainContent
}) => {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [selectedMenuItem, setSelectedMenuItem] = useState(menuItems[0]?.id || '');

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          bgcolor: primaryColor
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Avatar sx={{ bgcolor: 'white', color: primaryColor, mr: 2 }}>
              {productIcon}
            </Avatar>
            <Typography variant="h6" noWrap>
              {productName}
            </Typography>
          </Box>

          <TextField
            placeholder="Search..."
            size="small"
            sx={{ 
              mr: 2,
              bgcolor: 'rgba(255,255,255,0.15)',
              borderRadius: 1,
              '& .MuiOutlinedInput-root': {
                color: 'white',
                '& fieldset': { borderColor: 'transparent' }
              }
            }}
            InputProps={{
              startAdornment: <SearchIcon sx={{ color: 'white', mr: 1 }} />
            }}
          />

          <IconButton color="inherit">
            <Badge badgeContent={3} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          
          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: 260,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 260,
            boxSizing: 'border-box',
            mt: 8,
            borderRight: '1px solid rgba(0,0,0,0.12)'
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            NAVIGATION
          </Typography>
          <List>
            {menuItems.map((item) => (
              <ListItemButton
                key={item.id}
                selected={selectedMenuItem === item.id}
                onClick={() => {
                  setSelectedMenuItem(item.id);
                  item.onClick?.();
                }}
                sx={{ 
                  borderRadius: 1, 
                  mb: 0.5,
                  '&.Mui-selected': {
                    bgcolor: `${primaryColor}15`,
                    '&:hover': { bgcolor: `${primaryColor}25` }
                  }
                }}
              >
                <ListItemIcon sx={{ color: selectedMenuItem === item.id ? primaryColor : 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ p: 2, bgcolor: `${primaryColor}10`, borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              System Status
            </Typography>
            <Chip label="Operational" color="success" size="small" />
            <Typography variant="caption" display="block" sx={{ mt: 1 }} color="text.secondary">
              All systems running normally
            </Typography>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: drawerOpen ? 0 : -32.5,
          transition: 'margin 0.3s'
        }}
      >
        <Container maxWidth="xl">
          {/* Stats Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {statsCards.map((card, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box>
                        <Typography color="text.secondary" variant="body2" gutterBottom>
                          {card.title}
                        </Typography>
                        <Typography variant="h4" sx={{ mb: 1 }}>
                          {card.value}
                        </Typography>
                        {card.subtitle && (
                          <Typography variant="body2" color="text.secondary">
                            {card.subtitle}
                          </Typography>
                        )}
                        {card.trendValue && (
                          <Typography 
                            variant="body2" 
                            color={
                              card.trend === 'up' ? 'success.main' : 
                              card.trend === 'down' ? 'error.main' : 
                              'text.secondary'
                            }
                            sx={{ mt: 0.5 }}
                          >
                            {card.trend === 'up' ? '↑' : card.trend === 'down' ? '↓' : '→'} {card.trendValue}
                          </Typography>
                        )}
                      </Box>
                      {card.icon && (
                        <Avatar sx={{ bgcolor: card.color || primaryColor }}>
                          {card.icon}
                        </Avatar>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Main Content Area */}
          {mainContent}
        </Container>
      </Box>
    </Box>
  );
};

export default BaseDashboard;