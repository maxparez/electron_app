
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

