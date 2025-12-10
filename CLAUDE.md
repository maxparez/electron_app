# CLAUDE.md - Project Context for Electron App

## 🔄 Pro pokračování v práci
Pokud se vracíte k projektu po delší době, přečtěte si:
@CLAUDE_CONTEXT_GUIDE.md @STARTUP_PROMPT.md

## Project Overview

**Name:** Electron App - Zpracování projektové dokumentace  
**Purpose:** Desktop application for processing school project documentation (OP JAK)  
**Users:** 10 colleagues (administrative workers, non-technical)  
**Development Path:** `/root/vyvoj_sw/electron_app/`

## Core Architecture

- **Frontend:** Electron (Node.js) - User interface
- **Backend:** Python Flask - Business logic
- **Communication:** REST API on localhost:5000
- **Critical Dependency:** xlwings (Windows only, preserves Excel formatting)

## Tools to Implement

1. **Inv Vzd Copy** (PRIORITY 1)
   - Process innovative education attendance (16/32 hours)
   - Must preserve Excel templates with formatting, macros, formulas
   
2. **Zor Spec Dat** (PRIORITY 2)
   - Process attendance from multiple classes
   - Generate HTML reports and unique student lists
   
3. **Plakat Generator** (PRIORITY 3)
   - Generate PDF posters for projects
   - Rewrite from web app to Python

## Development Principles

### MANDATORY Rules:
1. **English-only code** - ALL code artifacts in English
2. **Czech UI only** - User-facing texts in Czech
3. **Development checklist** - Create before implementation
4. **KISS, DRY, YAGNI** - Keep it simple, avoid duplication, no speculation

### Project Structure:
```
/root/vyvoj_sw/electron_app/
├── legacy_code/          # Original Python scripts
├── src/
│   ├── electron/        # Frontend
│   └── python/          # Backend
├── docs/                # All MD documentation
└── tests/               # Test suites
```

## Key Technical Decisions

1. **xlwings requirement:** Cannot be replaced - needed for Excel template preservation
2. **Windows-only features:** Accept limitation for xlwings functionality
3. **Single installer:** Bundle Python + Electron into one .exe
4. **Localization:** i18n system with cs.json for Czech texts

## Testing Requirements

- Unit tests for Python business logic
- Integration tests for API
- E2E tests for complete workflows
- Manual testing on Windows 10/11 with MS Office

## Consultant Agents (use sparingly)

Two specialist subagents live in `.claude/agents` for second opinions:

- **`chatgpt-consultant`** – Run only for risky backend/Electron/installer changes (e.g., `backend-manager.js`, `install-windows*.bat`, shared Flask endpoints). It reads `CLAUDE.md`, `PROGRESS.md`, `PROJECT_PLAN.md`, `PRODUCTION_WORKFLOW.md`, and logs results in `_context_notes.md`. Use it when a change could break Windows packaging or xlwings processing; skip it for routine refactors.
- **`gemini-consultant`** – Use for deployment/test strategy, localization checks, or xlwings/data-validation sanity reviews (e.g., before syncing `production`, updating Czech UI text, or altering template processors). It also records to `_context_notes.md`.

Guidelines:
1. **One consultant per decision.** Do not chain or loop unless the first identifies blockers needing follow-up.
2. **Always reference `_context_notes.md`** in the main reply so teammates see what was reviewed.
3. **If the CLI call fails**, state it and proceed without external advice; never block work.

## Documentation Agents (ALWAYS cite before coding)

The `python-docs` and `js-docs` subagents are tied to the Context7 MCP service. Before implementing or refactoring any non-trivial logic:

- **Use `python-docs`** for questions about Flask, pandas, xlwings, reportlab, Windows batch/Python integration, etc. It must pull fresh references from Context7 and summarize them with URLs.
- **Use `js-docs`** for Electron/Node/renderer APIs, packaging behavior, IPC details, or Windows-specific options (`child_process`, dialogs, etc.).

Rules:
1. **No guessing.** If you are unsure about an API or flag, consult the relevant doc agent first and include its summary (with source links) in your reasoning.
2. **Do not bypass Context7.** These agents must issue at least one lookup/search per consultation; if nothing is found, report that explicitly.
3. **Still follow local docs.** After the external lookup, re-check `CORE_DEVELOPMENT_PRINCIPLES.md`, `DEVELOPMENT_GUIDE.md`, or other repo files if the change touches them.

This keeps our responses grounded in real documentation and prevents hallucinated Electron/xlwings behavior.

## Commands & Scripts

```bash
# Development - ALWAYS USE VENV!
cd /root/vyvoj_sw/electron_app
source venv/bin/activate         # Activate Python virtual environment
npm run dev                      # Start Electron dev
python src/python/server.py      # Start Python backend (in venv)

# Debug mode (default ON for development)
FLASK_DEBUG=true python src/python/server.py   # Debug ON
FLASK_DEBUG=false python src/python/server.py  # Debug OFF (production)

# Testing
source venv/bin/activate && pytest  # Python tests (in venv)
npm test                            # JavaScript tests

# Build
npm run make                     # Create installer
```

## Critical Files to Preserve

- Excel templates formatting
- VBA macros in templates
- Locked cells and formulas
- Original output structure

## MCP Servers Configuration

Projekt používá pouze jeden MCP server:

- **Context7:** Up-to-date documentation for libraries and frameworks
  - Used by `python-docs` and `js-docs` agents
  - Provides real-time API references and code examples

Built-in Claude Code tools are used for:
- **Filesystem operations:** Read, Write, Edit, Glob, Grep
- **Version control:** Git operations via Bash tool
- **API testing:** WebFetch tool

## Progress Tracking

Use TodoWrite/TodoRead tools frequently for:
- Planning implementation steps
- Tracking completed features
- Managing bug fixes
- Coordinating testing phases

## Communication Style

- Be concise and direct
- Explain technical decisions clearly
- Ask for clarification when needed
- Report blockers immediately

## Current Phase

Ready to start development following PROJECT_PLAN.md timeline:
- Week 1: Environment setup
- Weeks 2-3: Python backend
- Weeks 4-5: Electron frontend
- Week 6: Testing and deployment

## Git Workflow

- **Commit frequently**: Every 2 hours or after completing a feature
- **Use tags**: [feat-XXX], [fix-XXX], [refactor-XXX], [test-XXX], [docs-XXX]
- **Push to GitHub**: Minimum 2x per day, always before breaks
- **Branch strategy**: main → develop → feature/fix branches
- **See docs/GIT_WORKFLOW.md** for detailed Git workflow and conventions
- **Always do commit & push**

### Quick Git Commands
```bash
# Quick save work in progress
git add -A && git commit -m "[chore-$(date +%Y%m%d)] WIP: Save progress" && git push

# Create tagged commit
git commit -m "[feat-005] Add new feature description"
git push origin $(git branch --show-current)
```
