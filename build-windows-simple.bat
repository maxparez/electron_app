@echo off
echo ========================================
echo Building Windows App with Embedded Python
echo ========================================

REM Create directories
if not exist python-embed mkdir python-embed
if not exist resources mkdir resources

REM Download Python embedded if not exists
if not exist python-embed\python.exe (
    echo Downloading Python 3.11.9 embedded...
    curl -L -o python-embed.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
    
    echo Extracting Python...
    powershell -command "Expand-Archive -Path python-embed.zip -DestinationPath python-embed -Force"
    del python-embed.zip
    
    REM Enable site packages
    echo import site >> python-embed\python311._pth
)

REM Install pip if not exists
if not exist python-embed\Scripts\pip.exe (
    echo Installing pip...
    curl -L -o python-embed\get-pip.py https://bootstrap.pypa.io/get-pip.py
    python-embed\python.exe python-embed\get-pip.py --no-warn-script-location
)

REM Install required packages
echo Installing Python packages...
python-embed\python.exe -m pip install --upgrade pip
python-embed\python.exe -m pip install flask flask-cors openpyxl xlwings pandas reportlab --no-warn-script-location

REM Copy Python to resources
echo Copying Python to resources...
if not exist resources\python-dist mkdir resources\python-dist
xcopy /E /I /Y python-embed resources\python-dist\python

REM Build Electron app
echo Building Electron app...
call npm run make

echo ========================================
echo Build complete!
echo Output: out\make\zip\win32\x64\
echo ========================================
pause