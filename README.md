# Projektová dokumentace - Electron App

Desktop aplikace pro zpracování školní projektové dokumentace (OP JAK).

Aktuální aplikace obsahuje čtyři nástroje:
- Inovativní vzdělávání
- Specifické datové položky do ZoR
- Generátor plakátů
- DVPP report

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

## Instalace pro Windows uživatele

Pro jednoduchou instalaci klientské verze na Windows sledujte
`docs/windows_install.html`, kde je popsána větev `windows-install`,
požadované programy a skripty pro kontrolu závislostí a vytvoření zástupce.

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

## Poznámky k provozu

- Electron komunikuje s lokálním Flask backendem na `127.0.0.1` přes konfigurovatelný port, výchozí je `5000`.
- Generátor plakátů používá externí službu `publicita.dotaceeu.cz`, takže vyžaduje síťové připojení.
- Praktické smoke testy jsou v tomto repozitáři převážně root-level Python skripty, například `test_inv_vzd.py`, `test_zor_spec_dat.py` a `test_complete_processing.py`.

## Licence

MIT
