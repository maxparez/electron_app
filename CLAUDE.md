# CLAUDE.md - Project Context for Electron App

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

## Commands & Scripts

```bash
# Development - ALWAYS USE VENV!
cd /root/vyvoj_sw/electron_app
source venv/bin/activate         # Activate Python virtual environment
npm run dev                      # Start Electron dev
python src/python/server.py      # Start Python backend (in venv)

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

- **Filesystem:** Access to project files
- **Git:** Version control
- **Context7:** Library documentation
- **Fetch:** API testing

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

### Quick Git Commands
```bash
# Quick save work in progress
git add -A && git commit -m "[chore-$(date +%Y%m%d)] WIP: Save progress" && git push

# Create tagged commit
git commit -m "[feat-005] Add new feature description"
git push origin $(git branch --show-current)
```