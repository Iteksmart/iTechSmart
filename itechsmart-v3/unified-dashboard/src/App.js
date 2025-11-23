import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { io } from 'socket.io-client';

// iTechSmart Components
import MasterDashboard from './components/MasterDashboard';
import UnifiedNavbar from './components/UnifiedNavbar';
import UnifiedSidebar from './components/UnifiedSidebar';
import NotificationCenter from './components/NotificationCenter';
import AIAssistant from './components/AIAssistant';

// Create unified iTechSmart theme
const itechsmartTheme = createTheme({
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
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    success: {
      main: '#28a745',
    },
    warning: {
      main: '#ffc107',
    },
    error: {
      main: '#dc3545',
    },
    info: {
      main: '#17a2b8',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h4: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          borderRadius: 16,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  const [socket, setSocket] = useState(null);
  const [realTimeData, setRealTimeData] = useState({
    security: {},
    finops: {},
    devops: {},
    events: []
  });
  const [notifications, setNotifications] = useState([]);
  const [aiAssistantOpen, setAiAssistantOpen] = useState(false);

  useEffect(() => {
    // Connect to iTechSmart Neural Hub
    const newSocket = io(process.env.REACT_APP_NEURAL_HUB_URL || 'http://localhost:8080');
    
    newSocket.on('connect', () => {
      console.log('🔌 Connected to iTechSmart Neural Hub');
    });

    newSocket.on('neural-event', (event) => {
      handleNeuralEvent(event);
    });

    newSocket.on('security-update', (data) => {
      setRealTimeData(prev => ({
        ...prev,
        security: { ...prev.security, ...data }
      }));
    });

    newSocket.on('finops-update', (data) => {
      setRealTimeData(prev => ({
        ...prev,
        finops: { ...prev.finops, ...data }
      }));
    });

    newSocket.on('devops-update', (data) => {
      setRealTimeData(prev => ({
        ...prev,
        devops: { ...prev.devops, ...data }
      }));
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const handleNeuralEvent = (event) => {
    // Process events from Neural Data Plane
    switch (event.type) {
      case 'SECURITY_THREAT':
        handleSecurityThreat(event);
        break;
      case 'COST_ANOMALY':
        handleCostAnomaly(event);
        break;
      case 'DEPLOYMENT_EVENT':
        handleDeploymentEvent(event);
        break;
      default:
        setRealTimeData(prev => ({
          ...prev,
          events: [event, ...prev.events].slice(0, 100)
        }));
    }
  };

  const handleSecurityThreat = (event) => {
    setRealTimeData(prev => ({
      ...prev,
      security: {
        ...prev.security,
        threats: [event, ...(prev.security.threats || [])].slice(0, 50),
        threatCount: (prev.security.threatCount || 0) + 1
      }
    }));

    addNotification({
      type: 'security',
      severity: 'error',
      title: 'Security Threat Detected',
      message: event.description,
      timestamp: new Date(),
      actions: [
        { label: 'Investigate', action: 'investigate-threat' },
        { label: 'Mitigate', action: 'mitigate-threat' }
      ]
    });
  };

  const handleCostAnomaly = (event) => {
    setRealTimeData(prev => ({
      ...prev,
      finops: {
        ...prev.finops,
        anomalies: [event, ...(prev.finops.anomalies || [])].slice(0, 50),
        totalSpend: (prev.finops.totalSpend || 0) + (event.costImpact || 0)
      }
    }));

    addNotification({
      type: 'finops',
      severity: 'warning',
      title: 'Cost Anomaly Detected',
      message: `Unusual spending pattern: ${event.description}`,
      timestamp: new Date(),
      actions: [
        { label: 'Analyze', action: 'analyze-costs' },
        { label: 'Optimize', action: 'optimize-costs' }
      ]
    });
  };

  const handleDeploymentEvent = (event) => {
    setRealTimeData(prev => ({
      ...prev,
      devops: {
        ...prev.devops,
        deployments: [event, ...(prev.devops.deployments || [])].slice(0, 50),
        deploymentCount: (prev.devops.deploymentCount || 0) + 1
      }
    }));

    addNotification({
      type: 'devops',
      severity: 'info',
      title: 'Deployment Event',
      message: event.description,
      timestamp: new Date(),
      actions: [
        { label: 'View Details', action: 'view-deployment' },
        { label: 'Rollback', action: 'rollback-deployment' }
      ]
    });
  };

  const addNotification = (notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 100));
  };

  const handleAIVoiceCommand = async (command) => {
    if (socket) {
      try {
        const response = await fetch(`${process.env.REACT_APP_NEURAL_HUB_URL}/api/ai/command`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            command,
            context: {
              currentUser: 'admin',
              timestamp: new Date().toISOString(),
              dashboard: 'master'
            }
          })
        });

        const result = await response.json();
        
        // Show AI response
        addNotification({
          type: 'ai',
          severity: 'success',
          title: 'AI Command Executed',
          message: `Executed: ${command}`,
          timestamp: new Date(),
          details: result
        });

      } catch (error) {
        addNotification({
          type: 'ai',
          severity: 'error',
          title: 'AI Command Failed',
          message: error.message,
          timestamp: new Date()
        });
      }
    }
  };

  return (
    <ThemeProvider theme={itechsmartTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <UnifiedSidebar notifications={notifications} />
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <UnifiedNavbar 
              notifications={notifications}
              onAIClick={() => setAiAssistantOpen(true)}
            />
            <Box component="main" sx={{ flex: 1, p: 3 }}>
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <MasterDashboard 
                      realTimeData={realTimeData}
                      onEventClick={handleNeuralEvent}
                    />
                  } 
                />
              </Routes>
            </Box>
          </Box>
        </Box>
        
        <NotificationCenter 
          notifications={notifications}
          onNotificationClick={(action) => console.log('Notification action:', action)}
        />
        
        <AIAssistant 
          open={aiAssistantOpen}
          onClose={() => setAiAssistantOpen(false)}
          onCommand={handleAIVoiceCommand}
        />
      </Router>
    </ThemeProvider>
  );
}

export default App;