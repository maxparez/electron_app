@echo off
echo Starting Electron App - Backend and Frontend
echo ===========================================

REM Start backend in new window
start "Flask Backend" cmd /k start-backend.bat

REM Wait a bit for backend to start
echo Waiting for backend to start...
timeout /t 5

REM Start frontend in new window
start "Electron Frontend" cmd /k start-frontend.bat

echo.
echo Both backend and frontend should be starting in separate windows.
echo.
echo Backend: http://localhost:5000
echo Frontend: Electron window should open automatically
echo.
echo Press any key to exit this window...
pause > nul