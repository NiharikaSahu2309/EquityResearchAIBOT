@echo off
REM Equity Research Assistant Bot Startup Script for Windows

echo 🚀 Starting Equity Research Assistant Bot...
echo ==================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo Please create a .env file with your GROQ API credentials:
    echo GROQ_API_KEY='your_api_key_here'
    echo GROQ_API_URL='https://api.groq.com/openai/v1'
    pause
    exit /b 1
)

REM Start the Streamlit app
echo 🌐 Starting Streamlit application...
echo The app will open in your default browser at http://localhost:8501
echo Press Ctrl+C to stop the application
echo ==================================

streamlit run app.py

pause
