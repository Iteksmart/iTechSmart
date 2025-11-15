import { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

export default function Dashboard() {
  const [stats] = useState({
    totalModels: 24,
    activeModels: 18,
    totalPredictions: 1250000,
    avgAccuracy: 94.5,
  });

  const [modelPerformance] = useState([
    { name: 'Classification', accuracy: 96.2, f1Score: 94.8 },
    { name: 'Regression', accuracy: 92.5, f1Score: 91.3 },
    { name: 'Clustering', accuracy: 88.7, f1Score: 87.2 },
    { name: 'NLP', accuracy: 95.1, f1Score: 93.9 },
    { name: 'Computer Vision', accuracy: 97.3, f1Score: 96.5 },
  ]);

  const [trainingHistory] = useState([
    { epoch: 1, loss: 0.85, accuracy: 72.3 },
    { epoch: 2, loss: 0.62, accuracy: 81.5 },
    { epoch: 3, loss: 0.48, accuracy: 87.2 },
    { epoch: 4, loss: 0.35, accuracy: 91.8 },
    { epoch: 5, loss: 0.28, accuracy: 94.5 },
    { epoch: 6, loss: 0.22, accuracy: 96.1 },
  ]);

  const [recentModels] = useState([
    { name: 'Customer Churn Predictor', type: 'Classification', accuracy: 96.2, status: 'deployed' },
    { name: 'Sales Forecaster', type: 'Regression', accuracy: 92.5, status: 'training' },
    { name: 'Image Classifier', type: 'Computer Vision', accuracy: 97.3, status: 'deployed' },
    { name: 'Sentiment Analyzer', type: 'NLP', accuracy: 95.1, status: 'deployed' },
  ]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI Platform Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Monitor ML models, training, and predictions
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Models
              </Typography>
              <Typography variant="h3">
                {stats.totalModels}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stats.activeModels} active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Avg Accuracy
              </Typography>
              <Typography variant="h3" color="success.main">
                {stats.avgAccuracy}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={stats.avgAccuracy}
                sx={{ mt: 1 }}
                color="success"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Predictions
              </Typography>
              <Typography variant="h3">
                {(stats.totalPredictions / 1000000).toFixed(2)}M
              </Typography>
              <Typography variant="body2" color="text.secondary">
                This month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Training Jobs
              </Typography>
              <Typography variant="h3" color="primary.main">
                3
              </Typography>
              <Typography variant="body2" color="text.secondary">
                In progress
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Model Performance by Type
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={modelPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="accuracy" fill="#2196f3" name="Accuracy %" />
                <Bar dataKey="f1Score" fill="#4caf50" name="F1 Score %" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Training Progress
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trainingHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="epoch" />
                <YAxis yAxisId="left" domain={[0, 1]} />
                <YAxis yAxisId="right" orientation="right" domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="loss" stroke="#f44336" name="Loss" />
                <Line yAxisId="right" type="monotone" dataKey="accuracy" stroke="#4caf50" name="Accuracy %" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Models */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Models
            </Typography>
            <List>
              {recentModels.map((model, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1" fontWeight="medium">
                          {model.name}
                        </Typography>
                        <Chip label={model.type} size="small" variant="outlined" />
                      </Box>
                    }
                    secondary={`Accuracy: ${model.accuracy}%`}
                  />
                  <Chip
                    label={model.status}
                    color={model.status === 'deployed' ? 'success' : 'primary'}
                    size="small"
                    icon={model.status === 'deployed' ? <CheckIcon /> : <TrendingUpIcon />}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}