import { Typography, Box } from '@mui/material';

export default function ProgressTracking() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>
        Progress Tracking 📊
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Track project progress and milestones
      </Typography>
    </Box>
  );
}