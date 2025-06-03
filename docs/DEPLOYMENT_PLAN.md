# Deployment Plan - Electron App

## 📋 Přehled deploymentu

**Cíl:** Vytvoření rozumného kompromisu mezi jednoduchostí pro uživatele a složitostí vývoje

**Cílová skupina:** 10 kolegů (administrativní pracovníci)

**Klíčové požadavky:**
- Jeden klik pro spuštění aplikace
- Snadná instalace s návodem
- Technicky správné řešení (venv izolace)
- Využití standardních nástrojů

## 🎯 Finální distribuční řešení

### Obsah distribučního balíčku "ElektronApp-v1.0"

```
ElektronApp-v1.0/
├── 📄 README-instalace.md           # Hlavní návod
├── 🎥 video-tutorial.mp4            # 5min video návod
├── ⚙️ ElektronApp-Setup.exe         # Electron frontend installer
├── 🐍 python-backend-install.bat    # Python backend auto-setup
├── 📝 requirements.txt              # Python závislosti
└── 🚀 launcher.exe                  # Hlavní spouštěč (po instalaci)
```

### 👥 Postup pro uživatele (3 jednoduché kroky)

1. **Spustit `ElektronApp-Setup.exe`**
   - Nainstaluje Electron frontend
   - Vytvoří ikonu na ploše
   - Nastaví základní strukturu

2. **Spustit `python-backend-install.bat`**
   - Automaticky vytvoří Python venv
   - Nainstaluje všechny závislosti
   - Ověří funkčnost

3. **Kliknout na ikonu aplikace**
   - Launcher automaticky spustí backend
   - Spustí frontend
   - Aplikace je připravena k použití

## 🔧 Technické detaily

### Struktura po instalaci

```
C:\Program Files\ElektronApp\
├── launcher.exe                     # 🎯 HLAVNÍ SPOUŠTĚČ - ikona na ploše
├── electron-app.exe                 # Frontend
├── python-backend-install.bat       # Setup script
├── requirements.txt                 # Závislosti
├── src/
│   └── python/                      # Backend kód
│       ├── server.py
│       ├── tools/
│       └── ...
└── electron-app-env/               # 🐍 Automaticky vytvořený venv
    ├── Scripts/
    │   ├── python.exe              # Izolovaný Python runtime
    │   └── pip.exe
    └── Lib/                        # Nainstalované balíčky
```

### Python backend setup script

**python-backend-install.bat:**
```bat
@echo off
echo ========================================
echo     ElektronApp - Python Backend Setup
echo ========================================
echo.

REM Kontrola Python instalace
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python není nainstalován!
    echo Prosím nainstalujte Python z https://python.org
    pause
    exit /b 1
)

echo ✅ Python nalezen

REM Vytvoření venv pokud neexistuje
if not exist "electron-app-env" (
    echo 🔧 Vytvářím Python prostředí...
    python -m venv electron-app-env
    if errorlevel 1 (
        echo ❌ Chyba při vytváření Python prostředí
        pause
        exit /b 1
    )
    echo ✅ Python prostředí vytvořeno
) else (
    echo ✅ Python prostředí již existuje
)

REM Instalace závislostí
echo 📦 Instaluji závislosti...
electron-app-env\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo ❌ Chyba při instalaci závislostí
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Backend úspěšně nainstalován!
echo ========================================
echo.
echo Nyní můžete spustit aplikaci kliknutím na ikonu
echo "ElektronApp" na ploše nebo v Start menu.
echo.
pause
```

### Launcher logika

**launcher.exe funkcionalita:**
1. **Health check backendu** - zkontroluje port 5000
2. **Spuštění backendu** - pokud neběží: `electron-app-env\Scripts\python.exe src\python\server.py`
3. **Čekání na startup** - health check každých 500ms (max 10s)
4. **Spuštění frontendu** - `electron-app.exe`
5. **Process management** - při ukončení ukončí i backend

## 📦 Vývojářský deployment checklist

### Příprava distribuce

- [ ] **Electron build**
  ```bash
  npm run make  # Vytvoří ElektronApp-Setup.exe
  ```

- [ ] **Launcher build**
  ```bash
  # Vytvoří launcher.exe s process management logikou
  ```

- [ ] **Requirements.txt aktualizace**
  ```txt
  xlwings==0.33.15
  flask==3.0.0
  pandas==2.1.4
  openpyxl==3.1.2
  numpy==1.24.3
  ```

- [ ] **Dokumentace**
  - [ ] README-instalace.md
  - [ ] Video tutorial (5 min)
  - [ ] Troubleshooting guide

### Testování před distribucí

- [ ] **Čistý Windows test**
  - [ ] Test na Windows bez Python
  - [ ] Test na Windows s existujícím Python
  - [ ] Test všech 3 nástrojů

- [ ] **Installer test**
  - [ ] Test instalace z čistého stavu
  - [ ] Test odinstalace
  - [ ] Test opakované instalace

- [ ] **User experience test**
  - [ ] Test s netechnickým uživatelem
  - [ ] Měření času instalace
  - [ ] Validace návodu

## 🎥 Podpora uživatelů

### Video tutorial obsah (5 min)

1. **Úvod** (30s)
   - Co aplikace dělá
   - Co budeme instalovat

2. **Instalace** (2min)
   - Spuštění ElektronApp-Setup.exe
   - Spuštění python-backend-install.bat
   - Vysvětlení co se děje

3. **První spuštění** (1min)
   - Klik na ikonu
   - Ukázka hlavního menu
   - Kde najít nápovědu

4. **Základní použití** (1.5min)
   - Rychlá ukázka každého nástroje
   - Kde hledat soubory

### README-instalace.md obsah

- Systémové požadavky
- Krok za krokem instalace (s obrázky)
- Troubleshooting obvyklých problémů
- Kontakt na podporu

## ⚠️ Známá rizika a řešení

| Riziko | Pravděpodobnost | Řešení |
|--------|-----------------|---------|
| Python není nainstalován | Střední | Návod na instalace Python z MS Store |
| Antivirus blokuje .exe | Střední | Instrukce pro whitelist, podepsání |
| Execution policy problém | Nízká | PowerShell alternativa pro .bat |
| Port 5000 obsazený | Nízká | Dynamická detekce volného portu |

## 🚀 Postup distribuce

1. **Vytvoření distribučního balíčku**
2. **Interní testování** (2-3 lidé)
3. **Beta test** (2-3 cíloví uživatelé)
4. **Finální distribuce** (zbývajících 5-7 lidí)
5. **Podpora a feedback**

## ✅ Výhody tohoto přístupu

**Pro uživatele:**
- Jeden klik pro spuštění
- Jasný 3-krokový návod
- Video podpora
- Individuální pomoc k dispozici

**Pro vývojáře:**
- Využívá standardní nástroje
- Snadné debugování
- Možnost rychlých updates
- Minimální custom logika

**Technické:**
- Venv izolace (žádné konflikty)
- Čisté prostředí
- Automatické process management
- Reprodukovatelná instalace

---

*Vytvořeno: 2025-06-03*  
*Status: Připraveno k implementaci*  
*Odhadovaný čas implementace: 2-3 dny*