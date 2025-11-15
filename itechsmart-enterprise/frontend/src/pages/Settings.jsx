import React from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  TextField,
  Button,
  Divider
} from '@mui/material';

function Settings() {
  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Account Settings
        </Typography>
        <Box component="form" sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Email"
            defaultValue="admin@itechsmart.dev"
            margin="normal"
          />
          <TextField
            fullWidth
            label="Name"
            defaultValue="Admin User"
            margin="normal"
          />
          <Button variant="contained" sx={{ mt: 2 }}>
            Save Changes
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Change Password
        </Typography>
        <Box component="form" sx={{ mt: 2 }}>
          <TextField
            fullWidth
            type="password"
            label="Current Password"
            margin="normal"
          />
          <TextField
            fullWidth
            type="password"
            label="New Password"
            margin="normal"
          />
          <TextField
            fullWidth
            type="password"
            label="Confirm New Password"
            margin="normal"
          />
          <Button variant="contained" sx={{ mt: 2 }}>
            Update Password
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          System Information
        </Typography>
        <Divider sx={{ my: 2 }} />
        <Typography variant="body2" paragraph>
          <strong>Version:</strong> 1.0.0
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>Environment:</strong> Production
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>API Status:</strong> Healthy
        </Typography>
      </Paper>
    </Container>
  );
}

export default Settings;