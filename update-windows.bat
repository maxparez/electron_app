@echo off
chcp 65001 >nul
setlocal
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         Aktualizace - Nástroje pro ŠI a ŠII OP JAK           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR:~0,-1%"
set "UPDATE_SCRIPT=%SCRIPT_DIR%scripts\update_windows.ps1"

if not exist "%UPDATE_SCRIPT%" (
    echo ❌ CHYBA: Nenalezen skript %UPDATE_SCRIPT%
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%UPDATE_SCRIPT%" -RepoPath "%REPO_DIR%" %*
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if not "%EXIT_CODE%"=="0" (
    echo ❌ Aktualizace selhala. Podrobnosti najdete v logs\update\
    pause
    exit /b %EXIT_CODE%
)

echo ✅ Aktualizace dokončena. Transcript najdete v logs\update\
pause
exit /b 0
