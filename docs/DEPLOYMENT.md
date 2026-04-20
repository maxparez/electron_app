# Deployment Guide - Nástroje pro ŠI a ŠII OP JAK

## Přehled

Tato příručka popisuje nasazení aplikace na Windows 11 včetně recovery mechanismů, aktualizací a správy logů.

## Funkce pro produkční nasazení

### 1. Auto-recovery po pádu

Backend Python server má implementovaný automatický restart po pádu:

- **Max pokusů:** 5 (konfigurovatelné)
- **Zpoždění restartu:** 3-60 sekund (adaptivní)
- **Crash log:** Ukládá se do `%APPDATA%/NastrojeOPJAK/logs/crash-*.json`

### 2. Logging systém

Aplikace loguje do souborů:

- **Python backend:** 
  - `logs/server_YYYYMMDD.log` - všechny logy
  - `logs/server_errors_YYYYMMDD.log` - pouze chyby
  - `logs/tools_YYYYMMDD.log` - logy z nástrojů

- **Electron frontend:**
  - Console logy v main procesu
  - Crash logy při pádu backendu

### 3. Konfigurace

Dva konfigurační soubory:

- `config/production.json` - produkční nastavení
- `config/development.json` - vývojové nastavení

Uživatelská konfigurace: `%APPDATA%/NastrojeOPJAK/config.json`

### 4. Update mechanismus

- Kolegové instalují a aktualizují aplikaci ze zjednodušené větve `windows-install`
- Pro řízené testování lze existující instalaci přepnout na `windows-install-test`
- Instalace probíhá přes `install.bat` / `install-windows-standalone.bat`
- Aktualizace probíhá manuálně přes `update.bat` / `update-windows.bat`
- Skripty synchronizují pouze curated obsah, respektují aktivní update kanál z `channel-config.json` a následně zkontrolují Python a Node.js závislosti

## Instalace

### 1. Build aplikace

```bash
# Development
npm run dev

# Production build
npm run make
```

### 2. Výstupní soubory

Po buildu najdete instalátor v:
```
out/make/squirrel.windows/x64/ProjektovaDokumentace-Setup.exe
```

### 3. Požadavky na systém

- Windows 10/11
- MS Office s Excel (pro xlwings)
- .NET Framework 4.7.2+
- 4GB RAM minimum
- 500MB volného místa

## Struktura složek po instalaci

```
C:\Program Files\NastrojeOPJAK\
├── NastrojeOPJAK.exe
├── resources/
│   ├── app.asar
│   ├── python/
│   └── venv/
└── locales/

%APPDATA%\NastrojeOPJAK\
├── config.json
├── logs/
│   ├── server_20250105.log
│   ├── server_errors_20250105.log
│   └── crash-1704456789.json
└── Cache/
```

## Spuštění a zastavení

### Normální spuštění
- Dvojklik na ikonu aplikace
- Python backend se spustí automaticky

### Recovery po pádu
- Backend se automaticky restartuje (max 5x)
- Uživatel je informován po vyčerpání pokusů
- Možnost manuálního restartu přes UI

### Ukončení
- Zavření okna aplikace
- Backend se ukončí automaticky

## Debug režim

Pro troubleshooting lze spustit v debug režimu:

```bash
# Windows Command Prompt
set FLASK_DEBUG=true
NastrojeOPJAK.exe

# PowerShell
$env:FLASK_DEBUG="true"
.\NastrojeOPJAK.exe
```

## Řešení problémů

### Backend se nespouští

1. Zkontrolujte logy v `%APPDATA%/NastrojeOPJAK/logs/`
2. Ověřte, že port 5000 není obsazený
3. Restartujte aplikaci

### Excel soubory se nezpracovávají

1. Ověřte instalaci MS Office
2. Zkontrolujte oprávnění k souborům
3. Ujistěte se, že Excel není otevřený

### Aktualizace se nestahuje

1. Zkontrolujte internetové připojení
2. Ověřte, že instalace pochází z git clone větve `windows-install` nebo `windows-install-test`
3. Spusťte `update-windows.bat` z instalační složky znovu

## Monitorování

### Log soubory

Pravidelně kontrolujte:
- Velikost log souborů (automaticky se mažou po 30 dnech)
- Chybové logy pro opakující se problémy
- Crash logy pro analýzu pádů

### Metriky

Sledujte:
- Počet restartů backendu
- Doba zpracování souborů
- Využití paměti

## Aktualizace

### Aktuální postup pro kolegy

1. Otevřete instalační složku aplikace
2. Spusťte `update-windows.bat` nebo `update.bat`
3. Skript synchronizuje větev uloženou v `channel-config.json`

### Přepnutí kanálu

První přepnutí na testovací kanál:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update_windows.ps1 -Branch windows-install-test
```

Návrat na stabilní kanál:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update_windows.ps1 -Branch windows-install
```

Každá aktualizace ukládá transcript do `logs\update\`. Testovací kanál navíc zapisuje start aplikace do `logs\launcher\` a backend se hlásí jako `test` kanál v runtime konfiguraci.
4. Skript podle potřeby aktualizuje Python a Node.js závislosti

## Bezpečnost

- Aplikace běží pouze lokálně (localhost:5000)
- Žádná externí komunikace kromě instalace a ruční aktualizace z GitHubu
- Logy neobsahují citlivá data
- Uživatelská data zůstávají lokální

## Podpora

Pro hlášení problémů:
1. Sesbírejte logy z `%APPDATA%/NastrojeOPJAK/logs/`
2. Popište kroky k reprodukci
3. Vytvořte issue na GitHub
