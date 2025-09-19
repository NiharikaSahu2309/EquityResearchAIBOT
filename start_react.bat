@echo off
echo ============================================
echo  Starting Equity Research Assistant (React)
echo ============================================
echo.

REM Check if backend directory exists
if not exist "backend" (
    echo ERROR: Backend directory not found
    echo Please run setup_react.bat first
    pause
    exit /b 1
)

REM Check if frontend directory exists
if not exist "frontend" (
    echo ERROR: Frontend directory not found
    echo Please run setup_react.bat first
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ✅ Both servers are starting...
echo.
echo 🌐 Application will be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo.
echo 📚 Press any key to open the application in your browser...
pause >nul

start http://localhost:3000
