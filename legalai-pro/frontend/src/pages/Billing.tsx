import { Box, Typography, Card, CardContent } from '@mui/material';

export default function Billing() {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Billing & Invoicing
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Streamlined billing with automated time tracking
        </Typography>
      </Box>
      <Card>
        <CardContent>
          <Typography>Billing interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}