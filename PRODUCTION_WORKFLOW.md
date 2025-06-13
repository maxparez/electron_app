# 🚀 Production Workflow - Jak z dev udělat prod

## Kontext
- **Development branch**: `feature/next-phase` (300+ souborů, všechny testy, docs, legacy kód)
- **Production branch**: `production` (25 čistých souborů, jen aplikace)
- **Uživatelé**: Stahují z production branch přes `install-windows-standalone.bat`

## 📋 Postup: Dev → Prod

### 1. Dokončení vývoje na dev branch
```bash
# Práce na feature/next-phase
git checkout feature/next-phase
# ... vývoj, opravy, testy ...
git add -A && git commit -m "[fix-XXX] Popis opravy"
git push origin feature/next-phase
```

### 2. Přepnutí na production branch
```bash
git checkout production
git merge feature/next-phase
```

### 3. Vyčištění nepotřebných souborů
```bash
# Smazání vývojářských složek
rm -rf legacy_code/ docs/ logs/ tests/ _img/ out/ venv/ node_modules/ dist/

# Smazání test/debug skriptů
rm -f test_*.py debug_*.py inspect_*.py simple_test.py create_test_template.py

# Smazání dokumentace (kromě README.md)
find . -name "*.md" -not -name "README.md" -delete

# Smazání dev batch souborů
rm -f build-windows*.bat debug-*.bat sandbox-*.bat test-*.bat quick-*.bat
rm -f python-backend-install*.bat start-backend.bat start-frontend.bat start-with-python.bat

# Smazání dalších dev souborů
rm -f *.html *.sh create-desktop-shortcut.ps1 standalone-backend.py
rm -rf scripts/ config/ 

# Vyčištění Python cache a logs
find src/python -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find src/python -name "*.log" -delete

# Smazání backup souborů
rm -f src/electron/updater.js.bak
rm -rf src/electron/main/ src/python/api/

# Smazání xlsx šablon (uživatel má vlastní)
rm -f template_*.xlsx src/python/templates/template_*.xlsx
```

### 4. Kontrola čistoty
```bash
# Počet souborů (mělo by být ~25)
find . -type f -not -path "./.git/*" -not -path "./node_modules/*" | wc -l

# Velikost (mělo by být ~11MB)
du -sh .

# Seznam podstatných souborů
find . -name "*.js" -o -name "*.py" -o -name "*.bat" -o -name "*.json" -o -name "*.md" | wc -l
```

### 5. Commit a push production
```bash
git add -A
git commit -m "[prod-XXX] Update production from dev - clean build"
git push origin production
```

## 📁 Co má zůstat v production

### ✅ Nutné soubory (25x):
```
├── README.md                     # Návod pro uživatele
├── package.json, package-lock.json  # NPM závislosti
├── requirements-windows.txt      # Python závislosti  
├── forge.config.js              # Electron build config
├── install-windows-standalone.bat  # Hlavní instalátor
├── install-windows.bat          # Lokální instalátor
├── start-app.bat                # Spuštění aplikace
├── update-windows.bat           # Aktualizace
├── 4691206_electron_icon.png    # Ikona pro shortcuts
└── src/
    ├── electron/                # Frontend (10 souborů)
    │   ├── main.js, preload.js, backend-manager.js, config.js
    │   ├── renderer/ (5 souborů: html, js, css)
    │   ├── assets/ (ikony)
    │   └── locales/cs.json
    └── python/                  # Backend (8 souborů)
        ├── server.py, logger.py
        ├── tools/ (5 .py souborů)
        └── templates/ (prázdná)
```

### ❌ Co smazat (300+ souborů):
- `legacy_code/`, `docs/`, `logs/`, `tests/`, `_img/`, `out/`, `venv/`
- Všechny `test_*.py`, `debug_*.py`, `inspect_*.py` 
- Všechny `.md` soubory kromě `README.md`
- Dev batch soubory (`build-*.bat`, `debug-*.bat`, atd.)
- `scripts/`, `config/`, `*.html`, `*.sh`
- Python `__pycache__`, `*.log`
- `template_*.xlsx` (uživatel má vlastní)

## 🔄 Automatizace (budoucnost)

### Vytvoření build scriptu:
```bash
# create-production.bat
@echo off
echo Creating production build...
git checkout production
git merge feature/next-phase
call clean-production.bat
git add -A
git commit -m "[prod-auto] Automated production build"
git push origin production
echo Production build complete!
```

## 🎯 Klíčové body
1. **Production branch = jen nutné soubory pro uživatele**
2. **install-windows-standalone.bat stahuje z production branch**
3. **Vždy testovat production build před pushnutím**
4. **README.md aktualizovat pro uživatele, ne vývojáře**

---
*Návod vytvořen: 2025-06-07*
*Při změnách aktualizovat tento postup*