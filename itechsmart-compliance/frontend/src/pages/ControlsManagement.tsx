/**
 * iTechSmart Compliance - Controls Management
 * Manage compliance controls across frameworks
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  Edit,
  Visibility,
  Assignment,
  AttachFile,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Search,
  FilterList
} from '@mui/icons-material';

interface Control {
  control_id: string;
  framework: string;
  control_number: string;
  title: string;
  description: string;
  category: string;
  domain: string;
  status: string;
  assigned_to: string | null;
  evidence_count: number;
  last_assessed: string | null;
  next_assessment: string | null;
}

const ControlsManagement: React.FC = () => {
  const [controls, setControls] = useState<Control[]>([]);
  const [filteredControls, setFilteredControls] = useState<Control[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFramework, setSelectedFramework] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedControl, setSelectedControl] = useState<Control | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  const frameworks = [
    { value: '', label: 'All Frameworks' },
    { value: 'soc2', label: 'SOC 2' },
    { value: 'iso27001', label: 'ISO 27001' },
    { value: 'hipaa', label: 'HIPAA' },
    { value: 'gdpr', label: 'GDPR' },
    { value: 'pci_dss', label: 'PCI-DSS' }
  ];

  const statuses = [
    { value: '', label: 'All Statuses' },
    { value: 'implemented', label: 'Implemented' },
    { value: 'partially_implemented', label: 'Partially Implemented' },
    { value: 'not_implemented', label: 'Not Implemented' },
    { value: 'planned', label: 'Planned' }
  ];

  useEffect(() => {
    fetchControls();
  }, []);

  useEffect(() => {
    filterControls();
  }, [controls, selectedFramework, selectedStatus, selectedCategory, searchQuery]);

  const fetchControls = async () => {
    try {
      const response = await fetch('http://localhost:8019/compliance-center/controls');
      const data = await response.json();
      setControls(data.controls);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching controls:', error);
      setLoading(false);
    }
  };

  const filterControls = () => {
    let filtered = [...controls];

    if (selectedFramework) {
      filtered = filtered.filter((c) => c.framework === selectedFramework);
    }

    if (selectedStatus) {
      filtered = filtered.filter((c) => c.status === selectedStatus);
    }

    if (selectedCategory) {
      filtered = filtered.filter((c) => c.category === selectedCategory);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.control_number.toLowerCase().includes(query) ||
          c.title.toLowerCase().includes(query) ||
          c.description.toLowerCase().includes(query)
      );
    }

    setFilteredControls(filtered);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'implemented':
        return 'success';
      case 'partially_implemented':
        return 'warning';
      case 'not_implemented':
        return 'error';
      case 'planned':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'implemented':
        return <CheckCircle fontSize="small" />;
      case 'partially_implemented':
        return <Warning fontSize="small" />;
      case 'not_implemented':
        return <ErrorIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const handleViewDetails = async (controlId: string) => {
    try {
      const response = await fetch(
        `http://localhost:8019/compliance-center/controls/${controlId}`
      );
      const data = await response.json();
      setSelectedControl(data);
      setDetailsOpen(true);
    } catch (error) {
      console.error('Error fetching control details:', error);
    }
  };

  const handleUpdateStatus = async (controlId: string, newStatus: string) => {
    try {
      await fetch(`http://localhost:8019/compliance-center/controls/${controlId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchControls();
    } catch (error) {
      console.error('Error updating control status:', error);
    }
  };

  const categories = Array.from(new Set(controls.map((c) => c.category)));

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
          Controls Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage and track compliance controls across all frameworks
        </Typography>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search Controls"
                variant="outlined"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Framework</InputLabel>
                <Select
                  value={selectedFramework}
                  label="Framework"
                  onChange={(e) => setSelectedFramework(e.target.value)}
                >
                  {frameworks.map((fw) => (
                    <MenuItem key={fw.value} value={fw.value}>
                      {fw.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={selectedStatus}
                  label="Status"
                  onChange={(e) => setSelectedStatus(e.target.value)}
                >
                  {statuses.map((status) => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={selectedCategory}
                  label="Category"
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4">{filteredControls.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Controls
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="success.main">
                {filteredControls.filter((c) => c.status === 'implemented').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Implemented
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="warning.main">
                {filteredControls.filter((c) => c.status === 'partially_implemented').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Partial
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" color="error.main">
                {filteredControls.filter((c) => c.status === 'not_implemented').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Not Implemented
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Controls Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Control #</TableCell>
                  <TableCell>Framework</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Evidence</TableCell>
                  <TableCell>Assigned To</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredControls.map((control) => (
                  <TableRow key={control.control_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {control.control_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={control.framework.toUpperCase()}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{control.title}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {control.category}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(control.status)}
                        label={control.status.replace('_', ' ')}
                        color={getStatusColor(control.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <AttachFile fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="body2">{control.evidence_count}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {control.assigned_to || 'Unassigned'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(control.control_id)}
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton size="small">
                          <Edit fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Assign">
                        <IconButton size="small">
                          <Assignment fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Control Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedControl && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">
                  {selectedControl.control_number} - {selectedControl.title}
                </Typography>
                <Chip
                  label={selectedControl.framework.toUpperCase()}
                  color="primary"
                  size="small"
                />
              </Box>
            </DialogTitle>
            <DialogContent>
              <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 2 }}>
                <Tab label="Details" />
                <Tab label="Evidence" />
                <Tab label="History" />
              </Tabs>

              {tabValue === 0 && (
                <Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Description
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {selectedControl.description}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Category
                      </Typography>
                      <Typography variant="body2">{selectedControl.category}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Domain
                      </Typography>
                      <Typography variant="body2">{selectedControl.domain}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Status
                      </Typography>
                      <Chip
                        label={selectedControl.status.replace('_', ' ')}
                        color={getStatusColor(selectedControl.status) as any}
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Assigned To
                      </Typography>
                      <Typography variant="body2">
                        {selectedControl.assigned_to || 'Unassigned'}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {tabValue === 1 && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Evidence items will be displayed here
                  </Typography>
                </Box>
              )}

              {tabValue === 2 && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Audit history will be displayed here
                  </Typography>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsOpen(false)}>Close</Button>
              <Button variant="contained">Update Status</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default ControlsManagement;