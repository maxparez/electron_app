# Projektová dokumentace - Electron App

Desktop aplikace pro zpracování školní projektové dokumentace (OP JAK).

## Požadavky

- Windows 10/11
- MS Office (Excel)
- Node.js 18+
- Python 3.9+

## Instalace pro vývoj

```bash
# Klonování repozitáře
git clone git@github.com:maxparez/electron_app.git
cd electron_app

# Instalace Node.js závislostí
npm install

# Vytvoření Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate  # Windows

# Instalace Python závislostí
pip install -r requirements.txt
```

## Spuštění

```bash
# Spuštění v development módu
npm run dev
```

## Build

```bash
# Vytvoření instalátoru pro Windows
npm run make
```

## Struktura projektu

```
electron_app/
├── src/
│   ├── electron/      # Electron frontend
│   │   ├── main.js    # Hlavní proces
│   │   ├── preload.js # Preload script
│   │   └── renderer/  # UI komponenty
│   └── python/        # Python backend
│       ├── server.py  # Flask server
│       └── tools/     # Nástroje pro zpracování
├── docs/              # Dokumentace
├── tests/             # Testy
└── legacy_code/       # Původní Python skripty
```

## Licence

MIT