# Runtime Consistency Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove the highest-value runtime inconsistencies without changing the intentionally retained emergency backend shutdown behavior.

**Architecture:** Centralize backend base URL usage around the configured backend port, make backend metadata expose the package version, and ensure the poster endpoint cleans up temporary output directories after serializing files. Keep changes small and local to Electron bootstrapping, preload bridge, backend metadata, and installer/docs consistency.

**Tech Stack:** Electron, Node.js, Flask, Python `unittest`

### Task 1: Regression tests for runtime consistency

**Files:**
- Create: `test_runtime_consistency.py`

**Step 1: Write failing tests**
- Assert Electron sources no longer hardcode `http://localhost:5000` in runtime call sites.
- Assert `/api/config` reports the same version as `package.json`.
- Assert the plakat endpoint removes its temporary directory after returning a successful response.

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_runtime_consistency.py -v`

Expected: FAIL because current runtime still contains hardcoded backend URLs, `/api/config` returns `1.0.0`, and the plakat temp directory is not cleaned up.

### Task 2: Centralize backend URL usage and align version metadata

**Files:**
- Modify: `src/electron/main.js`
- Modify: `src/electron/preload.js`
- Modify: `src/electron/renderer/backend-monitor.js`
- Modify: `src/python/server.py`

**Step 1: Implement minimal runtime changes**
- Use a single backend base URL source in Electron runtime code.
- Make `/api/config` read the application version from `package.json`.
- Reuse the configured backend base URL in health checks.

**Step 2: Run targeted test**

Run: `python -m unittest test_runtime_consistency.py -v`

Expected: the hardcoded URL and version tests pass; cleanup test may still fail until Task 3 is complete.

### Task 3: Clean temporary plakat output directories

**Files:**
- Modify: `src/python/server.py`

**Step 1: Implement minimal cleanup**
- Ensure the temporary output directory used by `/api/process/plakat` is removed after the response payload is serialized.

**Step 2: Run targeted test**

Run: `python -m unittest test_runtime_consistency.py -v`

Expected: PASS.

### Task 4: Repair adjacent consistency issues

**Files:**
- Modify: `scripts/install_windows.ps1`
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`

**Step 1: Apply small follow-up fixes**
- Point the installer smoke check to the actual `test_students_16plus.py` path.
- Refresh docs to mention DVPP and the external plakát service.

**Step 2: Run verification**

Run:
- `python -m unittest test_runtime_consistency.py -v`
- `python -m unittest test_server_metadata.py -v`
- `python -m unittest test_channel_config.py -v`

Expected: PASS.
