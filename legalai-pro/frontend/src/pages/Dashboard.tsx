import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
} from '@mui/material';
import {
  TrendingUp,
  People,
  Gavel,
  AttachMoney,
  SmartToy,
  ArrowForward,
  CheckCircle,
  Schedule,
  Warning,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const statsData = [
  { title: 'Total Clients', value: '248', change: '+12%', icon: <People />, color: '#1976d2' },
  { title: 'Active Cases', value: '89', change: '+8%', icon: <Gavel />, color: '#9c27b0' },
  { title: 'Revenue (MTD)', value: '$124,500', change: '+15%', icon: <AttachMoney />, color: '#2e7d32' },
  { title: 'AI Queries', value: '1,247', change: '+45%', icon: <SmartToy />, color: '#ed6c02' },
];

const caseData = [
  { name: 'Civil', value: 35, color: '#1976d2' },
  { name: 'Criminal', value: 20, color: '#9c27b0' },
  { name: 'Family', value: 15, color: '#2e7d32' },
  { name: 'Corporate', value: 19, color: '#ed6c02' },
];

const revenueData = [
  { month: 'Jan', revenue: 85000 },
  { month: 'Feb', revenue: 92000 },
  { month: 'Mar', revenue: 78000 },
  { month: 'Apr', revenue: 105000 },
  { month: 'May', revenue: 98000 },
  { month: 'Jun', revenue: 124500 },
];

const recentCases = [
  { id: 1, title: 'Smith v. Johnson', client: 'John Smith', status: 'active', priority: 'high' },
  { id: 2, title: 'Estate Planning - Williams', client: 'Sarah Williams', status: 'pending', priority: 'medium' },
  { id: 3, title: 'Corporate Merger - TechCorp', client: 'TechCorp Inc.', status: 'active', priority: 'high' },
  { id: 4, title: 'Divorce Settlement - Brown', client: 'Michael Brown', status: 'review', priority: 'low' },
];

const upcomingEvents = [
  { id: 1, title: 'Court Hearing - Smith v. Johnson', time: 'Today, 2:00 PM', type: 'hearing' },
  { id: 2, title: 'Client Meeting - Williams Estate', time: 'Tomorrow, 10:00 AM', type: 'meeting' },
  { id: 3, title: 'Deposition - TechCorp Merger', time: 'Dec 28, 3:00 PM', type: 'deposition' },
  { id: 4, title: 'Filing Deadline - Brown Divorce', time: 'Dec 30, 5:00 PM', type: 'deadline' },
];

export default function Dashboard() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Welcome back, Attorney! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your practice today.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statsData.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
                      {stat.value}
                    </Typography>
                    <Chip
                      label={stat.change}
                      size="small"
                      sx={{
                        bgcolor: 'rgba(46, 125, 50, 0.1)',
                        color: '#2e7d32',
                        fontWeight: 600,
                      }}
                    />
                  </Box>
                  <Avatar sx={{ bgcolor: stat.color, width: 56, height: 56 }}>
                    {stat.icon}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Revenue Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Revenue Overview
                </Typography>
                <Button size="small" endIcon={<ArrowForward />}>
                  View Details
                </Button>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="revenue" fill="#1976d2" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Cases by Type */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Cases by Type
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={caseData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {caseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2 }}>
                {caseData.map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: item.color,
                          mr: 1,
                        }}
                      />
                      <Typography variant="body2">{item.name}</Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {item.value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Cases */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Recent Cases
                </Typography>
                <Button size="small" endIcon={<ArrowForward />}>
                  View All
                </Button>
              </Box>
              <List>
                {recentCases.map((case_) => (
                  <ListItem
                    key={case_.id}
                    sx={{
                      border: '1px solid #f0f0f0',
                      borderRadius: 2,
                      mb: 1,
                      '&:hover': { bgcolor: '#f5f7fa' },
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        <Gavel />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={case_.title}
                      secondary={case_.client}
                      primaryTypographyProps={{ fontWeight: 600 }}
                    />
                    <Chip
                      label={case_.status}
                      size="small"
                      color={case_.status === 'active' ? 'success' : 'default'}
                    />
                    {case_.priority === 'high' && (
                      <Warning sx={{ ml: 1, color: 'error.main' }} />
                    )}
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Events */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Upcoming Events
                </Typography>
                <Button size="small" endIcon={<ArrowForward />}>
                  View Calendar
                </Button>
              </Box>
              <List>
                {upcomingEvents.map((event) => (
                  <ListItem
                    key={event.id}
                    sx={{
                      border: '1px solid #f0f0f0',
                      borderRadius: 2,
                      mb: 1,
                      '&:hover': { bgcolor: '#f5f7fa' },
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'secondary.main' }}>
                        <Schedule />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={event.title}
                      secondary={event.time}
                      primaryTypographyProps={{ fontWeight: 600 }}
                    />
                    <Chip label={event.type} size="small" variant="outlined" />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Assistant Quick Access */}
        <Grid item xs={12}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={8}>
                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                    🤖 AI Assistant Ready to Help
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2, opacity: 0.9 }}>
                    Get instant legal research, document analysis, case predictions, and more with our revolutionary AI assistant.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label="Legal Research"
                      sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                    />
                    <Chip
                      label="Contract Analysis"
                      sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                    />
                    <Chip
                      label="Document Auto-Fill"
                      sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                    />
                    <Chip
                      label="Case Prediction"
                      sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
                  <Button
                    variant="contained"
                    size="large"
                    sx={{
                      bgcolor: 'white',
                      color: 'primary.main',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.9)' },
                      px: 4,
                      py: 1.5,
                    }}
                    endIcon={<ArrowForward />}
                  >
                    Open AI Assistant
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}