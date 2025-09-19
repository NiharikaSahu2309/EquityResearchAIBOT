# Stock Data Analysis Examples

This folder contains sample stock market data files for testing the Equity Research Assistant Bot.

## Files Description

### indexData.csv
Contains raw index data with the following structure:
- Date: Trading date
- Open: Opening price
- High: Highest price of the day
- Low: Lowest price of the day
- Close: Closing price
- Volume: Trading volume

### indexInfo.csv
Contains metadata and information about the indices:
- Index Name
- Symbol
- Market Cap
- Sector Information
- Exchange

### indexProcessed.csv
Contains processed and cleaned index data ready for analysis:
- Calculated returns
- Moving averages
- Technical indicators
- Volatility measures

## Usage

These files can be uploaded through the web interface to test the following features:

1. **Data Visualization**: Automatic chart generation
2. **Statistical Analysis**: Descriptive statistics and correlations
3. **AI Analysis**: GROQ-powered insights and recommendations
4. **Technical Analysis**: Moving averages, RSI, Bollinger Bands
5. **Risk Assessment**: Volatility and drawdown analysis

## Data Format

All CSV files follow standard financial data formats and are compatible with pandas DataFrame operations.

Example data structure:
```
Date,Open,High,Low,Close,Volume
2023-01-01,100.50,102.30,99.80,101.75,1500000
2023-01-02,101.75,103.20,101.00,102.90,1750000
...
```

## Adding Your Own Data

To add your own financial data:

1. Ensure your CSV files have proper column headers
2. Date columns should be in YYYY-MM-DD format
3. Numeric data should be clean (no currency symbols)
4. Missing values will be handled automatically

For best results, include the following columns:
- Date/Timestamp
- Open, High, Low, Close prices
- Volume
- Any additional metrics or indicators
