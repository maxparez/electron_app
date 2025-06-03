# Project Snapshot - Electron App (2025-03-06)

## Project Overview
- **Name:** Electron App - Zpracování projektové dokumentace
- **Purpose:** Desktop application for processing school project documentation (OP JAK)
- **Current Branch:** deployment-windows
- **Working Directory:** /root/vyvoj_sw/electron_app
- **Platform:** WSL2 Linux (5.15.167.4-microsoft-standard-WSL2)

## Current Git Status
- **Modified Files:**
  - PROGRESS.md
  - PROGRESS_CONTEXT.md
- **Last Commit:** 0eb3235 - [fix-046] Restore per-file details, remove only general processing messages

## Recent Development Activity (Last 20 Commits)
```
0eb3235 [fix-046] Restore per-file details, remove only general processing messages
eb88910 [fix-045] Clean up UI logs and simplify file display
b8a9292 [fix-044] Improved error handling: specific cell errors, no output on data errors, continue processing
c8dcdcd [fix-042][fix-043] Fix per-file status display and add detailed SDP verification logging
4312912 [fix-041] Perfect per-file message isolation and UI display
668fa87 [fix-040] Implement per-file logging and error display in UI
3ab15f1 [chore-039] Clean up test files
9402aeb [fix-038] Fix UI error display for InvVzd validation errors
ee6eda9 [fix-048] Improve error reporting to show in normal UI instead of fatal error
6e0bbdd [fix-047] Add validation for missing dates in activities
959f853 [cleanup-046] Remove debug logs and add text replacements constants
547a6e0 [fix-045] Show uncertain date fixes in UI log
c65eb23 [fix-044] Fix date parsing - specify dayfirst=True to prevent day/month swap
69be994 [debug-043] Add better debug logging to track date processing
d1ea37e [fix-042] Fix 32h legacy format to read actual dates from row 6
9dc6f7b [debug-041] Add debug logging for 32h date processing
5e1f778 [fix-040] Fix date processing for 32h template with proper column references
3997252 [feat-039] Improve InvVzd UI and add comprehensive date validation
5cf198f [feat-038] Add collapsible report UI for InvVzd tool
ad77b01 [fix-037] Fix SDP error display assignment and remove Unicode from logs
```

## Today's InvVzd Tool Improvements Summary

### Error Handling & Validation
1. **Cell-specific error reporting** - Shows exact cell location (e.g., "Chyba v buňce B15")
2. **Graceful error handling** - Continues processing despite errors, no output on data errors
3. **Date validation** - Detects and reports missing dates in activities
4. **Improved error display** - Shows errors in normal UI instead of fatal error modal

### UI/UX Improvements
1. **Per-file status display** - Clean separation of processing status for each file
2. **Collapsible report sections** - Better organization of validation results
3. **Cleaned up logging** - Removed excessive debug messages while keeping important details
4. **Better error formatting** - Clear, user-friendly error messages in Czech

### Date Processing Fixes
1. **Fixed date parsing** - Added `dayfirst=True` to prevent day/month swap
2. **32h template date fix** - Correctly reads dates from row 6 for legacy format
3. **Date uncertainty reporting** - Shows when dates were automatically fixed
4. **Comprehensive date validation** - Checks all date fields for completeness

### Technical Improvements
1. **SDP verification logging** - Detailed logging for debugging SDP calculations
2. **Message isolation** - Perfect per-file message isolation in UI
3. **Constants for text replacements** - Centralized text replacement rules
4. **Removed Unicode issues** - Cleaned up logs from Unicode characters

## Modified Files in Recent Session
```
src/electron/renderer/renderer.js     - UI improvements for error display
src/electron/renderer/styles.css      - Styling for collapsible reports
src/python/server.py                  - API error handling improvements
src/python/tools/base_tool.py         - Base tool error handling
src/python/tools/inv_vzd_processor.py - Core InvVzd processing logic
src/python/tools/zor_spec_dat_processor.py - ZorSpecDat tool updates
legacy_code/zor_spec_dat_nogui_refactored.py - Legacy code reference
_img/scr.png, scr2.png               - Updated screenshots
```

## Current Technical State

### Dependencies
- **Python:** 3.12 (in venv)
- **Key Python Packages:**
  - xlwings 0.33.15 (Windows-only, Excel formatting preservation)
  - Flask (REST API backend)
  - openpyxl (Excel file handling)
  - pandas (Data processing)
- **Node.js/Electron:** Latest stable versions
- **Frontend:** Electron with vanilla JS, i18n for Czech localization

### Architecture
```
Frontend (Electron) <---> Backend (Flask API on :5000) <---> Python Tools
     |                          |                               |
     └── renderer.js            └── server.py                  └── inv_vzd_processor.py
         styles.css                                                 zor_spec_dat_processor.py
         index.html                                                 plakat_generator.py
```

### File Structure
```
/root/vyvoj_sw/electron_app/
├── src/
│   ├── electron/           # Frontend code
│   │   ├── renderer/       # UI components
│   │   ├── locales/        # Czech translations
│   │   └── main.js         # Main process
│   └── python/             # Backend code
│       ├── tools/          # Processing tools
│       ├── api/            # API endpoints
│       └── server.py       # Flask server
├── legacy_code/            # Original Python scripts
├── tests/                  # Test suites
├── docs/                   # Documentation
└── templates/              # Excel templates
```

## Pending Issues & Tasks

### Known Issues
1. xlwings requires Windows with MS Office installed
2. Some date formats may still need manual verification
3. Error messages could be more detailed for specific edge cases

### Next Steps
1. Continue testing with real-world Excel files
2. Implement remaining tools (ZorSpecDat priority 2, Plakat priority 3)
3. Create Windows installer with bundled Python
4. Comprehensive testing on Windows 10/11 environments
5. User documentation in Czech

## Configuration & Environment

### Development Commands
```bash
# Always use virtual environment
cd /root/vyvoj_sw/electron_app
source venv/bin/activate

# Start development
npm run dev                      # Electron frontend
python src/python/server.py      # Flask backend

# Testing
pytest                           # Python tests
npm test                         # JavaScript tests

# Build
npm run make                     # Create installer
```

### Environment Variables
- `FLASK_DEBUG=true` (default for development)
- `FLASK_DEBUG=false` (for production)

### Key Configuration Files
- `package.json` - Node.js dependencies and scripts
- `requirements.txt` - Python dependencies
- `forge.config.js` - Electron Forge build configuration
- `src/electron/locales/cs.json` - Czech translations

## Git Workflow Reminders
- Commit every 2 hours or after feature completion
- Use tags: [feat-XXX], [fix-XXX], [refactor-XXX], [test-XXX], [docs-XXX]
- Push to GitHub minimum 2x per day
- Current branch: deployment-windows

## MCP Servers Active
- Filesystem - Project file access
- Git - Version control operations
- Context7 - Library documentation
- Supabase - Database operations (if needed)
- Sequential-thinking - Complex problem solving

## Notes for Next Session
1. The InvVzd tool is now stable with comprehensive error handling
2. UI displays per-file processing status cleanly
3. Date processing has been thoroughly debugged and fixed
4. Ready to focus on ZorSpecDat tool implementation
5. Consider creating test cases for edge cases found during debugging

---
*Snapshot created: 2025-03-06*
*Use this file to quickly restore context in a new Claude session*