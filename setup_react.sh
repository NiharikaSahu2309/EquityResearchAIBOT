#!/bin/bash

echo "========================================="
echo " Equity Research Assistant - React Setup"
echo "========================================="
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8+ from https://python.org/"
    exit 1
fi

echo "✅ Node.js and Python are installed"
echo

echo "📦 Setting up Backend (FastAPI)..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy .env file if it exists in parent directory
if [ -f "../.env" ]; then
    cp "../.env" ".env"
    echo "✅ Environment file copied"
else
    echo "⚠️  Warning: .env file not found in parent directory"
    echo "Please create backend/.env with your GROQ_API_KEY"
fi

cd ..

echo
echo "📦 Setting up Frontend (React)..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo
echo "========================================="
echo " 🎉 Setup Complete!"
echo "========================================="
echo
echo "To start the application:"
echo
echo "1. Start Backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo
echo "2. Start Frontend (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo
echo "The application will be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo
echo "📚 See README_React.md for detailed documentation"
echo
