
## Progres aktualizace - ZorSpec nástroj

### Aktuální stav
- ✅ InvVzd nástroj kompletně funkční s kroky zpracování
- ✅ UI vylepšení: Home navigace, clickable features, profesionální vzhled
- ✅ Template detekce a folder scanning pro InvVzd

### ZorSpec nástroj - požadavky
1. **Folder scan enhancement**: 
   - Načíst všechny soubory s listem 'Úvod a postup vyplňování'
   - Detekovat verzi (32h/16h) z buňky B1 na tomto listu
   - Zobrazit verzi u každého souboru

2. **Version mixing warning**:
   - Pokud folder obsahuje jak 32h tak 16h soubory → varování uživateli

3. **Auto-save results**:
   - Seznam žáků a result se automaticky uloží do složky se zdroji

### Implementace v dalším kontextovém okně
- Backend: Endpoint pro detekci ZorSpec souborů podle listu
- Frontend: Enhanced folder scanning s version info
- Processing: Auto-save do source folder místo download
- Validation: Mixed version detection a warnings

### Technické body
- Použít openpyxl pro čtení listu 'Úvod a postup vyplňování'
- Parser pro B1 buňku (regex pro '32 hodin'/'16 hodin')
- Enhanced UI pro zobrazení verze každého souboru
- Path utilities pro auto-save do source directory


### 2025-12-06 – Gemini Consultant Readiness Test
- **Status**: OPERATIONAL ✅
- **Test Date**: 2025-12-06
- **Tester**: Claude Haiku 4.5 (gemini-consultant agent)

#### Initialization Checks
1. **File Access**: ✅ PASSED
   - CLAUDE.md: Read successfully (156 lines)
   - PROGRESS.md: Read successfully (271 lines)
   - PRODUCTION_WORKFLOW.md: Read successfully (163 lines)
   - _context_notes.md: Existing log found (32 lines)

2. **Environment**:
   - GEMINI_API_KEY: ✅ Set and available
   - Working directory: `/root/vyvoj_sw/electron_app`
   - Git repo: ✅ Active (branch: feature/next-phase)
   - Recent commits: ✅ Last 5 commits reviewed

3. **Agent Configuration**:
   - Agent definition: ✅ Found at .claude/agents/gemini-consultant.md
   - Instructions: ✅ Complete and aligned with template
   - Constraints enforced: xlwings, Czech UI, Windows-only, KISS/DRY/YAGNI

#### Project Status Summary (from docs)
- **Application State**: 100% complete and production-ready
- **All 3 Tools**: InvVzd (16h/32h), ZorSpecDat, Plakat - fully functional
- **Windows Deployment**: Complete with install-windows*.bat scripts
- **Critical Fixes Applied**: [fix-062] through [fix-076] - CMD windows, lifecycle mgmt, admin removal
- **Production Branch**: Clean (25 essential files), ready for distribution

#### Consultation Readiness
✅ **READY FOR PRODUCTION CONSULTATIONS**

This agent can now:
1. Review deployment/installer strategy changes
2. Validate localization (Czech UI) text updates
3. Verify xlwings Excel template handling
4. Sanity-check data validation logic
5. Confirm release readiness before production syncs

#### Next Actions
- Agent is available for immediate use
- Use for: deployment reviews, test strategy alignment, localization QA, xlwings sanity
- Avoid using for: routine refactors, simple bug fixes (use chatgpt-consultant instead)
- Always log results back to this file


### 2025-12-06 – ZorSpecDat School Type Statistics Enhancement
- **Feature**: Added per-school-type statistics (MŠ/ZŠ/ŠD with ≥16 hours)
- **Implementation Date**: 2025-12-06
- **Developer**: Claude Sonnet 4.5

#### Documentation Consulted
- **Context7 pandas docs** (/websites/pandas_pydata): groupby, aggregation, filtering
  - Sources: https://pandas.pydata.org/docs/dev/_sources/user_guide/groupby
  - Key methods: `df.groupby().agg("sum")`, `df.groupby().filter()`, `as_index=False`
