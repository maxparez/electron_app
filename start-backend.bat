@echo off
echo Starting Python Flask Backend...
echo ==============================

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Start Flask server
echo Starting Flask server on http://localhost:5000
python src\python\server.py

pause