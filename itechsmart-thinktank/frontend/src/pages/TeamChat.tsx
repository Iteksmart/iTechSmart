import { Typography, Box, Paper } from '@mui/material';

export default function TeamChat() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>
        Team Chat 💬
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Real-time collaboration with your team and external clients
      </Typography>

      <Paper sx={{ p: 3, mt: 3, height: 'calc(100vh - 300px)' }}>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 10 }}>
          Real-time chat interface with WebSocket support
        </Typography>
      </Paper>
    </Box>
  );
}