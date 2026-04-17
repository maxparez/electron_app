# DVPP Certificate Extraction POC Design

## Goal

Ověřit mimo hlavní Electron aplikaci, zda Gemini API přes Python CLI dokáže z jednoho vstupního souboru (`pdf`, `jpg`, `jpeg`, `png`) extrahovat data z DVPP certifikátů se srovnatelnou kvalitou jako dnešní ruční workflow v Google AI Studiu.

## Scope

První iterace je záměrně úzká:

- samostatný Python script mimo Electron UI
- zpracování pouze jednoho vstupního souboru na běh
- ruční volba modelu:
  - `gemini-3-flash-preview`
  - `gemini-3.1-pro-preview`
- structured output přes `PydanticAI`
- finální výstup jako:
  - validovaný JSON
  - TSV kompatibilní s interním workflow

Mimo scope první iterace:

- multipage orchestrace
- dávkové zpracování více souborů
- automatický fallback mezi modely
- ukládání historie běhů
- integrace do Electron aplikace

## Architecture

POC je jeden CLI script `scripts/dvpp_cert_extract.py` plus podpůrný Python modul pro datové modely, validaci a převod do TSV. Script přijme cestu k jednomu souboru a název Gemini modelu, načte API key z prostředí, zavolá Gemini přes `PydanticAI`, validuje odpověď a vytiskne TSV na stdout. Pro multimodální vstup používá `BinaryContent.from_path(...)` a lazy importy pro Google/PydanticAI vrstvu, aby šly unit testy spouštět bez živého API volání.

Architektura má tři vrstvy:

1. `CLI layer`
   - parsování argumentů
   - načtení souboru
   - výběr modelu
   - zápis výstupů

2. `Extraction layer`
   - `PydanticAI` agent
   - prompt
   - structured response contract

3. `Normalization layer`
   - lokální `CertificateRecord` / `ExtractionResult` dataclasses
   - odstranění titulů
   - normalizace dat do `dd.mm.yyyy`
   - validace tématu proti whitelistu
   - převod do TSV řádků

## Data Model

Top-level response model:

- `ExtractionResult`
  - `certificates: list[CertificateRecord]`

Každý `CertificateRecord` obsahuje:

- `surname`
- `name`
- `birth_date`
- `course_name`
- `completion_date`
- `hours`
- `topic`
- `uncertainty_notes` (volitelné, pro diagnostiku POC)

První verze bude pracovat se string reprezentací dat, protože model může vracet nejisté nebo neúplné hodnoty. Normalizace do přesného formátu proběhne až po obdržení odpovědi.

## Prompt Strategy

Prompt bude co nejvěrnější stávajícímu AI Studio promptu. Hlavní změna bude pouze v cíli výstupu:

- místo raw tab-separated textu bude model instruován vrátit data podle schema
- logika témat, nejistoty a výběru data ukončení zůstane zachovaná

Výhoda:

- zachová se existující know-how
- sníží se riziko, že POC selže jen kvůli zbytečné změně promptu

## Validation Rules

Po odpovědi modelu proběhne:

1. structured output validace přes `PydanticAI`
2. převod do lokálních `CertificateRecord` / `ExtractionResult` dataclasses
3. normalizace jmen a dat
4. whitelist validace pole `topic`
5. převod do interní TSV struktury

TSV výstup bude mít přesné pořadí polí:

`Příjmení<TAB>Jméno<TAB>Datum narození<TAB>Název kurzu<TAB>Datum ukončení vzdělávání<TAB>Počet hodin<TAB><TAB>Téma`

Pokud bude potřeba zachovat jinou interní tabulkovou strukturu, formatter se upraví bez zásahu do extrakční vrstvy.

## CLI Interface

Aktuální CLI:

```bash
.venv/bin/python scripts/dvpp_cert_extract.py \
  --input path/to/certificate.pdf \
  --model gemini-3-flash-preview
```

Volitelné přepínače:

- `--output-json path/to/result.json`
- `--output-tsv path/to/result.tsv`

Výchozí chování:

- TSV se tiskne na `stdout`
- JSON a TSV soubor se zapisují jen pokud jsou explicitně předané přes flagy

API key:

- primárně `GEMINI_API_KEY`
- fallback `GOOGLE_API_KEY`

## Current Implementation Notes

Aktuální implementace už obsahuje:

- validaci podporovaných formátů `pdf/jpg/jpeg/png`
- ruční přepínání mezi `gemini-3-flash-preview` a `gemini-3.1-pro-preview`
- serializaci do validovaného JSON a TSV
- unit testy pro CLI parsing, env lookup, mocked extraction orchestration a základní error handling

Zatím stále chybí:

- live Gemini smoke test nad reálným dokumentem
- multipage PDF orchestrace
- dávkové zpracování více souborů
- ukládání raw provider response

## Success Criteria

POC je úspěšný, pokud:

- zpracuje jeden soubor bez ruční editace kódu
- vrátí validní structured output
- vyrobí TSV použitelný pro další ruční nebo poloautomatické zpracování
- umožní prakticky porovnat `flash` a `pro` na reálných certifikátech

## Next Iterations

Pokud single-file POC dopadne dobře:

1. multipage PDF
2. více souborů
3. kombinace multipage + batch
4. teprve potom integrace do Electron aplikace
