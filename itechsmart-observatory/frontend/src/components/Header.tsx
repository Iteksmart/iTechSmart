import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { Visibility } from '@mui/icons-material';

const Header: React.FC = () => {
  return (
    <AppBar position="static" color="primary" elevation={2}>
      <Toolbar>
        <Visibility sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          iTechSmart Observatory
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button color="inherit" component={RouterLink} to="/observatory">
            Dashboard
          </Button>
          <Button color="inherit" component={RouterLink} to="/observatory/metrics">
            Metrics
          </Button>
          <Button color="inherit" component={RouterLink} to="/observatory/traces">
            Traces
          </Button>
          <Button color="inherit" component={RouterLink} to="/observatory/logs">
            Logs
          </Button>
          <Button color="inherit" component={RouterLink} to="/observatory/alerts">
            Alerts
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;