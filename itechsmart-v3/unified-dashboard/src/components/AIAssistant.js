import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Avatar,
  Fab,
  Slide,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Send,
  Mic,
  MicOff,
  SmartToy,
  Close,
  Code,
  Security,
  AttachMoney,
  Cloud,
  Settings,
  TrendingUp,
  Assessment,
  Speed,
  Build,
  Lock,
} from '@mui/material';
import { speechToText, textToSpeech } from '../services/speechService';

const Transition = React.forwardRef((props, ref) => (
  <Slide direction="up" ref={ref} {...props} />
));

const AIAssistant = ({ open, onClose, onCommand }) => {
  const theme = useTheme();
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [capabilities, setCapabilities] = useState([]);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (open) {
      initializeConversation();
      loadCapabilities();
      loadSuggestions();
    }
  }, [open]);

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const initializeConversation = () => {
    setConversation([
      {
        type: 'ai',
        message: '🤖 Hello! I\'m iTechSmart Ninja, your AI operations assistant. I can help you manage security, optimize costs, and orchestrate deployments across all iTechSmart products.',
        timestamp: new Date(),
        capabilities: [
          'Scale infrastructure globally',
          'Update security policies',
          'Analyze spending patterns',
          'Deploy applications',
          'Monitor system health',
          'Orchestrate workflows'
        ]
      }
    ]);
  };

  const loadCapabilities = () => {
    setCapabilities([
      {
        icon: <Cloud />,
        title: 'Infrastructure Management',
        description: 'Scale resources, manage deployments, optimize performance',
        commands: ['Scale up fleet in Asia', 'Deploy new version', 'Check system health']
      },
      {
        icon: <Security />,
        title: 'Security Operations',
        description: 'Update firewall rules, investigate threats, manage access',
        commands: ['Update firewall rules', 'Lock down compromised systems', 'Check security status']
      },
      {
        icon: <AttachMoney />,
        title: 'Financial Operations',
        description: 'Analyze costs, optimize spending, create budgets',
        commands: ['Analyze cloud costs', 'Find cost savings', 'Create spending report']
      },
      {
        icon: <Code />,
        title: 'DevOps Automation',
        description: 'Trigger deployments, manage pipelines, roll back changes',
        commands: ['Deploy to production', 'Rollback last deployment', 'Check pipeline status']
      },
      {
        icon: <Assessment />,
        title: 'Analytics & Monitoring',
        description: 'Generate reports, analyze trends, monitor metrics',
        commands: ['Generate performance report', 'Analyze user trends', 'Check system metrics']
      },
      {
        icon: <Settings />,
        title: 'System Configuration',
        description: 'Update settings, manage configurations, apply policies',
        commands: ['Update system settings', 'Apply new policies', 'Backup configurations']
      }
    ]);
  });

  const loadSuggestions = () => {
    setSuggestions([
      'Scale up the fleet in Asia and update the firewall rules',
      'Analyze recent cloud cost spikes and find the cause',
      'Deploy the latest version to production',
      'Check for any security threats in the last hour',
      'Generate a performance report for all services',
      'Optimize spending across all cloud providers'
    ]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage = {
      type: 'user',
      message: input,
      timestamp: new Date()
    };

    setConversation(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      // Process command through Neural Hub
      const result = await onCommand(input);
      
      const aiResponse = {
        type: 'ai',
        message: generateAIResponse(input, result),
        timestamp: new Date(),
        result: result,
        actions: result.actionsExecuted || []
      };

      setConversation(prev => [...prev, aiResponse]);
      
      // Update suggestions based on context
      updateSuggestions(input, result);

    } catch (error) {
      const errorResponse = {
        type: 'ai',
        message: `❌ I encountered an error: ${error.message}. Please try rephrasing your command.`,
        timestamp: new Date(),
        error: true
      };

      setConversation(prev => [...prev, errorResponse]);
    } finally {
      setIsProcessing(false);
    }
  };

  const generateAIResponse = (command, result) => {
    const actions = result.actionsExecuted || [];
    
    if (actions.length === 0) {
      return `I understand you want to "${command}". Let me process that request and execute the necessary actions across iTechSmart products.`;
    }

    let response = `✅ **Command Executed Successfully**\n\n`;
    response += `I've processed your request: "${command}"\n\n`;
    response += `**Actions Taken:**\n`;

    actions.forEach((action, index) => {
      response += `${index + 1}. ${action.product}: ${action.action}\n`;
    });

    response += `\n**Status:** All operations completed successfully`;
    response += `\n**Completed at:** ${new Date().toLocaleString()}`;

    return response;
  };

  const updateSuggestions = (command, result) => {
    // Context-aware suggestion updates
    const contextSuggestions = [];

    if (command.toLowerCase().includes('scale')) {
      contextSuggestions.push(
        'Monitor the scaled resources',
        'Set up alerts for the new instances',
        'Check cost impact of scaling'
      );
    }

    if (command.toLowerCase().includes('security')) {
      contextSuggestions.push(
        'Run full security scan',
        'Update all security policies',
        'Review security logs'
      );
    }

    if (command.toLowerCase().includes('cost')) {
      contextSuggestions.push(
        'Create cost optimization plan',
        'Set up budget alerts',
        'Analyze cost by service'
      );
    }

    if (contextSuggestions.length > 0) {
      setSuggestions(contextSuggestions.slice(0, 3));
    }
  };

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsListening(true);

      // Initialize speech recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          setIsListening(false);
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
        recognition.start();
      }
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          height: '80vh',
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.02)} 0%, ${alpha(theme.palette.secondary.main, 0.02)} 100%)`,
        }
      }}
      TransitionComponent={Transition}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
              <SmartToy />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight="bold">
                iTechSmart Ninja AI
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your AI Operations Assistant
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* Capabilities Overview */}
        {conversation.length === 1 && (
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>
              🚀 What I can do for you:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {capabilities.slice(0, 4).map((capability, index) => (
                <Chip
                  key={index}
                  icon={capability.icon}
                  label={capability.title}
                  variant="outlined"
                  size="small"
                  color="primary"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Conversation Area */}
        <Box flex={1} overflow="auto" mb={2}>
          <List>
            {conversation.map((msg, index) => (
              <ListItem
                key={index}
                sx={{
                  flexDirection: msg.type === 'user' ? 'row-reverse' : 'row',
                  mb: 1
                }}
              >
                <ListItemIcon>
                  <Avatar
                    sx={{
                      bgcolor: msg.type === 'user' ? 'secondary.main' : 'primary.main',
                      width: 32,
                      height: 32
                    }}
                  >
                    {msg.type === 'user' ? 'U' : <SmartToy />}
                  </Avatar>
                </ListItemIcon>
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: msg.type === 'user' ? 'grey.100' : 'primary.light',
                    color: msg.type === 'user' ? 'text.primary' : 'primary.contrastText'
                  }}
                >
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                    {msg.message}
                  </Typography>
                  
                  {msg.actions && msg.actions.length > 0 && (
                    <Box mt={1}>
                      <Typography variant="caption" fontWeight="bold">
                        Actions Executed:
                      </Typography>
                      {msg.actions.map((action, actionIndex) => (
                        <Box key={actionIndex} mt={0.5}>
                          <Chip
                            label={`${action.product}: ${action.action}`}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                        </Box>
                      ))}
                    </Box>
                  )}
                  
                  <Typography variant="caption" display="block" mt={1}>
                    {msg.timestamp.toLocaleTimeString()}
                  </Typography>
                </Paper>
              </ListItem>
            ))}
            {isProcessing && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <ListItemIcon>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                    <SmartToy />
                  </Avatar>
                </ListItemIcon>
                <Paper sx={{ p: 2, bgcolor: 'primary.light' }}>
                  <Box display="flex" alignItems="center">
                    <CircularProgress size={16} sx={{ mr: 1 }} />
                    <Typography variant="body2">Processing your command...</Typography>
                  </Box>
                </Paper>
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>
        </Box>

        {/* Suggestions */}
        {suggestions.length > 0 && conversation.length <= 2 && (
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>
              💡 Suggested commands:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {suggestions.map((suggestion, index) => (
                <Chip
                  key={index}
                  label={suggestion}
                  variant="outlined"
                  size="small"
                  clickable
                  onClick={() => handleSuggestionClick(suggestion)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Input Area */}
        <Box display="flex" gap={1} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={3}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me to scale infrastructure, update security, analyze costs, or deploy applications..."
            variant="outlined"
            disabled={isProcessing}
            InputProps={{
              startAdornment: (
                <Box position="absolute" top={8, left:8}>
                  <SmartToy color="action" />
                </Box>
              ),
              sx: { pl: 4 }
            }}
          />
          <IconButton
            onClick={isListening ? stopListening : startListening}
            color={isListening ? 'error' : 'primary'}
            disabled={isProcessing}
          >
            {isListening ? <MicOff /> : <Mic />}
          </IconButton>
          <Button
            variant="contained"
            onClick={handleSend}
            disabled={!input.trim() || isProcessing}
            startIcon={<Send />}
          >
            Send
          </Button>
        </Box>

        {/* Voice Status Indicator */}
        {isListening && (
          <Box mt={1} textAlign="center">
            <Chip
              icon={<Mic />}
              label="Listening... Speak now"
              color="error"
              variant="outlined"
              size="small"
            />
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default AIAssistant;