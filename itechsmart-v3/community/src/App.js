import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';

// iTechSmart Community Components
import CommunityDashboard from './components/CommunityDashboard';
import CertificationCenter from './components/CertificationCenter';
import TalentMarketplace from './components/TalentMarketplace';
import LearningPlatform from './components/LearningPlatform';
import Leaderboard from './components/Leaderboard';
import CommunityForum from './components/CommunityForum';
import UnifiedHeader from './components/UnifiedHeader';
import UnifiedSidebar from './components/UnifiedSidebar';

// iTechSmart Community Theme
const communityTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#667eea',
      light: '#8b9aff',
      dark: '#4c5edb',
    },
    secondary: {
      main: '#764ba2',
      light: '#9d71c5',
      dark: '#573a8a',
    },
    success: {
      main: '#28a745',
      light: '#34ce57',
      dark: '#1e7e34',
    },
    warning: {
      main: '#ffc107',
      light: '#ffcd39',
      dark: '#d39e00',
    },
    error: {
      main: '#dc3545',
      light: '#e4606d',
      dark: '#bd2130',
    },
    info: {
      main: '#17a2b8',
      light: '#33b5e5',
      dark: '#117a8b',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '3rem',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2.5rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h4: {
      fontWeight: 500,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
          borderRadius: 16,
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          padding: '10px 24px',
        },
        contained: {
          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
          '&:hover': {
            boxShadow: '0 6px 20px rgba(102, 126, 234, 0.4)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [communityStats, setCommunityStats] = useState({
    totalMembers: 0,
    certifiedArchitects: 0,
    activeJobs: 0,
    completedCourses: 0,
  });

  useEffect(() => {
    // Initialize user data
    const initializeUser = () => {
      const userData = {
        id: 'user-001',
        name: 'Alex Chen',
        email: 'alex.chen@itechsmart.dev',
        avatar: 'https://i.pravatar.cc/150?img=1',
        level: 'Professional',
        points: 2850,
        badges: [
          { id: 'first-certification', name: 'First Certification', icon: '🏆' },
          { id: 'community-leader', name: 'Community Leader', icon: '🌟' },
          { id: 'ai-expert', name: 'AI Expert', icon: '🤖' },
        ],
        certificates: [
          { id: 'associate', name: 'UAIO Associate', obtained: '2024-01-15' },
          { id: 'professional', name: 'UAIO Professional', obtained: '2024-06-20' },
        ],
        enrolledCourses: 3,
        completedCourses: 12,
        forumPosts: 45,
        reputation: 1250,
      };
      setUser(userData);
    };

    // Load community statistics
    const loadCommunityStats = () => {
      setCommunityStats({
        totalMembers: 15420,
        certifiedArchitects: 3280,
        activeJobs: 247,
        completedCourses: 45680,
      });
    };

    initializeUser();
    loadCommunityStats();
  }, []);

  const handleNotification = (notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 50));
  };

  return (
    <ThemeProvider theme={communityTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <UnifiedSidebar user={user} />
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <UnifiedHeader 
              user={user}
              notifications={notifications}
              communityStats={communityStats}
            />
            <Box component="main" sx={{ flex: 1, p: 3 }}>
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <CommunityDashboard 
                      user={user}
                      communityStats={communityStats}
                      onNotification={handleNotification}
                    />
                  } 
                />
                <Route 
                  path="/certification" 
                  element={
                    <CertificationCenter 
                      user={user}
                      onNotification={handleNotification}
                    />
                  } 
                />
                <Route 
                  path="/marketplace" 
                  element={
                    <TalentMarketplace 
                      user={user}
                      onNotification={handleNotification}
                    />
                  } 
                />
                <Route 
                  path="/learning" 
                  element={
                    <LearningPlatform 
                      user={user}
                      onNotification={handleNotification}
                    />
                  } 
                />
                <Route 
                  path="/leaderboard" 
                  element={
                    <Leaderboard 
                      user={user}
                      onNotification={handleNotification}
                    />
                  } 
                />
                <Route 
                  path="/forum" 
                  element={
                    <CommunityForum 
                      user={user}
                      onNotification={handleNotification}
                    />
                  } 
                />
              </Routes>
            </Box>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;