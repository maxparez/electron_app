<#
.SYNOPSIS
    Kompletní instalace aplikace Nástroje OP JAK na Windows.
.DESCRIPTION
    Skript ověří přítomnost všech závislostí, připraví složku s projektem
    z větve windows-install, vytvoří Python virtual environment, nainstaluje
    Node moduly a přidá zástupce na plochu.
#>
param(
    [string]$RepoUrl = "https://github.com/maxparez/electron_app.git",
    [string]$Branch = "",
    [string]$InstallRoot = "C:\OPJAK"
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Test-Dependency {
    param(
        [string]$CommandName,
        [string]$DisplayName,
        [string]$DownloadUrl
    )
    try {
        $null = Get-Command $CommandName -ErrorAction Stop
        return $true
    }
    catch {
        Write-Host ("- {0} chybí ({1})" -f $DisplayName, $DownloadUrl) -ForegroundColor Yellow
        return $false
    }
}

function Get-DefaultBranch {
    $configPath = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..")).Path "channel-config.json"
    if (-not (Test-Path $configPath)) {
        return "windows-install"
    }

    try {
        $config = Get-Content -Raw -Path $configPath | ConvertFrom-Json
        if ($config.branch) {
            return [string]$config.branch
        }
    }
    catch {
        Write-Host "Varování: channel-config.json není čitelný, používám windows-install." -ForegroundColor Yellow
    }

    return "windows-install"
}

Write-Step "Kontrola prostředí"
$requirements = @(
    @{ Command = "python"; Name = "Python 3.11+"; Url = "https://www.python.org/downloads/" },
    @{ Command = "pip"; Name = "pip"; Url = "https://pip.pypa.io/en/stable/installation/" },
    @{ Command = "node"; Name = "Node.js 18 LTS"; Url = "https://nodejs.org/" },
    @{ Command = "npm"; Name = "npm"; Url = "https://nodejs.org/" },
    @{ Command = "git"; Name = "Git for Windows"; Url = "https://git-scm.com/download/win" }
)

$missing = @()
foreach ($req in $requirements) {
    if (-not (Test-Dependency -CommandName $req.Command -DisplayName $req.Name -DownloadUrl $req.Url)) {
        $missing += $req.Name
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Instalaci nelze pokračovat. Nejprve doinstalujte výše uvedené položky." -ForegroundColor Red
    exit 1
}

if (-not $Branch) {
    $Branch = Get-DefaultBranch
}

$python = (Get-Command python).Source
$nodeVersion = (& node -v)
$pythonVersion = (& python --version)
Write-Host ("Použit Python {0}, Node {1}" -f $pythonVersion, $nodeVersion)

Write-Step "Příprava instalační složky"
if (-not (Test-Path $InstallRoot)) {
    New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
}
$repoPath = Join-Path $InstallRoot "electron_app"

if (-not (Test-Path (Join-Path $repoPath ".git"))) {
    Write-Host "Klonuji repozitář..."
    git clone -b $Branch $RepoUrl $repoPath
}
else {
    Write-Host "Větev již existuje, aktualizuji..."
    Push-Location $repoPath
    git fetch origin
    git checkout $Branch
    git reset --hard ("origin/{0}" -f $Branch)
    git clean -fd
    Pop-Location
}

Write-Step "Nastavení Python virtual environment"
$venvPath = Join-Path $repoPath "venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & $python -m venv $venvPath
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $repoPath "requirements-windows.txt")

Write-Step "Instalace Node modulů (runtime)"
Push-Location $repoPath
npm ci --omit=dev
Pop-Location

Write-Step "Rychlá kontrola backendu"
try {
    Push-Location $repoPath
    & $venvPython -m pytest tests/test_students_16plus.py
    Pop-Location
}
catch {
    Write-Host "Upozornění: test selhal, zkontrolujte logy." -ForegroundColor Yellow
}

Write-Step "Vytvářím zástupce na ploše"
$shortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "Nastroje OP JAK.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $repoPath "start-app.bat"
$shortcut.WorkingDirectory = $repoPath
$icon = Join-Path $repoPath "icon.ico"
if (Test-Path $icon) {
    $shortcut.IconLocation = $icon
}
$shortcut.Save()

Write-Step "Instalace dokončena"
Write-Host "Aplikaci spustíte dvojklikem na zástupce nebo skrze start-app.bat." -ForegroundColor Green
