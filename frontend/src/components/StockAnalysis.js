import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { Search, TrendingUp, ExpandMore } from '@mui/icons-material';
import Plot from 'react-plotly.js';
import toast from 'react-hot-toast';

import apiService from '../services/apiService';

const StockAnalysis = () => {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [stockData, setStockData] = useState(null);
  const [charts, setCharts] = useState([]);
  const [error, setError] = useState(null);

  const handleStockFetch = async () => {
    if (!symbol.trim()) {
      toast.error('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.fetchStockData(symbol.toUpperCase());
      
      if (result.success) {
        setStockData(result);
        
        // Process charts
        if (result.charts && result.charts.length > 0) {
          const parsedCharts = result.charts.map(chartJson => {
            try {
              return JSON.parse(chartJson);
            } catch (e) {
              console.error('Failed to parse chart:', e);
              return null;
            }
          }).filter(Boolean);
          setCharts(parsedCharts);
        }
        
        toast.success(`Stock data loaded for ${symbol.toUpperCase()}`);
      } else {
        throw new Error('Failed to fetch stock data');
      }
    } catch (error) {
      console.error('Stock fetch error:', error);
      setError(error.message);
      toast.error(`Failed to fetch data for ${symbol.toUpperCase()}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleStockFetch();
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const renderStockInfo = () => {
    if (!stockData) return null;

    const { stock_info, stock_data } = stockData;
    const priceChangeColor = stock_data?.price_change >= 0 ? 'success' : 'error';

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h5" gutterBottom>
          {stock_info.longName || stockData.symbol}
        </Typography>
        
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Price
                </Typography>
                <Typography variant="h4" color="primary">
                  {formatCurrency(stock_data.latest_price)}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Chip
                    label={`${stock_data.price_change >= 0 ? '+' : ''}${formatCurrency(stock_data.price_change)}`}
                    color={priceChangeColor}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Cap
                </Typography>
                <Typography variant="h5">
                  {stock_info.marketCap ? formatNumber(stock_info.marketCap) : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Points
                </Typography>
                <Typography variant="h5">
                  {stock_data.shape[0]} days
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Historical data available
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Additional Stock Info */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">Detailed Information</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {Object.entries(stock_info).map(([key, value]) => {
                if (key === 'longName') return null;
                return (
                  <Grid item xs={12} sm={6} md={4} key={key}>
                    <Typography variant="subtitle2" color="text.secondary">
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </Typography>
                    <Typography variant="body1">
                      {typeof value === 'number' ? formatNumber(value) : String(value)}
                    </Typography>
                  </Grid>
                );
              })}
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Box>
    );
  };

  const renderCharts = () => {
    if (charts.length === 0) return null;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Price Charts & Analysis
        </Typography>
        {charts.map((chart, index) => (
          <Paper key={index} sx={{ p: 2, mb: 2 }} className="chart-container">
            <Plot
              data={chart.data}
              layout={{
                ...chart.layout,
                autosize: true,
                margin: { l: 50, r: 50, t: 50, b: 50 },
              }}
              useResizeHandler
              style={{ width: '100%', height: '400px' }}
              config={{ responsive: true, displayModeBar: false }}
            />
          </Paper>
        ))}
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Stock Analysis
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Enter a stock symbol to fetch real-time data and generate analysis charts.
      </Typography>

      {/* Search Input */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <TextField
            label="Stock Symbol"
            variant="outlined"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            onKeyPress={handleKeyPress}
            placeholder="e.g., AAPL, GOOGL, MSFT"
            disabled={loading}
            sx={{ flexGrow: 1 }}
          />
          <Button
            variant="contained"
            onClick={handleStockFetch}
            disabled={loading || !symbol.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <Search />}
            sx={{ minWidth: 120 }}
          >
            {loading ? 'Fetching...' : 'Analyze'}
          </Button>
        </Box>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {stockData && (
        <>
          {renderStockInfo()}
          {renderCharts()}
        </>
      )}

      {/* Example Symbols */}
      {!stockData && !loading && (
        <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Popular Stocks to Try
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX'].map((symbolExample) => (
              <Chip
                key={symbolExample}
                label={symbolExample}
                onClick={() => setSymbol(symbolExample)}
                clickable
                variant="outlined"
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default StockAnalysis;
