import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
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
  LinearProgress,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import {
  Search,
  Visibility,
  ExpandMore,
  Timeline,
  Speed,
  Error,
  CheckCircle,
  Warning,
} from '@mui/icons-material';

interface Trace {
  trace_id: string;
  trace_name: string;
  start_time: string;
  duration_ms: number;
  status: string;
  http_method: string;
  http_status_code: number;
}

interface TraceDetails {
  trace_id: string;
  service_id: string;
  trace_name: string;
  start_time: string;
  duration_ms: number;
  status: string;
  spans: Array<{
    span_id: string;
    parent_span_id: string | null;
    span_name: string;
    service_name: string;
    duration_ms: number;
    status: string;
  }>;
}

interface TraceAnalysis {
  total_spans: number;
  total_duration_ms: number;
  slowest_spans: Array<{
    span_name: string;
    service_name: string;
    duration_ms: number;
    percentage: number;
  }>;
  error_spans: Array<{
    span_name: string;
    error_message: string;
  }>;
}

const ObservatoryTraces: React.FC = () => {
  const [services, setServices] = useState<any[]>([]);
  const [traces, setTraces] = useState<Trace[]>([]);
  const [selectedService, setSelectedService] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedTrace, setSelectedTrace] = useState<TraceDetails | null>(null);
  const [traceAnalysis, setTraceAnalysis] = useState<TraceAnalysis | null>(null);

  useEffect(() => {
    fetchServices();
  }, []);

  useEffect(() => {
    if (selectedService) {
      fetchTraces();
    }
  }, [selectedService, statusFilter]);

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/observatory/services');
      const data = await response.json();
      setServices(data.services || []);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  const fetchTraces = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...(statusFilter !== 'all' && { status: statusFilter }),
      });

      const response = await fetch(
        `/api/observatory/traces/service/${selectedService}?${params}`
      );
      const data = await response.json();
      setTraces(data.traces || []);
    } catch (error) {
      console.error('Error fetching traces:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewTrace = async (traceId: string) => {
    try {
      // Fetch trace details
      const detailsResponse = await fetch(`/api/observatory/traces/${traceId}`);
      const detailsData = await detailsResponse.json();
      setSelectedTrace(detailsData.trace);

      // Fetch trace analysis
      const analysisResponse = await fetch(`/api/observatory/traces/${traceId}/analyze`);
      const analysisData = await analysisResponse.json();
      setTraceAnalysis(analysisData.analysis);

      setDetailsDialogOpen(true);
    } catch (error) {
      console.error('Error fetching trace details:', error);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'> = {
      ok: 'success',
      error: 'error',
      timeout: 'warning',
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactElement> = {
      ok: <CheckCircle />,
      error: <Error />,
      timeout: <Warning />,
    };
    return icons[status] || <CheckCircle />;
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const filteredTraces = traces.filter((trace) =>
    trace.trace_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        Distributed Traces
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Service</InputLabel>
                <Select
                  value={selectedService}
                  label="Service"
                  onChange={(e) => setSelectedService(e.target.value)}
                >
                  {services.map((service) => (
                    <MenuItem key={service.id} value={service.id}>
                      {service.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="ok">OK</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                  <MenuItem value="timeout">Timeout</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={5}>
              <TextField
                fullWidth
                placeholder="Search traces..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Traces Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Traces</Typography>
            <Chip label={`${filteredTraces.length} traces`} color="primary" />
          </Box>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Trace ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Method</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Duration</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTraces.length > 0 ? (
                  filteredTraces.map((trace) => (
                    <TableRow key={trace.trace_id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {trace.trace_id.substring(0, 8)}
                        </Typography>
                      </TableCell>
                      <TableCell>{trace.trace_name}</TableCell>
                      <TableCell>
                        <Chip label={trace.http_method} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(trace.status)}
                          label={trace.status.toUpperCase()}
                          color={getStatusColor(trace.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={formatDuration(trace.duration_ms)}
                          color={trace.duration_ms > 1000 ? 'warning' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(trace.start_time).toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewTrace(trace.trace_id)}
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
                        {selectedService ? 'No traces found' : 'Select a service to view traces'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Trace Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Timeline sx={{ mr: 1 }} />
            Trace Details
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedTrace && (
            <Box sx={{ mt: 2 }}>
              {/* Trace Info */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Trace ID
                  </Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    {selectedTrace.trace_id}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    icon={getStatusIcon(selectedTrace.status)}
                    label={selectedTrace.status.toUpperCase()}
                    color={getStatusColor(selectedTrace.status)}
                    size="small"
                    sx={{ mt: 0.5 }}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Duration
                  </Typography>
                  <Typography variant="h6">
                    {formatDuration(selectedTrace.duration_ms)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Started
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedTrace.start_time).toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>

              {/* Performance Analysis */}
              {traceAnalysis && (
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Performance Analysis</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Alert severity="info" sx={{ mb: 2 }}>
                          Total Spans: {traceAnalysis.total_spans} | Total Duration:{' '}
                          {formatDuration(traceAnalysis.total_duration_ms)}
                        </Alert>
                        <Typography variant="subtitle2" gutterBottom>
                          Slowest Spans
                        </Typography>
                        {traceAnalysis.slowest_spans.map((span, index) => (
                          <Box
                            key={index}
                            sx={{
                              p: 1,
                              mb: 1,
                              border: '1px solid #e0e0e0',
                              borderRadius: 1,
                            }}
                          >
                            <Typography variant="body2" fontWeight="medium">
                              {span.span_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {span.service_name} - {formatDuration(span.duration_ms)} (
                              {span.percentage.toFixed(1)}%)
                            </Typography>
                          </Box>
                        ))}
                      </Grid>
                      <Grid item xs={12} md={6}>
                        {traceAnalysis.error_spans.length > 0 && (
                          <>
                            <Typography variant="subtitle2" gutterBottom>
                              Error Spans
                            </Typography>
                            {traceAnalysis.error_spans.map((span, index) => (
                              <Alert key={index} severity="error" sx={{ mb: 1 }}>
                                <Typography variant="body2" fontWeight="medium">
                                  {span.span_name}
                                </Typography>
                                <Typography variant="caption">
                                  {span.error_message}
                                </Typography>
                              </Alert>
                            ))}
                          </>
                        )}
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Spans */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    Spans ({selectedTrace.spans.length})
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Span Name</TableCell>
                          <TableCell>Service</TableCell>
                          <TableCell>Duration</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedTrace.spans.map((span) => (
                          <TableRow key={span.span_id}>
                            <TableCell>
                              <Typography
                                variant="body2"
                                sx={{
                                  pl: span.parent_span_id ? 2 : 0,
                                }}
                              >
                                {span.span_name}
                              </Typography>
                            </TableCell>
                            <TableCell>{span.service_name}</TableCell>
                            <TableCell>{formatDuration(span.duration_ms)}</TableCell>
                            <TableCell>
                              <Chip
                                label={span.status.toUpperCase()}
                                color={getStatusColor(span.status)}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ObservatoryTraces;