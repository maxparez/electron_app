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

## Vytěžování certifikátů DVPP

Vytěžování certifikátů je už integrované přímo v Electron aplikaci jako samostatný nástroj `Vytěžování certifikátů`.

Aktuální workflow v aplikaci:
- import certifikátů přes `Gemini API`
- nebo ruční vložení `Raw text z Google AI Studia`
- společná editovatelná tabulka záznamů
- export do `TSV`
- export do připravené `Excel` šablony
- generování `ESF import` CSV

Podporované vstupy pro Gemini režim:
- `pdf`
- `jpg`
- `jpeg`
- `png`

Podporované modely:
- `gemini-3-flash-preview`
- `gemini-3.1-pro-preview`

Batch zpracování v aplikaci posílá každý soubor samostatně a výsledky potom sloučí. Nepoužívá multi-file request do jednoho Gemini callu.

Repo stále obsahuje i pomocný Python CLI nástroj pro vývoj a rychlé experimenty:

```bash
export GEMINI_API_KEY=your-key

python scripts/dvpp_cert_extract.py \
  --input path/to/certificate.pdf \
  --model gemini-3-flash-preview
```

Batch přes CLI:

```bash
python scripts/dvpp_cert_extract.py \
  --input-dir path/to/folder \
  --model gemini-3-flash-preview \
  --output-tsv out/batch.tsv
```

## Instalace pro Windows uživatele

Pro běžné Windows uživatele je doporučený instalační i aktualizační tok přes
release skript `install.bat`:

- stáhnout aktuální `install.bat` z `Releases`
- spustit ho dvojklikem
- skript provede čistou instalaci nebo aktualizuje existující `C:\OPJAK\electron_app`

Podrobný návod je v [docs/windows_install.html](docs/windows_install.html).
Skripty `update-windows.bat` a `update.bat` berte jako interní/servisní cestu,
ne jako primární doporučený postup pro koncové uživatele.

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
