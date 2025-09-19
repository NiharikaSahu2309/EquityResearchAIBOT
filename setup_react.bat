@echo off
echo =========================================
echo  Equity Research Assistant - React Setup
echo =========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org/
    pause
    exit /b 1
)

echo ✅ Node.js and Python are installed
echo.

echo 📦 Setting up Backend (FastAPI)...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Copy .env file if it exists in parent directory
if exist "..\\.env" (
    copy "..\\.env" ".env" >nul
    echo ✅ Environment file copied
) else (
    echo ⚠️  Warning: .env file not found in parent directory
    echo Please create backend\.env with your GROQ_API_KEY
)

cd ..

echo.
echo 📦 Setting up Frontend (React)...
cd frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

cd ..

echo.
echo =========================================
echo  🎉 Setup Complete!
echo =========================================
echo.
echo To start the application:
echo.
echo 1. Start Backend (in one terminal):
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. Start Frontend (in another terminal):
echo    cd frontend
echo    npm start
echo.
echo The application will be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo.
echo 📚 See README_React.md for detailed documentation
echo.
pause
