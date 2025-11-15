import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { Upload } from '@mui/icons-material';

export default function Documents() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered document management with auto-fill templates
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Upload />}>
          Upload Document
        </Button>
      </Box>
      <Card>
        <CardContent>
          <Typography>Document management interface coming soon...</Typography>
        </CardContent>
      </Card>
    </Box>
  );
}