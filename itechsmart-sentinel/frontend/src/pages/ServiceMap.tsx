import { Box, Typography, Card, CardContent } from '@mui/material';
import { AccountTree as AccountTreeIcon } from '@mui/icons-material';

export default function ServiceMap() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Service Map
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Visualize service dependencies and communication patterns
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <AccountTreeIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Service Topology
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View service dependencies and data flow
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}