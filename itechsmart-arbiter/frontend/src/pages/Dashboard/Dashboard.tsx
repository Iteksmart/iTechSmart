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
  AlertTitle,
  Button,
} from '@mui/material';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  TrendingUp,
  Users,
  Lock,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

// Services
import { arbiterApi } from '../../services/api';

// Components
import MetricCard from '../../components/MetricCard/MetricCard';
import RecentDecisions from '../../components/RecentDecisions/RecentDecisions';
import RiskChart from '../../components/RiskChart/RiskChart';

interface DashboardMetrics {
  total_decisions_24h: number;
  approved: number;
  denied: number;
  pending_approval: number;
  approval_rate: number;
  average_risk_score: number;
  emergency_stop_active: boolean;
  top_agents: Array<{ agent_id: string; count: number }>;
}

const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');

  const { data: metrics, isLoading, error, refetch } = useQuery<DashboardMetrics>(
    ['metrics', timeRange],
    () => arbiterApi.getMetrics(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const { data: status } = useQuery(
    'status',
    () => arbiterApi.getStatus(),
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  );

  useEffect(() => {
    if (status?.emergency_stop_active) {
      toast.error('⚠️ Emergency Stop is Active!', {
        duration: 0,
        icon: '🚨',
      });
    }
  }, [status?.emergency_stop_active]);

  if (isLoading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <Typography>Loading dashboard...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        <AlertTitle>Error</AlertTitle>
        Failed to load dashboard data. Please try refreshing the page.
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h3" component="h1" gutterBottom>
            iTechSmart Arbiter Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            AI Governance & Safety Layer - Real-time Monitoring
          </Typography>
        </motion.div>

        {/* Emergency Alert */}
        {status?.emergency_stop_active && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
              <AlertTitle>🚨 EMERGENCY STOP ACTIVE</AlertTitle>
              All AI actions are currently blocked. Contact your system administrator immediately.
              <Button
                variant="outlined"
                color="error"
                size="small"
                sx={{ ml: 2 }}
                href="/emergency"
              >
                View Details
              </Button>
            </Alert>
          </motion.div>
        )}
      </Box>

      {/* Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <MetricCard
              title="Total Decisions (24h)"
              value={metrics?.total_decisions_24h || 0}
              icon={<Activity className="w-6 h-6" />}
              color="primary"
              subtitle="AI actions evaluated"
            />
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <MetricCard
              title="Approval Rate"
              value={`${metrics?.approval_rate?.toFixed(1) || 0}%`}
              icon={<CheckCircle className="w-6 h-6" />}
              color="success"
              subtitle="Actions approved"
            />
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <MetricCard
              title="Average Risk Score"
              value={metrics?.average_risk_score?.toFixed(1) || 0}
              icon={<TrendingUp className="w-6 h-6" />}
              color="warning"
              subtitle="Risk level (0-100)"
            />
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <MetricCard
              title="Pending Approvals"
              value={metrics?.pending_approval || 0}
              icon={<Clock className="w-6 h-6" />}
              color="info"
              subtitle="Awaiting human review"
            />
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts and Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk Distribution
                </Typography>
                <RiskChart />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Active Agents
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {metrics?.top_agents?.slice(0, 5).map((agent, index) => (
                    <Box key={agent.agent_id} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {agent.agent_id}
                        </Typography>
                        <Chip
                          label={agent.count}
                          size="small"
                          color={index === 0 ? 'primary' : 'default'}
                        />
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={(agent.count / (metrics?.top_agents?.[0]?.count || 1)) * 100}
                        sx={{ height: 4, borderRadius: 2 }}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <RecentDecisions />
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;