import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Edit as EditIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:8100/api';

interface PortAssignment {
  service_id: string;
  port: number;
}

function PortManagement() {
  const [assignments, setAssignments] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedService, setSelectedService] = useState<string>('');
  const [newPort, setNewPort] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const response = await axios.get(`${API_URL}/ports/assignments`);
      setAssignments(response.data.assignments);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assignments:', error);
      setError('Failed to fetch port assignments');
      setLoading(false);
    }
  };

  const handleEditClick = (serviceId: string, currentPort: number) => {
    setSelectedService(serviceId);
    setNewPort(currentPort.toString());
    setEditDialog(true);
    setError('');
  };

  const handleSavePort = async () => {
    try {
      const portNumber = parseInt(newPort);
      if (isNaN(portNumber) || portNumber < 1024 || portNumber > 65535) {
        setError('Port must be between 1024 and 65535');
        return;
      }

      await axios.post(`${API_URL}/ports/reassign`, {
        service_id: selectedService,
        new_port: portNumber
      });

      setSuccess(`Successfully updated ${selectedService} to port ${portNumber}`);
      setEditDialog(false);
      fetchAssignments();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to update port');
    }
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
          Port Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={fetchAssignments}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Card>
        <CardContent>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Service ID</strong></TableCell>
                  <TableCell><strong>Current Port</strong></TableCell>
                  <TableCell><strong>Category</strong></TableCell>
                  <TableCell align="right"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(assignments).map(([serviceId, port]) => {
                  const category = serviceId.includes('enterprise') || serviceId.includes('ninja') || serviceId.includes('analytics')
                    ? 'Foundation'
                    : serviceId.includes('dataflow') || serviceId.includes('pulse') || serviceId.includes('shield')
                    ? 'Strategic'
                    : 'Business';
                  
                  return (
                    <TableRow key={serviceId} hover>
                      <TableCell>{serviceId}</TableCell>
                      <TableCell>
                        <Chip label={port} color="primary" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={category}
                          color={category === 'Foundation' ? 'success' : category === 'Strategic' ? 'warning' : 'info'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => handleEditClick(serviceId, port)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="default">
                          <HistoryIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Edit Port Dialog */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Port Assignment</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Service: <strong>{selectedService}</strong>
            </Typography>
            <TextField
              fullWidth
              label="New Port"
              type="number"
              value={newPort}
              onChange={(e) => setNewPort(e.target.value)}
              sx={{ mt: 2 }}
              helperText="Port must be between 1024 and 65535"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button onClick={handleSavePort} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default PortManagement;