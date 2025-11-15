import { Typography, Box, Button, Grid, Card, CardContent, Chip } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

export default function Projects() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom fontWeight={700}>
            Projects
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage all custom app projects
          </Typography>
        </div>
        <Button variant="contained" startIcon={<AddIcon />}>
          New Project
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Grid item xs={12} md={6} lg={4} key={i}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Project {i}
                </Typography>
                <Chip label="In Progress" color="primary" size="small" />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}