@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo     ElektronApp - Python Backend Setup
echo ========================================
echo.
echo Nastavuji Python prostředí pro ElektronApp...
echo.

REM Kontrola Python instalace
echo [1/4] Kontroluji Python instalaci...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ CHYBA: Python není nainstalován!
    echo.
    echo Prosím nainstalujte Python z:
    echo https://www.python.org/downloads/
    echo.
    echo Nebo z Microsoft Store:
    echo https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K
    echo.
    echo Po instalaci spusťte tento script znovu.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% nalezen

REM Kontrola pip
echo.
echo [2/4] Kontroluji pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CHYBA: pip není dostupný
    echo Prosím reinstalujte Python s pip podporou
    pause
    exit /b 1
)
echo ✅ pip je dostupný

REM Vytvoření nebo kontrola venv
echo.
echo [3/4] Připravuji Python prostředí...
if not exist electron-app-env (
    echo 🔧 Vytvářím nové Python prostředí (electron-app-env)...
    python -m venv electron-app-env
    if errorlevel 1 (
        echo ❌ CHYBA: Nepodařilo se vytvořit Python prostředí
        echo Zkontrolujte oprávnění a místo na disku
        pause
        exit /b 1
    )
    echo ✅ Python prostředí vytvořeno
) else (
    echo ✅ Python prostředí již existuje
)

REM Kontrola existence requirements.txt
if not exist requirements.txt (
    echo ❌ CHYBA: Soubor requirements.txt nebyl nalezen
    echo Zkontrolujte, že jste spustili script ve správné složce
    pause
    exit /b 1
)

REM Instalace závislostí
echo.
echo [4/4] Instaluji Python knihovny...
echo 📦 Toto může trvat několik minut...
echo.

electron-app-env\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
electron-app-env\Scripts\pip.exe install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ CHYBA: Nepodařilo se nainstalovat některé závislosti
    echo.
    echo Možná řešení:
    echo - Zkontrolujte připojení k internetu
    echo - Spusťte jako administrátor
    echo - Zkontrolujte antivirus nastavení
    echo.
    pause
    exit /b 1
)

REM Ověření klíčových knihoven
echo.
echo 🔍 Ověřuji instalaci...
electron-app-env\Scripts\python.exe -c "import flask, pandas, openpyxl; print('✅ Základní knihovny OK')" 2>nul
if errorlevel 1 (
    echo ⚠️  Varování: Některé knihovny nemusí být správně nainstalovány
) else (
    echo ✅ Všechny knihovny úspěšně nainstalovány
)

REM Závěrečná zpráva
echo.
echo ========================================
echo ✅ INSTALACE DOKONČENA ÚSPĚŠNĚ!
echo ========================================
echo.
echo Backend je připraven k použití.
echo.
echo Nyní můžete:
echo 1. Spustit aplikaci kliknutím na ikonu "ElektronApp"
echo 2. Nebo spustit "launcher.exe" 
echo.
echo V případě problémů kontaktujte podporu.
echo.
echo Stiskněte libovolnou klávesu pro ukončení...
pause >nul

REM Cleanup
endlocal