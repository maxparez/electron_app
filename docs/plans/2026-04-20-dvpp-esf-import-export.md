# DVPP ESF Import Export Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Přidat z certifikátové tabulky export `osoby.csv` pro ESF s pevnou hlavičkou, `;` oddělovačem a defaultními hodnotami ze vzoru.

**Architecture:** Export poběží stejně jako TSV a Excel: renderer pošle aktuální `records` na nový backend endpoint, backend použije jeden centrální ESF header a jednu centrální default row, přepíše jen `Jmeno_Osoby`, `Prijmeni_Osoby` a `DatumNarozeni_Osoby`, a vrátí cestu k vytvořenému CSV. V první iteraci nebude žádná další konfigurace, mapování ani import vzorového souboru za běhu.

**Tech Stack:** Electron renderer, Flask route v `server.py`, Python exporter v `src/python/dvpp_certificates/exporters.py`, unit testy přes `unittest`.

### Task 1: Backend exporter

**Files:**
- Modify: `src/python/dvpp_certificates/exporters.py`
- Test: `test_dvpp_certificate_exporters.py`

1. Přidat failing test pro generování ESF CSV se 32 poli a `;`.
2. Ověřit fail.
3. Dopsat minimální `export_records_to_esf_csv`.
4. Ověřit pass.

### Task 2: Processor a route

**Files:**
- Modify: `src/python/tools/dvpp_certificate_processor.py`
- Modify: `src/python/server.py`
- Test: `test_dvpp_certificate_exporters.py`

1. Přidat failing test endpointu `/api/dvpp-certificates/export/esf`.
2. Ověřit fail.
3. Dopsat `export_esf` v processoru a route v serveru.
4. Ověřit pass.

### Task 3: Renderer wiring

**Files:**
- Modify: `src/electron/renderer/renderer.js`

1. Nahradit placeholder tlačítka `Vygenerovat ESF import`.
2. Uložit `.csv`, zavolat endpoint, zobrazit success message.
3. Volitelně otevřít výsledný soubor stejně jako Excel.

### Task 4: Verification

**Files:**
- Test: `test_dvpp_certificate_exporters.py`
- Test: `test_dvpp_certificate_processor.py`

1. Spustit relevantní Python testy.
2. Zkontrolovat syntaxi rendereru přes `node --check`.
3. Commitnout po ověření.
