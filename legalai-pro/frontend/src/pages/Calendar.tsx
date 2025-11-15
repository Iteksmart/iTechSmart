import { Box, Typography, Card, CardContent } from '@mui/material';

export default function Calendar() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Calendar & Docketing
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Never miss a deadline with intelligent calendar management
        </Typography>
      </Box>
      <Card>
        <CardContent>
          <Typography>Calendar interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}