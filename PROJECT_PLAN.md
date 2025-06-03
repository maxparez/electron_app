# Plán projektu - Electron App pro zpracování projektové dokumentace

## Přehled projektu

### Účel
Vytvoření jednotné desktopové aplikace pro zpracování projektové dokumentace škol v rámci projektů OP JAK. Aplikace nahradí 3 samostatné Python skripty jedním uživatelsky přívětivým nástrojem.

### Cílová skupina
- 10 kolegů z práce (administrativní pracovníci)
- Běžní uživatelé PC bez IT znalostí
- Potřebují jednoduché a spolehlivé řešení

### Hlavní cíle
1. Jednotné uživatelské rozhraní pro všechny nástroje
2. Jednoduchá instalace (jeden .exe soubor)
3. Zachování všech funkcí původních skriptů
4. Multiplatformní podpora (primárně Windows)

## Nástroje k implementaci

### 1. Inv Vzd Copy (PRIORITA 1) ✅ VYLEPŠENO
- **Funkce**: Zpracování docházky inovativního vzdělávání
- **Vstup**: Excel soubory s docházkou (16/32 hodin)
- **Výstup**: Vyplněné oficiální šablony s zachovaným formátováním
- **Kritické**: Musí zachovat makra, vzorce, formátování
- **Vylepšení (2025-01-06)**:
  - Detailní validační chyby s čísly buněk (např. "Chybí datum v buňce Z6")
  - Per-file zpracování s izolovanými logy
  - Automatické pokračování při chybách
  - Čisté UI s rozbalovacími detaily

### 2. Zor Spec Dat (PRIORITA 2)
- **Funkce**: Zpracování docházky z různých tříd
- **Vstup**: Excel soubory s docházkou + šablona
- **Výstup**: 
  - Vyplněné oficiální dokumenty
  - HTML report se souhrnem
  - Seznam unikátních žáků
- **Proces**: Iterativní zpracování všech souborů

### 3. Plakát Generátor (PRIORITA 3)
- **Funkce**: Hromadné generování PDF plakátů
- **Vstup**: Seznam projektů z Excelu
- **Výstup**: PDF plakáty A3
- **Implementace**: Přepis z webové aplikace do Pythonu

## Technické řešení

### Architektura
- **Frontend**: Electron (Node.js)
- **Backend**: Python server (Flask/FastAPI)
- **Komunikace**: REST API přes localhost

### Klíčové technologie
- **Electron**: UI framework
- **Python**: Business logika
- **xlwings**: Zachování Excel formátování (Windows only)
- **PyInstaller**: Balení Python části
- **Electron Forge**: Vytvoření instalátoru

## Časový harmonogram

### Fáze 1: Příprava prostředí (Týden 1) ✅
- [x] Nastavení vývojového prostředí WSL Ubuntu
- [x] Instalace a konfigurace MCP serverů
- [x] Vytvoření základní struktury projektu
- [x] Import legacy kódu

### Fáze 2: Python Backend (Týdny 2-3) ✅
- [x] Refaktoring inv_vzd_copy.py ✅ InvVzdProcessor
- [x] Refaktoring zor_spec_dat.py ✅ ZorSpecDatProcessor  
- [x] Přepis plakat_gen do Pythonu ✅ PlakatGenerator
- [x] Vytvoření REST API ✅ Flask server

### Fáze 3: Electron Frontend (Týdny 4-5) ✅
- [x] Základní UI s navigací ✅
- [x] Implementace jednotlivých nástrojů ✅
- [x] Integrace s Python backendem ✅
- [x] Testování komunikace ✅
- [x] **BONUS:** Progress indikátory, auto-save, config systém

### Fáze 4: Testování a finalizace (Týden 6) 🔄
- [x] Uživatelské testování nových funkcí ✅
- [x] Oprava chyb v InvVzd nástroji ✅
  - [x] Per-file error isolation
  - [x] Specifické chybové hlášky s čísly buněk
  - [x] UI zobrazuje detaily validace
- [ ] Testování na Windows s xlwings (PŘIPRAVENO)
- [ ] Vytvoření Windows instalátoru  
- [ ] Dokumentace pro uživatele
- [ ] Nasazení a distribuce

## Struktura projektu

```
/root/vyvoj_sw/electron_app/
├── legacy_code/          # Původní Python skripty
│   ├── inv_vzd_copy.py
│   ├── zor_spec_dat.py
│   └── test_data/
├── docs/                 # Projektová dokumentace
│   ├── PROJECT_PLAN.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── ARCHITECTURE.md
├── src/
│   ├── electron/        # Frontend
│   │   ├── main.js
│   │   ├── renderer/
│   │   └── assets/
│   └── python/          # Backend
│       ├── server.py
│       ├── tools/
│       └── templates/
├── tests/               # Testy
├── dist/               # Výstupní buildy
└── package.json

```

## Rizika a řešení

| Riziko | Pravděpodobnost | Dopad | Řešení | Status |
|--------|-----------------|-------|---------|---------|
| xlwings kompatibilita | Střední | Vysoký | Fallback na openpyxl pro základní funkce | ✅ Vyřešeno |
| Velikost instalátoru | Vysoká | Nízký | Optimalizace, odstranění nepotřebných knihoven | 🔄 |
| Různé verze Windows | Nízká | Střední | Testování na Win 10/11 | 🔄 |
| Antivirus blokace | Střední | Vysoký | Code signing certificate | ⏳ |
| Validační chyby | - | - | - | ✅ Vyřešeno |

## Úspěšné dokončení

Projekt bude považován za úspěšný když:
1. ✅ Všechny 3 nástroje fungují správně **SPLNĚNO**
2. 🔄 Instalace je jednoduchá (jeden .exe) **V PŘÍPRAVĚ**
3. ✅ Uživatelé nepotřebují školení **SPLNĚNO** - intuitivní UI
4. ✅ Aplikace je stabilní a rychlá **SPLNĚNO**
5. ✅ Zachovány všechny funkce původních skriptů **SPLNĚNO + VYLEPŠENO**

### Bonus funkce implementované:
- ✅ Auto-save s výběrem složky
- ✅ Paměť posledních adresářů  
- ✅ Progress indikátory
- ✅ Czech lokalizace
- ✅ Vylepšený plakát generátor

## Poznámky
- Vývoj bude probíhat postupně bez časového tlaku
- Důraz na kvalitu a použitelnost
- Původní skripty zůstanou k dispozici jako záloha
- Průběžné testování s reálnými daty

## Aktuální stav (2025-01-06)
- **Branch**: deployment-windows
- **Připravenost**: 98% - čeká se pouze na Windows deployment
- **InvVzd nástroj**: Plně funkční s vylepšeným error handlingem
- **UI/UX**: Modernizováno, intuitivní ovládání
- **Poslední úpravy**: Per-file error isolation, specifické validační chyby