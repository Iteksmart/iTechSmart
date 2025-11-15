import { Typography, Box } from '@mui/material';

export default function Settings() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>
        Settings ⚙️
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Configure Think-Tank settings and integrations
      </Typography>
    </Box>
  );
}