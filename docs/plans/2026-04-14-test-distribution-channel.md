# Test Distribution Channel Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Přidat testovací distribuční kanál `windows-install-test`, na který lze přepnout existující Windows instalaci a který si nese vlastní update target i zvýšené debug logování.

**Architecture:** Repozitář bude mít jednoduché branch metadata v repu, ze kterých Windows skripty zjistí, z jaké větve se mají aktualizovat a zda mají zapnout rozšířené logování. První přepnutí na test kanál proběhne přes PowerShell update skript s explicitním `-Branch windows-install-test`; další aktualizace už poběží automaticky z branch markeru uloženého v testovací větvi.

**Tech Stack:** Windows batch, PowerShell, Python 3.11+, existing Electron/Python logging.

### Task 1: Add channel metadata and tested loader

**Files:**
- Create: `channel-config.json`
- Create: `src/python/channel_config.py`
- Create: `test_channel_config.py`

**Step 1: Write the failing test**

Add tests for loading channel metadata with defaults and with explicit debug settings.

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest test_channel_config.py`

**Step 3: Write minimal implementation**

Implement a tiny loader that reads `channel-config.json` and returns branch/debug metadata.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest test_channel_config.py`

### Task 2: Update runtime and update scripts

**Files:**
- Modify: `start-app.bat`
- Modify: `update-windows.bat`
- Modify: `scripts/update_windows.ps1`

Make `update-windows.bat` and `scripts/update_windows.ps1` read branch/debug info from `channel-config.json` when no branch override is passed. Add timestamped update logs under `logs\update\`. Update `start-app.bat` to keep launch logs and enable extra Electron logging in debug channel mode.

### Task 3: Document test-channel switching

**Files:**
- Modify: `README-windows-install.md`
- Modify: `INSTALACE-WINDOWS.md`
- Modify: `docs/DEPLOYMENT.md`

Document:
- first switch to test channel
- routine updates while on test channel
- rollback to stable `windows-install`

### Task 4: Verify and publish

**Files:**
- Verify modified files only

Run targeted unit tests, syntax checks, and a diff check. Then create/push branch `windows-install-test` so a Windows install can pull from it.
