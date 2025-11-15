import { Box, Typography, Card, CardContent } from '@mui/material';

export default function TimeTracking() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Time Tracking
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Accurate time tracking for billable hours
        </Typography>
      </Box>
      <Card>
        <CardContent>
          <Typography>Time tracking interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}