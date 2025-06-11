@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Instalace - Nástroje pro ŠI a ŠII OP JAK            ║
echo ║                    Samostatný instalátor                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Tento instalátor stáhne a nainstaluje aplikaci do:
echo %PROGRAMFILES%\zor_nastroje
echo.

REM Kontrola administrátorských práv
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ CHYBA: Tento skript vyžaduje administrátorská práva!
    echo.
    echo Klikněte pravým tlačítkem na tento soubor a vyberte:
    echo "Spustit jako správce"
    echo.
    pause
    exit /b 1
)

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

REM Kontrola Git
echo [3/6] Kontroluji Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CHYBA: Git není nainstalován!
    echo.
    echo Prosím nainstalujte Git z:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)
echo ✅ Git nalezen

REM Vytvoření instalační složky
echo.
echo [4/6] Vytvářím instalační složku...
set "INSTALL_DIR=%PROGRAMFILES%\zor_nastroje"
if exist "%INSTALL_DIR%" (
    echo Odstraňujem starou instalaci...
    rmdir /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"
echo ✅ Složka vytvořena: %INSTALL_DIR%

REM Git clone z správné větve
echo.
echo [5/6] Stahuji aplikaci z GitHubu...
cd /d "%INSTALL_DIR%"
git clone -b feature/next-phase https://github.com/maxparez/electron_app.git .
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se stáhnout aplikaci z GitHubu!
    echo Zkontrolujte připojení k internetu.
    pause
    exit /b 1
)
echo ✅ Aplikace stažena

REM Python virtual environment
echo.
echo [6/6] Instaluji Python závislosti...
if exist venv (
    echo Mažu staré virtuální prostředí...
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
echo Instaluji Node.js moduly...
call npm install
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat Node.js moduly!
    pause
    exit /b 1
)
echo ✅ Node.js moduly nainstalovány

REM Vytvoření zástupce na ploše s lepší ikonou
echo.
echo Vytvářím zástupce na ploše...
powershell -ExecutionPolicy Bypass -Command "& {
    $WshShell = New-Object -comObject WScript.Shell;
    $Desktop = [System.Environment]::GetFolderPath('Desktop');
    $ShortcutPath = '$Desktop\Nástroje OP JAK.lnk';
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath);
    $Shortcut.TargetPath = '%INSTALL_DIR%\start-app.bat';
    $Shortcut.WorkingDirectory = '%INSTALL_DIR%';
    $Shortcut.IconLocation = '%INSTALL_DIR%\src\electron\assets\icon.ico';
    $Shortcut.Description = 'Nástroje pro zpracování dokumentace OP JAK';
    $Shortcut.Save();
    Write-Host '✅ Zástupce vytvořen na ploše' -ForegroundColor Green
}"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ INSTALACE DOKONČENA!                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Aplikace je nainstalována v: %INSTALL_DIR%
echo.
echo Aplikaci spustíte:
echo   1. Dvojklikem na zástupce "Nástroje OP JAK" na ploše
echo   2. Nebo spuštěním start-app.bat ze složky aplikace
echo.
echo Pro aktualizace spusťte update-windows.bat ze složky aplikace
echo.
pause