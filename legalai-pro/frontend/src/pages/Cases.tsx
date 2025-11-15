import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { Add } from '@mui/icons-material';

export default function Cases() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Cases
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive case management with AI insights
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Add />}>
          New Case
        </Button>
      </Box>
      <Card>
        <CardContent>
          <Typography>Case management interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}