# DVPP Certificates Layout Refresh Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Přestavět obrazovku `Vytěžování certifikátů` na přehledný top-down workflow: import, full-width grid, dva exportní boxy vedle sebe a diagnostika až dole.

**Architecture:** Import zůstane funkčně stejný, ale přesune se do horního samostatného bloku. Grid a hromadné akce se sjednotí do hlavní full-width sekce. Exportní metadata se rozdělí na dva oddělené boxy `Excel export` a `ESF import`, které poběží nad stejným `state.certificateExtraction.exportMetadata`. Diagnostika se stáhne do spodního pomocného bloku, aby nepřekážela hlavní práci.

**Tech Stack:** Renderer HTML/CSS/vanilla JS, AG Grid Community, Python testy `unittest` pro statickou kontrolu UI.

### Task 1: Reshape page structure in HTML

**Files:**
- Modify: `src/electron/renderer/index.html`
- Test: `test_dvpp_certificate_ui_static.py`

**Step 1: Write the failing test**

Rozšířit statický UI test o očekávání:
- import blok je nad review blokem
- review blok obsahuje grid přes celou šířku bez pravého side panelu
- export sekce má dva boxy `Excel export` a `ESF import`
- diagnostika je v samostatném spodním bloku

**Step 2: Run test to verify it fails**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_dvpp_certificate_ui_static.py -v`
Expected: FAIL on missing layout markers.

**Step 3: Write minimal implementation**

V `index.html`:
- nahradit `cert-review-layout` jednokolonovou strukturou
- vytvořit sekce:
  - `cert-import-block`
  - `cert-review-block`
  - `cert-export-block`
  - `cert-diagnostics-block`
- v `cert-export-block` vytvořit dva boxy:
  - `cert-excel-export-card`
  - `cert-esf-export-card`

**Step 4: Run test to verify it passes**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_dvpp_certificate_ui_static.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/electron/renderer/index.html test_dvpp_certificate_ui_static.py
git commit -m "[feat-157] Restructure DVPP certificates page layout"
```

### Task 2: Rebind renderer logic to new layout

**Files:**
- Modify: `src/electron/renderer/renderer.js`
- Test: `test_dvpp_certificate_ui_static.py`

**Step 1: Write the failing test**

Rozšířit test o očekávání:
- renderer stále binduje všechny existující inputy a tlačítka po přesunu bloků
- import collapse summary dál funguje
- diagnostika se renderuje do spodního bloku

**Step 2: Run test to verify it fails**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_dvpp_certificate_ui_static.py -v`
Expected: FAIL on missing renderer strings or moved ids.

**Step 3: Write minimal implementation**

V `renderer.js`:
- zachovat stávající `state` a export flow
- přepojit DOM ids, pokud se změní wrappery
- zajistit, že:
  - import zůstane nahoře
  - grid je jediný hlavní review block
  - Excel metadata a ESF metadata mají vlastní export card wrapper
  - diagnostika se renderuje dolů, ne vedle gridu

**Step 4: Run test to verify it passes**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_dvpp_certificate_ui_static.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/electron/renderer/renderer.js test_dvpp_certificate_ui_static.py
git commit -m "[feat-157] Wire DVPP certificates top-down workflow"
```

### Task 3: Refresh CSS for top-down workflow

**Files:**
- Modify: `src/electron/renderer/styles.css`
- Test: `test_dvpp_certificate_ui_static.py`

**Step 1: Write the failing test**

Rozšířit test o CSS očekávání:
- grid wrapper je full width
- export boxy používají dvousloupcový layout
- při menší šířce se boxy skládají pod sebe
- default layout už neobsahuje starý pravý side panel pattern

**Step 2: Run test to verify it fails**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_dvpp_certificate_ui_static.py -v`
Expected: FAIL on missing CSS markers.

**Step 3: Write minimal implementation**

Ve `styles.css`:
- odstranit starý `cert-review-layout` side-by-side pattern
- nastavit:
  - full-width review block
  - export cards grid/flex se dvěma sloupci
  - breakpoint pro zalomení pod sebe
- nastavit rozumnou šířku a spacing pro `1024px` default window

**Step 4: Run test to verify it passes**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_dvpp_certificate_ui_static.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/electron/renderer/styles.css test_dvpp_certificate_ui_static.py
git commit -m "[feat-157] Style DVPP certificates top-down layout"
```

### Task 4: Set default BrowserWindow width

**Files:**
- Modify: `src/electron/main.js`
- Test: `test_runtime_consistency.py` or new narrow static assertion if needed

**Step 1: Write the failing test**

Přidat malý test nebo statickou kontrolu, že default šířka okna je `1024`.

**Step 2: Run test to verify it fails**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_runtime_consistency.py -v`
Expected: FAIL if the assertion is new.

**Step 3: Write minimal implementation**

V `main.js` změnit default width window na `1024`.

**Step 4: Run test to verify it passes**

Run: `/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest test_runtime_consistency.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/electron/main.js test_runtime_consistency.py
git commit -m "[fix-157] Set default window width for DVPP workflow"
```

### Task 5: Verification

**Files:**
- Test: `test_dvpp_certificate_ui_static.py`
- Test: `test_dvpp_certificate_exporters.py`
- Test: `test_dvpp_certificate_processor.py`
- Test: `test_dvpp_certificates_domain.py`

**Step 1: Run focused verification**

```bash
/root/vyvoj_sw/electron_app/.venv/bin/python -m unittest \
  test_dvpp_certificate_ui_static.py \
  test_dvpp_certificate_exporters.py \
  test_dvpp_certificate_processor.py \
  test_dvpp_certificates_domain.py -v
node --check src/electron/renderer/renderer.js
node --check src/electron/main.js
```

Expected: all tests PASS, node checks exit 0.

**Step 2: Commit final polish**

```bash
git add .
git commit -m "[feat-157] Refresh DVPP certificates workflow layout"
```
