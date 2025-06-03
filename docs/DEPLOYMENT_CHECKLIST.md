# 📋 Deployment Checklist - ElektronApp

**Kompletní checklist pro vytvoření distribučního balíčku**

---

## 🔧 Příprava před buildem

### ✅ Ověření kódu
- [ ] Všechny TODO úkoly dokončeny
- [ ] Kód je commited do git
- [ ] Verze v package.json aktualizována
- [ ] Všechny nástroje testovány a funkční
- [ ] requirements.txt obsahuje správné verze

### ✅ Dokumentace
- [ ] README-instalace.md aktualizován
- [ ] DEPLOYMENT_PLAN.md je aktuální
- [ ] Troubleshooting sekce kompletní

---

## 🏗️ Build proces

### Krok 1: Příprava prostředí
```bash
# Ujistěte se, že jste v project root
cd /root/vyvoj_sw/electron_app

# Aktivujte Python venv
source venv/bin/activate

# Aktualizujte Node.js dependencies
npm install

# Vyčistěte předchozí builds
rm -rf dist/ out/
```

### Krok 2: Build launcher
```bash
# Vytvoř launcher.exe
npm run build-launcher

# Ověř výstup
ls -la dist/launcher*
```

### Krok 3: Build Electron aplikace
```bash
# Vytvoř Windows installer
npm run make

# Nebo specificky pro Windows
npm run make-launcher

# Ověř výstupy
ls -la out/
```

### Krok 4: Příprava distribučního balíčku
```bash
# Vytvoř distribuční složku
mkdir -p dist/ElektronApp-v1.0

# Zkopíruj všechny potřebné soubory
cp out/make/squirrel.windows/x64/ElektronApp-Setup.exe dist/ElektronApp-v1.0/
cp python-backend-install.bat dist/ElektronApp-v1.0/
cp requirements.txt dist/ElektronApp-v1.0/
cp README-instalace.md dist/ElektronApp-v1.0/
cp dist/launcher.exe dist/ElektronApp-v1.0/ 2>/dev/null || cp dist/launcher.bat dist/ElektronApp-v1.0/
```

---

## 📦 Struktura distribučního balíčku

```
ElektronApp-v1.0/
├── 📄 README-instalace.md           # Hlavní návod (POVINNÝ)
├── 🎥 video-tutorial.mp4            # 5min video návod (VYTVOŘIT)
├── ⚙️ ElektronApp-Setup.exe         # Electron frontend installer
├── 🐍 python-backend-install.bat    # Python backend auto-setup
├── 📝 requirements.txt              # Python závislosti
└── 🚀 launcher.exe                  # Hlavní spouštěč (nebo launcher.bat)
```

---

## 🧪 Testovací proces

### Pre-release testování

#### Test 1: Čistá Windows instalace
- [ ] Virtuální nebo čistý Windows počítač
- [ ] Žádný Python předinstalovaný
- [ ] Test kompletní instalace od začátku
- [ ] Dokumentace všech kroků

#### Test 2: Windows s existujícím Python
- [ ] Windows s Python již nainstalovaným
- [ ] Test možných konfliktů
- [ ] Ověření venv izolace

#### Test 3: Antivirus test
- [ ] Test s Windows Defender
- [ ] Test s komerčním antivirem (pokud dostupný)
- [ ] Dokumentace potřebných výjimek

### Beta test se skutečnými uživateli

#### Beta testeři (2-3 lidé)
- [ ] Osoba 1: [jméno] - Windows 10, Excel 2019
- [ ] Osoba 2: [jméno] - Windows 11, Excel 365
- [ ] Osoba 3: [jméno] - Windows 10, Excel 2016

#### Beta test checklist
- [ ] Poslat distribuční balíček beta testerům
- [ ] Poskytnout kontakt pro okamžitou podporu
- [ ] Dokumentovat všechny problémy
- [ ] Sesbírat feedback k instalačnímu procesu
- [ ] Otestovat všechny 3 nástroje na reálných datech

---

## 📞 Podpora během nasazení

### Příprava support materiálů

#### Video tutorial (5 minut)
- [ ] **Úvod** (30s): Co aplikace dělá
- [ ] **Instalace** (2min): Krok za krokem
- [ ] **První spuštění** (1min): Ukázka menu
- [ ] **Základní použití** (1.5min): Každý nástroj