- **Project docs**: CLAUDE.md, CORE_DEVELOPMENT_PRINCIPLES.md

#### Implementation Details
1. **New Methods Added** (src/python/tools/zor_spec_dat_processor.py):
   - `_identify_school_type()`: Identifies school type from template name
     - MŠ: Keywords 'mš', 'mateřsk'
     - ZŠ: Keywords 'zš', 'základní'
     - ŠD: Keywords 'šd', 'školní družina', 'družin' (checked first for priority)
     - Jiné: Everything else

   - `_calculate_school_type_stats()`: Calculates per-type statistics
     - Groups data by template (school) and sums hours
     - Filters schools with ≥16 hours
     - Counts schools by type
     - Returns DataFrame with columns: ['Typ školy', 'Počet škol (≥16h)']

2. **HTML Report Enhancement** (zor_spec_dat_processor.py:303-316):
   - New table added to report header
   - Title: "Počet škol podle typu (s více než 16 hodinami)"
   - Uses existing CSS styling (.blue_light class)
   - Positioned before main "Údaje do ZoR" section

#### Testing
- ✅ Unit tests created (test_school_type_stats.py)
- ✅ All identification tests passed (8/8)
- ✅ Statistics calculation verified:
  - Correct filtering (≥16 hours)
  - Accurate counting by type
  - Edge cases handled (empty DataFrame, exactly 16 hours)
- ✅ Priority handling: ŠD detected before ZŠ in mixed names

#### Compliance Check
- ✅ English-only code (variables, functions, comments)
- ✅ Czech UI labels ("Typ školy", "Počet škol (≥16h)")
- ✅ KISS principle: Minimal, focused implementation
- ✅ DRY: Reused existing aggregation and HTML generation methods
- ✅ No new dependencies: Used existing pandas functionality

#### Output Format
New table in HTML report shows:
```
Počet škol podle typu (s více než 16 hodinami)
| Typ školy | Počet škol (≥16h) |
|-----------|-------------------|
| MŠ        | X                 |
| ZŠ        | Y                 |
| ŠD        | Z                 |
```

#### Next Steps
- Ready for commit with tag [feat-XXX]
- No breaking changes to existing functionality
- Backward compatible with existing reports


### 2025-12-06 – ZorSpecDat Student Count Enhancement (16+ Hours)
- **Feature**: Added table showing count of students with ≥16 hours by school type
- **Implementation Date**: 2025-12-06
- **Developer**: Claude Sonnet 4.5

#### Documentation Consulted
- **Pandas docs** (from previous implementation): groupby, aggregation, filtering
  - Key pattern: Group by (ca, jmena, sablona) to get per-student-per-school totals
  - Filter by hours >= 16
  - Count records by school type
- **Project docs**: CLAUDE.md, PROGRESS.md

#### Key Implementation Difference
**Previous feature (feat-077)**: Count of SCHOOLS with ≥16 hours
**This feature**: Count of STUDENT RECORDS with ≥16 hours

Important: Same student in different schools counts multiple times (as per requirements)

#### Implementation Details
1. **New Method** (src/python/tools/zor_spec_dat_processor.py:453-492):
   - `_calculate_students_16plus_by_type()`: Counts student records with ≥16h
     - Groups by (ca, jmena, sablona) - unique student-school combination
     - Sums hours for each combination
     - Filters combinations with ≥16 hours
     - Identifies school type from sablona
     - Counts records by type (MŠ, ZŠ, ŠD)
     - Returns single-row DataFrame with columns: MŠ, ZŠ, ŠD

2. **HTML Report Position** (zor_spec_dat_processor.py:317-319):
   - Table inserted AFTER main "Údaje do ZoR" table
   - Title: "Počet žáků s více jak 16 h inovativního vzdělávání"
   - Positioned ABOVE school type statistics table
   - Uses same CSS styling (.blue_light class)

