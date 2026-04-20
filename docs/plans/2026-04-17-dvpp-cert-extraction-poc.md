# DVPP Certificate Extraction POC Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python-only CLI proof of concept that extracts one DVPP certificate file through Gemini API into validated JSON and TSV output.

**Architecture:** The POC stays outside the Electron app and uses a small CLI entrypoint plus a focused extraction module. Gemini is called through `PydanticAI` with a strict `Pydantic` output model, then normalized and formatted into TSV.

**Tech Stack:** Python 3, Pydantic, PydanticAI, argparse, pathlib, unittest

### Task 1: Add response and normalization tests

**Files:**
- Create: `test_dvpp_cert_extraction.py`

**Step 1: Write the failing test**

Add tests for:
- TSV formatting order
- topic whitelist enforcement
- date normalization to `dd.mm.yyyy`
- title stripping from names

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: FAIL because the extraction module does not exist yet.

**Step 3: Write minimal implementation**

Create minimal extraction utilities that satisfy the tests.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add test_dvpp_cert_extraction.py src/python/dvpp_cert_extraction.py
git commit -m "[feat-157] Add DVPP cert normalization helpers"
```

### Task 2: Add structured extraction models and prompt builder

**Files:**
- Modify: `src/python/dvpp_cert_extraction.py`
- Test: `test_dvpp_cert_extraction.py`

**Step 1: Write the failing test**

Add tests for:
- `CertificateRecord` validation
- `ExtractionResult` top-level shape
- prompt content includes the required extraction instructions and topic catalog

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: FAIL on missing models or missing prompt builder.

**Step 3: Write minimal implementation**

Implement:
- `CertificateRecord`
- `ExtractionResult`
- `build_extraction_prompt()`

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add test_dvpp_cert_extraction.py src/python/dvpp_cert_extraction.py
git commit -m "[feat-157] Define DVPP cert extraction schema"
```

### Task 3: Add CLI argument and file validation layer

**Files:**
- Create: `scripts/dvpp_cert_extract.py`
- Modify: `src/python/dvpp_cert_extraction.py`
- Test: `test_dvpp_cert_extraction.py`

**Step 1: Write the failing test**

Add tests for:
- supported extensions (`pdf`, `jpg`, `jpeg`, `png`)
- unsupported extension rejection
- CLI argument parsing for `--input`, `--model`, and optional output paths

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: FAIL because the CLI and validators do not exist yet.

**Step 3: Write minimal implementation**

Implement:
- file type validation
- argument parsing
- simple CLI flow without real API call

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add test_dvpp_cert_extraction.py src/python/dvpp_cert_extraction.py scripts/dvpp_cert_extract.py
git commit -m "[feat-157] Add DVPP cert CLI shell"
```

### Task 4: Integrate PydanticAI Gemini extraction

**Files:**
- Modify: `src/python/dvpp_cert_extraction.py`
- Modify: `scripts/dvpp_cert_extract.py`
- Modify: `requirements.txt`
- Test: `test_dvpp_cert_extraction.py`

**Step 1: Write the failing test**

Add tests for:
- model name mapping acceptance for `gemini-3-flash-preview` and `gemini-3.1-pro-preview`
- environment variable lookup for `GEMINI_API_KEY`
- extraction function orchestration with a mocked PydanticAI agent response

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: FAIL because the extraction orchestration is not implemented yet.

**Step 3: Write minimal implementation**

Implement:
- PydanticAI agent factory
- single-file extraction function
- environment variable loading
- JSON and TSV serialization

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add test_dvpp_cert_extraction.py src/python/dvpp_cert_extraction.py scripts/dvpp_cert_extract.py requirements.txt
git commit -m "[feat-157] Wire Gemini POC extraction flow"
```

### Task 5: Add usage documentation and smoke verification

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/2026-04-17-dvpp-cert-extraction-poc-design.md`

**Step 1: Document usage**

Add a short developer-facing section covering:
- required environment variable
- supported input formats
- sample CLI commands
- intended POC limitations

**Step 2: Run verification**

Run:
- `.venv/bin/python -m unittest test_dvpp_cert_extraction.py -v`
- `.venv/bin/python -m unittest test_runtime_consistency.py -v`

Expected: PASS

**Step 3: Commit**

```bash
git add README.md docs/plans/2026-04-17-dvpp-cert-extraction-poc-design.md test_dvpp_cert_extraction.py src/python/dvpp_cert_extraction.py scripts/dvpp_cert_extract.py requirements.txt
git commit -m "[docs-157] Document DVPP extraction POC"
```
