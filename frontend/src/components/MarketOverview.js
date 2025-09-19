import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { TrendingUp, TrendingDown, ArrowUpward, ArrowDownward } from '@mui/icons-material';
import toast from 'react-hot-toast';

import apiService from '../services/apiService';

const MarketOverview = () => {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.getMarketOverview();
      
      if (result.success) {
        setMarketData(result.market_data);
        toast.success('Market data updated');
      } else {
        throw new Error('Failed to fetch market data');
      }
    } catch (error) {
      console.error('Market data error:', error);
      setError(error.message);
      toast.error('Failed to load market data');
    } finally {
      setLoading(false);
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

  const formatMarketCap = (value) => {
    if (value >= 1e12) {
      return `$${(value / 1e12).toFixed(2)}T`;
    } else if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`;
    }
    return `$${value}`;
  };

  const renderStockCard = (symbol, data) => {
    const isPositive = data.change >= 0;
    const changeColor = isPositive ? 'success' : 'error';
    const TrendIcon = isPositive ? TrendingUp : TrendingDown;
    const ArrowIcon = isPositive ? ArrowUpward : ArrowDownward;

    return (
      <Grid item xs={12} sm={6} md={4} key={symbol}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Box>
                <Typography variant="h6" component="div">
                  {symbol}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {data.company_name}
                </Typography>
              </Box>
              <TrendIcon color={changeColor} />
            </Box>
            
            <Typography variant="h5" component="div" gutterBottom>
              {formatCurrency(data.price)}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <ArrowIcon fontSize="small" color={changeColor} />
              <Chip
                label={`${isPositive ? '+' : ''}${formatCurrency(data.change)}`}
                color={changeColor}
                size="small"
              />
              <Chip
                label={`${isPositive ? '+' : ''}${data.change_percent.toFixed(2)}%`}
                color={changeColor}
                variant="outlined"
                size="small"
              />
            </Box>
            
            {data.market_cap > 0 && (
              <Typography variant="body2" color="text.secondary">
                Market Cap: {formatMarketCap(data.market_cap)}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading market data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  const marketDataEntries = marketData ? Object.entries(marketData) : [];
  const gainers = marketDataEntries.filter(([, data]) => data.change >= 0);
  const losers = marketDataEntries.filter(([, data]) => data.change < 0);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Market Overview
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Real-time market data for popular stocks. Data updates automatically.
      </Typography>

      {/* Market Summary */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}>
            <Box textAlign="center">
              <Typography variant="h3" color="success.main">
                {gainers.length}
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Gainers
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box textAlign="center">
              <Typography variant="h3" color="error.main">
                {losers.length}
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Losers
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box textAlign="center">
              <Typography variant="h3" color="primary.main">
                {marketDataEntries.length}
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Total Stocks
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Stock Cards */}
      {marketDataEntries.length > 0 ? (
        <Grid container spacing={3}>
          {marketDataEntries.map(([symbol, data]) => renderStockCard(symbol, data))}
        </Grid>
      ) : (
        <Alert severity="info">
          No market data available at the moment. Please try again later.
        </Alert>
      )}

      {/* Last Updated */}
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Last updated: {new Date().toLocaleString()}
        </Typography>
      </Box>
    </Box>
  );
};

export default MarketOverview;
