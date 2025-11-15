import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

export default function Datasets() {
  const [datasets] = useState([
    { id: 1, name: 'Customer Data 2024', size: '2.3 GB', rows: 1250000, columns: 45, format: 'CSV', uploaded: '2024-01-10' },
    { id: 2, name: 'Sales History', size: '890 MB', rows: 450000, columns: 28, format: 'Parquet', uploaded: '2024-01-08' },
    { id: 3, name: 'Product Images', size: '15.2 GB', rows: 85000, columns: 1, format: 'Images', uploaded: '2024-01-05' },
    { id: 4, name: 'Transaction Logs', size: '5.7 GB', rows: 3200000, columns: 32, format: 'JSON', uploaded: '2024-01-03' },
    { id: 5, name: 'User Reviews', size: '450 MB', rows: 125000, columns: 8, format: 'CSV', uploaded: '2024-01-01' },
  ]);

  const getFormatColor = (format: string) => {
    switch (format) {
      case 'CSV':
        return 'primary';
      case 'Parquet':
        return 'success';
      case 'JSON':
        return 'warning';
      case 'Images':
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" gutterBottom>
            Datasets
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage training and validation datasets
          </Typography>
        </div>
        <Button variant="contained" startIcon={<UploadIcon />}>
          Upload Dataset
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Dataset Name</TableCell>
              <TableCell>Format</TableCell>
              <TableCell align="right">Size</TableCell>
              <TableCell align="right">Rows</TableCell>
              <TableCell align="right">Columns</TableCell>
              <TableCell>Uploaded</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {datasets.map((dataset) => (
              <TableRow key={dataset.id} hover>
                <TableCell>
                  <Typography variant="body1" fontWeight="medium">
                    {dataset.name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={dataset.format}
                    color={getFormatColor(dataset.format) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">{dataset.size}</TableCell>
                <TableCell align="right">{dataset.rows.toLocaleString()}</TableCell>
                <TableCell align="right">{dataset.columns}</TableCell>
                <TableCell>{dataset.uploaded}</TableCell>
                <TableCell align="right">
                  <IconButton size="small" color="primary">
                    <DownloadIcon />
                  </IconButton>
                  <IconButton size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}