#### Testing
- ✅ Comprehensive unit tests created (test_students_16plus.py)
- ✅ Main scenario verified:
  - Student A in ZŠ (18h) → counted
  - Student A in MŠ (16h) → counted separately (same student, different school)
  - Student B in ZŠ (12h total) → not counted
  - Student C in MŠ (18h) → counted
  - Student D in ŠD (8h) → not counted
  - Result: MŠ=2, ZŠ=1, ŠD=0 ✅

- ✅ Edge cases passed:
  - Empty DataFrame → all zeros
  - Exactly 16 hours → counted (>=, not >)
  - Multiple students in same school → all counted
  - Same student in different schools → counted multiple times

#### Output Format
New table in HTML report (horizontal layout):
```
Počet žáků s více jak 16 h inovativního vzdělávání
| MŠ | ZŠ | ŠD |
|----|----|----|
| X  | Y  | Z  |
```

#### Compliance Check
- ✅ English-only code (variables, functions, docstrings)
- ✅ Czech UI labels ("Počet žáků s více jak 16 h...")
- ✅ KISS principle: Reused existing _identify_school_type()
- ✅ DRY: Followed same pattern as school stats
- ✅ No new dependencies
- ✅ Backward compatible

#### Report Structure (Top to Bottom)
1. "Specifické datové položky pro ZoR" (H1)
2. "Počet škol podle typu (s více než 16 hodinami)" (H3 + table)
3. **"Počet žáků s více jak 16 h inovativního vzdělávání" (H3 + table)** ← NEW
4. "Údaje do ZoR" (H2)
5. "Unikátní žáci v ZoR: X" (H3)
6. Main aggregated table (forma/téma)
7. "SDP ZoR" (H2)
8. Per-template tables

#### Next Steps
- Ready for commit with tag [feat-081]
- All tests passing
- No breaking changes


### 2025-12-07 – ChatGPT GUI Redesign Review (ZorSpecDat Results)
- **Topic**: Visual redesign of ZorSpecDat results summary display
- **Implementation Date**: 2025-12-07
- **Consultant**: ChatGPT (GPT-5.1) via Codex CLI
- **Reviewer**: Claude Sonnet 4.5 (chatgpt-consultant agent)

#### Documents Reviewed
- `CLAUDE.md`: Project overview, user profile (10 non-tech colleagues)
- `CORE_DEVELOPMENT_PRINCIPLES.md`: KISS/DRY/YAGNI enforcement
- `src/electron/renderer/styles.css`: Current styles (lines 848-877)
- `src/electron/renderer/renderer.js`: ZorSpecDat results rendering logic

#### Proposed Changes
From js-docs agent consultation:
1. Two-row grid layout (top: totals, bottom: school breakdown)
2. `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))`
3. Modern card design: box-shadow, gradients, border-left color coding
4. Hover effects for interactivity

#### ChatGPT Findings (via Codex)
1. **Layout Improvement**: Two-row grid helps non-tech users scan totals first, then school breakdown
   - Current: Single flex row (lines 848-877)
   - Improved scannability with stacked rows
   
2. **Typography Concerns**: 
   - Current labels: 12px (line 869)
   - Recommendation: Bump to 14px for better readability on school desktops
   - Keep large value text (24px, line 876)
   
3. **Color/Gradient Warning**:
   - Subtle gradients on white can flatten cards
   - Border-left needs high-contrast accent colors
   - Risk: 12px labels may blend into gradient backgrounds
   
4. **Spacing Validation**:
   - Proposed: gap 24px (rows), 16px (cards)
   - Current padding: 15-20px (lines 854-860)
   - Verdict: Keep current padding to avoid cramped appearance
   
5. **Grid Responsiveness**:
   - `auto-fit` can collapse cards <200px width
   - May cause abrupt second-row push on narrow windows
   - Alternative: Consider `auto-fill` for consistent column counts
   
