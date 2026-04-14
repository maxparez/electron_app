@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Instalace - Nástroje pro ŠI a ŠII OP JAK            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Kontrola Python 3.13
echo [1/6] Kontroluji Python 3.13...
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
echo [2/6] Kontroluji Node.js...
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

REM Kontrola npm
echo Kontroluji npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CHYBA: npm není dostupné!
    echo.
    echo Zkontrolujte instalaci Node.js nebo přidejte npm do PATH.
    echo Pokud jste Node.js právě doinstalovali, zavřete a znovu otevřete okno příkazové řádky.
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('npm --version') do set NPM_VERSION=%%v
echo ✅ npm nalezen (verze %NPM_VERSION%)

REM Kontrola Git (volitelné)
echo [3/6] Kontroluji Git...
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
echo [4/6] Vytvářím Python virtuální prostředí...
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
echo [5/6] Instaluji Node.js moduly...
call npm ci --omit=dev
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat Node.js moduly!
    pause
    exit /b 1
)
echo ✅ Node.js moduly nainstalovány

REM Vytvoření zástupce na ploše
echo.
echo Vytvářím zástupce na ploše...
powershell -ExecutionPolicy Bypass -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Desktop = [System.Environment]::GetFolderPath('Desktop'); $ShortcutPath = \"$Desktop\Nástroje OP JAK.lnk\"; $Shortcut = $WshShell.CreateShortcut($ShortcutPath); $Shortcut.TargetPath = '%CD%\start-app.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = '%CD%\icon.ico'; $Shortcut.Description = 'Nástroje pro zpracování dokumentace OP JAK'; $Shortcut.Save(); Write-Host '✅ Zástupce vytvořen na ploše' -ForegroundColor Green}"
if errorlevel 1 (
    echo ⚠️  Nepodařilo se vytvořit zástupce automaticky
    echo Můžete vytvořit zástupce ručně - ukázat na start-app.bat
)

echo.
echo [6/6] Dokončuji instalaci
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
