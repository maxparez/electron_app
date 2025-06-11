# 🧪 Testovací scénář - Windows 11 Sandbox

## 📋 Příprava Windows Sandbox

### 1. Aktivace Windows Sandbox
```powershell
# Spustit PowerShell jako administrátor
Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
```

### 2. Vytvoření sandbox konfigurace
Vytvořte soubor `electron-app-test.wsb`:
```xml
<Configuration>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\electron_app_test</HostFolder>
      <SandboxFolder>C:\electron_app</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell.exe -ExecutionPolicy Bypass -File C:\electron_app\sandbox-setup.ps1</Command>
  </LogonCommand>
  <MemoryInMB>4096</MemoryInMB>
</Configuration>
```

## 🚀 Testovací postup

### Krok 1: Příprava souborů
1. Stáhněte aplikaci z GitHubu jako ZIP
2. Rozbalte do `C:\electron_app_test`
3. Vytvořte `sandbox-setup.ps1` v hlavní složce:

```powershell
# sandbox-setup.ps1
Write-Host "=== INSTALACE ELECTRON APP V SANDBOX ==="
Set-Location C:\electron_app

# 1. Instalace základních programů
Write-Host "`n[1/4] Stahování instalátorů..."

# Python 3.13
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe" -OutFile "python-installer.exe"
Start-Process -FilePath "python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait

# Node.js LTS
Invoke-WebRequest -Uri "https://nodejs.org/dist/v20.18.2/node-v20.18.2-x64.msi" -OutFile "node-installer.msi"
Start-Process msiexec.exe -ArgumentList "/i", "node-installer.msi", "/quiet" -Wait

# Git (volitelné)
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.47.0.windows.2/Git-2.47.0.2-64-bit.exe" -OutFile "git-installer.exe"
Start-Process -FilePath "git-installer.exe" -ArgumentList "/SILENT" -Wait

Write-Host "`n[2/4] Restartování PATH..."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "`n[3/4] Kontrola instalací..."
python --version
node --version
git --version

Write-Host "`n[4/4] Spouštím instalaci aplikace..."
Start-Process cmd -ArgumentList "/c install-windows.bat" -Wait -NoNewWindow

Write-Host "`n✅ Instalace dokončena! Můžete spustit aplikaci."
```

### Krok 2: Spuštění sandbox
1. Dvojklik na `electron-app-test.wsb`
2. Počkejte na dokončení automatické instalace (cca 5-10 minut)
3. Po dokončení uvidíte zprávu "✅ Instalace dokončena!"

### Krok 3: Test aplikace
1. Spusťte aplikaci dvojklikem na "Nástroje OP JAK" na ploše
2. Nebo otevřete CMD a spusťte: `cd C:\electron_app && start-app.bat`

## ✅ Testovací checklist

### Instalace
- [ ] Python 3.13 se nainstaloval správně
- [ ] Node.js se nainstaloval správně
- [ ] Git se nainstaloval správně (volitelné)
- [ ] install-windows.bat proběhl bez chyb
- [ ] Vytvořil se zástupce na ploše
- [ ] Virtuální prostředí (venv) bylo vytvořeno

### Spuštění aplikace
- [ ] Aplikace se spustí dvojklikem na zástupce
- [ ] Backend (Python) se spustí na pozadí
- [ ] Frontend (Electron) se zobrazí správně
- [ ] Všechna 3 tlačítka nástrojů jsou viditelná

### Test nástrojů
#### 1. Inovativní vzdělávání
- [ ] Lze vybrat šablonu (16h nebo 32h)
- [ ] Lze vybrat soubory k zpracování
- [ ] Zpracování proběhne bez chyb
- [ ] Výstupní soubory se vytvoří správně

#### 2. Speciální data ZoR
- [ ] Lze vybrat složku nebo soubory
- [ ] Zpracování vytvoří HTML report
- [ ] Seznam žáků se vygeneruje správně

#### 3. Generátor plakátů
- [ ] Lze vložit projekty (oddělené ; nebo tab)
- [ ] PDF plakáty se vygenerují
- [ ] Automatické ukládání funguje

### Chybové stavy
- [ ] Aplikace správně hlásí chyby při špatných datech
- [ ] Chybové hlášky jsou v češtině a srozumitelné
- [ ] Aplikace nezamrzne při chybě

## 🔍 Co sledovat

### Logy
- Zkontrolujte složku `logs\electron.log` pro chyby
- Backend logy jsou vidět v černém okně na pozadí

### Časté problémy v sandbox
1. **Pomalá instalace** - sandbox má omezené prostředky
2. **Chybí Excel** - některé funkce vyžadují MS Office
3. **Síťové problémy** - sandbox může mít omezený přístup

## 📊 Reportování výsledků

Po dokončení testu zaznamenejte:
1. Verze nainstalovaných programů
2. Čas instalace
3. Všechny chyby nebo varování
4. Screenshot hlavního okna aplikace
5. Výkon aplikace (rychlost odezvy)

## 🔄 Opakování testu

Pro čistý test:
1. Zavřete sandbox (automaticky se vymaže)
2. Spusťte znovu `electron-app-test.wsb`
3. Vše začne od začátku

---
*Testovací scénář v1.0 - leden 2025*