6. **Technical Compatibility**:
   - Electron (Chromium) fully supports CSS Grid, gradients, hover
   - No rendering red flags for Windows
   - Pure CSS = zero performance/security impact

#### Constraint Compliance Check
- Windows-only: No issues
- Existing Electron renderer: Compatible
- Czech UI labels: Maintained
- KISS principle: Pure CSS, no new dependencies
- No architectural changes: Just style tweaks

#### Recommendations
1. **IMPLEMENT** the two-row grid layout
2. **ADJUST** label font size from 12px to 14px
3. **CAREFUL** with gradient stops - ensure contrast near text
4. **TEST** responsive behavior at minimum window width
5. **KEEP** current padding (15-20px)
6. **ENSURE** high-contrast border-left colors for categorization

#### Next Steps
- Implement redesign with ChatGPT's typography adjustments
- Test at various window widths (especially minimum supported)
- Verify gradient contrast with 14px labels
- Consider auto-fill vs auto-fit based on window behavior
- Ready for commit with tag [feat-XXX]

#### Verdict
**APPROVED FOR IMPLEMENTATION** with minor adjustments:
- Bump labels to 14px
- Keep existing padding
- Test grid responsiveness
- Ensure gradient contrast

No blocking issues. Design is appropriate for non-tech Windows users.


### 2025-12-08 – ChatGPT Review: InvVzd Time Range Extraction
- **Topic**: Parsing time ranges in row 7 (e.g., "8:50-9:35" → "8:50")
- **Implementation Date**: 2025-12-08
- **Consultant**: ChatGPT (GPT-5.1) via Codex CLI
- **Reviewer**: Claude Sonnet 4.5 (chatgpt-consultant agent)

#### Documents Reviewed
- `CLAUDE.md`: Core principles (xlwings requirement, Windows-only, KISS/DRY/YAGNI)
- `PROGRESS.md`: InvVzd tool status (100% complete, production-ready)
- `CORE_DEVELOPMENT_PRINCIPLES.md`: Mandatory English code, Czech UI
- `src/python/tools/inv_vzd_processor.py` (lines 513-515): Current time extraction logic

#### Proposed Change
**File**: `src/python/tools/inv_vzd_processor.py`
**Lines**: 513-515

**Current Code**:
```python
time_cell = sheet.cell(row=7, column=col).value
cas = str(time_cell) if time_cell else ''
```

**Proposed Code**:
```python
time_cell = sheet.cell(row=7, column=col).value
cas_raw = str(time_cell).strip() if time_cell else ''
if '-' in cas_raw:
    cas = cas_raw.split('-')[0].strip()
    # log the change
else:
    cas = cas_raw
```

#### ChatGPT Findings (GPT-5.1 via Codex)
1. **CRITICAL: datetime Object Corruption**
   - Excel may store times as `datetime.datetime` or `datetime.time` objects
   - `str(datetime(2024, 1, 10, 8, 30))` → `"2024-01-10 08:30:00"`
   - Proposed code would split on `-` and return `"2024"`, corrupting all proper datetime values
   - **Risk**: Breaking existing files with Excel-formatted times

2. **Type Handling Required**
   - openpyxl returns different types: `str`, `datetime.datetime`, `datetime.time`, or `None`
   - Must use `isinstance()` checks before string operations
   - Recommend `strftime('%H:%M')` for datetime objects to ensure consistent formatting

3. **Dash Character Variants**
   - Users may enter en-dash (`–`), em-dash (`—`), or ASCII hyphen (`-`)
   - Proposed code only checks ASCII `-`, missing other variants
   - Recommend regex: `r'\s*[-–—]\s*'` to support all dash types

4. **Pattern Matching Needed**
   - Only split when string matches time range pattern: `HH:MM-HH:MM`
   - Regex: `^\s*\d{1,2}:\d{2}\s*[-–—]\s*\d{1,2}:\d{2}`
   - Prevents false positives on unrelated hyphenated content

