import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Security,
  AttachMoney,
  Code,
  TrendingUp,
  Warning,
  CheckCircle,
  Error,
  Info,
  ZoomIn,
  Timeline,
  Assessment,
  Speed,
  Cloud,
  Lock,
  Build,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const MasterDashboard = ({ realTimeData, onEventClick }) => {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [correlationDialog, setCorrelationDialog] = useState(false);
  const [correlationData, setCorrelationData] = useState(null);

  // Real-time metrics from Neural Data Plane
  const securityMetrics = realTimeData.security || {};
  const finopsMetrics = realTimeData.finops || {};
  const devopsMetrics = realTimeData.devops || {};

  // Calculate cross-domain correlations
  const calculateCorrelations = () => {
    const correlations = [];

    // Cost anomaly correlation with deployments
    if (finopsMetrics.anomalies && devopsMetrics.deployments) {
      finopsMetrics.anomalies.forEach(anomaly => {
        const relatedDeployments = devopsMetrics.deployments.filter(
          deployment => Math.abs(new Date(anomaly.timestamp) - new Date(deployment.timestamp)) < 3600000 // 1 hour
        );
        
        if (relatedDeployments.length > 0) {
          correlations.push({
            type: 'COST_DEPLOYMENT',
            finopsEvent: anomaly,
            devopsEvents: relatedDeployments,
            description: `Cost spike of $${anomaly.costImpact?.toFixed(2)} correlated with ${relatedDeployments.length} deployment(s)`,
            severity: anomaly.costImpact > 1000 ? 'high' : 'medium'
          });
        }
      });
    }

    // Security threats correlation with deployments
    if (securityMetrics.threats && devopsMetrics.deployments) {
      securityMetrics.threats.forEach(threat => {
        const relatedDeployments = devopsMetrics.deployments.filter(
          deployment => Math.abs(new Date(threat.timestamp) - new Date(deployment.timestamp)) < 7200000 // 2 hours
        );
        
        if (relatedDeployments.length > 0) {
          correlations.push({
            type: 'SECURITY_DEPLOYMENT',
            securityEvent: threat,
            devopsEvents: relatedDeployments,
            description: `Security threat "${threat.description}" detected after recent deployment`,
            severity: threat.severity || 'high'
          });
        }
      });
    }

    return correlations;
  };

  const correlations = calculateCorrelations();

  const handleCorrelationClick = (correlation) => {
    setCorrelationData(correlation);
    setCorrelationDialog(true);
  };

  // Security Dashboard Component
  const SecurityDashboard = () => (
    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%)' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Security sx={{ mr: 1, color: '#dc3545' }} />
          <Typography variant="h6" fontWeight="bold">Security Operations</Typography>
          <Box ml="auto">
            <Chip 
              label={`${securityMetrics.threatCount || 0} Active Threats`}
              color="error"
              size="small"
            />
          </Box>
        </Box>

        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="error.main">
                {securityMetrics.threatCount || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">Active Threats</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                {securityMetrics.resolvedCount || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">Resolved Today</Typography>
            </Paper>
          </Grid>
        </Grid>

        <Typography variant="subtitle2" mb={1}>Recent Security Events</Typography>
        <TableContainer sx={{ maxHeight: 200 }}>
          <Table size="small">
            <TableBody>
              {(securityMetrics.threats || []).slice(0, 5).map((threat, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      {threat.severity === 'high' ? <Error color="error" /> : <Warning color="warning" />}
                      <Box ml={1}>
                        <Typography variant="body2" fontWeight="medium">
                          {threat.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(threat.timestamp).toLocaleTimeString()}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => onEventClick(threat)}>
                      <ZoomIn />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  // FinOps Dashboard Component
  const FinOpsDashboard = () => (
    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%)' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <AttachMoney sx={{ mr: 1, color: '#28a745' }} />
          <Typography variant="h6" fontWeight="bold">Financial Operations</Typography>
          <Box ml="auto">
            <Chip 
              label={`$${(finopsMetrics.totalSpend || 0).toFixed(2)}`}
              color="success"
              size="small"
            />
          </Box>
        </Box>

        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="success.main">
                ${(finopsMetrics.totalSpend || 0).toFixed(0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">Monthly Spend</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main">
                {finopsMetrics.anomalies?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">Cost Anomalies</Typography>
            </Paper>
          </Grid>
        </Grid>

        <Typography variant="subtitle2" mb={1">Cost Trend Analysis</Typography>
        <ResponsiveContainer width="100%" height={150}>
          <AreaChart data={finopsMetrics.costTrend || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <RechartsTooltip />
            <Area type="monotone" dataKey="cost" stroke="#28a745" fill="#e6ffed" />
          </AreaChart>
        </ResponsiveContainer>

        <Typography variant="subtitle2" mt={2} mb={1">Recent Cost Anomalies</Typography>
        <TableContainer sx={{ maxHeight: 150 }}>
          <Table size="small">
            <TableBody>
              {(finopsMetrics.anomalies || []).slice(0, 3).map((anomaly, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {anomaly.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Impact: ${anomaly.costImpact?.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => onEventClick(anomaly)}>
                      <ZoomIn />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  // DevOps Dashboard Component
  const DevOpsDashboard = () => (
    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Code sx={{ mr: 1, color: '#1976d2' }} />
          <Typography variant="h6" fontWeight="bold">DevOps Operations</Typography>
          <Box ml="auto">
            <Chip 
              label={`${devopsMetrics.deploymentCount || 0} Deployments`}
              color="primary"
              size="small"
            />
          </Box>
        </Box>

        <Grid container spacing={2} mb={2}>
          <Grid item xs={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h5" color="primary.main">
                {devopsMetrics.deploymentCount || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">Deployments</Typography>
            </Paper>
          </Grid>
          <Grid item xs={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h5" color="success.main">
                {devopsMetrics.successRate || 98}%
              </Typography>
              <Typography variant="body2" color="text.secondary">Success Rate</Typography>
            </Paper>
          </Grid>
          <Grid item xs={4}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h5" color="warning.main">
                {devopsMetrics.pipelineCount || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">Active Pipelines</Typography>
            </Paper>
          </Grid>
        </Grid>

        <Typography variant="subtitle2" mb={1}>Deployment Pipeline Status</Typography>
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={devopsMetrics.pipelineStatus || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="pipeline" />
            <YAxis />
            <RechartsTooltip />
            <Bar dataKey="success" fill="#4caf50" />
            <Bar dataKey="failed" fill="#f44336" />
            <Bar dataKey="pending" fill="#ff9800" />
          </BarChart>
        </ResponsiveContainer>

        <Typography variant="subtitle2" mt={2} mb={1">Recent Deployments</Typography>
        <TableContainer sx={{ maxHeight: 150 }}>
          <Table size="small">
            <TableBody>
              {(devopsMetrics.deployments || []).slice(0, 3).map((deployment, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      {deployment.status === 'success' ? 
                        <CheckCircle color="success" /> : 
                        <Error color="error" />
                      }
                      <Box ml={1}>
                        <Typography variant="body2" fontWeight="medium">
                          {deployment.service}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {deployment.version} • {new Date(deployment.timestamp).toLocaleTimeString()}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => onEventClick(deployment)}>
                      <ZoomIn />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  // Cross-Domain Correlations Component
  const CorrelationDashboard = () => (
    <Card sx={{ background: 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Timeline sx={{ mr: 1, color: '#ff9800' }} />
          <Typography variant="h6" fontWeight="bold">Cross-Domain Correlations</Typography>
          <Box ml="auto">
            <Chip 
              label={`${correlations.length} Insights`}
              color="warning"
              size="small"
            />
          </Box>
        </Box>

        {correlations.length === 0 ? (
          <Alert severity="info">
            No cross-domain correlations detected at this time.
          </Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableBody>
                {correlations.map((correlation, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {correlation.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Severity: {correlation.severity}
                          </Typography>
                        </Box>
                        <Button 
                          size="small" 
                          variant="outlined"
                          onClick={() => handleCorrelationClick(correlation)}
                        >
                          Analyze
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          iTechSmart Master Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time cross-domain visibility and correlation analysis
        </Typography>
      </Box>

      {/* Main Dashboard Grid */}
      <Grid container spacing={3}>
        {/* Security, FinOps, DevOps Row */}
        <Grid item xs={12} md={4}>
          <SecurityDashboard />
        </Grid>
        <Grid item xs={12} md={4}>
          <FinOpsDashboard />
        </Grid>
        <Grid item xs={12} md={4}>
          <DevOpsDashboard />
        </Grid>

        {/* Cross-Domain Correlations */}
        <Grid item xs={12}>
          <CorrelationDashboard />
        </Grid>

        {/* Real-time Events Stream */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Assessment sx={{ mr: 1, color: '#667eea' }} />
                <Typography variant="h6" fontWeight="bold">Real-time Event Stream</Typography>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Time</TableCell>
                      <TableCell>Domain</TableCell>
                      <TableCell>Event</TableCell>
                      <TableCell>Severity</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {realTimeData.events?.slice(0, 10).map((event, index) => (
                      <TableRow key={index} hover>
                        <TableCell>
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={event.domain || 'System'}
                            size="small"
                            color={
                              event.domain === 'security' ? 'error' :
                              event.domain === 'finops' ? 'success' :
                              event.domain === 'devops' ? 'primary' : 'default'
                            }
                          />
                        </TableCell>
                        <TableCell>{event.description}</TableCell>
                        <TableCell>
                          <Chip 
                            label={event.severity || 'info'}
                            size="small"
                            color={event.severity === 'critical' ? 'error' : 'default'}
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" onClick={() => onEventClick(event)}>
                            <ZoomIn />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Correlation Detail Dialog */}
      <Dialog 
        open={correlationDialog} 
        onClose={() => setCorrelationDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <Assessment sx={{ mr: 1 }} />
            Cross-Domain Correlation Analysis
          </Box>
        </DialogTitle>
        <DialogContent>
          {correlationData && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {correlationData.description}
              </Typography>
              
              <Grid container spacing={2} mt={2}>
                {correlationData.finopsEvent && (
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" color="success.main" gutterBottom>
                          <AttachMoney sx={{ mr: 1, verticalAlign: 'middle' }} />
                          FinOps Event
                        </Typography>
                        <Typography variant="body2">
                          {correlationData.finopsEvent.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Impact: ${correlationData.finopsEvent.costImpact?.toFixed(2)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {correlationData.devopsEvents && (
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" color="primary.main" gutterBottom>
                          <Code sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Related Deployments
                        </Typography>
                        {correlationData.devopsEvents.map((deployment, index) => (
                          <Box key={index} mb={1}>
                            <Typography variant="body2">
                              {deployment.service} - {deployment.version}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(deployment.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {correlationData.securityEvent && (
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" color="error.main" gutterBottom>
                          <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Security Event
                        </Typography>
                        <Typography variant="body2">
                          {correlationData.securityEvent.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Severity: {correlationData.securityEvent.severity}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  This correlation was automatically detected by the iTechSmart Neural Data Plane,
                  connecting events across different domains to provide comprehensive insights.
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCorrelationDialog(false)}>
            Close
          </Button>
          <Button variant="contained" color="primary">
            Take Action
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MasterDashboard;