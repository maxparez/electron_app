@echo off
setlocal
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "INSTALL_SCRIPT=%SCRIPT_DIR%scripts\install_windows.ps1"

if not exist "%INSTALL_SCRIPT%" (
    echo ❌ CHYBA: Instalační skript "%INSTALL_SCRIPT%" nebyl nalezen.
    echo.
    echo Ujistěte se, že spouštíte install-windows.bat z kořene instalační složky.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%INSTALL_SCRIPT%" %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Instalace selhala s kódem %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%
