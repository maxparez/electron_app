@echo off
echo Building Electron app for Windows...

REM Clean previous builds
if exist out rmdir /s /q out
if exist dist rmdir /s /q dist

REM Install dependencies
echo Installing npm dependencies...
call npm install

REM Install Python dependencies in a temp location
echo Setting up Python environment...
if not exist python-dist mkdir python-dist
cd python-dist

REM Download Python embedded
if not exist python-3.11.9-embed-amd64.zip (
    echo Downloading Python embedded...
    curl -L -o python-3.11.9-embed-amd64.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
)

REM Extract Python
if not exist python (
    echo Extracting Python...
    powershell -command "Expand-Archive -Path python-3.11.9-embed-amd64.zip -DestinationPath python -Force"
)

REM Install pip
if not exist python\get-pip.py (
    echo Downloading pip...
    curl -L -o python\get-pip.py https://bootstrap.pypa.io/get-pip.py
)

REM Enable site packages
echo import site >> python\python311._pth

REM Install Python dependencies
echo Installing Python packages...
python\python.exe python\get-pip.py --no-warn-script-location
python\python.exe -m pip install flask flask-cors openpyxl xlwings pandas reportlab --no-warn-script-location

cd ..

REM Copy Python files
echo Copying Python files...
xcopy /E /I /Y src\python python-dist\app
xcopy /E /I /Y python-dist\python resources\python

REM Build Electron app
echo Building Electron app...
call npm run make

echo Build complete!
pause