import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Build as BuildIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:8100/api';

interface Conflict {
  type: string;
  port: number;
  services?: string[];
  service?: string;
  severity: string;
}

function ConflictResolution() {
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState(false);
  const [success, setSuccess] = useState<string>('');

  useEffect(() => {
    fetchConflicts();
  }, []);

  const fetchConflicts = async () => {
    try {
      const response = await axios.get(`${API_URL}/ports/conflicts`);
      setConflicts(response.data.conflicts);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching conflicts:', error);
      setLoading(false);
    }
  };

  const handleResolveConflicts = async () => {
    setResolving(true);
    try {
      const response = await axios.post(`${API_URL}/ports/resolve-conflicts`);
      setSuccess(`Resolved ${response.data.count} conflict(s)`);
      fetchConflicts();
    } catch (error) {
      console.error('Error resolving conflicts:', error);
    }
    setResolving(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Conflict Resolution
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchConflicts}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<BuildIcon />}
            onClick={handleResolveConflicts}
            disabled={conflicts.length === 0 || resolving}
          >
            {resolving ? 'Resolving...' : 'Auto-Resolve'}
          </Button>
        </Box>
      </Box>

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {conflicts.length === 0 ? (
        <Card>
          <CardContent>
            <Box display="flex" flexDirection="column" alignItems="center" py={4}>
              <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                No Conflicts Detected
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All port assignments are valid and conflict-free
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent>
            <Alert severity="warning" sx={{ mb: 2 }}>
              {conflicts.length} port conflict(s) detected. Click "Auto-Resolve" to fix automatically.
            </Alert>
            <List>
              {conflicts.map((conflict, index) => (
                <ListItem
                  key={index}
                  sx={{
                    border: '1px solid',
                    borderColor: conflict.severity === 'critical' ? 'error.main' : 'warning.main',
                    borderRadius: 1,
                    mb: 1
                  }}
                >
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <WarningIcon color={conflict.severity === 'critical' ? 'error' : 'warning'} />
                        <Typography variant="subtitle1">
                          {conflict.type === 'duplicate_assignment'
                            ? `Duplicate Port Assignment: ${conflict.port}`
                            : `System Conflict: Port ${conflict.port}`}
                        </Typography>
                        <Chip
                          label={conflict.severity}
                          color={conflict.severity === 'critical' ? 'error' : 'warning'}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      conflict.services
                        ? `Services: ${conflict.services.join(', ')}`
                        : `Service: ${conflict.service}`
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default ConflictResolution;