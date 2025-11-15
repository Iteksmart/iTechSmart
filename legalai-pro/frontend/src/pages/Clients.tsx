import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { Add } from '@mui/icons-material';

export default function Clients() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Clients
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your client database with AI-powered auto-fill
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Add />}>
          Add Client
        </Button>
      </Box>
      <Card>
        <CardContent>
          <Typography>Client management interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}