5. **Logging Gap**
   - Inline comment says "# log the change" but no actual logging call
   - Non-tech users need transparency when values are modified
   - Must use `self.add_info()` to show the transformation in UI

#### Constraint Compliance Check
- Windows-only: No issues (existing constraint)
- xlwings compatibility: Safe (change happens before xlwings write)
- KISS principle: WARNING - regex adds complexity, but necessary for correctness
- No new dependencies: Uses existing `re` module (already imported)
- English code / Czech UI: Must maintain (logging in Czech)

#### Recommendations
1. **IMPLEMENT** type checking before string operations:
   ```python
   from datetime import datetime, time
   
   if isinstance(time_cell, (datetime, time)):
       cas = time_cell.strftime('%H:%M')
   elif isinstance(time_cell, str):
       # proceed with range extraction
   ```

2. **USE** regex pattern to identify time ranges only:
   ```python
   import re
   pattern = r'^\s*\d{1,2}:\d{2}\s*[-–—]\s*\d{1,2}:\d{2}'
   if re.match(pattern, cas_raw):
       cas = re.split(r'\s*[-–—]\s*', cas_raw, maxsplit=1)[0].strip()
   ```

3. **ADD** actual logging call:
   ```python
   from openpyxl.utils import get_column_letter
   col_letter = get_column_letter(col)
   self.add_info(f"Upraven čas v buňce {col_letter}7: {cas_raw} → {cas}")
   ```

4. **TEST** edge cases:
   - `datetime.time(8, 50)` → should become `"08:50"` (not split)
   - `datetime.datetime(2024, 1, 10, 8, 50)` → `"08:50"` (not `"2024"`)
   - `"8:50-9:35"` → `"8:50"` (split)
   - `"08:50 – 09:35"` → `"08:50"` (en-dash, spaces)
   - `"8:50 "` → `"8:50"` (trailing space)
   - `None` → `""` (empty)
   - `"8:50"` → `"8:50"` (no split, simple time)

#### Verdict
**CRITICAL ISSUES FOUND - DO NOT IMPLEMENT AS PROPOSED**

The original proposed change has a **critical bug** that will corrupt datetime objects stored by Excel. Must implement type checking and regex pattern matching before proceeding.

#### Recommended Implementation
```python
# Get time (row 7) - specific to 16h
time_cell = sheet.cell(row=7, column=col).value

# Handle different types openpyxl may return
if time_cell is None:
    cas = ''
elif isinstance(time_cell, datetime):
    # Excel datetime object - format time part only
    cas = time_cell.strftime('%H:%M')
elif isinstance(time_cell, time):
    # Excel time object
    cas = time_cell.strftime('%H:%M')
elif isinstance(time_cell, str):
    cas_raw = time_cell.strip()
    
    # Check if it's a time range pattern (HH:MM-HH:MM with various dashes)
    import re
    if re.match(r'^\s*\d{1,2}:\d{2}\s*[-–—]\s*\d{1,2}:\d{2}', cas_raw):
        # Extract start time from range
        cas = re.split(r'\s*[-–—]\s*', cas_raw, maxsplit=1)[0].strip()
        col_letter = get_column_letter(col)
        self.add_info(f"Upraven čas v buňce {col_letter}7: {cas_raw} → {cas}")
    else:
        cas = cas_raw
else:
    # Fallback for unexpected types
    cas = str(time_cell).strip()
```

#### Next Steps
- Implement recommended version with type checking and regex
- Create unit tests for all edge cases listed above
- Test with real Excel files containing both datetime objects and string ranges
- Commit with tag [fix-XXX] after testing
- Document this change in user manual (time range auto-extraction feature)

#### Compliance
- Adheres to KISS (minimal necessary complexity for correctness)
- Follows DRY (reuses existing imports and patterns)
- Respects YAGNI (no speculative features, solves real user problem)
- English code, Czech logging messages
- No new dependencies
- Windows-compatible (regex, datetime are cross-platform)


