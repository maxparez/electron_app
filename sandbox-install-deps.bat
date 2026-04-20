@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        AUTOMATICKÁ INSTALACE ZÁVISLOSTÍ PRO SANDBOX            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Python 3.13
echo [1/3] Instaluji Python 3.13...
echo Stahuji instalátor...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe' -OutFile 'python-installer.exe'"
echo Instaluji Python (tiše s PATH)...
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
echo Čekám na dokončení instalace...
timeout /t 30 /nobreak >nul

REM Node.js
echo.
echo [2/3] Instaluji Node.js LTS...
echo Stahuji instalátor...
powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.18.2/node-v20.18.2-x64.msi' -OutFile 'node-installer.msi'"
echo Instaluji Node.js...
msiexec /i node-installer.msi /quiet /norestart
echo Čekám na dokončení instalace...
timeout /t 30 /nobreak >nul

REM Git (volitelné)
echo.
echo [3/3] Instaluji Git...
echo Stahuji instalátor...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.47.0.windows.2/Git-2.47.0.2-64-bit.exe' -OutFile 'git-installer.exe'"
echo Instaluji Git...
git-installer.exe /VERYSILENT /NORESTART
echo Čekám na dokončení instalace...
timeout /t 20 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo Restartování prostředí PATH...
echo Prosím zavřete toto okno a otevřete NOVÉ CMD okno!
echo Poté spusťte: install-windows.bat
echo.
echo V novém CMD ověřte instalace pomocí:
echo   python --version
echo   node --version
echo   git --version
echo.
pause