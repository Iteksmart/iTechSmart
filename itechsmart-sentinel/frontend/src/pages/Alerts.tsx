import { Box, Typography, Card, CardContent } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';

export default function Alerts() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Smart Alerting
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        ML-based alert fatigue reduction and intelligent routing
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <NotificationsIcon sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Alert Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and respond to alerts with smart routing
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}