@echo off
echo Starting Equity Research Assistant Bot (React + FastAPI)
echo.

REM Set Node.js PATH
set "PATH=C:\Program Files\nodejs;%PATH%"

REM Open backend in new window
echo Starting Backend Server on port 8081...
start "Backend Server" cmd /k "cd /d "c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\backend" && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8081"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

REM Open frontend in new window
echo Starting Frontend Development Server...
start "Frontend Server" cmd /k "cd /d "c:\Users\Niharika Sahu\Documents\GitHub\Equity Research Assistant Bot\frontend" && set "PATH=C:\Program Files\nodejs;%PATH%" && npm start"

REM Wait and open browser
timeout /t 10 /nobreak > nul
echo Opening application in browser...
start http://localhost:3000

echo.
echo Backend: http://localhost:8080
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
