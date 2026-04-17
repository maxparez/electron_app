# DVPP Certificates App Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a new Electron app section for DVPP certificate extraction with two input modes (`Gemini API` and pasted `raw text`), one shared editable table, TSV export, Excel template export, and future-ready hooks for ESF CSV.

**Architecture:** Implement this as a new standalone tool in the Electron app, not as part of the current `DVPP report`. Both import paths must normalize into one canonical `CertificateRecord` workflow, with the renderer owning the editable table state and Python backend handling import, normalization, validation, and export adapters.

**Tech Stack:** Electron renderer/preload/main IPC, Flask endpoints, Python dataclasses/processors, `pydantic-ai-slim[google]`, `xlwings`, root-level `unittest`

### Task 1: Create Canonical Domain Model

**Files:**
- Create: `src/python/dvpp_certificates/domain.py`
- Create: `src/python/dvpp_certificates/__init__.py`
- Modify: `src/python/dvpp_cert_extraction.py`
- Test: `test_dvpp_certificates_domain.py`

**Step 1: Write the failing test**

Add tests for:
- `CertificateRecord` canonical fields
- `RecordOrigin` provenance fields
- `WorkingRecord` preserving both extracted and editable values
- batch/session container objects

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_domain.py -v`
Expected: FAIL because the new domain module does not exist yet.

**Step 3: Write minimal implementation**

Implement dataclasses for:
- `RecordOrigin`
- `CertificateRecord`
- `WorkingRecord`
- `ExtractionBatch`
- `ExportMetadata`

Keep only fields that are already known:
- extracted certificate fields
- source mode/file/raw row/model
- editable export metadata placeholders

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_domain.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/python/dvpp_certificates/__init__.py src/python/dvpp_certificates/domain.py src/python/dvpp_cert_extraction.py test_dvpp_certificates_domain.py
git commit -m "[feat-157] Add DVPP certificate domain model"
```

### Task 2: Extract Shared Normalization And Validation Layer

**Files:**
- Create: `src/python/dvpp_certificates/normalization.py`
- Modify: `src/python/dvpp_cert_extraction.py`
- Test: `test_dvpp_certificates_normalization.py`

**Step 1: Write the failing test**

Add tests for:
- title stripping
- date normalization including `?`
- topic whitelist normalization
- conversion from raw extracted values into canonical `CertificateRecord`

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_normalization.py -v`
Expected: FAIL because the normalization module does not exist yet.

**Step 3: Write minimal implementation**

Move normalization helpers out of `dvpp_cert_extraction.py` into the new module and expose a single conversion function such as:
- `normalize_certificate_fields(raw_record, origin) -> CertificateRecord`

Keep `dvpp_cert_extraction.py` as a thin adapter over the shared normalization layer.

**Step 4: Run test to verify it passes**

Run:
- `.venv/bin/python -m unittest test_dvpp_certificates_normalization.py -v`
- `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/python/dvpp_certificates/normalization.py src/python/dvpp_cert_extraction.py test_dvpp_certificates_normalization.py test_dvpp_cert_extraction.py
git commit -m "[feat-157] Share DVPP certificate normalization"
```

### Task 3: Add Strict Raw Text Importer

**Files:**
- Create: `src/python/dvpp_certificates/raw_text_parser.py`
- Modify: `src/python/dvpp_certificates/domain.py`
- Test: `test_dvpp_certificates_raw_text_parser.py`

**Step 1: Write the failing test**

Add tests for:
- accepting exact tab-separated rows in the agreed field order
- rejecting malformed rows with wrong column count
- preserving one row per certificate
- attaching `source_mode="raw_text"` and `raw_row`

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_raw_text_parser.py -v`
Expected: FAIL because the parser does not exist yet.

**Step 3: Write minimal implementation**

Implement:
- `parse_raw_text_batch(text: str) -> ExtractionBatch`

Rules:
- split by lines
- require exact TSV field order
- ignore empty lines only
- fail loudly on malformed lines

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_raw_text_parser.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/python/dvpp_certificates/raw_text_parser.py src/python/dvpp_certificates/domain.py test_dvpp_certificates_raw_text_parser.py
git commit -m "[feat-157] Add DVPP raw text importer"
```

### Task 4: Add Gemini Batch Import Processor

**Files:**
- Create: `src/python/dvpp_certificates/importers.py`
- Create: `src/python/tools/dvpp_certificate_processor.py`
- Modify: `src/python/dvpp_cert_extraction.py`
- Modify: `src/python/server.py`
- Test: `test_dvpp_certificate_processor.py`

**Step 1: Write the failing test**

Add tests for:
- importing a folder as `1 file = 1 request`
- collecting per-file warnings/errors
- returning one shared batch payload
- rejecting malformed Gemini responses

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificate_processor.py -v`
Expected: FAIL because the new processor and endpoints do not exist yet.

**Step 3: Write minimal implementation**

Implement:
- `GeminiCertificateImporter`
- `DvppCertificateProcessor`
- Flask endpoint `POST /api/dvpp-certificates/import/gemini`

The endpoint should:
- accept folder path, selected files, model choice
- resolve API key from secure storage or current request
- process files sequentially
- return canonical rows plus per-file diagnostics

**Step 4: Run test to verify it passes**

