import { useState } from 'react';
import {
  Box,
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

export default function Scans() {
  const [openDialog, setOpenDialog] = useState(false);
  const [scanType, setScanType] = useState('full');
  const [autoFix, setAutoFix] = useState(false);

  const [scans] = useState([
    { id: 1, type: 'Full Suite', status: 'completed', score: 94.1, products: 28, checks: 1120, passed: 1054, failed: 42, warning: 24, duration: '45m', startedAt: '2024-01-15 10:00' },
    { id: 2, type: 'Security', status: 'completed', score: 97.2, products: 28, checks: 140, passed: 136, failed: 2, warning: 2, duration: '12m', startedAt: '2024-01-15 08:00' },
    { id: 3, type: 'Performance', status: 'running', score: null, products: 28, checks: 112, passed: 98, failed: 0, warning: 0, duration: '8m', startedAt: '2024-01-15 11:30' },
    { id: 4, type: 'Documentation', status: 'completed', score: 89.5, products: 28, checks: 252, passed: 225, failed: 15, warning: 12, duration: '18m', startedAt: '2024-01-15 06:00' },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleStartScan = () => {
    // TODO: Implement scan start logic
    setOpenDialog(false);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            QA Scans
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Run comprehensive quality assurance scans across products
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          New Scan
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Scan Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Score</TableCell>
              <TableCell align="center">Products</TableCell>
              <TableCell align="center">Checks</TableCell>
              <TableCell align="center">Passed</TableCell>
              <TableCell align="center">Failed</TableCell>
              <TableCell align="center">Warning</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Started At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {scans.map((scan) => (
              <TableRow key={scan.id} hover>
                <TableCell>
                  <Typography variant="body1" fontWeight="medium">
                    {scan.type}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={scan.status}
                    color={getStatusColor(scan.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {scan.score ? (
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={scan.score >= 95 ? 'success.main' : scan.score >= 85 ? 'warning.main' : 'error.main'}
                    >
                      {scan.score}%
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      In progress
                    </Typography>
                  )}
                </TableCell>
                <TableCell align="center">{scan.products}</TableCell>
                <TableCell align="center">{scan.checks}</TableCell>
                <TableCell align="center">
                  <Typography color="success.main">{scan.passed}</Typography>
                </TableCell>
                <TableCell align="center">
                  <Typography color="error.main">{scan.failed}</Typography>
                </TableCell>
                <TableCell align="center">
                  <Typography color="warning.main">{scan.warning}</Typography>
                </TableCell>
                <TableCell>{scan.duration}</TableCell>
                <TableCell>{scan.startedAt}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* New Scan Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Start New QA Scan</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Scan Type</InputLabel>
              <Select
                value={scanType}
                label="Scan Type"
                onChange={(e) => setScanType(e.target.value)}
              >
                <MenuItem value="full">Full Suite Scan</MenuItem>
                <MenuItem value="security">Security Scan</MenuItem>
                <MenuItem value="performance">Performance Scan</MenuItem>
                <MenuItem value="documentation">Documentation Scan</MenuItem>
                <MenuItem value="api">API Health Scan</MenuItem>
                <MenuItem value="database">Database Scan</MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Checkbox
                  checked={autoFix}
                  onChange={(e) => setAutoFix(e.target.checked)}
                />
              }
              label="Enable auto-fix for failed checks (15 checks support auto-fix)"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleStartScan} variant="contained">
            Start Scan
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}