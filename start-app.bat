@echo off
chcp 65001 >nul

REM Kontrola, zda je venv vytvořen
if not exist venv (
    echo ❌ CHYBA: Aplikace není nainstalována!
    echo Nejprve spusťte: install-windows.bat
    pause
    exit /b 1
)

REM Nastavení cesty k Python prostředí pro Electron
set ELECTRON_APP_PYTHON_ENV=%cd%\venv

REM Spuštění Electron aplikace (ta si sama spustí a ukončí Python backend)
npm start