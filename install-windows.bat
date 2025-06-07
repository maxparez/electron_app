@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Instalace - Nástroje pro ŠI a ŠII OP JAK            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Kontrola Python 3.13
echo [1/5] Kontroluji Python 3.13...
python --version 2>nul | findstr "3.13" >nul
if errorlevel 1 (
    echo ❌ CHYBA: Python 3.13 není nainstalován!
    echo.
    echo Prosím nainstalujte Python 3.13 z:
    echo https://www.python.org/downloads/
    echo.
    echo ⚠️  Při instalaci zaškrtněte "Add Python to PATH"!
    echo.
    pause
    exit /b 1
)
echo ✅ Python 3.13 nalezen

REM Kontrola Node.js
echo [2/5] Kontroluji Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CHYBA: Node.js není nainstalován!
    echo.
    echo Prosím nainstalujte Node.js LTS z:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js nalezen

REM Kontrola Git (volitelné)
echo [3/5] Kontroluji Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  UPOZORNĚNÍ: Git není nainstalován
    echo    Pro snadné aktualizace doporučujeme nainstalovat Git z:
    echo    https://git-scm.com/download/win
    echo.
    echo Pokračovat bez Gitu? (aktualizace budou složitější)
    pause
) else (
    echo ✅ Git nalezen
)

REM Python virtual environment
echo.
echo [4/5] Vytvářím Python virtuální prostředí...
if exist venv (
    echo Virtuální prostředí již existuje, mažu staré...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se vytvořit virtuální prostředí!
    pause
    exit /b 1
)

echo Aktivuji virtuální prostředí...
call venv\Scripts\activate.bat

echo Aktualizuji pip...
python -m pip install --upgrade pip

echo Instaluji Python knihovny...
pip install -r requirements-windows.txt
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat Python knihovny!
    echo Zkontrolujte připojení k internetu a zkuste znovu.
    pause
    exit /b 1
)
echo ✅ Python knihovny nainstalovány

REM Node.js moduly
echo.
echo [5/5] Instaluji Node.js moduly...
call npm install
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat Node.js moduly!
    pause
    exit /b 1
)
echo ✅ Node.js moduly nainstalovány

REM Vytvoření zástupce na ploše
echo.
echo Vytvářím zástupce na ploše...
powershell -ExecutionPolicy Bypass -File create-desktop-shortcut.ps1

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ INSTALACE DOKONČENA!                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Aplikaci spustíte:
echo   1. Dvojklikem na zástupce na ploše
echo   2. Nebo spuštěním start-app.bat
echo.
echo Pro aktualizace použijte: update-windows.bat
echo.
pause