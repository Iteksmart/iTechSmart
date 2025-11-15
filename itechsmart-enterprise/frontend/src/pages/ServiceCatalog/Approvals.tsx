import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface PendingApproval {
  id: number;
  request: {
    id: number;
    request_number: string;
    service_item: {
      name: string;
      icon: string;
      description: string;
    };
    requester_name: string;
    requester_email: string;
    form_data: any;
    submitted_at: string;
    due_date: string;
  };
  step_name: string;
  step_number: number;
  requested_at: string;
}

const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [selectedApproval, setSelectedApproval] = useState<PendingApproval | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [decisionNotes, setDecisionNotes] = useState('');
  const [processing, setProcessing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadApprovals();
    
    // Refresh every 30 seconds
    const interval = setInterval(loadApprovals, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadApprovals = async () => {
    try {
      const response = await fetch('/api/service-catalog/approvals/pending');
      const data = await response.json();
      setApprovals(data.approvals);
      setLoading(false);
    } catch (error) {
      console.error('Error loading approvals:', error);
      setLoading(false);
    }
  };

  const handleViewDetails = (approval: PendingApproval) => {
    setSelectedApproval(approval);
    setDecisionNotes('');
    setDialogOpen(true);
  };

  const handleApprove = async () => {
    if (!selectedApproval) return;
    
    setProcessing(true);
    
    try {
      const response = await fetch(
        `/api/service-catalog/requests/${selectedApproval.request.id}/approve`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ decision_notes: decisionNotes })
        }
      );
      
      if (response.ok) {
        setDialogOpen(false);
        loadApprovals();
        alert('Request approved successfully!');
      } else {
        const data = await response.json();
        alert('Error approving request: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error approving request:', error);
      alert('Error approving request');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!selectedApproval) return;
    
    if (!decisionNotes.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }
    
    setProcessing(true);
    
    try {
      const response = await fetch(
        `/api/service-catalog/requests/${selectedApproval.request.id}/reject`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ decision_notes: decisionNotes })
        }
      );
      
      if (response.ok) {
        setDialogOpen(false);
        loadApprovals();
        alert('Request rejected');
      } else {
        const data = await response.json();
        alert('Error rejecting request: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error rejecting request:', error);
      alert('Error rejecting request');
    } finally {
      setProcessing(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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
          ✓ Pending Approvals
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Review and approve service requests
        </Typography>
      </Box>

      {/* Summary */}
      <Alert severity="info" sx={{ mb: 4 }}>
        You have <strong>{approvals.length}</strong> pending approval{approvals.length !== 1 ? 's' : ''}
      </Alert>

      {/* Approval Cards */}
      <Grid container spacing={3}>
        {approvals.map((approval) => (
          <Grid item xs={12} md={6} key={approval.id}>
            <Card
              sx={{
                borderLeft: '4px solid #ff9800',
                '&:hover': {
                  boxShadow: 4
                }
              }}
            >
              <CardContent>
                {/* Header */}
                <Box display="flex" alignItems="center" mb={2}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      backgroundColor: '#ff980020',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '1.5rem',
                      mr: 2
                    }}
                  >
                    {approval.request.service_item.icon}
                  </Box>
                  <Box flexGrow={1}>
                    <Typography variant="h6" fontWeight="bold">
                      {approval.request.request_number}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {approval.request.service_item.name}
                    </Typography>
                  </Box>
                  <Chip
                    icon={<HourglassEmptyIcon />}
                    label={approval.step_name}
                    color="warning"
                    size="small"
                  />
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Requester Info */}
                <Box mb={2}>
                  <Typography variant="caption" color="text.secondary">
                    Requested by:
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {approval.request.requester_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {approval.request.requester_email}
                  </Typography>
                </Box>

                {/* Timing */}
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Submitted:
                    </Typography>
                    <Typography variant="body2">
                      {formatDate(approval.request.submitted_at)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Due:
                    </Typography>
                    <Typography variant="body2">
                      {formatDate(approval.request.due_date)}
                    </Typography>
                  </Box>
                </Box>

                {/* Quick Preview */}
                <Paper variant="outlined" sx={{ p: 1.5, backgroundColor: '#f5f5f5' }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Request Details:
                  </Typography>
                  {Object.entries(approval.request.form_data).slice(0, 3).map(([key, value]) => (
                    <Typography key={key} variant="body2" fontSize="0.85rem">
                      <strong>{key.replace(/_/g, ' ')}:</strong> {String(value)}
                    </Typography>
                  ))}
                  {Object.keys(approval.request.form_data).length > 3 && (
                    <Typography variant="caption" color="text.secondary">
                      + {Object.keys(approval.request.form_data).length - 3} more fields
                    </Typography>
                  )}
                </Paper>
              </CardContent>

              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<InfoIcon />}
                  onClick={() => handleViewDetails(approval)}
                >
                  View Full Details
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {approvals.length === 0 && (
        <Box textAlign="center" py={8}>
          <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No pending approvals
          </Typography>
          <Typography variant="body2" color="text.secondary">
            You're all caught up!
          </Typography>
        </Box>
      )}

      {/* Approval Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => !processing && setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedApproval && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center">
                <span style={{ fontSize: '2rem', marginRight: 12 }}>
                  {selectedApproval.request.service_item.icon}
                </span>
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    {selectedApproval.request.request_number}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedApproval.request.service_item.name}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              {/* Service Description */}
              <Alert severity="info" sx={{ mb: 3 }}>
                {selectedApproval.request.service_item.description}
              </Alert>

              {/* Requester Info */}
              <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                  Requester Information
                </Typography>
                <Typography variant="body2">
                  <strong>Name:</strong> {selectedApproval.request.requester_name}
                </Typography>
                <Typography variant="body2">
                  <strong>Email:</strong> {selectedApproval.request.requester_email}
                </Typography>
                <Typography variant="body2">
                  <strong>Submitted:</strong> {formatDate(selectedApproval.request.submitted_at)}
                </Typography>
                <Typography variant="body2">
                  <strong>Due Date:</strong> {formatDate(selectedApproval.request.due_date)}
                </Typography>
              </Paper>

              {/* Request Details */}
              <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom fontWeight="bold">
                  Request Details
                </Typography>
                {Object.entries(selectedApproval.request.form_data).map(([key, value]) => (
                  <Box key={key} mb={1}>
                    <Typography variant="body2">
                      <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>{' '}
                      {String(value)}
                    </Typography>
                  </Box>
                ))}
              </Paper>

              {/* Decision Notes */}
              <TextField
                fullWidth
                label="Decision Notes (Optional for Approval, Required for Rejection)"
                multiline
                rows={4}
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                placeholder="Add any notes about your decision..."
              />
            </DialogContent>
            <DialogActions sx={{ p: 3 }}>
              <Button
                onClick={() => setDialogOpen(false)}
                disabled={processing}
              >
                Cancel
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={processing ? <CircularProgress size={20} /> : <CancelIcon />}
                onClick={handleReject}
                disabled={processing}
              >
                Reject
              </Button>
              <Button
                variant="contained"
                color="success"
                startIcon={processing ? <CircularProgress size={20} /> : <CheckCircleIcon />}
                onClick={handleApprove}
                disabled={processing}
              >
                Approve
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default Approvals;