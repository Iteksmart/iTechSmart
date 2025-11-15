import { useState } from 'react';
import { Typography, Box, Paper, TextField, Button, List, ListItem, Avatar, Chip } from '@mui/material';
import { Send as SendIcon, SmartToy as AIIcon } from '@mui/icons-material';

export default function AIAgent() {
  const [message, setMessage] = useState('');

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={700}>
        SuperNinja AI Agent 🤖
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Your in-house AI assistant for code generation, app scaffolding, and more
      </Typography>

      <Paper sx={{ p: 3, mt: 3, height: 'calc(100vh - 300px)', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2 }}>
          <List>
            <ListItem>
              <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                <AIIcon />
              </Avatar>
              <Paper sx={{ p: 2, flexGrow: 1 }}>
                <Typography variant="body1">
                  Hello! I'm SuperNinja, your AI assistant. I can help you with:
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="Code Generation" size="small" />
                  <Chip label="App Scaffolding" size="small" />
                  <Chip label="Bug Fixing" size="small" />
                  <Chip label="Optimization" size="small" />
                  <Chip label="Documentation" size="small" />
                  <Chip label="Testing" size="small" />
                  <Chip label="Deployment" size="small" />
                </Box>
              </Paper>
            </ListItem>
          </List>
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Ask SuperNinja anything..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            multiline
            maxRows={3}
          />
          <Button variant="contained" endIcon={<SendIcon />}>
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}