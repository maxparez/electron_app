@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         Aktualizace - Nástroje pro ŠI a ŠII OP JAK           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Kontrola Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CHYBA: Git není nainstalován!
    echo.
    echo Pro automatické aktualizace potřebujete Git:
    echo https://git-scm.com/download/win
    echo.
    echo Nebo stáhněte novou verzi ručně z:
    echo https://github.com/maxparez/electron_app
    echo.
    pause
    exit /b 1
)

echo [1/3] Synchronizuji větev windows-install z GitHubu...
git fetch origin
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se stáhnout metadata z GitHubu!
    echo Zkontrolujte připojení k internetu a zkuste to znovu.
    pause
    exit /b 1
)

git checkout windows-install
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se přepnout na větev windows-install!
    pause
    exit /b 1
)

git reset --hard origin/windows-install
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se synchronizovat větev windows-install!
    pause
    exit /b 1
)

git clean -fd
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se stáhnout aktualizace!
    echo Možné příčiny:
    echo - Nemáte připojení k internetu
    echo - Instalace není git clone z větve windows-install
    echo.
    echo Zkuste: git status
    pause
    exit /b 1
)
echo ✅ Kód aktualizován z větve windows-install

echo.
echo [2/3] Kontroluji Python závislosti...
call venv\Scripts\activate.bat
pip check >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Nalezeny chybějící závislosti, aktualizuji...
    pip install -r requirements-windows.txt --upgrade
) else (
    echo ✅ Python knihovny jsou aktuální
)

echo.
echo [3/3] Kontroluji Node.js závislosti...
npm outdated >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Nalezeny zastaralé moduly, aktualizuji...
    call npm update
) else (
    echo ✅ Node.js moduly jsou aktuální
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ✅ AKTUALIZACE DOKONČENA!                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Co je nového můžete zjistit příkazem: git log --oneline -10
echo.
pause
