@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          Instalace - Nástroje pro ŠI a ŠII OP JAK            ║
echo ║                        Verze 1.1.2                             ║
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

REM --- KROK 1: Detekce příkazu pro Python ---
echo [1/4] Kontroluji Python...

set "PYTHON_CMD="

REM Zkusíme najít 'python'
where python >nul 2>&1
if %errorlevel% equ 0 set "PYTHON_CMD=python"

REM Pokud není 'python', zkusíme 'py' launcher (časté na Windows)
if not defined PYTHON_CMD (
    where py >nul 2>&1
    if !errorlevel! equ 0 set "PYTHON_CMD=py"
)

REM Pokud jsme nic nenašli, nahlásíme chybu
if not defined PYTHON_CMD (
    echo ❌ Python nebyl nalezen v PATH!
    echo    Vidím, že ho máte ve složce, ale systémový příkaz ho nevidí.
    echo    Zkuste napsat do příkazové řádky: set PATH=%%PATH%%;C:\Users\WDAGUtilityAccount\AppData\Local\Programs\Python\Python314\
    echo.
    set MISSING_DEPS=1
    goto :check_node
)

echo ✅ Nalezen příkaz: %PYTHON_CMD%

REM --- KROK 2: Kontrola verze Pythonu ---
REM Používáme cmd /c pro izolaci, aby chyby nezhroutily skript
REM Regex 3.1[0-9] pokryje verze 3.10 az 3.19 (včetně vaší 3.14)

cmd /c "%PYTHON_CMD% --version 2>&1" | findstr /R "3\.1[0-9]" >nul
if %errorlevel% equ 0 (
    echo ✅ Verze Pythonu je v pořádku:
    %PYTHON_CMD% --version
) else (
    echo ⚠️  Python nalezen, ale verze se zdá být starší než 3.10 nebo exotická.
    echo    Detekovaná verze:
    %PYTHON_CMD% --version
)

:check_node
REM --- KROK 3: Kontrola Node.js ---
echo.
echo [2/4] Kontroluji Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js není nainstalován!
    echo    ➜ Stáhněte z: https://nodejs.org/
    set MISSING_DEPS=1
) else (
    echo ✅ Node.js nalezen
    node --version 2>&1
)

REM --- KROK 4: Kontrola npm ---
echo [3/4] Kontroluji npm...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm není nainstalován!
    set MISSING_DEPS=1
) else (
    echo ✅ npm nalezen
    cmd /c npm --version
)

REM --- KROK 5: Kontrola Git ---
echo [4/4] Kontroluji Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git není nainstalován!
    echo    ➜ Stáhněte z: https://git-scm.com/download/win
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
    echo Prosím opravte instalace a spusťte znovu.
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

if not exist "C:\OPJAK" mkdir "C:\OPJAK"

if not exist "%INSTALL_DIR%\.git" (
    echo Stahují aplikaci...
    git clone -b %BRANCH% %REPO_URL% "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ❌ CHYBA: Nepodařilo se stáhnout aplikaci!
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

echo ✅ Aplikace stažena.
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
    echo Mazání starého venv...
    rmdir /s /q venv
)

echo Vytvářím venv pomocí: %PYTHON_CMD%
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se vytvořit virtuální prostředí!
    pause
    exit /b 1
)

echo Aktivuji venv a instaluji knihovny...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet

echo Instaluji requirements ^(chvilku strpení^)...
pip install -r requirements-windows.txt --quiet
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se nainstalovat knihovny!
    pause
    exit /b 1
)

echo ✅ Python OK.
echo.

REM ========================================================================
REM FÁZE 4: Instalace Node.js modulů
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 4/5: Instalace Node.js modulů                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Instaluji npm moduly...
call npm install --loglevel=error
if errorlevel 1 (
    echo ❌ CHYBA: npm install selhal!
    pause
    exit /b 1
)

echo ✅ Node.js moduly OK.
echo.

REM ========================================================================
REM FÁZE 5: Vytvoření zástupce na ploše
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 5/5: Dokončení instalace                                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

set "TARGET_FILE=%INSTALL_DIR%\start-app.bat"
set "ICON_FILE=%INSTALL_DIR%\icon.ico"
set "SHORTCUT_NAME=Nástroje OP JAK.lnk"

echo Vytvářím zástupce...

set "PS_COMMAND=$WshShell = New-Object -comObject WScript.Shell; "
set "PS_COMMAND=!PS_COMMAND! $Desktop = [System.Environment]::GetFolderPath('Desktop'); "
set "PS_COMMAND=!PS_COMMAND! $ShortcutPath = Join-Path $Desktop '%SHORTCUT_NAME%'; "
set "PS_COMMAND=!PS_COMMAND! $Shortcut = $WshShell.CreateShortcut($ShortcutPath); "
set "PS_COMMAND=!PS_COMMAND! $Shortcut.TargetPath = '%TARGET_FILE%'; "
set "PS_COMMAND=!PS_COMMAND! $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; "
if exist "%ICON_FILE%" (
    set "PS_COMMAND=!PS_COMMAND! $Shortcut.IconLocation = '%ICON_FILE%'; "
)
set "PS_COMMAND=!PS_COMMAND! $Shortcut.Description = 'Nástroje pro zpracování dokumentace OP JAK'; "
set "PS_COMMAND=!PS_COMMAND! $Shortcut.Save()"

powershell -ExecutionPolicy Bypass -Command "!PS_COMMAND!"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              ✅ INSTALACE ÚSPĚŠNĚ DOKONČENA!                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause