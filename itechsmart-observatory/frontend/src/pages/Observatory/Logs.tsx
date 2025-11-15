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
  Paper,
  LinearProgress,
  Grid,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search,
  Refresh,
  FilterList,
  Error,
  Warning,
  Info,
  BugReport,
  Visibility,
} from '@mui/icons-material';

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  message: string;
  service_id: string;
  trace_id: string | null;
}

interface LogStatistics {
  DEBUG?: number;
  INFO?: number;
  WARNING?: number;
  ERROR?: number;
  CRITICAL?: number;
}

const ObservatoryLogs: React.FC = () => {
  const [services, setServices] = useState<any[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedService, setSelectedService] = useState<string>('');
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState<LogStatistics>({});
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    fetchServices();
  }, []);

  useEffect(() => {
    if (selectedService) {
      fetchLogs();
      fetchStatistics();
    }
  }, [selectedService, levelFilter]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh && selectedService) {
      interval = setInterval(() => {
        fetchLogs();
        fetchStatistics();
      }, 5000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, selectedService, levelFilter]);

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/observatory/services');
      const data = await response.json();
      setServices(data.services || []);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...(levelFilter && { level: levelFilter }),
        limit: '100',
      });

      const response = await fetch(
        `/api/observatory/logs/service/${selectedService}?${params}`
      );
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(
        `/api/observatory/logs/statistics/${selectedService}?time_range=1h`
      );
      const data = await response.json();
      setStatistics(data.statistics || {});
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery) {
      fetchLogs();
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/observatory/logs/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_id: selectedService,
          search_query: searchQuery,
          level: levelFilter || undefined,
          limit: 100,
        }),
      });
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Error searching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      DEBUG: '#9e9e9e',
      INFO: '#2196f3',
      WARNING: '#ff9800',
      ERROR: '#f44336',
      CRITICAL: '#d32f2f',
    };
    return colors[level] || '#9e9e9e';
  };

  const getLevelIcon = (level: string) => {
    const icons: Record<string, React.ReactElement> = {
      DEBUG: <BugReport />,
      INFO: <Info />,
      WARNING: <Warning />,
      ERROR: <Error />,
      CRITICAL: <Error />,
    };
    return icons[level] || <Info />;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Logs
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={autoRefresh ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            Auto Refresh {autoRefresh ? 'ON' : 'OFF'}
          </Button>
          <IconButton onClick={fetchLogs} disabled={!selectedService}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Statistics */}
      {selectedService && Object.keys(statistics).length > 0 && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {Object.entries(statistics).map(([level, count]) => (
            <Grid item xs={6} sm={4} md={2.4} key={level}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ color: getLevelColor(level), mb: 1 }}>
                    {getLevelIcon(level)}
                  </Box>
                  <Typography variant="h5">{count}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {level}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

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
                <InputLabel>Level</InputLabel>
                <Select
                  value={levelFilter}
                  label="Level"
                  onChange={(e) => setLevelFilter(e.target.value)}
                >
                  <MenuItem value="">All Levels</MenuItem>
                  <MenuItem value="DEBUG">DEBUG</MenuItem>
                  <MenuItem value="INFO">INFO</MenuItem>
                  <MenuItem value="WARNING">WARNING</MenuItem>
                  <MenuItem value="ERROR">ERROR</MenuItem>
                  <MenuItem value="CRITICAL">CRITICAL</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={5}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Search logs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  disabled={!selectedService}
                >
                  Search
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Logs Display */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Log Entries</Typography>
            <Chip label={`${logs.length} logs`} color="primary" />
          </Box>

          <Paper
            variant="outlined"
            sx={{
              p: 2,
              backgroundColor: '#1e1e1e',
              color: '#fff',
              maxHeight: 600,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
            }}
          >
            {logs.length > 0 ? (
              logs.map((log) => (
                <Box
                  key={log.id}
                  sx={{
                    mb: 1,
                    pb: 1,
                    borderBottom: '1px solid #333',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: '#2a2a2a',
                    },
                  }}
                  onClick={() => {
                    setSelectedLog(log);
                    setDetailsDialogOpen(true);
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography
                      component="span"
                      sx={{ color: '#888', minWidth: '180px' }}
                    >
                      [{new Date(log.timestamp).toLocaleString()}]
                    </Typography>
                    <Typography
                      component="span"
                      sx={{
                        color: getLevelColor(log.level),
                        fontWeight: 'bold',
                        minWidth: '80px',
                      }}
                    >
                      {log.level}
                    </Typography>
                    <Typography component="span" sx={{ flexGrow: 1 }}>
                      {log.message}
                    </Typography>
                    {log.trace_id && (
                      <Chip
                        label={`Trace: ${log.trace_id.substring(0, 8)}`}
                        size="small"
                        sx={{ backgroundColor: '#333', color: '#64b5f6' }}
                      />
                    )}
                  </Box>
                </Box>
              ))
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="text.secondary">
                  {selectedService ? 'No logs found' : 'Select a service to view logs'}
                </Typography>
              </Box>
            )}
          </Paper>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      {selectedService && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Error Logs
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  View only error and critical logs
                </Typography>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={async () => {
                    try {
                      const response = await fetch(
                        `/api/observatory/logs/errors/${selectedService}?time_range=1h`
                      );
                      const data = await response.json();
                      setLogs(data.logs || []);
                    } catch (error) {
                      console.error('Error fetching error logs:', error);
                    }
                  }}
                >
                  View Error Logs
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Trace Logs
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  View logs for a specific trace
                </Typography>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Enter trace ID"
                  onKeyPress={async (e) => {
                    if (e.key === 'Enter') {
                      const traceId = (e.target as HTMLInputElement).value;
                      try {
                        const response = await fetch(
                          `/api/observatory/logs/trace/${traceId}`
                        );
                        const data = await response.json();
                        setLogs(data.logs || []);
                      } catch (error) {
                        console.error('Error fetching trace logs:', error);
                      }
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Log Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Log Details</DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedLog.timestamp).toLocaleString()}
                  </Typography>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Level
                  </Typography>
                  <Chip
                    icon={getLevelIcon(selectedLog.level)}
                    label={selectedLog.level}
                    sx={{
                      backgroundColor: getLevelColor(selectedLog.level),
                      color: '#fff',
                      mt: 0.5,
                    }}
                  />
                </Grid>

                {selectedLog.trace_id && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Trace ID
                    </Typography>
                    <Typography variant="body1" fontFamily="monospace">
                      {selectedLog.trace_id}
                    </Typography>
                  </Grid>
                )}

                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Message
                  </Typography>
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      mt: 1,
                      backgroundColor: '#f5f5f5',
                      fontFamily: 'monospace',
                    }}
                  >
                    {selectedLog.message}
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {selectedLog?.trace_id && (
            <Button
              onClick={() => {
                setDetailsDialogOpen(false);
                // Navigate to trace view
                window.location.href = `/observatory/traces?trace_id=${selectedLog.trace_id}`;
              }}
            >
              View Trace
            </Button>
          )}
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ObservatoryLogs;