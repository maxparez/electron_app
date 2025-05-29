@echo off
echo Quick fix for Python backend...

REM Install Python packages globally
pip install flask flask-cors openpyxl xlwings pandas reportlab

REM Create a wrapper that uses system Python
echo @echo off > "%~dp0run-with-system-python.bat"
echo cd /d "%~dp0" >> "%~dp0run-with-system-python.bat"
echo set PYTHONPATH=%~dp0resources\app.asar.unpacked\src\python >> "%~dp0run-with-system-python.bat"
echo python "%~dp0resources\app.asar.unpacked\src\python\server.py" >> "%~dp0run-with-system-python.bat"

echo.
echo Fix applied! Now you can:
echo 1. Run the app normally (it will try to find Python)
echo 2. Or run run-with-system-python.bat first, then the app
pause