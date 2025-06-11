@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           RYCHLÝ TEST V WINDOWS SANDBOX                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Tento skript připraví aplikaci pro test v Windows Sandbox
echo.

REM Vytvoř testovací složku
if not exist "C:\electron_app_sandbox_test" mkdir "C:\electron_app_sandbox_test"

REM Zkopíruj aplikaci
echo [1/3] Kopíruji aplikaci...
xcopy /E /I /Y "." "C:\electron_app_sandbox_test\electron_app" >nul

REM Vytvoř sandbox konfiguraci
echo [2/3] Vytvářím sandbox konfiguraci...
(
echo ^<Configuration^>
echo   ^<MappedFolders^>
echo     ^<MappedFolder^>
echo       ^<HostFolder^>C:\electron_app_sandbox_test\electron_app^</HostFolder^>
echo       ^<SandboxFolder^>C:\electron_app^</SandboxFolder^>
echo       ^<ReadOnly^>false^</ReadOnly^>
echo     ^</MappedFolder^>
echo   ^</MappedFolders^>
echo   ^<LogonCommand^>
echo     ^<Command^>cmd.exe /c "cd C:\electron_app && echo SANDBOX TEST && timeout 5"^</Command^>
echo   ^</LogonCommand^>
echo   ^<MemoryInMB^>4096^</MemoryInMB^>
echo ^</Configuration^>
) > "C:\electron_app_sandbox_test\electron-app-test.wsb"

REM Vytvoř pomocný instalační skript
echo [3/3] Vytvářím pomocné skripty...
(
echo @echo off
echo echo.
echo echo ╔════════════════════════════════════════════════════════════════╗
echo echo ║     MANUÁLNÍ INSTALACE V SANDBOX                               ║
echo echo ╚════════════════════════════════════════════════════════════════╝
echo echo.
echo echo 1. Otevřete prohlížeč v sandbox
echo echo 2. Stáhněte a nainstalujte:
echo echo    - Python 3.13: https://www.python.org/downloads/
echo echo    - Node.js LTS: https://nodejs.org/
echo echo    - Git ^(volitelné^): https://git-scm.com/
echo echo.
echo echo 3. Po instalaci restartujte CMD a spusťte:
echo echo    cd C:\electron_app
echo echo    install-windows.bat
echo echo.
echo pause
) > "C:\electron_app_sandbox_test\electron_app\sandbox-manual-install.bat"

echo.
echo ✅ Připraveno pro sandbox test!
echo.
echo Nyní:
echo 1. Spusťte: C:\electron_app_sandbox_test\electron-app-test.wsb
echo 2. V sandbox spusťte: C:\electron_app\sandbox-manual-install.bat
echo 3. Postupujte podle instrukcí
echo.
echo Pro automatickou instalaci viz: docs\WINDOWS_SANDBOX_TEST.md
echo.
pause