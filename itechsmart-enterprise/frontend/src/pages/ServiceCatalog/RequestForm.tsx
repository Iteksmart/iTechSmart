import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Divider
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';

interface FormField {
  name: string;
  label: string;
  type: string;
  required: boolean;
  options?: string[];
}

interface ServiceItem {
  id: number;
  name: string;
  description: string;
  category: string;
  icon: string;
  form_schema: {
    fields: FormField[];
  };
  sla_hours: number;
  requires_approval: boolean;
  automation_enabled: boolean;
  ai_assisted: boolean;
  approval_workflow?: any[];
}

const RequestForm: React.FC = () => {
  const navigate = useNavigate();
  const { serviceId } = useParams<{ serviceId: string }>();
  const [serviceItem, setServiceItem] = useState<ServiceItem | null>(null);
  const [formData, setFormData] = useState<{ [key: string]: any }>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [requestNumber, setRequestNumber] = useState<string>('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    loadServiceItem();
  }, [serviceId]);

  const loadServiceItem = async () => {
    try {
      const response = await fetch(`/api/service-catalog/items/${serviceId}`);
      const data = await response.json();
      setServiceItem(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading service item:', error);
      setLoading(false);
    }
  };

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    // Clear error for this field
    if (errors[fieldName]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    
    serviceItem?.form_schema.fields.forEach(field => {
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    setSubmitting(true);
    
    try {
      const response = await fetch('/api/service-catalog/requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          service_item_id: parseInt(serviceId!),
          form_data: formData
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setRequestNumber(data.request_number);
        setSubmitted(true);
      } else {
        alert('Error submitting request: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error submitting request:', error);
      alert('Error submitting request');
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (field: FormField) => {
    const value = formData[field.name] || '';
    const error = errors[field.name];

    switch (field.type) {
      case 'text':
      case 'email':
        return (
          <TextField
            fullWidth
            label={field.label}
            type={field.type}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
            error={!!error}
            helperText={error}
          />
        );
      
      case 'textarea':
        return (
          <TextField
            fullWidth
            label={field.label}
            multiline
            rows={4}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
            error={!!error}
            helperText={error}
          />
        );
      
      case 'select':
        return (
          <FormControl fullWidth error={!!error}>
            <InputLabel>{field.label}</InputLabel>
            <Select
              value={value}
              label={field.label}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              required={field.required}
            >
              {field.options?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            {error && (
              <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                {error}
              </Typography>
            )}
          </FormControl>
        );
      
      case 'number':
        return (
          <TextField
            fullWidth
            label={field.label}
            type="number"
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
            error={!!error}
            helperText={error}
          />
        );
      
      case 'date':
        return (
          <TextField
            fullWidth
            label={field.label}
            type="date"
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
            error={!!error}
            helperText={error}
            InputLabelProps={{ shrink: true }}
          />
        );
      
      case 'datetime':
        return (
          <TextField
            fullWidth
            label={field.label}
            type="datetime-local"
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
            error={!!error}
            helperText={error}
            InputLabelProps={{ shrink: true }}
          />
        );
      
      default:
        return (
          <TextField
            fullWidth
            label={field.label}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            required={field.required}
            error={!!error}
            helperText={error}
          />
        );
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!serviceItem) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error">Service item not found</Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/service-catalog')}
          sx={{ mt: 2 }}
        >
          Back to Catalog
        </Button>
      </Container>
    );
  }

  if (submitted) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom fontWeight="bold" color="success.main">
            Request Submitted Successfully!
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Request Number: <strong>{requestNumber}</strong>
          </Typography>
          
          <Box mt={4} p={3} sx={{ backgroundColor: '#f5f5f5', borderRadius: 2 }}>
            <Typography variant="body1" gutterBottom>
              <strong>What happens next?</strong>
            </Typography>
            
            {serviceItem.requires_approval ? (
              <>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Your request will go through the following approval steps:
                </Typography>
                <Stepper orientation="vertical" sx={{ mt: 2 }}>
                  {serviceItem.approval_workflow?.map((step, index) => (
                    <Step key={index} active>
                      <StepLabel>{step.name}</StepLabel>
                    </Step>
                  ))}
                  <Step active>
                    <StepLabel>Automated Fulfillment</StepLabel>
                  </Step>
                </Stepper>
              </>
            ) : (
              <>
                {serviceItem.automation_enabled ? (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Your request is being processed automatically. You'll receive a notification when complete.
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Your request has been assigned to the fulfillment team. You'll receive updates via email.
                  </Typography>
                )}
              </>
            )}
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              ⏱️ Expected completion: <strong>{serviceItem.sla_hours} hours</strong>
            </Typography>
          </Box>

          <Box mt={4} display="flex" gap={2} justifyContent="center">
            <Button
              variant="outlined"
              onClick={() => navigate('/service-catalog')}
            >
              Back to Catalog
            </Button>
            <Button
              variant="contained"
              onClick={() => navigate('/service-catalog/my-requests')}
            >
              View My Requests
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/service-catalog')}
        sx={{ mb: 3 }}
      >
        Back to Catalog
      </Button>

      {/* Service Info */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: 2,
              backgroundColor: `${categoryColors[serviceItem.category]}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2.5rem',
              mr: 2
            }}
          >
            {serviceItem.icon}
          </Box>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              {serviceItem.name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {serviceItem.description}
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1} mt={2}>
          {serviceItem.automation_enabled && (
            <Chip label="⚡ Auto-Fulfill" color="success" size="small" />
          )}
          {serviceItem.ai_assisted && (
            <Chip label="🤖 AI-Assisted" color="primary" size="small" />
          )}
          {serviceItem.requires_approval && (
            <Chip label="✓ Approval Required" color="warning" size="small" />
          )}
          <Chip label={`⏱️ SLA: ${serviceItem.sla_hours}h`} size="small" />
        </Box>
      </Paper>

      {/* Request Form */}
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Request Details
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          {serviceItem.form_schema.fields.map((field) => (
            <Grid item xs={12} key={field.name}>
              {renderField(field)}
            </Grid>
          ))}
        </Grid>

        {/* Approval Workflow Info */}
        {serviceItem.requires_approval && serviceItem.approval_workflow && (
          <Box mt={4} p={2} sx={{ backgroundColor: '#fff3e0', borderRadius: 2 }}>
            <Typography variant="subtitle2" gutterBottom fontWeight="bold">
              📋 Approval Workflow
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This request will require approval from:
            </Typography>
            <Box mt={1}>
              {serviceItem.approval_workflow.map((step, index) => (
                <Chip
                  key={index}
                  label={step.name}
                  size="small"
                  sx={{ mr: 1, mt: 1 }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* AI Assistance Info */}
        {serviceItem.ai_assisted && (
          <Alert severity="info" sx={{ mt: 3 }}>
            <strong>🤖 AI-Assisted Fulfillment:</strong> This request will be processed with AI assistance 
            for faster and more accurate fulfillment.
          </Alert>
        )}

        {/* Submit Button */}
        <Box mt={4} display="flex" gap={2}>
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate('/service-catalog')}
            disabled={submitting}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            size="large"
            endIcon={submitting ? <CircularProgress size={20} /> : <SendIcon />}
            onClick={handleSubmit}
            disabled={submitting}
            fullWidth
          >
            {submitting ? 'Submitting...' : 'Submit Request'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default RequestForm;