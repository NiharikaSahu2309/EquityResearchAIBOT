import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Chip,
  Alert,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { Send, Search, ExpandMore, Psychology } from '@mui/icons-material';
import toast from 'react-hot-toast';

import apiService from '../services/apiService';

const ChatInterface = ({ agenticAvailable = false }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI-powered financial research assistant. I can help you analyze financial data, answer questions about uploaded documents, and provide insights using advanced agentic reasoning. How can I assist you today?',
      metadata: { mode: 'welcome' }
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatMode, setChatMode] = useState(agenticAvailable ? 'agentic' : 'standard');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: currentMessage,
      metadata: { mode: chatMode }
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const response = await apiService.sendChatMessage(currentMessage, chatMode);
      
      if (response.success) {
        const assistantMessage = {
          role: 'assistant',
          content: response.message,
          metadata: response.metadata || { mode: chatMode }
        };
        setMessages(prev => [...prev, assistantMessage]);
        
        // Show confidence score for agentic responses
        if (response.metadata?.confidence && chatMode === 'agentic') {
          const confidence = Math.round(response.metadata.confidence * 100);
          toast.success(`Response generated with ${confidence}% confidence`);
        }
      } else {
        throw new Error(response.error || 'Chat service unavailable');
      }
    } catch (error) {
      console.error('Chat error:', error);
      
      let errorMsg = 'Failed to get response';
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMsg = `Request timed out. ${chatMode === 'agentic' ? 'Agentic analysis can take time - try a simpler question or switch to standard mode.' : 'Please try again or contact support.'}`;
      } else if (error.response?.status === 500) {
        errorMsg = 'Server error occurred. Please try again.';
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      const errorMessage = {
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${errorMsg}`,
        metadata: { mode: 'error', error: true }
      };
      setMessages(prev => [...prev, errorMessage]);
      
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        toast.error('Request timed out - try a simpler question');
      } else {
        toast.error('Failed to get response');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Chat cleared. How can I help you with your financial research?',
        metadata: { mode: 'system' }
      }
    ]);
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    const isError = message.metadata?.error;
    const mode = message.metadata?.mode;

    return (
      <Box
        key={index}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Paper
          sx={{
            p: 2,
            maxWidth: '80%',
            bgcolor: isError
              ? 'error.light'
              : isUser
              ? 'primary.main'
              : 'background.paper',
            color: isError
              ? 'error.contrastText'
              : isUser
              ? 'primary.contrastText'
              : 'text.primary',
            borderRadius: 2,
          }}
        >
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {message.content}
          </Typography>
          
          {/* Message metadata */}
          {message.metadata && (mode === 'agentic' || mode === 'search') && (
            <Box sx={{ mt: 1 }}>
              <Chip
                label={mode === 'agentic' ? 'Agentic AI' : 'Document Search'}
                size="small"
                color={mode === 'agentic' ? 'secondary' : 'info'}
                icon={mode === 'agentic' ? <Psychology /> : <Search />}
              />
              
              {message.metadata.confidence && (
                <Chip
                  label={`${Math.round(message.metadata.confidence * 100)}% confidence`}
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
            </Box>
          )}

          {/* Agentic analysis details */}
          {message.metadata?.plan && message.metadata.plan.length > 0 && (
            <Accordion sx={{ mt: 2, bgcolor: 'rgba(255,255,255,0.1)' }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle2">Analysis Plan</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box component="ol" sx={{ pl: 2 }}>
                  {message.metadata.plan.map((step, i) => (
                    <Typography component="li" key={i} variant="body2">
                      {typeof step === 'string' ? step : `${step.description || step.tool || `Step ${i + 1}`}`}
                    </Typography>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Agentic reasoning steps */}
          {message.metadata?.intermediate_results && Object.keys(message.metadata.intermediate_results).length > 0 && (
            <Accordion sx={{ mt: 2, bgcolor: 'rgba(255,255,255,0.1)' }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle2">Reasoning Steps</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ pl: 2 }}>
                  {Object.entries(message.metadata.intermediate_results).map(([stepKey, stepResult], i) => (
                    <Box key={i} sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {typeof stepResult === 'object' && stepResult.step_description 
                          ? stepResult.step_description 
                          : `Step ${i + 1}: ${stepKey}`
                        }
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {typeof stepResult === 'object' && stepResult.result 
                          ? stepResult.result 
                          : typeof stepResult === 'string' 
                          ? stepResult 
                          : 'Step completed'
                        }
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Sources */}
          {message.metadata?.sources && message.metadata.sources.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Sources: {message.metadata.sources.join(', ')}
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI Financial Assistant
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Ask questions about your uploaded documents, request financial analysis, 
        or get market insights using our advanced AI assistant.
      </Typography>

      {/* Chat Mode Selector */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <FormControl fullWidth>
          <InputLabel>Chat Mode</InputLabel>
          <Select
            value={chatMode}
            onChange={(e) => setChatMode(e.target.value)}
            label="Chat Mode"
          >
            <MenuItem value="standard">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Send />
                Standard Chat
              </Box>
            </MenuItem>
            {agenticAvailable && (
              <MenuItem value="agentic">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Psychology />
                  Agentic AI (Advanced Reasoning)
                </Box>
              </MenuItem>
            )}
            <MenuItem value="search">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Search />
                Document Search
              </Box>
            </MenuItem>
          </Select>
        </FormControl>
        
        {chatMode === 'agentic' && (
          <Alert severity="info" sx={{ mt: 1 }}>
            Agentic mode uses advanced multi-step reasoning for more precise financial analysis.
          </Alert>
        )}
        
        {chatMode === 'search' && (
          <Alert severity="info" sx={{ mt: 1 }}>
            Search mode will find relevant information from your uploaded documents.
          </Alert>
        )}
      </Paper>

      {/* Chat Messages */}
      <Paper sx={{ height: 400, overflow: 'auto', p: 2, mb: 2 }} className="chat-container">
        {messages.map((message, index) => renderMessage(message, index))}
        
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
            <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  {chatMode === 'agentic' 
                    ? 'Analyzing with AI reasoning... (This may take up to 2 minutes)' 
                    : chatMode === 'search'
                    ? 'Searching documents...'
                    : 'Thinking...'
                  }
                </Typography>
              </Box>
              {chatMode === 'agentic' && (
                <Typography variant="caption" color="text.disabled" sx={{ mt: 1, display: 'block' }}>
                  The AI is planning, analyzing, and synthesizing a comprehensive response
                </Typography>
              )}
            </Paper>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Paper>

      {/* Message Input */}
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          variant="outlined"
          placeholder={
            chatMode === 'agentic'
              ? 'Ask for detailed financial analysis...'
              : chatMode === 'search'
              ? 'Search your uploaded documents...'
              : 'Type your message...'
          }
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <IconButton
          color="primary"
          onClick={handleSendMessage}
          disabled={loading || !currentMessage.trim()}
          sx={{ height: 56 }}
        >
          <Send />
        </IconButton>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button size="small" onClick={handleClearChat}>
          Clear Chat
        </Button>
        <Chip
          label="Sample: What are the key financial trends?"
          onClick={() => setCurrentMessage('What are the key financial trends in my uploaded data?')}
          clickable
          size="small"
        />
        <Chip
          label="Sample: Analyze market performance"
          onClick={() => setCurrentMessage('Can you analyze the market performance based on my data?')}
          clickable
          size="small"
        />
      </Box>
    </Box>
  );
};

export default ChatInterface;
