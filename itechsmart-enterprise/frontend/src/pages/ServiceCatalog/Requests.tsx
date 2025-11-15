import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Stepper,
  Step,
  StepLabel,
  LinearProgress,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  Visibility,
  CheckCircle,
  Cancel,
  Edit,
  Comment,
  Timeline,
  Assignment,
  Schedule,
} from '@mui/icons-material';

interface ServiceRequest {
  id: string;
  service_id: string;
  service_name: string;
  requester_id: string;
  requester_name: string;
  status: string;
  priority: string;
  business_justification: string;
  cost_center: string;
  form_data: Record<string, any>;
  created_at: string;
  updated_at: string;
  approval_chain?: Array<{
    approver_name: string;
    status: string;
    comments: string;
    approved_at: string;
  }>;
  fulfillment_tasks?: Array<{
    title: string;
    status: string;
    assigned_to: string;
  }>;
}

const ServiceCatalogRequests: React.FC = () => {
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [filteredRequests, setFilteredRequests] = useState<ServiceRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState<ServiceRequest | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [commentDialogOpen, setCommentDialogOpen] = useState(false);
  const [comment, setComment] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const statusOptions = [
    'all',
    'draft',
    'submitted',
    'pending_approval',
    'approved',
    'in_progress',
    'fulfilled',
    'rejected',
    'cancelled',
  ];

  useEffect(() => {
    fetchRequests();
  }, []);

  useEffect(() => {
    filterRequests();
  }, [requests, statusFilter]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/service-catalog/requests');
      const data = await response.json();
      setRequests(data.requests || []);
    } catch (error) {
      console.error('Error fetching requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterRequests = () => {
    if (statusFilter === 'all') {
      setFilteredRequests(requests);
    } else {
      setFilteredRequests(requests.filter(r => r.status === statusFilter));
    }
  };

  const handleViewDetails = async (requestId: string) => {
    try {
      const response = await fetch(`/api/service-catalog/requests/${requestId}`);
      const data = await response.json();
      setSelectedRequest(data);
      setDetailsDialogOpen(true);
    } catch (error) {
      console.error('Error fetching request details:', error);
    }
  };

  const handleCancelRequest = async (requestId: string) => {
    try {
      await fetch(`/api/service-catalog/requests/${requestId}/cancel`, {
        method: 'POST',
      });
      fetchRequests();
      setDetailsDialogOpen(false);
    } catch (error) {
      console.error('Error cancelling request:', error);
    }
  };

  const handleAddComment = async () => {
    if (!selectedRequest || !comment) return;

    try {
      await fetch(`/api/service-catalog/requests/${selectedRequest.id}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment }),
      });
      setComment('');
      setCommentDialogOpen(false);
      handleViewDetails(selectedRequest.id);
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      draft: 'default',
      submitted: 'info',
      pending_approval: 'warning',
      approved: 'primary',
      in_progress: 'secondary',
      fulfilled: 'success',
      rejected: 'error',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      low: 'info',
      medium: 'primary',
      high: 'warning',
      critical: 'error',
    };
    return colors[priority] || 'default';
  };

  const getWorkflowSteps = () => {
    return [
      'Submitted',
      'Pending Approval',
      'Approved',
      'In Progress',
      'Fulfilled',
    ];
  };

  const getActiveStep = (status: string) => {
    const stepMap: Record<string, number> = {
      draft: 0,
      submitted: 0,
      pending_approval: 1,
      approved: 2,
      in_progress: 3,
      fulfilled: 4,
      rejected: 1,
      cancelled: 0,
    };
    return stepMap[status] || 0;
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        My Service Requests
      </Typography>

      {/* Status Filter Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={statusFilter}
          onChange={(e, newValue) => setStatusFilter(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {statusOptions.map((status) => (
            <Tab
              key={status}
              label={status.replace(/_/g, ' ').toUpperCase()}
              value={status}
            />
          ))}
        </Tabs>
      </Box>

      {/* Requests Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Request ID</TableCell>
                  <TableCell>Service</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Cost Center</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredRequests.length > 0 ? (
                  filteredRequests.map((request) => (
                    <TableRow key={request.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {request.id.substring(0, 8)}
                        </Typography>
                      </TableCell>
                      <TableCell>{request.service_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={request.priority.toUpperCase()}
                          color={getPriorityColor(request.priority)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={request.status.replace(/_/g, ' ').toUpperCase()}
                          color={getStatusColor(request.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(request.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{request.cost_center || 'N/A'}</TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(request.id)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No requests found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Request Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Request Details: {selectedRequest?.service_name}
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box sx={{ mt: 2 }}>
              {/* Status and Priority */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={selectedRequest.status.replace(/_/g, ' ').toUpperCase()}
                    color={getStatusColor(selectedRequest.status)}
                    sx={{ mt: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Priority
                  </Typography>
                  <Chip
                    label={selectedRequest.priority.toUpperCase()}
                    color={getPriorityColor(selectedRequest.priority)}
                    sx={{ mt: 1 }}
                  />
                </Grid>
              </Grid>

              {/* Workflow Progress */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Workflow Progress
                </Typography>
                <Stepper activeStep={getActiveStep(selectedRequest.status)} alternativeLabel>
                  {getWorkflowSteps().map((label) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>

              {/* Request Information */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Request Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Business Justification
                    </Typography>
                    <Typography variant="body1">
                      {selectedRequest.business_justification}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Cost Center
                    </Typography>
                    <Typography variant="body1">
                      {selectedRequest.cost_center || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Requester
                    </Typography>
                    <Typography variant="body1">
                      {selectedRequest.requester_name}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>

              {/* Approval Chain */}
              {selectedRequest.approval_chain && selectedRequest.approval_chain.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Approval Chain
                  </Typography>
                  {selectedRequest.approval_chain.map((approval, index) => (
                    <Alert
                      key={index}
                      severity={
                        approval.status === 'approved'
                          ? 'success'
                          : approval.status === 'rejected'
                          ? 'error'
                          : 'info'
                      }
                      sx={{ mb: 1 }}
                    >
                      <Typography variant="body2">
                        <strong>{approval.approver_name}</strong> -{' '}
                        {approval.status.toUpperCase()}
                      </Typography>
                      {approval.comments && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {approval.comments}
                        </Typography>
                      )}
                    </Alert>
                  ))}
                </Box>
              )}

              {/* Fulfillment Tasks */}
              {selectedRequest.fulfillment_tasks && selectedRequest.fulfillment_tasks.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Fulfillment Tasks
                  </Typography>
                  {selectedRequest.fulfillment_tasks.map((task, index) => (
                    <Box
                      key={index}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        mb: 1,
                        p: 1,
                        border: '1px solid #e0e0e0',
                        borderRadius: 1,
                      }}
                    >
                      <Assignment sx={{ mr: 1 }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2">{task.title}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Assigned to: {task.assigned_to}
                        </Typography>
                      </Box>
                      <Chip
                        label={task.status.toUpperCase()}
                        size="small"
                        color={task.status === 'completed' ? 'success' : 'default'}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            startIcon={<Comment />}
            onClick={() => setCommentDialogOpen(true)}
          >
            Add Comment
          </Button>
          {selectedRequest?.status !== 'cancelled' &&
            selectedRequest?.status !== 'fulfilled' && (
              <Button
                color="error"
                startIcon={<Cancel />}
                onClick={() => handleCancelRequest(selectedRequest.id)}
              >
                Cancel Request
              </Button>
            )}
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Comment Dialog */}
      <Dialog
        open={commentDialogOpen}
        onClose={() => setCommentDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Comment</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCommentDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddComment} disabled={!comment}>
            Add Comment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServiceCatalogRequests;