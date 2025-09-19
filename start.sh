#!/bin/bash

# Equity Research Assistant Bot Startup Script

echo "🚀 Starting Equity Research Assistant Bot..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your GROQ API credentials:"
    echo "GROQ_API_KEY='your_api_key_here'"
    echo "GROQ_API_URL='https://api.groq.com/openai/v1'"
    exit 1
fi

# Start the Streamlit app
echo "🌐 Starting Streamlit application..."
echo "The app will open in your default browser at http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo "=================================="

streamlit run app.py
