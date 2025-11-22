import React, { useState, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const SortableItem = ({ id, component, onEdit, onDelete }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Card sx={{ mb: 2, cursor: 'move' }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{component.name}</Typography>
            <Box>
              <Button size="small" onClick={() => onEdit(id)}>Edit</Button>
              <Button size="small" color="error" onClick={() => onDelete(id)}>
                Delete
              </Button>
            </Box>
          </Box>
          <Typography variant="body2" color="textSecondary">
            {component.type} - {component.description}
          </Typography>
        </CardContent>
      </Card>
    </div>
  );
};

const PortalBuilder = () => {
  const [portalName, setPortalName] = useState('');
  const [portalType, setPortalType] = useState('');
  const [components, setComponents] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingComponent, setEditingComponent] = useState(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const componentLibrary = [
    { id: 'header', name: 'Header', type: 'layout', description: 'Website header with navigation' },
    { id: 'hero', name: 'Hero Section', type: 'content', description: 'Main hero banner' },
    { id: 'content', name: 'Content Block', type: 'content', description: 'Text and image content' },
    { id: 'features', name: 'Features Grid', type: 'content', description: 'Feature showcase' },
    { id: 'testimonials', name: 'Testimonials', type: 'social', description: 'Customer testimonials' },
    { id: 'pricing', name: 'Pricing Table', type: 'content', description: 'Pricing plans' },
    { id: 'contact', name: 'Contact Form', type: 'form', description: 'Contact information form' },
    { id: 'footer', name: 'Footer', type: 'layout', description: 'Website footer' },
  ];

  const templates = [
    { id: 'corporate', name: 'Corporate Website', description: 'Professional business website' },
    { id: 'saas', name: 'SaaS Product', description: 'Software as a Service landing page' },
    { id: 'ecommerce', name: 'E-commerce', description: 'Online store front' },
    { id: 'portfolio', name: 'Portfolio', description: 'Creative portfolio showcase' },
    { id: 'blog', name: 'Blog', description: 'Content blog platform' },
  ];

  const handleAddComponent = (componentTemplate) => {
    const newComponent = {
      ...componentTemplate,
      id: `${componentTemplate.id}_${Date.now()}`,
      content: getDefaultContent(componentTemplate.id),
    };
    setComponents([...components, newComponent]);
  };

  const getDefaultContent = (componentId) => {
    const defaults = {
      header: { logo: 'Your Logo', menuItems: ['Home', 'About', 'Services', 'Contact'] },
      hero: { title: 'Welcome to Your Portal', subtitle: 'Build amazing experiences', cta: 'Get Started' },
      content: { heading: 'About Us', text: 'Your content goes here...', image: '' },
      features: { title: 'Our Features', items: ['Feature 1', 'Feature 2', 'Feature 3'] },
      testimonials: { title: 'What Our Customers Say', testimonials: [] },
      pricing: { title: 'Pricing Plans', plans: [] },
      contact: { title: 'Contact Us', fields: ['name', 'email', 'message'] },
      footer: { text: '© 2024 Your Company. All rights reserved.' },
    };
    return defaults[componentId] || {};
  };

  const handleEditComponent = (componentId) => {
    const component = components.find(c => c.id === componentId);
    setEditingComponent(component);
    setEditDialogOpen(true);
  };

  const handleDeleteComponent = (componentId) => {
    setComponents(components.filter(c => c.id !== componentId));
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      setComponents((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);

        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleSaveEdit = () => {
    if (editingComponent) {
      setComponents(components.map(c => 
        c.id === editingComponent.id ? editingComponent : c
      ));
      setEditDialogOpen(false);
      setEditingComponent(null);
    }
  };

  const handlePreview = () => {
    // Generate preview logic
    console.log('Generating preview for portal:', portalName);
    console.log('Components:', components);
  };

  const handleDeploy = async () => {
    try {
      const response = await fetch('/api/portals/deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: portalName,
          type: portalType,
          components,
          template: selectedTemplate,
        }),
      });
      const result = await response.json();
      console.log('Deployment result:', result);
    } catch (error) {
      console.error('Deployment failed:', error);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Portal Builder - Build Amazing Web Experiences
      </Typography>
      
      <Grid container spacing={3}>
        {/* Portal Configuration */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Portal Configuration
            </Typography>
            <TextField
              fullWidth
              label="Portal Name"
              value={portalName}
              onChange={(e) => setPortalName(e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Portal Type</InputLabel>
              <Select
                value={portalType}
                onChange={(e) => setPortalType(e.target.value)}
              >
                <MenuItem value="corporate">Corporate Website</MenuItem>
                <MenuItem value="customer">Customer Portal</MenuItem>
                <MenuItem value="partner">Partner Extranet</MenuItem>
                <MenuItem value="ecommerce">E-commerce</MenuItem>
                <MenuItem value="microsite">Microsite</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Template</InputLabel>
              <Select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
              >
                {templates.map((template) => (
                  <MenuItem key={template.id} value={template.id}>
                    {template.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                onClick={handlePreview}
                sx={{ mr: 1 }}
                disabled={!portalName || components.length === 0}
              >
                Preview
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleDeploy}
                disabled={!portalName || components.length === 0}
              >
                Deploy
              </Button>
            </Box>
          </Paper>

          {/* Component Library */}
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Component Library
            </Typography>
            {componentLibrary.map((component) => (
              <Button
                key={component.id}
                variant="outlined"
                fullWidth
                sx={{ mb: 1, textTransform: 'none' }}
                onClick={() => handleAddComponent(component)}
              >
                <Box>
                  <Typography variant="subtitle2">{component.name}</Typography>
                  <Typography variant="caption" display="block">
                    {component.description}
                  </Typography>
                </Box>
              </Button>
            ))}
          </Paper>
        </Grid>

        {/* Canvas Area */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, minHeight: 600 }}>
            <Typography variant="h6" gutterBottom>
              Portal Canvas
            </Typography>
            {components.length === 0 ? (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight={400}
                border="2px dashed"
                borderColor="grey.300"
                borderRadius={2}
              >
                <Typography variant="h6" color="textSecondary">
                  Drag and drop components here to start building your portal
                </Typography>
              </Box>
            ) : (
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
              >
                <SortableContext
                  items={components.map(c => c.id)}
                  strategy={verticalListSortingStrategy}
                >
                  {components.map((component) => (
                    <SortableItem
                      key={component.id}
                      id={component.id}
                      component={component}
                      onEdit={handleEditComponent}
                      onDelete={handleDeleteComponent}
                    />
                  ))}
                </SortableContext>
              </DndContext>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Component</DialogTitle>
        <DialogContent>
          {editingComponent && (
            <Box>
              <TextField
                fullWidth
                label="Component Name"
                value={editingComponent.name}
                onChange={(e) => setEditingComponent({
                  ...editingComponent,
                  name: e.target.value
                })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Description"
                value={editingComponent.description}
                onChange={(e) => setEditingComponent({
                  ...editingComponent,
                  description: e.target.value
                })}
                multiline
                rows={4}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Content (JSON)"
                value={JSON.stringify(editingComponent.content, null, 2)}
                onChange={(e) => {
                  try {
                    const content = JSON.parse(e.target.value);
                    setEditingComponent({
                      ...editingComponent,
                      content
                    });
                  } catch (err) {
                    // Invalid JSON, don't update
                  }
                }}
                multiline
                rows={8}
                sx={{ fontFamily: 'monospace' }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PortalBuilder;