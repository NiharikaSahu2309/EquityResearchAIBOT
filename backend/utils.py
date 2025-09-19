import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

class DataProcessor:
    """Data processing utilities for financial data"""
    
    @staticmethod
    def clean_financial_data(df):
        """Clean and preprocess financial data"""
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Convert date columns
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
        
        # Fill missing numeric values with forward fill
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].ffill()
        
        return df
    
    @staticmethod
    def calculate_returns(prices):
        """Calculate returns from price series"""
        return prices.pct_change().dropna()
    
    @staticmethod
    def calculate_moving_averages(data, windows=[20, 50, 200]):
        """Calculate moving averages for given windows"""
        result = data.copy()
        for window in windows:
            result[f'MA_{window}'] = data.rolling(window=window).mean()
        return result
    
    @staticmethod
    def calculate_volatility(returns, window=30):
        """Calculate rolling volatility"""
        return returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
    
    @staticmethod
    def detect_outliers(data, method='iqr'):
        """Detect outliers in financial data"""
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (data < lower_bound) | (data > upper_bound)
        return None

class FinancialAnalyzer:
    """Financial analysis utilities"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate/252
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    @staticmethod
    def calculate_max_drawdown(prices):
        """Calculate maximum drawdown"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    @staticmethod
    def calculate_beta(stock_returns, market_returns):
        """Calculate stock beta"""
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return covariance / market_variance
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

def fetch_market_data(symbols, period="1y"):
    """Fetch market data for multiple symbols"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data[symbol] = ticker.history(period=period)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return data

def create_portfolio_analysis(symbols, weights=None, period="1y"):
    """Create portfolio analysis"""
    if weights is None:
        weights = [1/len(symbols)] * len(symbols)
    
    # Fetch data
    data = fetch_market_data(symbols, period)
    
    # Calculate portfolio returns
    returns = {}
    for symbol in symbols:
        if symbol in data:
            returns[symbol] = DataProcessor.calculate_returns(data[symbol]['Close'])
    
    # Create portfolio
    portfolio_returns = sum(weight * returns[symbol] for weight, symbol in zip(weights, symbols) if symbol in returns)
    
    # Calculate metrics
    sharpe = FinancialAnalyzer.calculate_sharpe_ratio(portfolio_returns)
    max_dd = FinancialAnalyzer.calculate_max_drawdown((1 + portfolio_returns).cumprod())
    
    return {
        'portfolio_returns': portfolio_returns,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'annual_return': portfolio_returns.mean() * 252,
        'annual_volatility': portfolio_returns.std() * np.sqrt(252)
    }
