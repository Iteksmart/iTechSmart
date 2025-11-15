import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Chip,
  Paper,
} from '@mui/material';
import { PlayArrow as StartIcon, Stop as StopIcon } from '@mui/icons-material';

export default function Training() {
  const [jobs] = useState([
    { id: 1, name: 'Sales Forecaster v1.4', status: 'running', progress: 65, epoch: 13, totalEpochs: 20, accuracy: 91.2 },
    { id: 2, name: 'Image Classifier v3.1', status: 'running', progress: 40, epoch: 8, totalEpochs: 20, accuracy: 88.5 },
    { id: 3, name: 'Sentiment Analyzer v1.9', status: 'running', progress: 85, epoch: 17, totalEpochs: 20, accuracy: 94.8 },
    { id: 4, name: 'Fraud Detector v2.6', status: 'queued', progress: 0, epoch: 0, totalEpochs: 15, accuracy: 0 },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'primary';
      case 'queued':
        return 'default';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            Training Jobs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monitor and manage model training
          </Typography>
        </div>
        <Button variant="contained" startIcon={<StartIcon />}>
          New Training Job
        </Button>
      </Box>

      <Grid container spacing={3}>
        {jobs.map((job) => (
          <Grid item xs={12} md={6} key={job.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <div>
                    <Typography variant="h6" gutterBottom>
                      {job.name}
                    </Typography>
                    <Chip
                      label={job.status}
                      color={getStatusColor(job.status) as any}
                      size="small"
                    />
                  </div>
                  {job.status === 'running' && (
                    <Button size="small" variant="outlined" color="error" startIcon={<StopIcon />}>
                      Stop
                    </Button>
                  )}
                </Box>

                {job.status === 'running' && (
                  <>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Progress
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {job.progress}%
                        </Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={job.progress} />
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                          <Typography variant="body2" color="text.secondary">
                            Epoch
                          </Typography>
                          <Typography variant="h6">
                            {job.epoch} / {job.totalEpochs}
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={6}>
                        <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                          <Typography variant="body2" color="text.secondary">
                            Accuracy
                          </Typography>
                          <Typography variant="h6" color="success.main">
                            {job.accuracy}%
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  </>
                )}

                {job.status === 'queued' && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Waiting for available resources...
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}