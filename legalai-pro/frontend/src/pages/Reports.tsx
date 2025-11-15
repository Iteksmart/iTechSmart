import { Box, Typography, Card, CardContent } from '@mui/material';

export default function Reports() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Reports & Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive insights into your practice
        </Typography>
      </Box>
      <Card>
        <CardContent>
          <Typography>Reports interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}