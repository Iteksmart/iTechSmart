/**
 * iTechSmart Compliance - Compliance Dashboard
 * Multi-framework compliance posture overview
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
  Info,
  TrendingUp,
  Assessment,
  Policy,
  Security
} from '@mui/icons-material';

interface CompliancePosture {
  framework: string;
  overall_status: string;
  compliance_score: number;
  total_controls: number;
  implemented: number;
  partially_implemented: number;
  not_implemented: number;
  planned: number;
  last_updated: string;
}

const ComplianceDashboard: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState<string>('soc2');
  const [posture, setPosture] = useState<CompliancePosture | null>(null);
  const [multiFramework, setMultiFramework] = useState<CompliancePosture[]>([]);
  const [loading, setLoading] = useState(true);

  const frameworks = [
    { value: 'soc2', label: 'SOC 2 Type II' },
    { value: 'iso27001', label: 'ISO 27001' },
    { value: 'hipaa', label: 'HIPAA' },
    { value: 'gdpr', label: 'GDPR' },
    { value: 'pci_dss', label: 'PCI-DSS' }
  ];

  useEffect(() => {
    fetchComplianceData();
    fetchMultiFrameworkData();
  }, [selectedFramework]);

  const fetchComplianceData = async () => {
    try {
      const response = await fetch(
        `http://localhost:8019/compliance-center/dashboard/posture?framework=${selectedFramework}`
      );
      const data = await response.json();
      setPosture(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching compliance data:', error);
      setLoading(false);
    }
  };

  const fetchMultiFrameworkData = async () => {
    try {
      const response = await fetch(
        'http://localhost:8019/compliance-center/dashboard/multi-framework'
      );
      const data = await response.json();
      setMultiFramework(data.frameworks);
    } catch (error) {
      console.error('Error fetching multi-framework data:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'success';
      case 'partially_compliant':
        return 'warning';
      case 'non_compliant':
        return 'error';
      case 'under_review':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string): React.ReactElement => {
    switch (status) {
      case 'compliant':
        return <CheckCircle />;
      case 'partially_compliant':
        return <Warning />;
      case 'non_compliant':
        return <Error />;
      case 'under_review':
        return <Info />;
      default:
        return <Info />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 95) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
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
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Compliance Center Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Multi-framework compliance tracking and policy alignment
        </Typography>
      </Box>

      {/* Framework Selector */}
      <Box sx={{ mb: 4 }}>
        <FormControl sx={{ minWidth: 300 }}>
          <InputLabel>Select Framework</InputLabel>
          <Select
            value={selectedFramework}
            label="Select Framework"
            onChange={(e) => setSelectedFramework(e.target.value)}
          >
            {frameworks.map((fw) => (
              <MenuItem key={fw.value} value={fw.value}>
                {fw.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Main Metrics */}
      {posture && (
        <>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Overall Status Card */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getStatusIcon(posture.overall_status)}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      Overall Status
                    </Typography>
                  </Box>
                  <Chip
                    label={posture.overall_status.replace('_', ' ').toUpperCase()}
                    color={getStatusColor(posture.overall_status) as any}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {posture.framework.toUpperCase()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Compliance Score Card */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TrendingUp />
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      Compliance Score
                    </Typography>
                  </Box>
                  <Typography variant="h3" color={getScoreColor(posture.compliance_score)}>
                    {posture.compliance_score.toFixed(1)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={posture.compliance_score}
                    color={getScoreColor(posture.compliance_score) as any}
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Total Controls Card */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Assessment />
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      Total Controls
                    </Typography>
                  </Box>
                  <Typography variant="h3">{posture.total_controls}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {posture.implemented} Implemented
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Implementation Progress Card */}
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Security />
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      Implementation
                    </Typography>
                  </Box>
                  <Typography variant="h3" color="success.main">
                    {posture.implemented}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    of {posture.total_controls} controls
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Control Status Breakdown */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Control Status Breakdown
                  </Typography>
                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                        <Typography variant="h4">{posture.implemented}</Typography>
                        <Typography variant="body2">Implemented</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
                        <Typography variant="h4">{posture.partially_implemented}</Typography>
                        <Typography variant="body2">Partially Implemented</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
                        <Typography variant="h4">{posture.not_implemented}</Typography>
                        <Typography variant="body2">Not Implemented</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                        <Typography variant="h4">{posture.planned}</Typography>
                        <Typography variant="body2">Planned</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}

      {/* Multi-Framework Comparison */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Multi-Framework Compliance Overview
          </Typography>
          <TableContainer component={Paper} sx={{ mt: 2 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Framework</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Score</TableCell>
                  <TableCell align="right">Total Controls</TableCell>
                  <TableCell align="right">Implemented</TableCell>
                  <TableCell align="right">Not Implemented</TableCell>
                  <TableCell>Progress</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {multiFramework.map((fw) => (
                  <TableRow key={fw.framework}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {fw.framework.toUpperCase()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={fw.overall_status.replace('_', ' ')}
                        color={getStatusColor(fw.overall_status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        color={getScoreColor(fw.compliance_score)}
                        fontWeight="bold"
                      >
                        {fw.compliance_score.toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{fw.total_controls}</TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="success.main">
                        {fw.implemented}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="error.main">
                        {fw.not_implemented}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LinearProgress
                          variant="determinate"
                          value={fw.compliance_score}
                          color={getScoreColor(fw.compliance_score) as any}
                          sx={{ flexGrow: 1, mr: 1 }}
                        />
                        <Typography variant="body2">
                          {fw.compliance_score.toFixed(0)}%
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item>
              <Button variant="contained" startIcon={<Assessment />}>
                Start Assessment
              </Button>
            </Grid>
            <Grid item>
              <Button variant="outlined" startIcon={<Policy />}>
                View Gap Analysis
              </Button>
            </Grid>
            <Grid item>
              <Button variant="outlined" startIcon={<Security />}>
                Generate Report
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ComplianceDashboard;