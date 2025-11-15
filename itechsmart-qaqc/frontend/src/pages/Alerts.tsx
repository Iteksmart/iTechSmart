import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as ResolveIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

export default function Alerts() {
  const [alerts] = useState([
    {
      id: 1,
      severity: 'high',
      title: 'API Response Time Exceeded',
      message: 'DataFlow API endpoint /api/v1/pipelines is responding in 850ms (threshold: 500ms)',
      product: 'iTechSmart DataFlow',
      timestamp: '5 minutes ago',
      isResolved: false,
    },
    {
      id: 2,
      severity: 'medium',
      title: 'Documentation Outdated',
      message: 'README.md has not been updated in 35 days',
      product: 'iTechSmart Connect',
      timestamp: '1 hour ago',
      isResolved: false,
    },
    {
      id: 3,
      severity: 'low',
      title: 'Code Coverage Below Target',
      message: 'Test coverage is 78% (target: 80%)',
      product: 'iTechSmart Vault',
      timestamp: '2 hours ago',
      isResolved: false,
    },
    {
      id: 4,
      severity: 'critical',
      title: 'Database Connection Pool Exhausted',
      message: 'All 20 database connections are in use',
      product: 'iTechSmart Pulse',
      timestamp: '10 minutes ago',
      isResolved: false,
    },
    {
      id: 5,
      severity: 'medium',
      title: 'Dependency Update Available',
      message: 'Security update available for fastapi (0.104.1 -> 0.105.0)',
      product: 'iTechSmart Shield',
      timestamp: '3 hours ago',
      isResolved: false,
    },
  ]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <ErrorIcon color="error" />;
      case 'medium':
        return <WarningIcon color="warning" />;
      case 'low':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            Alerts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time alerts from QA/QC monitoring system
          </Typography>
        </div>
        <Button variant="outlined">
          Mark All as Read
        </Button>
      </Box>

      <Paper>
        <List>
          {alerts.map((alert, index) => (
            <Box key={alert.id}>
              <ListItem
                secondaryAction={
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton edge="end" aria-label="resolve" color="success">
                      <ResolveIcon />
                    </IconButton>
                    <IconButton edge="end" aria-label="dismiss">
                      <CloseIcon />
                    </IconButton>
                  </Box>
                }
              >
                <ListItemIcon>
                  {getSeverityIcon(alert.severity)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body1" fontWeight="medium">
                        {alert.title}
                      </Typography>
                      <Chip
                        label={alert.severity}
                        color={getSeverityColor(alert.severity) as any}
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="text.primary" sx={{ mb: 0.5 }}>
                        {alert.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {alert.product} • {alert.timestamp}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
              {index < alerts.length - 1 && <Divider />}
            </Box>
          ))}
        </List>
      </Paper>
    </Box>
  );
}