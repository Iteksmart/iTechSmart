/**
 * iTechSmart Compliance - Gap Analysis
 * Identify and track compliance gaps
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
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
  Chip,
  Button,
  LinearProgress,
  Alert
} from '@mui/material';
import { Download, TrendingDown } from '@mui/icons-material';

interface Gap {
  control_id: string;
  control_number: string;
  title: string;
  status: string;
  category: string;
  domain: string;
  assigned_to: string | null;
  gap_analysis: string | null;
}

const GapAnalysis: React.FC = () => {
  const [framework, setFramework] = useState('soc2');
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGapAnalysis();
  }, [framework]);

  const fetchGapAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8019/compliance-center/dashboard/gap-analysis?framework=${framework}`
      );
      const data = await response.json();
      setGaps(data.gaps);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching gap analysis:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'not_implemented' ? 'error' : 'warning';
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
            Gap Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Identify and remediate compliance gaps
          </Typography>
        </Box>
        <Button variant="outlined" startIcon={<Download />}>
          Export Report
        </Button>
      </Box>

      {/* Framework Selector */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <FormControl sx={{ minWidth: 300 }}>
            <InputLabel>Select Framework</InputLabel>
            <Select
              value={framework}
              label="Select Framework"
              onChange={(e) => setFramework(e.target.value)}
            >
              <MenuItem value="soc2">SOC 2</MenuItem>
              <MenuItem value="iso27001">ISO 27001</MenuItem>
              <MenuItem value="hipaa">HIPAA</MenuItem>
              <MenuItem value="gdpr">GDPR</MenuItem>
              <MenuItem value="pci_dss">PCI-DSS</MenuItem>
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {/* Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingDown color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Gaps</Typography>
              </Box>
              <Typography variant="h3" color="error.main">
                {gaps.length}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Controls requiring attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Not Implemented
              </Typography>
              <Typography variant="h3" color="error.main">
                {gaps.filter((g) => g.status === 'not_implemented').length}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Critical priority
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Partially Implemented
              </Typography>
              <Typography variant="h3" color="warning.main">
                {gaps.filter((g) => g.status === 'partially_implemented').length}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Needs completion
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alert */}
      {gaps.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {gaps.length} compliance gap{gaps.length !== 1 ? 's' : ''} identified for{' '}
          {framework.toUpperCase()}. Immediate action recommended.
        </Alert>
      )}

      {/* Gaps Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Identified Gaps
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Control #</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Domain</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Assigned To</TableCell>
                  <TableCell>Gap Analysis</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {gaps.map((gap) => (
                  <TableRow key={gap.control_id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {gap.control_number}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{gap.title}</Typography>
                    </TableCell>
                    <TableCell>{gap.category}</TableCell>
                    <TableCell>{gap.domain}</TableCell>
                    <TableCell>
                      <Chip
                        label={gap.status.replace('_', ' ')}
                        color={getStatusColor(gap.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{gap.assigned_to || 'Unassigned'}</TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {gap.gap_analysis || 'Not analyzed'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Container>
  );
};

export default GapAnalysis;