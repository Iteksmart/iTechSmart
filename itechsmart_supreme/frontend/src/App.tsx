import React, { useState } from 'react';
import {
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Container,
  Grid,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  CalendarMonth as CalendarIcon,
  LocalHospital as HospitalIcon,
  Receipt as ReceiptIcon,
  Science as ScienceIcon,
  Inventory as InventoryIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const drawerWidth = 260;

// Create theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00bcd4',
    },
    secondary: {
      main: '#ff4081',
    },
    background: {
      default: '#0a1929',
      paper: '#132f4c',
    },
  },
});

// Mock data
const dashboardStats = {
  total_patients: 1247,
  active_patients: 1189,
  today_appointments: 34,
  pending_appointments: 67,
  pending_bills_amount: 125430.50,
  revenue_this_month: 487650.00,
};

const appointmentData = [
  { name: 'Mon', appointments: 45 },
  { name: 'Tue', appointments: 52 },
  { name: 'Wed', appointments: 48 },
  { name: 'Thu', appointments: 61 },
  { name: 'Fri', appointments: 55 },
  { name: 'Sat', appointments: 28 },
  { name: 'Sun', appointments: 15 },
];

const patientsByAge = [
  { name: '0-18', value: 245 },
  { name: '19-35', value: 387 },
  { name: '36-50', value: 412 },
  { name: '51-65', value: 156 },
  { name: '65+', value: 47 },
];

const recentAppointments = [
  { id: 1, patient: 'John Smith', time: '09:00 AM', doctor: 'Dr. Johnson', status: 'Confirmed' },
  { id: 2, patient: 'Sarah Williams', time: '09:30 AM', doctor: 'Dr. Martinez', status: 'In Progress' },
  { id: 3, patient: 'Michael Brown', time: '10:00 AM', doctor: 'Dr. Johnson', status: 'Scheduled' },
  { id: 4, patient: 'Emily Davis', time: '10:30 AM', doctor: 'Dr. Lee', status: 'Scheduled' },
  { id: 5, patient: 'David Wilson', time: '11:00 AM', doctor: 'Dr. Martinez', status: 'Scheduled' },
];

const COLORS = ['#00bcd4', '#ff4081', '#4caf50', '#ff9800', '#9c27b0'];

function App() {
  const [selectedPage, setSelectedPage] = useState('dashboard');

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'patients', label: 'Patients', icon: <PeopleIcon /> },
    { id: 'appointments', label: 'Appointments', icon: <CalendarIcon /> },
    { id: 'medical-records', label: 'Medical Records', icon: <HospitalIcon /> },
    { id: 'billing', label: 'Billing', icon: <ReceiptIcon /> },
    { id: 'lab-tests', label: 'Lab Tests', icon: <ScienceIcon /> },
    { id: 'inventory', label: 'Inventory', icon: <InventoryIcon /> },
    { id: 'reports', label: 'Reports', icon: <AssessmentIcon /> },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Confirmed':
        return 'success';
      case 'In Progress':
        return 'warning';
      case 'Scheduled':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        {/* App Bar */}
        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            background: 'linear-gradient(135deg, #00bcd4 0%, #0097a7 100%)',
          }}
        >
          <Toolbar>
            <HospitalIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
              iTechSmart Supreme - Healthcare Management
            </Typography>
            <Chip label="iTechSmart Suite" color="secondary" size="small" />
          </Toolbar>
        </AppBar>

        {/* Sidebar */}
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              background: 'linear-gradient(180deg, #132f4c 0%, #0a1929 100%)',
              borderRight: '1px solid rgba(0, 188, 212, 0.2)',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto', mt: 2 }}>
            <List>
              {menuItems.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemButton
                    selected={selectedPage === item.id}
                    onClick={() => setSelectedPage(item.id)}
                    sx={{
                      mx: 1,
                      borderRadius: 1,
                      '&.Mui-selected': {
                        background: 'linear-gradient(135deg, rgba(0, 188, 212, 0.2) 0%, rgba(0, 151, 167, 0.2) 100%)',
                        borderLeft: '3px solid #00bcd4',
                      },
                    }}
                  >
                    <ListItemIcon sx={{ color: selectedPage === item.id ? '#00bcd4' : 'inherit' }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: '#0a1929', minHeight: '100vh' }}>
          <Toolbar />
          <Container maxWidth="xl">
            {selectedPage === 'dashboard' && (
              <>
                <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
                  Healthcare Dashboard
                </Typography>

                {/* Stats Cards */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #00bcd4 0%, #0097a7 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Total Patients</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>
                          {dashboardStats.total_patients.toLocaleString()}
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          {dashboardStats.active_patients} active
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ff4081 0%, #f50057 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Today's Appointments</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>
                          {dashboardStats.today_appointments}
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          {dashboardStats.pending_appointments} pending
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Revenue (Month)</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>
                          ${(dashboardStats.revenue_this_month / 1000).toFixed(0)}K
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          +12.5% from last month
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Pending Bills</Typography>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>
                          ${(dashboardStats.pending_bills_amount / 1000).toFixed(0)}K
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                          Awaiting payment
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Charts */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 3, background: '#132f4c' }}>
                      <Typography variant="h6" gutterBottom>Weekly Appointments</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={appointmentData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#2c5282" />
                          <XAxis dataKey="name" stroke="#90caf9" />
                          <YAxis stroke="#90caf9" />
                          <Tooltip contentStyle={{ backgroundColor: '#132f4c', border: '1px solid #00bcd4' }} />
                          <Legend />
                          <Bar dataKey="appointments" fill="#00bcd4" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Paper>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, background: '#132f4c' }}>
                      <Typography variant="h6" gutterBottom>Patients by Age</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={patientsByAge}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {patientsByAge.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip contentStyle={{ backgroundColor: '#132f4c', border: '1px solid #00bcd4' }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </Paper>
                  </Grid>
                </Grid>

                {/* Recent Appointments */}
                <Paper sx={{ p: 3, background: '#132f4c' }}>
                  <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                    Today's Appointments
                  </Typography>
                  <Grid container spacing={2}>
                    {recentAppointments.map((apt) => (
                      <Grid item xs={12} key={apt.id}>
                        <Card sx={{ background: '#0a1929' }}>
                          <CardContent>
                            <Grid container alignItems="center" spacing={2}>
                              <Grid item xs={12} sm={3}>
                                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                  {apt.patient}
                                </Typography>
                              </Grid>
                              <Grid item xs={12} sm={2}>
                                <Typography variant="body2" color="text.secondary">
                                  {apt.time}
                                </Typography>
                              </Grid>
                              <Grid item xs={12} sm={3}>
                                <Typography variant="body2" color="text.secondary">
                                  {apt.doctor}
                                </Typography>
                              </Grid>
                              <Grid item xs={12} sm={2}>
                                <Chip
                                  label={apt.status}
                                  color={getStatusColor(apt.status) as any}
                                  size="small"
                                />
                              </Grid>
                              <Grid item xs={12} sm={2}>
                                <Button variant="outlined" size="small" fullWidth>
                                  View
                                </Button>
                              </Grid>
                            </Grid>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>
              </>
            )}

            {selectedPage !== 'dashboard' && (
              <Paper sx={{ p: 4, textAlign: 'center', background: '#132f4c' }}>
                <Typography variant="h5" gutterBottom>
                  {menuItems.find(item => item.id === selectedPage)?.label}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                  This section is ready for implementation. The backend API is fully functional.
                </Typography>
                <Button variant="contained" sx={{ mt: 3 }}>
                  Get Started
                </Button>
              </Paper>
            )}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;