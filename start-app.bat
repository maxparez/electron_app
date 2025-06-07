@echo off
chcp 65001 >nul
title Nástroje pro ŠI a ŠII OP JAK

REM Kontrola, zda je venv vytvořen
if not exist venv (
    echo ❌ CHYBA: Aplikace není nainstalována!
    echo Nejprve spusťte: install-windows.bat
    pause
    exit /b 1
)

REM Aktivace venv a spuštění
echo Spouštím aplikaci...
call venv\Scripts\activate.bat

REM Spuštění Python backendu na pozadí
start /B python src\python\server.py

REM Počkej 2 sekundy než se server nastartuje
timeout /t 2 /nobreak >nul

REM Spuštění Electron aplikace
npm start

REM Po ukončení Electronu zabij Python server
taskkill /F /IM python.exe >nul 2>&1

exit