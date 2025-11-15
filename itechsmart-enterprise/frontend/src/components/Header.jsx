import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { useNavigate } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';

function Header() {
  const navigate = useNavigate();

  return (
    <AppBar position="static">
      <Toolbar>
        <DashboardIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          iTechSmart Enterprise
        </Typography>
        <Button color="inherit" onClick={() => navigate('/')}>
          Dashboard
        </Button>
        <Button color="inherit" onClick={() => navigate('/tickets')}>
          Tickets
        </Button>
        <Button color="inherit" onClick={() => navigate('/integrations')}>
          Integrations
        </Button>
        <Button color="inherit" onClick={() => navigate('/settings')}>
          Settings
        </Button>
      </Toolbar>
    </AppBar>
  );
}

export default Header;