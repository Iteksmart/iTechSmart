import { Box, Typography, Card, CardContent } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

export default function Incidents() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Incident Management
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Automated incident creation, runbooks, and post-mortems
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <WarningIcon sx={{ fontSize: 80, color: 'warning.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Incident Tracking
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Track and resolve incidents with automated workflows
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}