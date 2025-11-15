import { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Paper,
  Chip,
  Avatar,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Search,
  Description,
  Gavel,
  TrendingUp,
  AutoAwesome,
  ContentCopy,
  ThumbUp,
} from '@mui/icons-material';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const quickActions = [
  { label: 'Legal Research', icon: <Search />, prompt: 'Help me research case law on...' },
  { label: 'Draft Motion', icon: <Description />, prompt: 'Draft a motion for summary judgment for...' },
  { label: 'Analyze Contract', icon: <Gavel />, prompt: 'Analyze this contract and identify risks...' },
  { label: 'Case Prediction', icon: <TrendingUp />, prompt: 'Predict the outcome of my case...' },
];

const features = [
  {
    title: 'Legal Research',
    description: 'Search case law, statutes, and legal precedents instantly',
    icon: <Search />,
  },
  {
    title: 'Document Auto-Fill',
    description: 'Automatically populate documents with client and case data',
    icon: <Description />,
  },
  {
    title: 'Contract Analysis',
    description: 'AI-powered risk assessment and compliance checking',
    icon: <Gavel />,
  },
  {
    title: 'Case Prediction',
    description: 'Predict outcomes, timelines, and settlement values',
    icon: <TrendingUp />,
  },
];

export default function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI legal assistant. I can help you with legal research, document analysis, case predictions, and much more. How can I assist you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        role: 'assistant',
        content: `I understand you're asking about "${input}". Based on my analysis of relevant case law and legal precedents, here's what I found:\n\n1. **Key Legal Principles**: The primary legal framework governing this matter includes...\n\n2. **Relevant Case Law**: Several cases are particularly relevant:\n   - Smith v. Jones (2020): Established that...\n   - Brown v. Williams (2019): Held that...\n\n3. **Recommendations**: Based on this analysis, I recommend:\n   - Consider filing a motion for...\n   - Gather additional evidence on...\n   - Review the statute of limitations...\n\nWould you like me to elaborate on any of these points or help you draft specific documents?`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1500);
  };

  const handleQuickAction = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          🤖 AI Legal Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your revolutionary AI-powered legal research and analysis assistant
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Main Chat Interface */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: 'calc(100vh - 280px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 2 }}>
              <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
                <Tab label="Chat" />
                <Tab label="Legal Research" />
                <Tab label="Document Analysis" />
                <Tab label="Case Prediction" />
              </Tabs>
            </Box>

            {/* Messages */}
            <Box
              sx={{
                flex: 1,
                overflowY: 'auto',
                p: 3,
                bgcolor: '#f5f7fa',
              }}
            >
              {messages.map((message, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2,
                  }}
                >
                  {message.role === 'assistant' && (
                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                      <SmartToy />
                    </Avatar>
                  )}
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor: message.role === 'user' ? 'primary.main' : 'white',
                      color: message.role === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                      <Typography variant="caption" sx={{ opacity: 0.7 }}>
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                      {message.role === 'assistant' && (
                        <Box>
                          <IconButton size="small" sx={{ ml: 1 }}>
                            <ContentCopy fontSize="small" />
                          </IconButton>
                          <IconButton size="small">
                            <ThumbUp fontSize="small" />
                          </IconButton>
                        </Box>
                      )}
                    </Box>
                  </Paper>
                  {message.role === 'user' && (
                    <Avatar sx={{ bgcolor: 'secondary.main', ml: 2 }}>
                      <Person />
                    </Avatar>
                  )}
                </Box>
              ))}
            </Box>

            {/* Input */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                {quickActions.map((action, index) => (
                  <Chip
                    key={index}
                    label={action.label}
                    icon={action.icon}
                    onClick={() => handleQuickAction(action.prompt)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Ask me anything about your legal matters..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  multiline
                  maxRows={3}
                />
                <Button
                  variant="contained"
                  onClick={handleSend}
                  sx={{
                    minWidth: 100,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  }}
                  endIcon={<Send />}
                >
                  Send
                </Button>
              </Box>
            </Box>
          </Card>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                AI Capabilities
              </Typography>
              <List>
                {features.map((feature, index) => (
                  <Box key={index}>
                    <ListItem sx={{ px: 0 }}>
                      <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                        {feature.icon}
                      </Avatar>
                      <ListItemText
                        primary={feature.title}
                        secondary={feature.description}
                        primaryTypographyProps={{ fontWeight: 600 }}
                      />
                    </ListItem>
                    {index < features.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Recent Conversations
              </Typography>
              <List>
                {[
                  'Contract review for TechCorp merger',
                  'Research on employment law',
                  'Motion for summary judgment draft',
                  'Case outcome prediction',
                ].map((item, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      px: 0,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: '#f5f7fa' },
                      borderRadius: 1,
                    }}
                  >
                    <ListItemText
                      primary={item}
                      secondary={`${index + 1} hour${index > 0 ? 's' : ''} ago`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}