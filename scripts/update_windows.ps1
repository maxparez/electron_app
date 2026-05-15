<#
.SYNOPSIS
    Aktualizace instalace aplikace Nástroje OP JAK na Windows.
.DESCRIPTION
    Skript obnoví repozitář z aktivního update kanálu nebo z explicitně zadané
    větve, zaktualizuje Python i Node závislosti a uloží detailní transcript do
    logs\update\ bez kolize s git clean.
#>
param(
    [string]$Branch = "",
    [string]$RepoPath = "",
    [string]$InstallRoot = "C:\OPJAK",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

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

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw ("git {0} failed with exit code {1}" -f ($Arguments -join " "), $LASTEXITCODE)
    }
}

function Resolve-RepoPath {
    param(
        [string]$ExplicitRepoPath,
        [string]$InstallRoot
    )

    if ($ExplicitRepoPath) {
        return (Resolve-Path $ExplicitRepoPath).Path
    }

    $scriptRepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    if (Test-Path (Join-Path $scriptRepoPath ".git")) {
        return $scriptRepoPath
    }

    return (Join-Path $InstallRoot "electron_app")
}

function Load-ChannelConfig {
    param([string]$ResolvedRepoPath)

    $defaults = @{
        channel = "stable"
        branch = "windows-install"
        debug_logging = $false
    }

    $configPath = Join-Path $ResolvedRepoPath "channel-config.json"
    if (-not (Test-Path $configPath)) {
        return [pscustomobject]$defaults
    }

    try {
        $rawConfig = Get-Content -Raw -Path $configPath | ConvertFrom-Json
        return [pscustomobject]@{
            channel = if ($rawConfig.channel) { [string]$rawConfig.channel } else { $defaults.channel }
            branch = if ($rawConfig.branch) { [string]$rawConfig.branch } else { $defaults.branch }
            debug_logging = [bool]$rawConfig.debug_logging
        }
    }
    catch {
        Write-Host "Varování: channel-config.json není čitelný, používám výchozí nastavení." -ForegroundColor Yellow
        return [pscustomobject]$defaults
    }
}

function Start-UpdateTranscript {
    param([string]$ResolvedRepoPath)

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $tempLogDir = Join-Path $env:TEMP "opjak-update-logs"
    New-Item -ItemType Directory -Force -Path $tempLogDir | Out-Null
    $tempLogPath = Join-Path $tempLogDir ("update_{0}.log" -f $timestamp)
    Start-Transcript -Path $tempLogPath -Append | Out-Null
    return $tempLogPath
}

function Stop-UpdateTranscriptSafely {
    try {
        Stop-Transcript | Out-Null
    }
    catch {
    }
}

function Publish-UpdateTranscript {
    param(
        [string]$ResolvedRepoPath,
        [string]$TempTranscriptPath
    )

    if (-not $TempTranscriptPath) {
        return $null
    }

    $logDir = Join-Path $ResolvedRepoPath "logs\update"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $finalLogPath = Join-Path $logDir ([System.IO.Path]::GetFileName($TempTranscriptPath))
    Copy-Item -Force -Path $TempTranscriptPath -Destination $finalLogPath
    return $finalLogPath
}

Ensure-Command -CommandName "git" -DisplayName "Git for Windows" -DownloadUrl "https://git-scm.com/download/win"
Ensure-Command -CommandName "python" -DisplayName "Python 3.11+" -DownloadUrl "https://www.python.org/downloads/"
Ensure-Command -CommandName "npm" -DisplayName "Node.js 18 LTS" -DownloadUrl "https://nodejs.org/"

$resolvedRepoPath = Resolve-RepoPath -ExplicitRepoPath $RepoPath -InstallRoot $InstallRoot
if (-not (Test-Path (Join-Path $resolvedRepoPath ".git"))) {
    Write-Host "Instalace nebyla nalezena v $resolvedRepoPath. Spusťte nejprve install_windows.ps1." -ForegroundColor Red
    exit 1
}

$tempTranscriptPath = Start-UpdateTranscript -ResolvedRepoPath $resolvedRepoPath
$publishedLogPath = $null
$locationPushed = $false

try {
    $initialConfig = Load-ChannelConfig -ResolvedRepoPath $resolvedRepoPath
    if (-not $Branch) {
        $Branch = $initialConfig.branch
    }
    if (-not $Branch) {
        $Branch = "windows-install"
    }

    Write-Host ("Repozitář: {0}" -f $resolvedRepoPath) -ForegroundColor Gray
    Write-Host ("Aktualizační kanál: {0}" -f $initialConfig.channel) -ForegroundColor Gray
    Write-Host ("Cílová větev: {0}" -f $Branch) -ForegroundColor Gray
    Write-Host ("Debug logging: {0}" -f $initialConfig.debug_logging) -ForegroundColor Gray
    Write-Host ("Dočasný transcript: {0}" -f $tempTranscriptPath) -ForegroundColor Gray

    Write-Step "Aktualizace zdrojového kódu"
    Push-Location $resolvedRepoPath
    $locationPushed = $true

    Invoke-Git -Arguments @("fetch", "origin")
    Invoke-Git -Arguments @("reset", "--hard", "HEAD")
    Invoke-Git -Arguments @("clean", "-fd")
    Invoke-Git -Arguments @("ls-remote", "--exit-code", "--heads", "origin", $Branch)
    Invoke-Git -Arguments @("checkout", "--force", "-B", $Branch, ("origin/{0}" -f $Branch))
    Invoke-Git -Arguments @("reset", "--hard", ("origin/{0}" -f $Branch))
    Invoke-Git -Arguments @("clean", "-fd")

    $currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
    $currentCommit = (git rev-parse --short HEAD).Trim()
    Write-Host ("Aktualizováno na větev {0}, commit {1}" -f $currentBranch, $currentCommit) -ForegroundColor Green

    $activeConfig = Load-ChannelConfig -ResolvedRepoPath $resolvedRepoPath
    if ($activeConfig.debug_logging) {
        Write-Step "Debug snapshot repozitáře"
        Invoke-Git -Arguments @("status", "--short", "--branch")
        Invoke-Git -Arguments @("log", "--oneline", "-5")
    }

    Write-Step "Python virtuální prostředí"
    $venvPath = Join-Path $resolvedRepoPath "venv"
    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    $systemPython = (Get-Command python).Source
    if (-not (Test-Path $venvPython)) {
        Write-Host "Vytvářím nové virtualenv..." -ForegroundColor Yellow
        & $systemPython -m venv $venvPath
        $venvPython = Join-Path $venvPath "Scripts\python.exe"
    }

    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r (Join-Path $resolvedRepoPath "requirements-windows.txt")

    Write-Step "Node.js závislosti"
    npm ci

    if (-not $SkipTests) {
        Write-Step "Test: students_16plus"
        try {
            & $venvPython -m pytest test_students_16plus.py
        }
        catch {
            Write-Host "Test selhal, zkontrolujte transcript a logy v adresáři logs." -ForegroundColor Yellow
        }
    }

    Write-Step "Aktualizace dokončena"
    Write-Host "Aplikaci můžete spustit zástupcem nebo start-app.bat." -ForegroundColor Green
}
finally {
    if ($locationPushed) {
        Pop-Location
    }
    Stop-UpdateTranscriptSafely
    $publishedLogPath = Publish-UpdateTranscript -ResolvedRepoPath $resolvedRepoPath -TempTranscriptPath $tempTranscriptPath
    if ($publishedLogPath) {
        Write-Host ("Log aktualizace: {0}" -f $publishedLogPath) -ForegroundColor Green
    }
}
