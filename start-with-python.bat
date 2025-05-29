@echo off
echo Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Installing required Python packages...
pip install flask flask-cors openpyxl xlwings pandas reportlab

echo Starting application...
start "" "%~dp0NastrojeOPJAK.exe"