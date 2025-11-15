import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  CircularProgress,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Cancel as CancelIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

interface ServiceRequest {
  id: number;
  request_number: string;
  service_item: {
    name: string;
    icon: string;
  };
  status: string;
  priority: number;
  submitted_at: string;
  due_date: string;
  completed_at?: string;
  form_data: any;
}

interface Activity {
  id: number;
  activity_type: string;
  description: string;
  user_name: string;
  created_at: string;
}

const statusColors: { [key: string]: any } = {
  submitted: 'info',
  pending_approval: 'warning',
  approved: 'success',
  in_progress: 'primary',
  completed: 'success',
  rejected: 'error',
  cancelled: 'default',
  failed: 'error'
};

const statusIcons: { [key: string]: React.ReactNode } = {
  submitted: <HourglassEmptyIcon />,
  pending_approval: <HourglassEmptyIcon />,
  approved: <CheckCircleIcon />,
  in_progress: <HourglassEmptyIcon />,
  completed: <CheckCircleIcon />,
  rejected: <CancelIcon />,
  cancelled: <CancelIcon />,
  failed: <ErrorIcon />
};

const MyRequests: React.FC = () => {
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [filteredRequests, setFilteredRequests] = useState<ServiceRequest[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<ServiceRequest | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    loadRequests();
  }, []);

  useEffect(() => {
    filterRequests();
  }, [tabValue, requests]);

  const loadRequests = async () => {
    try {
      const response = await fetch('/api/service-catalog/requests');
      const data = await response.json();
      setRequests(data);
      setFilteredRequests(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading requests:', error);
      setLoading(false);
    }
  };

  const filterRequests = () => {
    let filtered = requests;

    switch (tabValue) {
      case 0: // All
        break;
      case 1: // Pending
        filtered = requests.filter(r => 
          ['submitted', 'pending_approval', 'in_progress'].includes(r.status)
        );
        break;
      case 2: // Completed
        filtered = requests.filter(r => r.status === 'completed');
        break;
      case 3: // Rejected/Failed
        filtered = requests.filter(r => 
          ['rejected', 'cancelled', 'failed'].includes(r.status)
        );
        break;
    }

    setFilteredRequests(filtered);
  };

  const handleViewDetails = async (request: ServiceRequest) => {
    setSelectedRequest(request);
    
    // Load activities
    try {
      const response = await fetch(`/api/service-catalog/requests/${request.id}/activities`);
      const data = await response.json();
      setActivities(data.activities);
    } catch (error) {
      console.error('Error loading activities:', error);
    }
    
    setDialogOpen(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusLabel = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" gutterBottom fontWeight="bold" color="primary">
          📋 My Requests
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Track your service requests and their status
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="primary" fontWeight="bold">
                {requests.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Requests
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {requests.filter(r => ['submitted', 'pending_approval', 'in_progress'].includes(r.status)).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main" fontWeight="bold">
                {requests.filter(r => r.status === 'completed').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="info.main" fontWeight="bold">
                {requests.filter(r => r.status === 'in_progress').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                In Progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filter Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label={`All (${requests.length})`} />
          <Tab label={`Pending (${requests.filter(r => ['submitted', 'pending_approval', 'in_progress'].includes(r.status)).length})`} />
          <Tab label={`Completed (${requests.filter(r => r.status === 'completed').length})`} />
          <Tab label={`Rejected/Failed (${requests.filter(r => ['rejected', 'cancelled', 'failed'].includes(r.status)).length})`} />
        </Tabs>
      </Paper>

      {/* Requests Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell><strong>Request #</strong></TableCell>
              <TableCell><strong>Service</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Priority</strong></TableCell>
              <TableCell><strong>Submitted</strong></TableCell>
              <TableCell><strong>Due Date</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRequests.map((request) => (
              <TableRow key={request.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {request.request_number}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <span style={{ fontSize: '1.5rem', marginRight: 8 }}>
                      {request.service_item.icon}
                    </span>
                    {request.service_item.name}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getStatusLabel(request.status)}
                    color={statusColors[request.status]}
                    size="small"
                    icon={statusIcons[request.status]}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={`P${request.priority}`}
                    size="small"
                    color={request.priority <= 2 ? 'error' : request.priority === 3 ? 'warning' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {formatDate(request.submitted_at)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {formatDate(request.due_date)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<VisibilityIcon />}
                    onClick={() => handleViewDetails(request)}
                  >
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredRequests.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="text.secondary">
            No requests found
          </Typography>
        </Box>
      )}

      {/* Request Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedRequest && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center">
                <span style={{ fontSize: '2rem', marginRight: 12 }}>
                  {selectedRequest.service_item.icon}
                </span>
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    {selectedRequest.request_number}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedRequest.service_item.name}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              {/* Status */}
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>
                  Status
                </Typography>
                <Chip
                  label={getStatusLabel(selectedRequest.status)}
                  color={statusColors[selectedRequest.status]}
                  icon={statusIcons[selectedRequest.status]}
                />
              </Box>

              {/* Request Details */}
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                  Request Details
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                  {Object.entries(selectedRequest.form_data).map(([key, value]) => (
                    <Box key={key} mb={1}>
                      <Typography variant="caption" color="text.secondary">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                      </Typography>
                      <Typography variant="body2">
                        {String(value)}
                      </Typography>
                    </Box>
                  ))}
                </Paper>
              </Box>

              {/* Activity Timeline */}
              <Box>
                <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                  Activity Timeline
                </Typography>
                <Timeline>
                  {activities.map((activity, index) => (
                    <TimelineItem key={activity.id}>
                      <TimelineSeparator>
                        <TimelineDot color="primary" />
                        {index < activities.length - 1 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Typography variant="body2" fontWeight="bold">
                          {activity.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {activity.user_name} • {formatDate(activity.created_at)}
                        </Typography>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default MyRequests;