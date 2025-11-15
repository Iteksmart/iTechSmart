import { Typography, Box } from '@mui/material';

export default function IdeaBoard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>
        Idea Board 💡
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Brainstorm and collaborate on new app ideas
      </Typography>
    </Box>
  );
}