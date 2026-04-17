@echo off
echo Starting Electron Frontend...
echo ============================

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

REM Start Electron in dev mode
echo Starting Electron application...
npm run dev

pause