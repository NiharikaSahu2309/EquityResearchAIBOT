import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search,
  Delete,
  ExpandMore,
  Storage,
  Description,
  Info,
} from '@mui/icons-material';
import toast from 'react-hot-toast';

import apiService from '../services/apiService';

const RAGDashboard = ({ ragAvailable = false }) => {
  const [ragStats, setRagStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [clearDialogOpen, setClearDialogOpen] = useState(false);

  useEffect(() => {
    if (ragAvailable) {
      fetchRAGStats();
    }
  }, [ragAvailable]);

  const fetchRAGStats = async () => {
    setLoading(true);
    try {
      const stats = await apiService.getRAGStats();
      if (!stats.error) {
        setRagStats(stats);
      } else {
        console.warn('RAG stats error:', stats.error);
      }
    } catch (error) {
      console.error('Failed to fetch RAG stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setSearchLoading(true);
    try {
      const result = await apiService.searchDocuments(searchQuery, 10);
      
      if (result.success) {
        setSearchResults(result.results);
        toast.success(`Found ${result.count} results`);
      } else {
        setSearchResults([]);
        toast.warning(result.error || 'No results found');
      }
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search failed');
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleClearDatabase = async () => {
    try {
      const result = await apiService.clearRAGDatabase();
      if (result.success) {
        toast.success('RAG database cleared successfully');
        setRagStats(null);
        setSearchResults([]);
        fetchRAGStats();
      } else {
        toast.error('Failed to clear database');
      }
    } catch (error) {
      console.error('Clear database error:', error);
      toast.error('Failed to clear database');
    } finally {
      setClearDialogOpen(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const renderSearchResults = () => {
    if (searchResults.length === 0) return null;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Search Results ({searchResults.length})
        </Typography>
        
        {searchResults.map((result, index) => (
          <Accordion key={index} sx={{ mb: 1 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Description fontSize="small" />
                <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                  {result.metadata?.filename || `Result ${index + 1}`}
                </Typography>
                <Chip
                  label={`${(result.relevance_score * 100).toFixed(1)}% match`}
                  size="small"
                  color={result.relevance_score > 0.8 ? 'success' : result.relevance_score > 0.6 ? 'warning' : 'default'}
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" sx={{ mb: 2, fontFamily: 'monospace', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                {result.content}
              </Typography>
              {result.metadata && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Metadata:
                  </Typography>
                  <Table size="small">
                    <TableBody>
                      {Object.entries(result.metadata).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell sx={{ fontWeight: 'bold', width: '30%' }}>{key}</TableCell>
                          <TableCell>{String(value)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  if (!ragAvailable) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          RAG Knowledge Base
        </Typography>
        <Alert severity="warning">
          RAG (Retrieval-Augmented Generation) system is not available. 
          Please ensure the required dependencies are installed and the system is properly configured.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        RAG Knowledge Base Management
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your document database and search through uploaded content using advanced semantic search.
      </Typography>

      {/* RAG Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Storage color="primary" />
                <Typography variant="h6">Database Status</Typography>
              </Box>
              {loading ? (
                <CircularProgress size={24} sx={{ mt: 1 }} />
              ) : (
                <Typography variant="h4" color="primary" sx={{ mt: 1 }}>
                  {ragStats?.document_count || 0}
                </Typography>
              )}
              <Typography variant="body2" color="text.secondary">
                Documents stored
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Description color="primary" />
                <Typography variant="h6">Content Chunks</Typography>
              </Box>
              <Typography variant="h4" color="primary" sx={{ mt: 1 }}>
                {ragStats?.chunk_count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Searchable segments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Info color="primary" />
                <Typography variant="h6">System Status</Typography>
              </Box>
              <Chip
                label={ragStats ? 'Active' : 'Initializing'}
                color={ragStats ? 'success' : 'warning'}
                sx={{ mt: 1 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                RAG pipeline status
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search Interface */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Semantic Document Search
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            label="Search Query"
            variant="outlined"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search across all uploaded documents..."
            disabled={searchLoading}
          />
          <Button
            variant="contained"
            onClick={handleSearch}
            disabled={searchLoading || !searchQuery.trim()}
            startIcon={searchLoading ? <CircularProgress size={20} /> : <Search />}
            sx={{ minWidth: 120 }}
          >
            {searchLoading ? 'Searching...' : 'Search'}
          </Button>
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Use natural language to search across all uploaded documents. 
          Results are ranked by semantic relevance.
        </Typography>
      </Paper>

      {/* Search Results */}
      {renderSearchResults()}

      {/* Database Management */}
      <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
        <Typography variant="h6" gutterBottom>
          Database Management
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          Manage your RAG database. Warning: Clearing the database will remove all uploaded documents 
          and require re-uploading files.
        </Typography>
        
        <Button
          variant="outlined"
          color="error"
          startIcon={<Delete />}
          onClick={() => setClearDialogOpen(true)}
          disabled={!ragStats || ragStats.document_count === 0}
        >
          Clear Database
        </Button>
        
        {ragStats && ragStats.document_count === 0 && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Database is empty. Upload some documents to get started.
          </Typography>
        )}
      </Paper>

      {/* Clear Confirmation Dialog */}
      <Dialog open={clearDialogOpen} onClose={() => setClearDialogOpen(false)}>
        <DialogTitle>Clear RAG Database</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to clear the entire RAG database? This action cannot be undone.
            All uploaded documents will be removed and you'll need to re-upload them.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClearDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleClearDatabase} color="error" variant="contained">
            Clear Database
          </Button>
        </DialogActions>
      </Dialog>

      {/* Sample Queries */}
      {ragStats && ragStats.document_count > 0 && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Sample Search Queries
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {[
              'financial performance',
              'revenue growth',
              'market analysis',
              'risk factors',
              'investment recommendations',
              'quarterly results'
            ].map((query) => (
              <Chip
                key={query}
                label={query}
                onClick={() => setSearchQuery(query)}
                clickable
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default RAGDashboard;
