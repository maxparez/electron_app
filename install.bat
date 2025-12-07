@echo off
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Instalace - Nástroje pro ŠI a ŠII OP JAK            ║
echo ║                        Verze 1.1.0                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Tento skript nainstaluje aplikaci do složky C:\OPJAK\electron_app
echo a vytvoří zástupce na ploše.
echo.
pause
echo.

REM ========================================================================
REM FÁZE 1: Kontrola závislostí
REM ========================================================================
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 1/5: Kontrola závislostí                                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set MISSING_DEPS=

REM Kontrola Python
echo [1/4] Kontroluji Python 3.11+...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python není nainstalován!
    echo    ➜ Stáhněte z: https://www.python.org/downloads/
    echo    ⚠️  Při instalaci zaškrtněte "Add Python to PATH"
    echo.
    set MISSING_DEPS=1
) else (
    python --version 2>&1 | findstr /R "3\.1[1-3]" >nul
    if errorlevel 1 (
        echo ⚠️  Python je nainstalován, ale verze může být nekompatibilní
        echo    Doporučujeme Python 3.11 až 3.13
        python --version
    ) else (
        echo ✅ Python nalezen
        python --version 2>&1
    )
)

REM Kontrola Node.js
echo [2/4] Kontroluji Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js není nainstalován!
    echo    ➜ Stáhněte z: https://nodejs.org/
    echo.
    set MISSING_DEPS=1
) else (
    echo ✅ Node.js nalezen
    node --version 2>&1
)

REM Kontrola npm
echo [3/4] Kontroluji npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm není nainstalován!
    echo    ➜ npm se instaluje s Node.js z: https://nodejs.org/
    echo.
    set MISSING_DEPS=1
) else (
    echo ✅ npm nalezen
    npm --version 2>&1
)

REM Kontrola Git
echo [4/4] Kontroluji Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git není nainstalován!
    echo    ➜ Stáhněte z: https://git-scm.com/download/win
    echo.
    set MISSING_DEPS=1
) else (
    echo ✅ Git nalezen
    git --version 2>&1
)

echo.
if defined MISSING_DEPS (
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║ ❌ CHYBÍ POTŘEBNÝ SOFTWARE                                     ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo Prosím nainstalujte chybějící programy (viz odkazy výše) a poté
    echo spusťte tento instalátor znovu.
    echo.
    echo Dodatečně budete potřebovat:
    echo   • Microsoft Office s Excelem (2019+ nebo Microsoft 365)
    echo   • Microsoft Visual C++ Redistributable 2015-2022
    echo     ➜ https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    pause
    exit /b 1
)

echo ✅ Všechny potřebné programy jsou nainstalovány!
echo.
pause

REM ========================================================================
REM FÁZE 2: Stažení aplikace z GitHubu
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 2/5: Stahování aplikace z GitHubu                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set INSTALL_DIR=C:\OPJAK\electron_app
set REPO_URL=https://github.com/maxparez/electron_app.git
set BRANCH=windows-install

echo Instalační složka: %INSTALL_DIR%
echo GitHub repozitář: %REPO_URL%
echo Větev: %BRANCH%
echo.

REM Vytvoření složky
if not exist "C:\OPJAK" (
    echo Vytvářím složku C:\OPJAK...
    mkdir "C:\OPJAK"
)

REM Klonování nebo aktualizace
if not exist "%INSTALL_DIR%\.git" (
    echo Stahují aplikaci (může trvat několik minut)...
    git clone -b %BRANCH% %REPO_URL% "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ❌ CHYBA: Nepodařilo se stáhnout aplikaci z GitHubu!
        echo Zkontrolujte připojení k internetu a zkuste znovu.
        pause
        exit /b 1
    )
) else (
    echo Aplikace již existuje, aktualizuji...
    cd /d "%INSTALL_DIR%"
    git fetch origin
    git checkout %BRANCH%
    git reset --hard origin/%BRANCH%
    git clean -fd
)

echo ✅ Aplikace stažena do: %INSTALL_DIR%
echo.

REM ========================================================================
REM FÁZE 3: Vytvoření Python virtuálního prostředí
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 3/5: Příprava Python prostředí                           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%INSTALL_DIR%"

if exist "venv" (
    echo Virtuální prostředí již existuje, mažu staré...
    rmdir /s /q venv
)

echo Vytvářím Python virtuální prostředí...
python -m venv venv
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se vytvořit virtuální prostředí!
    pause
    exit /b 1
)

echo Aktivuji virtuální prostředí...
call venv\Scripts\activate.bat

echo Aktualizuji pip...
python -m pip install --upgrade pip --quiet

echo Instaluji Python knihovny (může trvat několik minut)...
pip install -r requirements-windows.txt --quiet
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat Python knihovny!
    echo Zkontrolujte připojení k internetu a zkuste znovu.
    pause
    exit /b 1
)

echo ✅ Python prostředí připraveno
echo.

REM ========================================================================
REM FÁZE 4: Instalace Node.js modulů
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 4/5: Instalace Node.js modulů                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Instaluji Node.js moduly (může trvat několik minut)...
call npm install --production --loglevel=error
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat Node.js moduly!
    pause
    exit /b 1
)

echo ✅ Node.js moduly nainstalovány
echo.

REM ========================================================================
REM FÁZE 5: Vytvoření zástupce na ploše
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 5/5: Dokončení instalace                                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Vytvářím zástupce na ploše...
powershell -ExecutionPolicy Bypass -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Desktop = [System.Environment]::GetFolderPath('Desktop'); $ShortcutPath = \"$Desktop\Nástroje OP JAK.lnk\"; $Shortcut = $WshShell.CreateShortcut($ShortcutPath); $Shortcut.TargetPath = '%INSTALL_DIR%\start-app.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\icon.ico'; $Shortcut.Description = 'Nástroje pro zpracování dokumentace OP JAK'; $Shortcut.Save()}"
if errorlevel 1 (
    echo ⚠️  Nepodařilo se vytvořit zástupce automaticky
    echo Můžete vytvořit zástupce ručně - odkázat na: %INSTALL_DIR%\start-app.bat
) else (
    echo ✅ Zástupce vytvořen na ploše
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ INSTALACE ÚSPĚŠNĚ DOKONČENA!                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📁 Aplikace nainstalována do: %INSTALL_DIR%
echo 🖥️  Zástupce vytvořen na ploše: "Nástroje OP JAK"
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ Jak spustit aplikaci:                                          │
echo │  1. Dvojklik na zástupce na ploše                             │
echo │  2. Nebo spusťte: %INSTALL_DIR%\start-app.bat       │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ Pro aktualizaci aplikace později:                              │
echo │  Spusťte: %INSTALL_DIR%\update.bat                   │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo ⚠️  DŮLEŽITÉ: Při prvním spuštění potvrďte oprávnění firewallu,
echo    pokud Windows o to požádá.
echo.
pause
