import { Box, Typography, Card, CardContent } from '@mui/material';
import { Description as DescriptionIcon } from '@mui/icons-material';

export default function Logs() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Log Aggregation
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Centralized logs with natural language search and anomaly detection
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <DescriptionIcon sx={{ fontSize: 80, color: 'info.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Log Search & Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Search and analyze logs from all services
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}