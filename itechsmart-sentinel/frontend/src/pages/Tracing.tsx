import { Box, Typography, Card, CardContent } from '@mui/material';
import { Timeline as TimelineIcon } from '@mui/icons-material';

export default function Tracing() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Distributed Tracing
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Track requests across all services with OpenTelemetry support
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <TimelineIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Distributed Tracing
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View and analyze traces across your entire infrastructure
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}