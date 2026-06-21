# Attendance Sheet Splitter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a standalone application tool that finds multi-sheet attendance workbooks and exports every valid attendance sheet into its own fidelity-preserving XLSX file.

**Architecture:** A new Python processor inspects workbook structure with `openpyxl` and delegates sheet copying to an injectable `xlwings` implementation. Flask endpoints expose candidate scanning and processing. The Electron renderer adds a dedicated tool using the existing file-selection, folder-selection, result, and navigation patterns.

**Tech Stack:** Python 3, openpyxl, xlwings, Flask, Electron, vanilla JavaScript, unittest.

### Task 1: Workbook inspection and filename rules

**Files:**
- Create: `src/python/tools/attendance_splitter.py`
- Create: `test_attendance_splitter.py`

**Step 1: Write failing tests**

Add tests that create temporary workbooks and assert:

- visible 16h/32h attendance sheets are detected;
- hidden and unrelated sheets are skipped with reasons;
- a workbook is eligible only with at least two attendance sheets;
- `2. a 3. ročník` normalizes to `2_a_3_rocnik`;
- output-name collisions receive numeric suffixes.

**Step 2: Run tests to verify failure**

Run:

```bash
/root/vyvoj_sw/electron_app/.venv/bin/python test_attendance_splitter.py
```

Expected: import failure because `tools.attendance_splitter` does not exist.

**Step 3: Implement minimal inspection code**

Create `AttendanceSplitter` with:

- `inspect_workbook(file_path)`;
- `scan_folder(folder_path)`;
- `normalize_sheet_name(sheet_name)`;
- `build_output_path(output_dir, sheet_name)`.

Use `openpyxl.load_workbook(..., read_only=False, data_only=False)` and inspect
sheet visibility plus the supported attendance header markers.

**Step 4: Run tests to verify pass**

Run the same unittest command and expect all tests to pass.

### Task 2: Fidelity-preserving split processing

**Files:**
- Modify: `src/python/tools/attendance_splitter.py`
- Modify: `test_attendance_splitter.py`

**Step 1: Write failing tests**

Add tests using an injected sheet copier. Assert that:

- every detected attendance sheet is copied;
- outputs are placed in `rozdelene_dochazky`;
- helper sheets are reported as skipped;
- one failed copy produces a partial result while remaining sheets continue.

**Step 2: Run tests to verify failure**

Run the splitter tests and confirm failures are caused by the missing process method.

**Step 3: Implement processing**

Implement `process(files, options=None)` and the default xlwings copier. Open one
hidden Excel application per source workbook, copy each selected sheet into a new
workbook, save as XLSX, and close workbooks/app in `finally` blocks.

**Step 4: Run tests to verify pass**

Run the splitter tests and expect all tests to pass.

### Task 3: Flask scan and process APIs

**Files:**
- Modify: `src/python/server.py`
- Create: `test_attendance_splitter_server.py`

**Step 1: Write failing API tests**

Use Flask's test client and patched processor calls to verify:

- `POST /api/attendance-splitter/scan` accepts `filePaths` or `folderPath`;
- paths are converted through the existing WSL helper;
- `POST /api/attendance-splitter/process` returns structured success/partial/error data;
- missing inputs return HTTP 400.

**Step 2: Run tests to verify failure**

Run:

```bash
/root/vyvoj_sw/electron_app/.venv/bin/python test_attendance_splitter_server.py
```

Expected: 404 responses for both endpoints.

**Step 3: Implement endpoints**

Import `AttendanceSplitter`, add scan and process routes, validate JSON input, and
return consistent Czech messages and result payloads.

**Step 4: Run tests to verify pass**

Run both splitter test files and expect all tests to pass.

### Task 4: Electron tool UI

**Files:**
- Modify: `src/electron/renderer/index.html`
- Modify: `src/electron/renderer/renderer.js`
- Create: `test_attendance_splitter_ui_static.py`

**Step 1: Write failing static UI tests**

Assert the HTML contains navigation, welcome card, tool panel, file/folder buttons,
file list, process button, result area, and the approved Czech hint. Assert renderer
state, listeners, scan endpoint, process endpoint, removal support, and report
rendering are wired without inline handlers.

**Step 2: Run tests to verify failure**

Run:

```bash
/root/vyvoj_sw/electron_app/.venv/bin/python test_attendance_splitter_ui_static.py
```

Expected: assertions fail because the tool is absent.

**Step 3: Implement renderer integration**

Add the new section using existing classes. Extend state and elements, implement
file validation, folder scanning, refresh, removal, ready-state checks, processing,
escaped result rendering, and output-folder opening.

**Step 4: Run tests to verify pass**

Run the UI static tests and existing UI static tests.

### Task 5: End-to-end verification

**Files:**
- Modify if required: files changed above

**Step 1: Run focused tests**

```bash
/root/vyvoj_sw/electron_app/.venv/bin/python test_attendance_splitter.py
/root/vyvoj_sw/electron_app/.venv/bin/python test_attendance_splitter_server.py
/root/vyvoj_sw/electron_app/.venv/bin/python test_attendance_splitter_ui_static.py
/root/vyvoj_sw/electron_app/.venv/bin/python test_dvpp_certificate_ui_static.py
/root/vyvoj_sw/electron_app/.venv/bin/python test_inv_vzd_date_interval.py
```

Expected: all pass.

**Step 2: Test the supplied workbook inspection**

Inspect:

```text
/root/vyvoj_sw/electron_app/tmp/dochazka_inovativni_vyuka_ZS_SD_ve_vyuce_1.xlsx
```

Expected: three attendance sheets and one skipped hidden `Data` sheet.

**Step 3: Run syntax checks**

```bash
/root/vyvoj_sw/electron_app/.venv/bin/python -m py_compile src/python/tools/attendance_splitter.py src/python/server.py
node --check src/electron/renderer/renderer.js
```

Expected: exit code 0.

**Step 4: Review changes**

Check `git diff --check`, `git status --short`, and the final diff. Do not include
line-ending-only changes created by the worktree environment.

**Step 5: Record Windows validation requirement**

Document that actual xlwings copy behavior still requires Windows with Microsoft
Excel before release.
