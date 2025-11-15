import { Box, Typography, Card, CardContent } from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';

export default function Settings() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Settings
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure Sentinel settings and integrations
      </Typography>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <SettingsIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage system settings and preferences
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}