@echo off
echo ElektronApp - Python 3.13 Setup (nejnovější verze)
echo.

REM Kontrola Python 3.13
python --version | findstr "3.13" >nul
if errorlevel 1 (
    echo VAROVANI: Detekovan Python jine verze nez 3.13
    echo Doporucujeme Python 3.13 pro nejlepsi kompatibilitu
    echo.
    echo Stahujte z: https://www.python.org/downloads/
    echo.
)

REM Vytvoř prostředí
echo Vytvarim Python prostredi...
python -m venv electron-app-env

REM Upgrade pip na nejnovější
echo Aktualizuji pip...
electron-app-env\Scripts\python.exe -m pip install --upgrade pip

REM Nainstaluj nejnovější verze všech knihoven
echo Instaluji nejnovesi verze knihoven...

electron-app-env\Scripts\pip.exe install flask flask-cors
electron-app-env\Scripts\pip.exe install pandas numpy
electron-app-env\Scripts\pip.exe install xlwings openpyxl
electron-app-env\Scripts\pip.exe install reportlab
electron-app-env\Scripts\pip.exe install requests beautifulsoup4
electron-app-env\Scripts\pip.exe install python-dateutil pytz

REM Test instalace
echo.
echo Testuji instalaci...
electron-app-env\Scripts\python.exe -c "import pandas, numpy, flask, xlwings; print('Vsechny knihovny uspesne nainstalovany!')"

if errorlevel 1 (
    echo.
    echo CHYBA: Nektera knihovna se nepodarila nainstalovat
    echo Zkuste jiny installer script
    pause
    exit /b 1
)

echo.
echo ===================================
echo INSTALACE DOKONCENA USPESNE!
echo Python 3.13 + nejnovesi knihovny
echo ===================================
echo.
pause