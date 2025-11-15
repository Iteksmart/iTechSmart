import { Box, Typography, Card, CardContent } from '@mui/material';
import { Speed as SpeedIcon } from '@mui/icons-material';

export default function SLO() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        SLO Tracking
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Service Level Objectives with error budgets and burn rate alerts
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <SpeedIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            SLO Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Track and manage Service Level Objectives
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}