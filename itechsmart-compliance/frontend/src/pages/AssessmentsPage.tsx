/**
 * iTechSmart Compliance - Assessments Page
 * Manage compliance assessments and audits
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress
} from '@mui/material';
import {
  Add,
  Visibility,
  Assessment as AssessmentIcon,
  CheckCircle
} from '@mui/icons-material';

interface Assessment {
  assessment_id: string;
  framework: string;
  assessment_type: string;
  assessor: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  overall_score: number;
  controls_assessed: number;
  controls_passed: number;
  controls_failed: number;
  findings_count: number;
}

const AssessmentsPage: React.FC = () => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newAssessment, setNewAssessment] = useState({
    framework: 'soc2',
    assessment_type: 'internal',
    scope: ''
  });

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      const response = await fetch('http://localhost:8019/compliance-center/assessments');
      const data = await response.json();
      setAssessments(data.assessments);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assessments:', error);
      setLoading(false);
    }
  };

  const handleCreateAssessment = async () => {
    try {
      await fetch('http://localhost:8019/compliance-center/assessments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAssessment)
      });
      setCreateOpen(false);
      fetchAssessments();
    } catch (error) {
      console.error('Error creating assessment:', error);
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'completed' ? 'success' : 'warning';
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Compliance Assessments
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and track compliance assessments and audits
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateOpen(true)}
        >
          New Assessment
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4">{assessments.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Assessments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main">
                {assessments.filter((a) => a.status === 'completed').length}
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
              <Typography variant="h4" color="warning.main">
                {assessments.filter((a) => a.status === 'in_progress').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                In Progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4">
                {assessments.length > 0
                  ? (
                      assessments.reduce((sum, a) => sum + a.overall_score, 0) /
                      assessments.length
                    ).toFixed(1)
                  : 0}
                %
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assessments Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Assessment ID</TableCell>
                  <TableCell>Framework</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Assessor</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Score</TableCell>
                  <TableCell align="right">Controls</TableCell>
                  <TableCell align="right">Findings</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assessments.map((assessment) => (
                  <TableRow key={assessment.assessment_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {assessment.assessment_id.substring(0, 12)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={assessment.framework.toUpperCase()}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{assessment.assessment_type}</TableCell>
                    <TableCell>{assessment.assessor}</TableCell>
                    <TableCell>
                      <Chip
                        label={assessment.status}
                        color={getStatusColor(assessment.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        {assessment.overall_score.toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {assessment.controls_passed}/{assessment.controls_assessed}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip label={assessment.findings_count} size="small" color="error" />
                    </TableCell>
                    <TableCell>
                      {new Date(assessment.started_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small">
                        <Visibility fontSize="small" />
                      </IconButton>
                      {assessment.status === 'in_progress' && (
                        <IconButton size="small" color="success">
                          <CheckCircle fontSize="small" />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create Assessment Dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Assessment</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Framework</InputLabel>
                <Select
                  value={newAssessment.framework}
                  label="Framework"
                  onChange={(e) =>
                    setNewAssessment({ ...newAssessment, framework: e.target.value })
                  }
                >
                  <MenuItem value="soc2">SOC 2</MenuItem>
                  <MenuItem value="iso27001">ISO 27001</MenuItem>
                  <MenuItem value="hipaa">HIPAA</MenuItem>
                  <MenuItem value="gdpr">GDPR</MenuItem>
                  <MenuItem value="pci_dss">PCI-DSS</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Assessment Type</InputLabel>
                <Select
                  value={newAssessment.assessment_type}
                  label="Assessment Type"
                  onChange={(e) =>
                    setNewAssessment({ ...newAssessment, assessment_type: e.target.value })
                  }
                >
                  <MenuItem value="internal">Internal</MenuItem>
                  <MenuItem value="external">External</MenuItem>
                  <MenuItem value="self">Self-Assessment</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scope"
                multiline
                rows={3}
                value={newAssessment.scope}
                onChange={(e) =>
                  setNewAssessment({ ...newAssessment, scope: e.target.value })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateAssessment}>
            Create Assessment
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AssessmentsPage;