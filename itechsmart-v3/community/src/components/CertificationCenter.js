import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  School,
  EmojiEvents,
  Timeline,
  ExpandMore,
  PlayArrow,
  CheckCircle,
  RadioButtonUnchecked,
  Star,
  TrendingUp,
  Book,
  Assessment,
  Code,
  Security,
  Cloud,
  AttachMoney,
  People,
  Lightbulb,
  Rocket,
  WorkspacePremium,
  MilitaryTech,
  Verified,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const CertificationCenter = ({ user, onNotification }) => {
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedCertification, setSelectedCertification] = useState(null);
  const [examDialog, setExamDialog] = useState(false);
  const [certificationProgress, setCertificationProgress] = useState({});

  // iTechSmart UAIO Certification Levels
  const certificationLevels = [
    {
      id: 'associate',
      name: 'UAIO Associate',
      description: 'Foundational knowledge of iTechSmart Suite and basic operations',
      duration: '2-3 months',
      difficulty: 'Beginner',
      prerequisites: ['Basic IT knowledge'],
      modules: 6,
      examDuration: '90 minutes',
      passingScore: 70,
      price: '$299',
      icon: <School />,
      color: '#4caf50',
      skills: [
        'Basic iTechSmart navigation',
        'Product overview',
        'Essential operations',
        'Security fundamentals',
        'Basic automation',
        'Monitoring concepts'
      ]
    },
    {
      id: 'professional',
      name: 'UAIO Professional',
      description: 'Advanced proficiency in iTechSmart Suite with hands-on implementation skills',
      duration: '4-6 months',
      difficulty: 'Intermediate',
      prerequisites: ['UAIO Associate', '6 months experience'],
      modules: 8,
      examDuration: '120 minutes',
      passingScore: 75,
      price: '$599',
      icon: <TrendingUp />,
      color: '#2196f3',
      skills: [
        'Advanced product integration',
        'Workflow automation',
        'Security management',
        'Cost optimization',
        'DevOps practices',
        'AI operations',
        'Cross-product orchestration'
      ]
    },
    {
      id: 'master',
      name: 'UAIO Master',
      description: 'Expert-level mastery with enterprise architecture and strategic implementation',
      duration: '8-12 months',
      difficulty: 'Advanced',
      prerequisites: ['UAIO Professional', '2 years experience'],
      modules: 12,
      examDuration: '180 minutes',
      passingScore: 80,
      price: '$999',
      icon: <WorkspacePremium />,
      color: '#ff9800',
      skills: [
        'Enterprise architecture',
        'Strategic planning',
        'Advanced AI integration',
        'Multi-cloud management',
        'Security architecture',
        'Business transformation',
        'Team leadership',
        'Innovation management'
      ]
    },
    {
      id: 'fellow',
      name: 'UAIO Fellow',
      description: 'Industry recognition for thought leadership and iTechSmart innovation',
      duration: 'Ongoing',
      difficulty: 'Expert',
      prerequisites: ['UAIO Master', '5 years experience', 'Industry contributions'],
      modules: 0,
      examDuration: 'Panel review',
      passingScore: 90,
      price: 'Application only',
      icon: <MilitaryTech />,
      color: '#9c27b0',
      skills: [
        'Thought leadership',
        'Industry innovation',
        'Community contribution',
        'Research & development',
        'Mentoring',
        'Strategic advisory',
        'Public speaking',
        'Publication'
      ]
    }
  ];

  // Sample course modules for Professional certification
  const courseModules = [
    {
      id: 1,
      title: 'Advanced iTechSmart Architecture',
      duration: '4 weeks',
      lessons: 12,
      difficulty: 'Intermediate',
      progress: 85,
      topics: ['Neural Data Plane', 'Event Bus Architecture', 'Microservices Integration'],
      icon: <Architecture />
    },
    {
      id: 2,
      title: 'AI-First Operations',
      duration: '3 weeks',
      lessons: 10,
      difficulty: 'Intermediate',
      progress: 60,
      topics: ['Natural Language Commands', 'Workflow Orchestration', 'AI Automation'],
      icon: <SmartToy />
    },
    {
      id: 3,
      title: 'Enterprise Security Management',
      duration: '5 weeks',
      lessons: 15,
      difficulty: 'Advanced',
      progress: 40,
      topics: ['Zero-Trust Architecture', 'Threat Intelligence', 'Compliance Management'],
      icon: <Security />
    },
    {
      id: 4,
      title: 'Financial Operations (FinOps)',
      duration: '3 weeks',
      lessons: 9,
      difficulty: 'Intermediate',
      progress: 25,
      topics: ['Cost Optimization', 'Budget Management', 'ROI Analysis'],
      icon: <AttachMoney />
    },
    {
      id: 5,
      title: 'DevOps and CI/CD Integration',
      duration: '4 weeks',
      lessons: 11,
      difficulty: 'Advanced',
      progress: 0,
      topics: ['Pipeline Automation', 'Container Management', 'Infrastructure as Code'],
      icon: <Code />
    },
    {
      id: 6,
      title: 'Multi-Cloud Infrastructure',
      duration: '5 weeks',
      lessons: 14,
      difficulty: 'Advanced',
      progress: 0,
      topics: ['Cloud Orchestration', 'Hybrid Management', 'Edge Computing'],
      icon: <Cloud />
    }
  ];

  // Learning progress data
  const learningProgress = [
    { month: 'Jan', completed: 2, started: 5 },
    { month: 'Feb', completed: 3, started: 7 },
    { month: 'Mar', completed: 4, started: 8 },
    { month: 'Apr', completed: 6, started: 9 },
    { month: 'May', completed: 8, started: 11 },
    { month: 'Jun', completed: 10, started: 12 },
  ];

  const handleCertificationSelect = (certification) => {
    setSelectedCertification(certification);
    setCurrentTab(1);
  };

  const handleStartExam = () => {
    setExamDialog(true);
    onNotification({
      type: 'certification',
      title: 'Exam Started',
      message: `You have started the ${selectedCertification.name} certification exam`,
      timestamp: new Date(),
    });
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const CertificationCard = ({ cert, isEnrolled = false, progress = 0 }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar sx={{ bgcolor: cert.color, mr: 2, width: 56, height: 56 }}>
            {cert.icon}
          </Avatar>
          <Box flex={1}>
            <Typography variant="h6" fontWeight="bold">
              {cert.name}
            </Typography>
            <Chip 
              label={cert.difficulty}
              size="small"
              color={cert.difficulty === 'Beginner' ? 'success' : 
                     cert.difficulty === 'Intermediate' ? 'primary' :
                     cert.difficulty === 'Advanced' ? 'warning' : 'error'}
            />
          </Box>
          {isEnrolled && (
            <Chip 
              icon={<TrendingUp />}
              label={`${progress}%`}
              color="primary"
              variant="outlined"
            />
          )}
        </Box>

        <Typography variant="body2" color="text.secondary" mb={2}>
          {cert.description}
        </Typography>

        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Duration</Typography>
            <Typography variant="body2" fontWeight="medium">{cert.duration}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Modules</Typography>
            <Typography variant="body2" fontWeight="medium">{cert.modules}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Exam Duration</Typography>
            <Typography variant="body2" fontWeight="medium">{cert.examDuration}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Passing Score</Typography>
            <Typography variant="body2" fontWeight="medium">{cert.passingScore}%</Typography>
          </Grid>
        </Grid>

        {isEnrolled && progress > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="text.secondary">Progress</Typography>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ mt: 0.5, height: 8, borderRadius: 4 }}
            />
          </Box>
        )}

        <Box mb={2}>
          <Typography variant="subtitle2" gutterBottom>Key Skills:</Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {cert.skills.slice(0, 3).map((skill, index) => (
              <Chip key={index} label={skill} size="small" variant="outlined" />
            ))}
          </Box>
        </Box>

        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" color="primary.main" fontWeight="bold">
            {cert.price}
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => handleCertificationSelect(cert)}
            startIcon={isEnrolled ? <PlayArrow /> : <School />}
          >
            {isEnrolled ? 'Continue Learning' : 'Enroll Now'}
          </Button>
        </Box>

        {user?.certificates?.find(c => c.id === cert.id) && (
          <Chip 
            icon={<Verified />}
            label="CERTIFIED"
            color="success"
            sx={{ position: 'absolute', top: -10, right: 20 }}
          />
        )}
      </CardContent>
    </Card>
  );

  const ModuleCard = ({ module }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
            {module.icon}
          </Avatar>
          <Box flex={1}>
            <Typography variant="h6" fontWeight="medium">
              {module.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {module.duration} • {module.lessons} lessons
            </Typography>
          </Box>
          <Box textAlign="right">
            <Typography variant="h6" color="primary.main">
              {module.progress}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Complete
            </Typography>
          </Box>
        </Box>

        <LinearProgress 
          variant="determinate" 
          value={module.progress} 
          sx={{ mb: 2, height: 8, borderRadius: 4 }}
        />

        <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
          {module.topics.map((topic, index) => (
            <Chip key={index} label={topic} size="small" variant="outlined" />
          ))}
        </Box>

        <Box display="flex" justifyContent="space-between">
          <Button variant="outlined" size="small">
            View Details
          </Button>
          <Button variant="contained" size="small">
            {module.progress > 0 ? 'Continue' : 'Start'} Module
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          🎓 UAIO Architect Certification
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Become a certified iTechSmart expert and join the elite community of AI operations professionals
        </Typography>
      </Box>

      {/* User Status */}
      {user && (
        <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'white', color: 'primary.main', mr: 2, width: 64, height: 64 }}>
                  <School />
                </Avatar>
                <Box>
                  <Typography variant="h5" fontWeight="bold">
                    {user.name}
                  </Typography>
                  <Typography variant="h6">
                    Level: {user.level}
                  </Typography>
                  <Box display="flex" alignItems-center" mt={1}>
                    <Star sx={{ mr: 1 }} />
                    <Typography variant="body1">
                      {user.points} points • {user.completedCourses} courses completed
                    </Typography>
                  </Box>
                </Box>
              </Box>
              <Box textAlign="right">
                <Typography variant="h4" fontWeight="bold">
                  {user.certificates?.length || 0}
                </Typography>
                <Typography variant="body2">
                  Certifications Earned
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} variant="scrollable">
          <Tab label="All Certifications" />
          <Tab label="Learning Path" />
          <Tab label="Progress & Analytics" />
          <Tab label="Exams & Assessments" />
          <Tab label="Community & Recognition" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {currentTab === 0 && (
        <Grid container spacing={3}>
          {certificationLevels.map((cert) => {
            const isEnrolled = user?.level === 'Professional' && cert.id !== 'associate';
            const progress = cert.id === 'professional' ? 65 : 0;
            
            return (
              <Grid item xs={12} md={6} key={cert.id}>
                <CertificationCard 
                  cert={cert} 
                  isEnrolled={isEnrolled}
                  progress={progress}
                />
              </Grid>
            );
          })}
        </Grid>
      )}

      {currentTab === 1 && selectedCertification && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h5" fontWeight="bold" mb={2}>
              Learning Path: {selectedCertification.name}
            </Typography>
            
            {courseModules.map((module) => (
              <ModuleCard key={module.id} module={module} />
            ))}
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>Prerequisites</Typography>
                <List dense>
                  {selectedCertification.prerequisites.map((prereq, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary={prereq} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Study Timeline</Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={learningProgress}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="completed" stroke="#667eea" strokeWidth={2} />
                    <Line type="monotone" dataKey="started" stroke="#764ba2" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {currentTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Learning Progress</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={learningProgress}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="completed" fill="#667eea" />
                    <Bar dataKey="started" fill="#764ba2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Achievement Statistics</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon><EmojiEvents color="primary" /></ListItemIcon>
                    <ListItemText 
                      primary="Total Points" 
                      secondary={`${user?.points || 0} points earned`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Book color="success" /></ListItemIcon>
                    <ListItemText 
                      primary="Courses Completed" 
                      secondary={`${user?.completedCourses || 0} courses`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Assessment color="warning" /></ListItemIcon>
                    <ListItemText 
                      primary="Exam Average" 
                      secondary="85.6% across all exams" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><TrendingUp color="info" /></ListItemIcon>
                    <ListItemText 
                      primary="Learning Streak" 
                      secondary="23 days consecutive learning" 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {currentTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Upcoming Exams</Typography>
                <List>
                  <ListItem divider>
                    <ListItemIcon><Assessment color="primary" /></ListItemIcon>
                    <ListItemText 
                      primary="UAIO Professional - Final Exam" 
                      secondary="Scheduled for July 15, 2024 • 120 minutes" 
                    />
                    <Button variant="contained" onClick={handleStartExam}>
                      Start Exam
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Assessment color="secondary" /></ListItemIcon>
                    <ListItemText 
                      primary="Module 5 Assessment" 
                      secondary="Available now • 30 minutes" 
                    />
                    <Button variant="outlined">
                      Practice
                    </Button>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Exam History</Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                    <ListItemText 
                      primary="UAIO Associate" 
                      secondary="Score: 92% • Jan 15, 2024" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                    <ListItemText 
                      primary="Module 1-4 Assessments" 
                      secondary="Average: 88% • Jun 2024" 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {currentTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Badges & Achievements</Typography>
                <Grid container spacing={2}>
                  {user?.badges?.map((badge, index) => (
                    <Grid item xs={6} key={index}>
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h3" mb={1}>{badge.icon}</Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {badge.name}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Community Recognition</Typography>
                <List>
                  <ListItem>
                    <ListItemIcon><People color="primary" /></ListItemIcon>
                    <ListItemText 
                      primary="Mentor Status" 
                      secondary="Mentoring 3 junior professionals" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Lightbulb color="warning" /></ListItemIcon>
                    <ListItemText 
                      primary="Innovation Contributor" 
                      secondary="5 workflow templates published" 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Rocket color="success" /></ListItemIcon>
                    <ListItemText 
                      primary="Early Adopter" 
                      secondary="First 100 certified professionals" 
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Exam Dialog */}
      <Dialog open={examDialog} onClose={() => setExamDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <Assessment sx={{ mr: 1 }} />
            {selectedCertification?.name} - Certification Exam
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            You are about to start the certification exam. Please review the following information:
          </Typography>
          
          <Box mt={2}>
            <Stepper activeStep={-1} orientation="vertical">
              <Step>
                <StepLabel>Exam Instructions</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    • You have {selectedCertification?.examDuration} to complete the exam<br/>
                    • Passing score: {selectedCertification?.passingScore}%<br/>
                    • Questions are multiple-choice and scenario-based<br/>
                    • You cannot pause the exam once started
                  </Typography>
                </StepContent>
              </Step>
              <Step>
                <StepLabel>System Check</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    • Stable internet connection required<br/>
                    • Webcam and microphone enabled<br/>
                    • Screen sharing will be monitored
                  </Typography>
                </StepContent>
              </Step>
              <Step>
                <StepLabel>Begin Exam</StepLabel>
                <StepContent>
                  <Typography variant="body2">
                    Click "Start Exam" when you're ready to begin. Good luck!
                  </Typography>
                </StepContent>
              </Step>
            </Stepper>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExamDialog(false)}>Cancel</Button>
          <Button variant="contained" color="primary">
            Start Exam
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CertificationCenter;