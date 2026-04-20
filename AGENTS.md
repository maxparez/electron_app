# Repository Guidelines

This file is the shared source of truth for repository-wide instructions. Keep agent-specific behavior in tool-specific files such as `CLAUDE.md`.

## Project Snapshot
- Desktop application for OP JAK document processing.
- Stack: Electron frontend in `src/electron/` and Flask backend in `src/python/`.
- Real production behavior depends on Windows + Microsoft Excel; `xlwings` is required for preserving Excel formatting, formulas, and macros.

## Project Structure
- `src/electron/`: main process, preload bridge, renderer UI, assets.
- `src/python/`: Flask server, logging, and processing tools.
- `templates/`: Excel templates bundled or referenced by the app.
- `scripts/`: packaging, launcher, and Windows install helpers.
- `tests/`: sample inputs and generated outputs; most executable checks live as root-level Python scripts.
- `legacy_code/`: historical reference implementations and sample source files.

## Setup And Commands
- `npm install`
- `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- `npm run dev`: run Electron directly for local debugging.
- `npm start`: run through Electron Forge.
- `npm run make`: build the Windows package.
- `npm run build-win`, `npm run build-launcher`, `npm run build-all`: release-oriented packaging helpers.

## Testing And Validation
- Prefer the smallest relevant Python check for the area you changed:
  - `python test_inv_vzd.py`
  - `python test_zor_spec_dat.py`
  - `python test_complete_processing.py`
- Treat `npm test` as non-authoritative unless you also maintain the missing JS test tooling; this repository currently relies on Python smoke/integration scripts and manual Electron validation.
- Changes touching `xlwings`, Excel templates, installer flow, or backend startup need a Windows validation pass with Excel available.

## Coding Conventions
- Code identifiers, filenames, comments, and commit messages are in English.
- User-facing UI text stays in Czech.
- JavaScript uses 4-space indentation and semicolons; Python uses 4-space indentation and snake_case.
- Prefer small, direct changes and keep Electron/UI concerns separate from Python processing logic.

## Git And Review Expectations
- Match the existing commit prefix scheme: `[feat-153]`, `[fix-155]`, `[docs-144]`, `[release-156]`.
- Use imperative commit summaries and include the reason for non-obvious changes.
- PRs should list validation steps, mention sample files/templates used for testing, and include screenshots for renderer/UI changes.

## Guardrails
- Do not replace `xlwings` with a library that loses Excel fidelity.
- Keep localhost API assumptions explicit; the default backend port is `5000`.
- Do not commit real school data, generated logs, `venv/`, or `node_modules/`.
