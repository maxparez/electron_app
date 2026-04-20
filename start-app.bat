@echo off

REM Pokud už není minimized, spusť minimized a ukonči
if not "%minimized%"=="true" (
    set minimized=true
    start /min cmd /c "%~dpnx0" %*
    exit
)

chcp 65001 >nul 2>&1
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR:~0,-1%"
set "CONFIG_PATH=%REPO_DIR%\channel-config.json"
set "APP_CHANNEL=stable"
set "DEBUG_LOGGING=False"

if exist "%CONFIG_PATH%" (
    for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$cfg = Get-Content -Raw '%CONFIG_PATH%' | ConvertFrom-Json; if ($cfg.channel) { $cfg.channel } else { 'stable' }"`) do set "APP_CHANNEL=%%i"
    for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$cfg = Get-Content -Raw '%CONFIG_PATH%' | ConvertFrom-Json; [bool]$cfg.debug_logging"`) do set "DEBUG_LOGGING=%%i"
)

REM Kontrola, zda je venv vytvořen
if not exist "%REPO_DIR%\venv" (
    echo ❌ CHYBA: Aplikace není nainstalována!
    echo Nejprve spusťte: install-windows.bat
    pause
    exit /b 1
)

set "LOG_DIR=%REPO_DIR%\logs\launcher"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"`) do set "TIMESTAMP=%%i"
set "LOG_FILE=%LOG_DIR%\start_%TIMESTAMP%.log"

pushd "%REPO_DIR%"

REM Nastavení cesty k Python prostředí pro Electron
set "ELECTRON_APP_PYTHON_ENV=%REPO_DIR%\venv"
set "ELECTRON_APP_CHANNEL=%APP_CHANNEL%"

if /i "%DEBUG_LOGGING%"=="True" (
    set "ELECTRON_ENABLE_LOGGING=1"
    set "ELECTRON_ENABLE_STACK_DUMPING=1"
    set "FLASK_DEBUG=true"
)

echo [START] Channel=%APP_CHANNEL% Debug=%DEBUG_LOGGING% > "%LOG_FILE%"
echo [START] WorkingDirectory=%REPO_DIR% >> "%LOG_FILE%"
echo [START] Timestamp=%TIMESTAMP% >> "%LOG_FILE%"

REM Spuštění Electron aplikace (ta si sama spustí a ukončí Python backend)
npm start >> "%LOG_FILE%" 2>&1

popd