#### Troubleshooting materiály
- [ ] FAQ dokument
- [ ] Screenshot galerie častých chyb
- [ ] Kontaktní informace
- [ ] Remote support nástroje (TeamViewer, atd.)

### Roll-out plán

#### Fáze 1: Pilotní skupina (2-3 lidé)
- [ ] Osobní instalace s podporou
- [ ] Týden testování
- [ ] Feedback a úpravy

#### Fáze 2: Rozšířené testování (další 3-4 lidé)
- [ ] Samoobslužná instalace s dokumentací
- [ ] Podpora na vyžádání
- [ ] Dva týdny používání

#### Fáze 3: Plné nasazení (zbývající uživatelé)
- [ ] Distribuční balíček + dokumentace
- [ ] Group training session (volitelně)
- [ ] Pravidelný check-in první měsíc

---

## 🔍 Kvalitní kontrola

### Finální ověření před distribucí

#### Soubory a obsah
- [ ] Všechny soubory v distribučním balíčku přítomny
- [ ] README-instalace.md neobsahuje chyby
- [ ] Video tutorial funguje a je srozumitelný
- [ ] python-backend-install.bat má správné kódování (UTF-8)

#### Funkčnost
- [ ] ElektronApp-Setup.exe se spustí bez chyb
- [ ] python-backend-install.bat projde bez problémů
- [ ] launcher.exe spustí oba procesy
- [ ] Všechny 3 nástroje fungují správně
- [ ] Správné ukončení všech procesů

#### Uživatelská zkušenost
- [ ] Instalační proces trvá méně než 10 minut
- [ ] Návod je jasný a srozumitelný
- [ ] Chybové hlášky jsou v češtině
- [ ] Aplikace se spouští do 15 sekund

---

## 📊 Metriky úspěchu

### Cíle pro nasazení
- [ ] **90%+ úspěšnost instalace** - méně než 1 z 10 má vážné problémy
- [ ] **Průměrný čas instalace < 10 minut** - včetně Python setup
- [ ] **Žádné data corruption** - všechny nástroje zachovávají data integrity
- [ ] **Pozitivní feedback** - uživatelé aplikaci preferují před původními skripty

### Sledování problémů
- [ ] **Log všech instalačních problémů**
- [ ] **Časová razítka všech kroků**
- [ ] **Verze komponent** (Windows, Excel, Python)
- [ ] **Error kódy a zprávy**

---

## 🚀 Spuštění do produkce

### Finální distribuční balíček

#### Vytvoření ZIP archivu
```bash
# Vytvoř finální ZIP
cd dist/
zip -r ElektronApp-v1.0.zip ElektronApp-v1.0/

# Ověř velikost (měla by být < 100MB bez video)
ls -lh ElektronApp-v1.0.zip

# Testuj ZIP - rozbal a otestuj na jiném počítači
```

#### Distribuční kanály
- [ ] **Email distribuce** - poslat zip + instrukce
- [ ] **Síťová složka** - umístit na společný disk
- [ ] **Cloud storage** - OneDrive/Google Drive link
- [ ] **Fyzické médium** - USB flash disk (backup)

### Post-launch podpora

#### První týden
- [ ] Denní check-in s každým uživatelem
- [ ] Okamžitá reakce na problémy
- [ ] Dokumentace všech issues

#### První měsíc
- [ ] Týdenní status update
- [ ] Shromažďování návrhů na vylepšení
- [ ] Plánování future updates

---

## ✅ Sign-off

### Před odesláním uživatelům

**Technical Lead**: [ ] Všechny nástroje testovány a funkční  
**QA**: [ ] Instalační proces ověřen na 3+ platformách  
**Documentation**: [ ] Všechny návody kompletní a aktuální  
**Project Manager**: [ ] Podporové procesy připraveny  

**Datum release**: _________________  
**Verze**: v1.0.0  
**Release notes**: Připojeny v README-instalace.md  

---

*Vytvořeno: 2025-06-03*  
*Pro projekt: ElektronApp v1.0*  
*Poslední aktualizace: [datum]*