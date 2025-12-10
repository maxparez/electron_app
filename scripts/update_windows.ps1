<#
.SYNOPSIS
    Aktualizace instalace aplikace Nástroje OP JAK na Windows.
.DESCRIPTION
    Skript obnoví repozitář z větve windows-install, zaktualizuje Python i
    Node závislosti a volitelně spustí test.
#>
param(
    [string]$InstallRoot = "C:\OPJAK",
    [string]$Branch = "windows-install",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Ensure-Command {
    param(
        [string]$CommandName,
        [string]$DisplayName,
        [string]$DownloadUrl
    )
    try {
        $null = Get-Command $CommandName -ErrorAction Stop
    }
    catch {
        Write-Host ("{0} chybí ({1})" -f $DisplayName, $DownloadUrl) -ForegroundColor Red
        exit 1
    }
}

Ensure-Command -CommandName "git" -DisplayName "Git for Windows" -DownloadUrl "https://git-scm.com/download/win"
Ensure-Command -CommandName "python" -DisplayName "Python 3.11+" -DownloadUrl "https://www.python.org/downloads/"
Ensure-Command -CommandName "npm" -DisplayName "Node.js 18 LTS" -DownloadUrl "https://nodejs.org/"

$repoPath = Join-Path $InstallRoot "electron_app"
if (-not (Test-Path $repoPath)) {
    Write-Host "Instalace nebyla nalezena v $repoPath. Spusťte nejprve install_windows.ps1." -ForegroundColor Red
    exit 1
}

Write-Step "Aktualizace zdrojového kódu"
Push-Location $repoPath
git fetch origin
git checkout $Branch
git reset --hard ("origin/{0}" -f $Branch)
git clean -fd
$currentCommit = (git rev-parse --short HEAD)
Pop-Location
Write-Host ("Aktualizováno na commit {0}" -f $currentCommit)

Write-Step "Python virtuální prostředí"
$venvPath = Join-Path $repoPath "venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$systemPython = (Get-Command python).Source
if (-not (Test-Path $venvPython)) {
    Write-Host "Vytvářím nové virtualenv..." -ForegroundColor Yellow
    & $systemPython -m venv $venvPath
    $venvPython = Join-Path $venvPath "Scripts\python.exe"
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $repoPath "requirements-windows.txt")

Write-Step "Node.js závislosti"
Push-Location $repoPath
npm install --production
Pop-Location

if (-not $SkipTests) {
    Write-Step "Test: students_16plus"
    try {
        & $venvPython -m pytest tests/test_students_16plus.py
    }
    catch {
        Write-Host "Test selhal, zkontrolujte logy v adresáři tests." -ForegroundColor Yellow
    }
}

Write-Step "Aktualizace dokončena"
Write-Host "Aplikaci můžete spustit zástupcem nebo start-app.bat." -ForegroundColor Green
