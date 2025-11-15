import { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Button,
  IconButton,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  FolderSpecial as ProjectIcon,
  People as TeamIcon,
  SmartToy as AIIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';

const COLORS = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0'];

export default function Dashboard() {
  const [stats] = useState({
    totalProjects: 12,
    activeProjects: 8,
    completedProjects: 4,
    teamMembers: 15,
    aiRequests: 245,
    avgProgress: 67.5,
  });

  const [projectsByStatus] = useState([
    { name: 'Ideation', value: 2, color: '#9c27b0' },
    { name: 'Planning', value: 1, color: '#2196f3' },
    { name: 'Development', value: 5, color: '#ff9800' },
    { name: 'Testing', value: 2, color: '#4caf50' },
    { name: 'Completed', value: 4, color: '#4caf50' },
  ]);

  const [weeklyActivity] = useState([
    { day: 'Mon', projects: 3, tasks: 12, ai: 8 },
    { day: 'Tue', projects: 4, tasks: 15, ai: 12 },
    { day: 'Wed', projects: 5, tasks: 18, ai: 15 },
    { day: 'Thu', projects: 4, tasks: 14, ai: 10 },
    { day: 'Fri', projects: 6, tasks: 20, ai: 18 },
    { day: 'Sat', projects: 2, tasks: 8, ai: 5 },
    { day: 'Sun', projects: 1, tasks: 4, ai: 3 },
  ]);

  const [recentProjects] = useState([
    { id: 1, name: 'E-Commerce Platform', client: 'TechCorp', progress: 75, status: 'development', team: 4 },
    { id: 2, name: 'Mobile Banking App', client: 'FinanceHub', progress: 45, status: 'development', team: 3 },
    { id: 3, name: 'Healthcare Portal', client: 'MediCare', progress: 90, status: 'testing', team: 5 },
    { id: 4, name: 'Inventory System', client: 'RetailPro', progress: 30, status: 'planning', team: 2 },
  ]);

  const [recentAIRequests] = useState([
    { id: 1, type: 'Code Generation', project: 'E-Commerce Platform', status: 'completed', time: '2 min ago' },
    { id: 2, type: 'App Scaffolding', project: 'Mobile Banking App', status: 'completed', time: '15 min ago' },
    { id: 3, type: 'Bug Fix', project: 'Healthcare Portal', status: 'processing', time: '30 min ago' },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'development': return 'primary';
      case 'testing': return 'warning';
      case 'planning': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Welcome to Think-Tank 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your AI-powered platform for creating custom applications
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                    Total Projects
                  </Typography>
                  <Typography variant="h3" color="white" fontWeight={700}>
                    {stats.totalProjects}
                  </Typography>
                  <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
                    {stats.activeProjects} active
                  </Typography>
                </Box>
                <ProjectIcon sx={{ fontSize: 48, color: 'white', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                    Team Members
                  </Typography>
                  <Typography variant="h3" color="white" fontWeight={700}>
                    {stats.teamMembers}
                  </Typography>
                  <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
                    Across all projects
                  </Typography>
                </Box>
                <TeamIcon sx={{ fontSize: 48, color: 'white', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                    AI Requests
                  </Typography>
                  <Typography variant="h3" color="white" fontWeight={700}>
                    {stats.aiRequests}
                  </Typography>
                  <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
                    This month
                  </Typography>
                </Box>
                <AIIcon sx={{ fontSize: 48, color: 'white', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                    Avg Progress
                  </Typography>
                  <Typography variant="h3" color="white" fontWeight={700}>
                    {stats.avgProgress}%
                  </Typography>
                  <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
                    Across active projects
                  </Typography>
                </Box>
                <TrendingUpIcon sx={{ fontSize: 48, color: 'white', opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Weekly Activity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weeklyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="projects" stroke="#2196f3" strokeWidth={2} name="Projects" />
                <Line type="monotone" dataKey="tasks" stroke="#4caf50" strokeWidth={2} name="Tasks" />
                <Line type="monotone" dataKey="ai" stroke="#ff9800" strokeWidth={2} name="AI Requests" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Projects by Status
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={projectsByStatus}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {projectsByStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight={600}>
                Active Projects
              </Typography>
              <Button size="small" variant="outlined">
                View All
              </Button>
            </Box>
            <List>
              {recentProjects.map((project) => (
                <ListItem
                  key={project.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    mb: 1,
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      <ProjectIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1" fontWeight={600}>
                          {project.name}
                        </Typography>
                        <Chip
                          label={project.status}
                          size="small"
                          color={getStatusColor(project.status) as any}
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Client: {project.client} • Team: {project.team} members
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={project.progress}
                            sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                          />
                          <Typography variant="caption" fontWeight={600}>
                            {project.progress}%
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" fontWeight={600}>
                Recent AI Activity
              </Typography>
              <Chip label="SuperNinja" color="secondary" size="small" />
            </Box>
            <List>
              {recentAIRequests.map((request) => (
                <ListItem
                  key={request.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    mb: 1,
                  }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'secondary.main' }}>
                      <AIIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Typography variant="body2" fontWeight={600}>
                        {request.type}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography variant="caption" color="text.secondary">
                          {request.project}
                        </Typography>
                        <br />
                        <Chip
                          label={request.status}
                          size="small"
                          color={request.status === 'completed' ? 'success' : 'primary'}
                          sx={{ mt: 0.5, height: 20 }}
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                          {request.time}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AIIcon />}
              sx={{ mt: 2 }}
            >
              Open SuperNinja Agent
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}