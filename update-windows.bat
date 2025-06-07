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

echo [1/4] Stahuji nejnovější verzi z GitHubu...
git pull origin main
if errorlevel 1 (
    echo ⚠️  Pokus o aktualizaci z hlavní větve...
    git pull origin deployment-windows
    if errorlevel 1 (
        echo ❌ CHYBA: Nepodařilo se stáhnout aktualizace!
        echo Možné příčiny:
        echo - Nemáte připojení k internetu
        echo - Máte lokální změny v souborech
        echo.
        echo Zkuste: git status
        pause
        exit /b 1
    )
)
echo ✅ Kód aktualizován

echo.
echo [2/4] Aktivuji virtuální prostředí...
call venv\Scripts\activate.bat

echo [3/4] Aktualizuji Python knihovny...
pip install -r requirements-windows.txt --upgrade
if errorlevel 1 (
    echo ⚠️  VAROVÁNÍ: Některé knihovny se nepodařilo aktualizovat
)

echo.
echo [4/4] Aktualizuji Node.js moduly...
call npm update
if errorlevel 1 (
    echo ⚠️  VAROVÁNÍ: Některé Node.js moduly se nepodařilo aktualizovat
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ✅ AKTUALIZACE DOKONČENA!                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Co je nového můžete zjistit příkazem: git log --oneline -10
echo.
pause