Run:
- `.venv/bin/python -m unittest test_dvpp_certificate_processor.py -v`
- `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/python/dvpp_certificates/importers.py src/python/tools/dvpp_certificate_processor.py src/python/server.py src/python/dvpp_cert_extraction.py test_dvpp_certificate_processor.py test_dvpp_cert_extraction.py
git commit -m "[feat-157] Add DVPP Gemini import processor"
```

### Task 5: Add Export Adapters For TSV And Excel

**Files:**
- Create: `src/python/dvpp_certificates/exporters.py`
- Modify: `src/python/tools/dvpp_certificate_processor.py`
- Modify: `src/python/server.py`
- Test: `test_dvpp_certificate_exporters.py`

**Step 1: Write the failing test**

Add tests for:
- TSV export from edited working records
- Excel export creating a copy of the template, never overwriting the source
- missing required export metadata failing before write
- default template path handling

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificate_exporters.py -v`
Expected: FAIL because the exporters do not exist yet.

**Step 3: Write minimal implementation**

Implement:
- `export_records_to_tsv(...)`
- `export_records_to_excel(...)`
- Flask endpoints:
  - `POST /api/dvpp-certificates/export/tsv`
  - `POST /api/dvpp-certificates/export/excel`

Excel rules:
- copy the template to a generated output filename
- validate required metadata before write
- use `xlwings` for workbook write path
- leave future `ESF CSV` as a stub interface only

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_certificate_exporters.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/python/dvpp_certificates/exporters.py src/python/tools/dvpp_certificate_processor.py src/python/server.py test_dvpp_certificate_exporters.py
git commit -m "[feat-157] Add DVPP certificate exporters"
```

### Task 6: Add Secure API Key Storage In Electron

**Files:**
- Modify: `package.json`
- Modify: `src/electron/main.js`
- Modify: `src/electron/preload.js`
- Test: `test_dvpp_certificates_electron_contract.py`

**Step 1: Write the failing test**

Add tests for:
- secure key save/load/delete contract exposed to renderer
- no raw key embedded in persisted normal app config
- session-only mode still supported

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_electron_contract.py -v`
Expected: FAIL because the IPC contract does not exist yet.

**Step 3: Write minimal implementation**

Implement:
- add `keytar` dependency
- main-process IPC handlers for save/load/delete Gemini key
- preload bridge methods:
  - `getStoredGeminiKeyStatus()`
  - `storeGeminiKey(key)`
  - `deleteGeminiKey()`

Do not expose the whole key back to renderer if not needed; returning status is preferable.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_electron_contract.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add package.json src/electron/main.js src/electron/preload.js test_dvpp_certificates_electron_contract.py
git commit -m "[feat-157] Add secure Gemini key storage"
```

### Task 7: Build Renderer UI For The New Tool

**Files:**
- Modify: `src/electron/renderer/index.html`
- Modify: `src/electron/renderer/renderer.js`
- Modify: `src/electron/renderer/styles.css`
- Optionally create: `src/electron/renderer/dvpp-certificates.js`
- Test: `test_dvpp_certificates_renderer_contract.py`

**Step 1: Write the failing test**

Add tests for:
- new nav item/tool panel exists
- mode switch between `Gemini API` and `Raw text`
- shared table rendering contract
- export form fields for template path and project metadata

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_renderer_contract.py -v`
Expected: FAIL because the UI contract does not exist yet.

**Step 3: Write minimal implementation**

Implement one screen with:
- mode selector
- Gemini folder import controls
- raw text textarea with prompt copy buttons
- editable results table
- export metadata block
- buttons for `Uložit TSV` and `Vytvořit Excel`

Keep model choice and template override in advanced section.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_certificates_renderer_contract.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/electron/renderer/index.html src/electron/renderer/renderer.js src/electron/renderer/styles.css src/electron/renderer/dvpp-certificates.js test_dvpp_certificates_renderer_contract.py
git commit -m "[feat-157] Add DVPP certificates UI"
```

### Task 8: Wire End-To-End Flow And Manual Validation

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/2026-04-17-dvpp-cert-extraction-poc-design.md`
- Modify: `docs/plans/2026-04-17-dvpp-certificates-app-feature.md`
- Test: existing test files as needed

**Step 1: Document usage**

Document:
- Gemini API mode
- raw text mode
- secure key storage behavior
- default Excel template path
- current limitations

**Step 2: Run verification**

Run:
- `.venv/bin/python -m unittest test_dvpp_certificates_domain.py -v`
- `.venv/bin/python -m unittest test_dvpp_certificates_normalization.py -v`
- `.venv/bin/python -m unittest test_dvpp_certificates_raw_text_parser.py -v`
- `.venv/bin/python -m unittest test_dvpp_certificate_processor.py -v`
- `.venv/bin/python -m unittest test_dvpp_certificate_exporters.py -v`
- `.venv/bin/python -m unittest test_dvpp_certificates_electron_contract.py -v`
- `.venv/bin/python -m unittest test_dvpp_certificates_renderer_contract.py -v`
- `.venv/bin/python -m unittest test_runtime_consistency.py -v`

Then run one manual smoke pass:
- import one folder through Gemini mode
- import one raw text sample
- edit one row
- export one TSV
- export one Excel copy

**Step 3: Commit**

```bash
git add README.md docs/plans/2026-04-17-dvpp-cert-extraction-poc-design.md docs/plans/2026-04-17-dvpp-certificates-app-feature.md
git commit -m "[docs-157] Document DVPP certificates app flow"
```
