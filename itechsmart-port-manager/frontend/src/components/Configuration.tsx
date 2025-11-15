import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  Backup as BackupIcon,
  Restore as RestoreIcon,
  RestartAlt as RestartAltIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = 'http://localhost:8100/api';

function Configuration() {
  const [success, setSuccess] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [resetDialog, setResetDialog] = useState(false);
  const [restoreDialog, setRestoreDialog] = useState(false);
  const [backupFile, setBackupFile] = useState<string>('');

  const handleBackup = async () => {
    try {
      const response = await axios.post(`${API_URL}/ports/backup`);
      setSuccess(`Configuration backed up to ${response.data.backup_file}`);
    } catch (error) {
      setError('Failed to create backup');
    }
  };

  const handleRestore = async () => {
    try {
      await axios.post(`${API_URL}/ports/restore`, null, {
        params: { backup_file: backupFile }
      });
      setSuccess('Configuration restored successfully');
      setRestoreDialog(false);
    } catch (error) {
      setError('Failed to restore configuration');
    }
  };

  const handleReset = async () => {
    try {
      await axios.post(`${API_URL}/ports/reset`);
      setSuccess('Port assignments reset to defaults');
      setResetDialog(false);
    } catch (error) {
      setError('Failed to reset configuration');
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        Configuration
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <BackupIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  Backup Configuration
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Create a backup of the current port configuration. This includes all port assignments, history, and reserved ports.
              </Typography>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={handleBackup}
                fullWidth
              >
                Create Backup
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <RestoreIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">
                  Restore Configuration
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Restore port configuration from a previous backup file. This will overwrite current settings.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<RestoreIcon />}
                onClick={() => setRestoreDialog(true)}
                fullWidth
              >
                Restore from Backup
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <RestartAltIcon sx={{ mr: 1, color: 'error.main' }} />
                <Typography variant="h6">
                  Reset to Defaults
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Reset all port assignments to their default values. This action cannot be undone without a backup.
              </Typography>
              <Button
                variant="outlined"
                color="error"
                startIcon={<RestartAltIcon />}
                onClick={() => setResetDialog(true)}
                fullWidth
              >
                Reset Configuration
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Restore Dialog */}
      <Dialog open={restoreDialog} onClose={() => setRestoreDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Restore Configuration</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Backup File Path"
            value={backupFile}
            onChange={(e) => setBackupFile(e.target.value)}
            sx={{ mt: 2 }}
            helperText="Enter the path to the backup file"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRestoreDialog(false)}>Cancel</Button>
          <Button onClick={handleRestore} variant="contained" disabled={!backupFile}>
            Restore
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Dialog */}
      <Dialog open={resetDialog} onClose={() => setResetDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Reset to Defaults</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This will reset all port assignments to their default values. This action cannot be undone without a backup.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialog(false)}>Cancel</Button>
          <Button onClick={handleReset} variant="contained" color="error">
            Reset
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Configuration;