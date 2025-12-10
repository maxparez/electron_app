@echo off
chcp 65001 >nul
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        Aktualizace - Nástroje pro ŠI a ŠII OP JAK            ║
echo ║                      Verze 1.2.0                               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Tento skript aktualizuje aplikaci na nejnovější verzi z GitHubu.
echo.
echo ⚠️  POZOR: Aktualizace přepíše všechny lokální změny v aplikaci!
echo    (Vaše data a výstupy v jiných složkách zůstanou nedotčeny)
echo.
pause
echo.

REM ========================================================================
REM FÁZE 1: Kontrola instalace
REM ========================================================================
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 1/5: Kontrola instalace                                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Zkontrolovat, že jsme ve správné složce
if not exist "package.json" (
    echo ❌ CHYBA: Tento skript musí být spuštěn ze složky aplikace!
    echo.
    echo Prosím přejděte do složky: C:\OPJAK\electron_app
    echo A spusťte: update.bat
    echo.
    pause
    exit /b 1
)

if not exist ".git" (
    echo ❌ CHYBA: Aplikace nebyla nainstalována přes Git!
    echo.
    echo Použijte raději install.bat pro čistou instalaci.
    echo.
    pause
    exit /b 1
)

echo ✅ Instalace nalezena
echo 📁 Složka: %CD%
echo.

REM ========================================================================
REM FÁZE 2: Stažení aktualizací z GitHubu
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 2/5: Stahování aktualizací                               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Stahuji nejnovější verzi z GitHubu...
git fetch origin
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se stáhnout aktualizace!
    echo Zkontrolujte připojení k internetu a zkuste znovu.
    pause
    exit /b 1
)

echo Kontroluji změny...
git diff --name-only HEAD origin/windows-install > nul
if errorlevel 1 (
    echo ✅ Aplikace je již aktuální
    echo.
    pause
    exit /b 0
)

echo Aplikuji aktualizace...
git checkout windows-install
git reset --hard origin/windows-install
git clean -fd

echo ✅ Aktualizace staženy
echo.

REM ========================================================================
REM FÁZE 3: Kontrola změn v Python závislostech
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 3/5: Aktualizace Python knihoven                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

if not exist "venv" (
    echo ⚠️  Virtuální prostředí neexistuje, vytvářím...
    python -m venv venv
)

echo Aktivuji virtuální prostředí...
call venv\Scripts\activate.bat

echo Aktualizuji pip...
python -m pip install --upgrade pip --quiet

echo Instaluji/aktualizuji Python knihovny...
pip install -r requirements-windows.txt --quiet --upgrade
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se aktualizovat Python knihovny!
    pause
    exit /b 1
)

echo ✅ Python knihovny aktualizovány
echo.

REM ========================================================================
REM FÁZE 4: Kontrola změn v Node.js závislostech
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 4/5: Aktualizace Node.js modulů                          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Instaluji/aktualizuji Node.js moduly...
call npm install --loglevel=error
if errorlevel 1 (
    echo ❌ CHYBA: Nepodařilo se aktualizovat Node.js moduly!
    pause
    exit /b 1
)

echo ✅ Node.js moduly aktualizovány
echo.

REM ========================================================================
REM FÁZE 5: Dokončení
REM ========================================================================
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║ FÁZE 5/5: Kontrola verze                                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo Aktuální verze:
git log -1 --format="  Commit: %%h%%n  Datum: %%ad%%n  Zpráva: %%s" --date=short
echo.

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║            ✅ AKTUALIZACE ÚSPĚŠNĚ DOKONČENA!                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Aplikace je nyní aktuální!
echo.
echo Můžete aplikaci spustit:
echo  • Dvojklikem na zástupce "Nástroje OP JAK" na ploše
echo  • Nebo spuštěním: start-app.bat
echo.
pause
