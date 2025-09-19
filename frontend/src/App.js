import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Paper,
  Chip,
  Alert,
} from '@mui/material';
import { TrendingUp, Database, MessageSquare, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';

// Import components
import FileUpload from './components/FileUpload';
import StockAnalysis from './components/StockAnalysis';
import ChatInterface from './components/ChatInterface';
import MarketOverview from './components/MarketOverview';
import RAGDashboard from './components/RAGDashboard';

// Import API service
import apiService from './services/apiService';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await apiService.getHealth();
      setSystemStatus(health);
      
      if (health.api_status === 'healthy') {
        toast.success('System initialized successfully!');
      } else {
        toast.error('System health check failed');
      }
    } catch (error) {
      console.error('Health check failed:', error);
      toast.error('Failed to connect to backend service');
      setSystemStatus({
        api_status: 'error',
        groq_client: false,
        rag_pipeline: false,
        agentic_rag: false
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status) => {
    if (status === 'healthy' || status === true) return 'success';
    if (status === 'error' || status === false) return 'error';
    return 'warning';
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        flexDirection="column"
      >
        <div className="loading-spinner" />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Initializing Equity Research Assistant...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <TrendingUp style={{ marginRight: '12px' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Equity Research Assistant
          </Typography>
          
          {/* Status indicators */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`API: ${systemStatus?.api_status || 'Unknown'}`}
              color={getStatusColor(systemStatus?.api_status)}
              size="small"
            />
            {systemStatus?.agentic_rag && (
              <Chip
                label="Agentic RAG"
                color="success"
                size="small"
              />
            )}
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        {/* System Status Alert */}
        {systemStatus?.api_status !== 'healthy' && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            System is running with limited functionality. Some features may not be available.
          </Alert>
        )}

        <Paper elevation={0} sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              aria-label="research assistant tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab
                icon={<BarChart3 size={20} />}
                label="Market Overview"
                iconPosition="start"
              />
              <Tab
                icon={<TrendingUp size={20} />}
                label="File Upload & Analysis"
                iconPosition="start"
              />
              <Tab
                icon={<Database size={20} />}
                label="Stock Analysis"
                iconPosition="start"
              />
              <Tab
                icon={<MessageSquare size={20} />}
                label="AI Assistant"
                iconPosition="start"
              />
              <Tab
                icon={<Database size={20} />}
                label="RAG Knowledge Base"
                iconPosition="start"
              />
            </Tabs>
          </Box>

          <TabPanel value={activeTab} index={0}>
            <MarketOverview />
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <FileUpload />
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <StockAnalysis />
          </TabPanel>

          <TabPanel value={activeTab} index={3}>
            <ChatInterface 
              agenticAvailable={systemStatus?.agentic_rag || false}
            />
          </TabPanel>

          <TabPanel value={activeTab} index={4}>
            <RAGDashboard 
              ragAvailable={systemStatus?.rag_pipeline || false}
            />
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;
