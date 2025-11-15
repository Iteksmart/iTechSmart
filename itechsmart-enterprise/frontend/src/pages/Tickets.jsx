import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button
} from '@mui/material';
import axios from 'axios';

function Tickets() {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    axios.get('/api/tickets')
      .then(response => {
        setTickets(response.data);
      })
      .catch(error => {
        console.error('Error fetching tickets:', error);
      });
  }, []);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Tickets
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.map((ticket) => (
              <TableRow key={ticket.id}>
                <TableCell>{ticket.id}</TableCell>
                <TableCell>{ticket.title}</TableCell>
                <TableCell>
                  <Chip label={ticket.status} size="small" />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={ticket.priority} 
                    color={getPriorityColor(ticket.priority)}
                    size="small" 
                  />
                </TableCell>
                <TableCell>{new Date(ticket.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Button size="small">View</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default Tickets;