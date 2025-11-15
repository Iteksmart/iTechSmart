import { Typography, Box } from '@mui/material';

export default function ClientPortal() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>
        Client Portal 👥
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Invite external clients to view project progress
      </Typography>
    </Box>
  );
}