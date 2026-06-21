# Automated Releases Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automate SemVer bumps and detailed Czech release notes, then display those notes in a native application modal when an update is available.

**Architecture:** JSON change fragments are consumed by a Node release tool that updates version-bearing files, changelog, and `release-notes.json`. The Git updater reads remote metadata without checking out the branch. The renderer replaces `window.confirm` with an accessible custom modal.

**Tech Stack:** Node.js, Git, Electron IPC, vanilla JavaScript, HTML/CSS, Python unittest wrappers.

### Task 1: Release preparation tool

**Files:**
- Create: `scripts/release-manager.js`
- Create: `test_release_manager.py`
- Modify: `package.json`

Write failing tests for SemVer bump selection, fragment grouping, version updates,
changelog generation, metadata output, and consumed fragment removal. Implement
pure exported helpers plus a CLI exposed as `npm run release:prepare`.

### Task 2: Remote release metadata

**Files:**
- Modify: `src/electron/update-manager.js`
- Modify: `test_update_manager.py`

Write failing tests proving that update checks return local/latest versions and
parsed remote release notes, with a fallback when metadata is absent.

### Task 3: Custom update modal

**Files:**
- Modify: `src/electron/renderer/index.html`
- Modify: `src/electron/renderer/renderer.js`
- Modify: `src/electron/renderer/styles.css`
- Modify: `test_update_auto_check_ui.py`

Write failing tests for modal structure, escaped release-note rendering, one-time
automatic display, later dismissal, and direct update start without a second
confirmation. Implement the modal using existing visual tokens.

### Task 4: Prepare version 1.4.0

**Files:**
- Create: `changes/*.json`
- Generate: `release-notes.json`
- Modify: `CHANGELOG.md`
- Modify: `package.json`
- Modify: `package-lock.json`
- Modify: `config/development.json`
- Modify: `config/production.json`
- Modify: `src/electron/config.js`

Add Czech fragments summarizing significant changes since `1.3.0`. Run
`npm run release:prepare`; verify that the automatic bump is `1.4.0` and all
version consistency tests pass.

### Task 5: Final verification

Run focused release, updater, runtime consistency, UI static, JavaScript syntax,
JSON parsing, and diff checks. Commit with the project release prefix and push
the existing test branch.