### 2025-12-08 - ZorSpecDat Control Sums Implementation Review

**Docs consulted:** CLAUDE.md, PROGRESS.md, CORE_DEVELOPMENT_PRINCIPLES.md, zor_spec_dat_processor.py, renderer.js

**Change summary:**
- Added `total_forma_hours` and `total_tema_hours` to ZorSpecDat results
- Backend: Sums `forma_result['cena celkem']` and `tema_result['cena celkem']`
- Frontend: New UI section "Kontrolní součty hodin" with two stat cards
- Lines changed: Python 311-313, 340-341; JS 717-739

**Gemini consultation attempt:**
- CLI invoked with focused prompt about data validation, Czech localization, edge cases
- Result: Timeout (>60s) - Gemini service unavailable/slow
- Decision: Proceed with local analysis per CLAUDE.md guidelines

**Local analysis findings:**

1. **Data Validation - Column Correctness:**
   - ✅ `'cena celkem'` is CORRECT - confirmed by examining `_aggregate()` method (lines 233-249)
   - The column is created from `pocet_hodin` (hours) aggregation
   - Column names defined in `self.result_cols_names = ["forma/téma", "číslo celkem", "cena celkem", "typ"]` (line 59)
   - Despite the name "cena" (price), it actually contains hours sum

2. **Calculation Logic:**
   - ✅ CORRECT - Uses `forma_result['cena celkem'].sum()` which aggregates ALL processed files
   - `forma_result` and `tema_result` are created from `concatenated` DataFrame containing all files (line 305-306)
   - Empty DataFrame check present: `if not forma_result.empty else 0`

3. **Czech Localization Quality:**
   - ✅ APPROPRIATE for target users (administrative workers)
   - "Kontrolní součty hodin" = Control sums of hours (standard accounting term in Czech)
   - "CELKEM HODIN - FORMY" = Total hours - forms (clear, matches existing terminology)
   - "CELKEM HODIN - TÉMATA" = Total hours - topics (consistent with FORMY label)
   - Matches existing Czech UI style (uppercase labels in stat cards)

4. **Edge Cases Handled:**
   - ✅ Empty DataFrames: `if not forma_result.empty else 0`
   - ✅ Frontend undefined check: `students16.total_forma_hours || 0`
   - ✅ Missing data: Conditional rendering checks both values exist
   - ✅ Type safety: `int()` conversion in Python, JavaScript fallback to 0

5. **xlwings Impact:**
   - ✅ NO IMPACT - This change only affects:
     - Post-processing aggregation (after Excel files are read)
     - Frontend display
     - Does NOT touch Excel template reading or writing

6. **Test Scenarios Needed:**
   - Single file processing (verify sum = file hours)
   - Multiple files processing (verify cumulative sum)
   - Empty folder (verify 0 displayed)
   - Mixed valid/invalid files (verify only valid counted)
   - Large dataset (performance check)
   - UI rendering (Czech labels visible, formatting correct)

**Constraint verdict:** ✅ COMPLIANT
- English code, Czech UI: ✅ (variable names English, labels Czech)
- No new dependencies: ✅ (uses existing pandas, JavaScript)
- Windows packaging intact: ✅ (no xlwings changes)
- KISS/DRY/YAGNI: ✅ (simple sum, no premature optimization)

**Final recommendation:**
APPROVE implementation with these verification steps:
1. Test with real multi-file dataset (confirm sums match manual calculation)
2. Verify UI displays properly on Windows (screenshot recommended)
3. Add test case to test suite: `test_zor_spec_dat_control_sums()`
4. Document in user manual if this is a reporting requirement

**Next steps:**
1. Manual testing with production data
2. Optional: Add unit test for control sum calculation
3. Update PROGRESS.md with feature completion
4. Consider adding to HTML report output (currently only in UI)

