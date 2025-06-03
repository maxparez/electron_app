@echo off
echo === Backend Debug ===
echo.

REM Check if Python exists in resources
if exist resources\python\python.exe (
    echo Found bundled Python at: resources\python\python.exe
    set PYTHON_PATH=resources\python\python.exe
) else (
    echo Bundled Python NOT FOUND!
    echo Using system Python...
    set PYTHON_PATH=python
)

REM Check if server.py exists
if exist resources\app.asar.unpacked\src\python\server.py (
    echo Found server.py at: resources\app.asar.unpacked\src\python\server.py
) else (
    echo ERROR: server.py NOT FOUND!
    pause
    exit /b 1
)

REM Set environment
set PYTHONPATH=resources\app.asar.unpacked\src\python
set FLASK_DEBUG=true
set PYTHONUNBUFFERED=1

REM Try to start backend
echo.
echo Starting backend...
echo Command: %PYTHON_PATH% resources\app.asar.unpacked\src\python\server.py
echo.

%PYTHON_PATH% resources\app.asar.unpacked\src\python\server.py

pause