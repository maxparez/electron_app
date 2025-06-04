"""
Constants for InvVzd processor
"""

# Version configurations
VERSIONS = {
    "16": {
        "hours": 16,
        "hours_per_session": 2,  # Hours per session/date
        "template_markers": ["16 hodin"],
        "data_start_row": 12,  # Row where student data starts (0-indexed)
        "data_start_col": 2,   # Column C (0-based index, so C = 2)
        "hours_row": 10,       # Row with hours (Excel row 11)
        "dates_row": 5,        # Row with dates (Excel row 6)
        "time_row": 6,         # Row with times (Excel row 7)
        "form_row": 7,         # Row with forms (Excel row 8)
        "topic_row": 8,        # Row with topics (Excel row 9)
        "teacher_row": 9,      # Row with teachers (Excel row 10)
        "activity_row": 4,     # Row with activity numbers (Excel row 5)
        "name_col": 1,         # Column B - student names
        "sdp_hours_col": 4,    # Column E - SDP hours for 16h
        "output_prefix": "16_hodin_inovativniho_vzdelavani",
        "short_prefix": "16h_inv"
    },
    "32": {
        "hours": 32,
        "hours_per_session": 4,  # Hours per session/date
        "template_markers": ["32 hodin"],
        "data_start_row": 11,  # Row where student data starts (0-indexed)
        "data_start_col": 2,   # Column B
        "hours_row": 10,       # Row with hours
        "dates_row": 7,        # Row with dates  
        "activity_row": 6,     # Row with activity numbers
        "name_col": 2,         # Column B - student names
        "sdp_hours_col": 3,    # Column D - SDP hours for 32h
        "output_prefix": "32_hodin_inovativniho_vzdelavani",
        "short_prefix": "32_inv"
    }
}

# Cell references for validation
VALIDATION_CELLS = {
    "template": {
        "version_cell": "B1",
        "sheet": "List1"
    },
    "source": {
        "16": {
            "date_marker": "B5",  
            "expected_text": "datum aktivity"
        },
        "32": {
            "date_marker": "B6",
            "expected_text": "datum aktivity"
        }
    }
}

# Output settings
OUTPUT_SETTINGS = {
    "normalize_filenames": True,
    "remove_diacritics": True,
    "date_format": "%d.%m.%Y",
    "decimal_places": 1
}

# Validation thresholds
VALIDATION_THRESHOLDS = {
    "min_attendance_percent": 0,  # Minimum attendance percentage
    "max_attendance_percent": 100,  # Maximum attendance percentage  
    "date_confidence": 0.7,  # Confidence threshold for date fixing
    "header_match_percent": 0.7  # Percentage of headers that must match
}

# Error messages
ERROR_MESSAGES = {
    "no_template": "Šablona nebyla poskytnuta",
    "no_files": "Žádné soubory k zpracování",
    "invalid_template": "Neplatná šablona",
    "version_mismatch": "Verze souboru neodpovídá šabloně",
    "missing_date": "Chybí datum aktivity v buňce {cell}",
    "invalid_date": "Chybí nebo neplatné datum v řádku {row}",
    "sum_mismatch": "NESOUHLASÍ součty v SDP!\nAktivity: {activities}h\nSDP forma: {forma}h\nSDP téma: {tema}h",
    "file_not_found": "Soubor nenalezen: {file}",
    "read_error": "Chyba při čtení souboru: {error}",
    "write_error": "Chyba při zápisu souboru: {error}",
    "xlwings_required": "Tato funkce vyžaduje Windows s nainstalovaným MS Excel",
    "hours_mismatch": "Nesouhlasí celkový počet hodin. Očekáváno: {expected}, Skutečnost: {actual}",
    "processing_error": "Chyba při zpracování dat: {error}",
    "invalid_excel": "Neplatný Excel soubor: {error}",
    "invalid_data": "Neplatná struktura dat: {error}",
    "no_activities": "Nenalezena žádná data aktivit: {error}",
    "no_data": "Žádná data k zápisu: {error}",
    "no_dates": "Nenalezeny žádné datumy: {error}"
}

# Info messages  
INFO_MESSAGES = {
    "version_detected": "Detekována verze: {version}h šablona",
    "processing_file": "Zpracovávám soubor: {file}",
    "file_complete": "Soubor zpracován: {file}",
    "dates_fixed": "Upozornění: {count} datumů se nepodařilo převést\nProblematické řádky: {rows}",
    "sum_warning": "ZKONTROLUJTE výsledný soubor - aktivity na listu 'Seznam aktivit'",
    "date_fixed": "Opraven datum v buňce {cell}: {original} → {fixed}"
}