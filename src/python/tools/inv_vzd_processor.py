import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import os
import warnings
from typing import Dict, Any, List, Optional, Tuple
import xlwings as xw
from datetime import datetime
import unicodedata
import re

from .base_tool import BaseTool

warnings.filterwarnings('ignore')

# Version-specific constants
VERSIONS = {
    "32": {
        "hours": 32,
        "template": {
            "B1": "32 hodin inovativního vzdělávání"
        },
        "source": {
            "B6": "datum aktivity",
            "B7": "Forma výuky",
            "sheet": "List1"
        },
        "output_prefix": "32_hodin_inovativniho_vzdelavani",
        "short_prefix": "32_inv",
        "data_start_row": 11,
        "data_start_col": 2,  # Column B
        "hours_row": 10,
        "name_col": 2,  # Column B
        "attendance_start_col": 3,  # Column C
        "skiprows": 9,  # Skip first 9 rows in template
        "hours_total_cell": "B10"  # Cell for total hours
    },
    "16": {
        "hours": 16,
        "template": {
            "B1": "Evidence 16 hodin inovativního vzdělávání"
        },
        "source": {
            "B2": "Pořadové číslo aktivity",
            "sheet": "Seznam aktivit"
        },
        "output_prefix": "16_hodin_inovativniho_vzdelavani",
        "short_prefix": "16_inv",
        "data_start_row": 3,
        "data_start_col": 2,  # Column B
        "column_mapping": {
            "datum": "C",
            "cas": "D", 
            "hodin": "E",
            "forma": "F",
            "tema": "G",
            "ucitel": "H"
        }
    }
}


class InvVzdProcessor(BaseTool):
    """Processor for innovative education attendance (16/32 hours)"""
    
    def __init__(self, version=None, logger=None):
        super().__init__(logger)
        self.hours_total = 0
        self.version = version
        self.config = VERSIONS.get(version) if version else None
        
    def validate_inputs(self, files: List[str], options: Dict[str, Any]) -> bool:
        """Validate input files and options"""
        self.clear_messages()
        
        # Check if files provided
        if not files:
            self.add_error("Žádné soubory nebyly poskytnuty")
            return False
            
        # Check if template provided
        template = options.get('template')
        if not template:
            self.add_error("Šablona nebyla poskytnuta")
            return False
            
        # Check if template exists
        if not self.file_exists(template):
            self.add_error(f"Šablona neexistuje: {template}")
            return False
            
        # Validate all source files exist
        for file in files:
            if not self.file_exists(file):
                self.add_error(f"Soubor neexistuje: {file}")
                return False
                
        # Detect template version
        template_version = self._detect_template_version(template)
        if not template_version:
            self.add_error("Nepodařilo se detekovat verzi šablony")
            return False
            
        self.version = template_version
        self.config = VERSIONS[template_version]
        self.add_info(f"Detekována verze šablony: {template_version} hodin")
        
        return True
        
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Process attendance files"""
        if not self.validate_inputs(files, options):
            return self.get_result(False)
            
        try:
            template = options.get('template')
            keep_filename = options.get('keep_filename', True)
            optimize = options.get('optimize', False)
            output_dir = options.get('output_dir', os.path.dirname(files[0]))
            
            results = []
            
            for source_file in files:
                self.add_info(f"Zpracovávám soubor: {os.path.basename(source_file)}")
                
                # Validate version match
                if not self._validate_version_match(source_file, template):
                    continue
                    
                # Process the file
                output_file = self._process_single_file(
                    source_file, 
                    template, 
                    output_dir,
                    keep_filename,
                    optimize
                )
                
                if output_file:
                    results.append({
                        "source": source_file,
                        "output": output_file,
                        "hours": self.hours_total
                    })
                    
            if results:
                self.add_info(f"Úspěšně zpracováno {len(results)} souborů")
                return self.get_result(True, {"processed_files": results})
            else:
                return self.get_result(False)
                
        except Exception as e:
            self.add_error(f"Chyba při zpracování: {str(e)}")
            return self.get_result(False)
            
    def _detect_template_version(self, template_path: str) -> Optional[str]:
        """Detect version from template content"""
        try:
            wb = load_workbook(template_path, read_only=True)
            sheet = wb.worksheets[0]
            
            for version, config in VERSIONS.items():
                match = True
                for cell, expected_value in config["template"].items():
                    actual_value = sheet[cell].value
                    if expected_value.lower() not in str(actual_value).lower():
                        match = False
                        break
                if match:
                    wb.close()
                    return version
                    
            wb.close()
            return None
        except Exception as e:
            self.add_error(f"Chyba při detekci verze šablony: {str(e)}")
            return None
            
    def _detect_source_version(self, source_file: str) -> Optional[str]:
        """Detect version from source content"""
        try:
            wb = load_workbook(source_file, read_only=True)
            sheet_names = wb.sheetnames
            
            # Priority 1: Check for "zdroj-dochazka" sheet (preferred format)
            if "zdroj-dochazka" in sheet_names:
                sheet = wb["zdroj-dochazka"]
                b7_value = sheet["B7"].value
                
                # If B7 contains "čas zahájení" then it's 16h version
                if b7_value and "čas zahájení" in str(b7_value).lower():
                    wb.close()
                    return "16"
                else:
                    # If zdroj-dochazka exists but no "čas zahájení" in B7, it's 32h
                    wb.close() 
                    return "32"
            
            # Priority 2: If no "zdroj-dochazka", use first sheet and check B6/B7
            if sheet_names:
                sheet = wb[sheet_names[0]]  # Take first sheet regardless of name
                b6_value = sheet["B6"].value
                b7_value = sheet["B7"].value
                
                # Check if B6 contains "datum aktivity"
                if b6_value and "datum aktivity" in str(b6_value).lower():
                    # If B7 contains "čas zahájení" then 16h, otherwise 32h
                    if b7_value and "čas zahájení" in str(b7_value).lower():
                        wb.close()
                        return "16"
                    else:
                        wb.close()
                        return "32"
            
            # Fallback: Check legacy formats
            # Check for 16 hour version (complex sheet structure)
            if "Seznam aktivit" in sheet_names:
                sheet = wb["Seznam aktivit"]
                b2_value = sheet["B2"].value
                
                if b2_value and "pořadové číslo aktivity" in str(b2_value).lower():
                    wb.close()
                    return "16"
                    
            wb.close()
            return None
        except Exception as e:
            self.add_error(f"Chyba při detekci verze zdroje: {str(e)}")
            return None
            
    def _validate_version_match(self, source_file: str, template_path: str) -> bool:
        """Validate that source data version matches template version"""
        source_version = self._detect_source_version(source_file)
        
        if source_version is None:
            self.add_error(f"Nepodařilo se detekovat verzi souboru: {os.path.basename(source_file)}")
            return False
            
        if source_version != self.version:
            source_hours = VERSIONS[source_version]["hours"]
            template_hours = self.config["hours"]
            self.add_error(
                f"Nesoulad verzí: zdrojový soubor má {source_hours} hodin, "
                f"ale šablona je pro {template_hours} hodin"
            )
            return False
            
        return True
        
    def _process_single_file(self, source_file: str, template_path: str, 
                           output_dir: str, keep_filename: bool, 
                           optimize: bool) -> Optional[str]:
        """Process a single attendance file"""
        try:
            # Read source data
            source_data = self._read_source_data(source_file)
            if source_data is None:
                return None
                
            # Optimize if requested
            if optimize:
                source_data = self._optimize_data(source_data)
                
            # Create output filename
            output_file = self._create_output_filename(
                source_file, output_dir, keep_filename
            )
            
            # Copy template and fill with data
            self._copy_template_with_data(
                template_path, output_file, source_data, source_file
            )
            
            self.add_info(f"Vytvořen výstupní soubor: {os.path.basename(output_file)}")
            return output_file
            
        except Exception as e:
            self.add_error(f"Chyba při zpracování souboru {os.path.basename(source_file)}: {str(e)}")
            return None
            
    def _read_source_data(self, source_file: str) -> Optional[pd.DataFrame]:
        """Read and process source data"""
        try:
            if self.version == "16":
                return self._read_16_hour_data(source_file)
            elif self.version == "32":
                return self._read_32_hour_data(source_file)
            else:
                self.add_error(f"Nepodporovaná verze: {self.version}")
                return None
                
        except Exception as e:
            self.add_error(f"Chyba při čtení zdrojových dat: {str(e)}")
            return None
            
    def _read_16_hour_data(self, source_file: str) -> Optional[pd.DataFrame]:
        """Read data from 16 hour source file (Seznam aktivit sheet)"""
        try:
            # Read from Seznam aktivit sheet with header=1 to use row 1 as headers
            df = pd.read_excel(source_file, sheet_name="Seznam aktivit", header=0)
            
            # The actual column names from the debug output
            expected_columns = {
                'Unnamed: 1': 'poradi',
                'Unnamed: 2': 'datum', 
                'Unnamed: 3': 'cas',
                'Unnamed: 4': 'hodin',
                'Unnamed: 5': 'forma',
                'Unnamed: 6': 'tema',
                'Unnamed: 7': 'ucitel'
            }
            
            # Rename columns 
            df = df.rename(columns=expected_columns)
            
            # Remove rows where poradi is NaN (empty rows)
            df = df.dropna(subset=['poradi'])
            
            # Keep only rows with actual activity numbers (skip header rows)
            df = df[df['poradi'].apply(lambda x: str(x).isdigit() if pd.notna(x) else False)]
            
            # Convert hours to numeric
            df['hodin'] = pd.to_numeric(df['hodin'], errors='coerce')
            
            # Remove rows with invalid hours
            df = df.dropna(subset=['hodin'])
            df = df[df['hodin'] > 0]
            
            # Format dates properly - ensure they include full date (DD.MM.YYYY)
            if 'datum' in df.columns:
                # First try to fix incomplete dates if they exist
                df['datum'] = self._fix_incomplete_dates(df['datum'])
                # Then convert to datetime and format
                df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
                # Format as DD.MM.YYYY (this also handles already-datetime objects)
                df['datum'] = df['datum'].dt.strftime('%d.%m.%Y')
            
            # Format time if present
            if 'cas' in df.columns:
                # Keep time as is or format if needed
                df['cas'] = df['cas'].astype(str)
            
            # Calculate total hours
            self.hours_total = df['hodin'].sum()
            self.add_info(f"Celkem hodin: {self.hours_total}")
            self.add_info(f"Načteno {len(df)} aktivit")
            
            # Select required columns for output
            required_columns = ['datum', 'cas', 'hodin', 'forma', 'tema', 'ucitel']
            df = df[required_columns]
            
            return df
            
        except Exception as e:
            self.add_error(f"Chyba při čtení 16 hodinových dat: {str(e)}")
            return None
            
    def _read_32_hour_data(self, source_file: str) -> Optional[pd.DataFrame]:
        """Read data from 32 hour source file (List1 or zdroj-dochazka sheet)"""
        try:
            wb = load_workbook(source_file)
            
            # Try to find the correct sheet - prefer zdroj-dochazka, fallback to List1
            sheet_name = None
            if "zdroj-dochazka" in wb.sheetnames:
                sheet_name = "zdroj-dochazka"
            elif "List1" in wb.sheetnames:
                sheet_name = "List1"
            else:
                # Use first sheet as fallback
                sheet_name = wb.sheetnames[0]
                
            sheet = wb[sheet_name]
            self.add_info(f"Čtu 32h data z listu: {sheet_name}")
            
            if sheet_name == "zdroj-dochazka":
                # New format with zdroj-dochazka sheet
                data = []
                
                # Read data from specific rows
                # Row 6: dates, Row 7: forms, Row 8: topics, Row 9: teachers, Row 10: hours
                col = 3  # Start from column C (first activity)
                
                while True:
                    # Check if there's data in this column
                    hours_cell = sheet.cell(row=10, column=col).value
                    if hours_cell is None or str(hours_cell).strip() == '':
                        break
                        
                    try:
                        hours = int(float(str(hours_cell)))
                        if hours <= 0:
                            break
                    except (ValueError, TypeError):
                        break
                    
                    # Get date (row 6)
                    date_cell = sheet.cell(row=6, column=col).value
                    if date_cell:
                        if hasattr(date_cell, 'strftime'):
                            # It's already a datetime object
                            datum = date_cell.strftime('%d.%m.%Y')
                        else:
                            # Try to parse as string
                            datum = str(date_cell)
                    else:
                        datum = datetime.now().strftime('%d.%m.%Y')
                    
                    # Get form (row 7)
                    forma_cell = sheet.cell(row=7, column=col).value
                    forma = str(forma_cell) if forma_cell else 'Neurčeno'
                    
                    # Get topic (row 8)
                    tema_cell = sheet.cell(row=8, column=col).value
                    tema = str(tema_cell) if tema_cell else 'Neurčeno'
                    
                    # Get teacher (row 9)
                    ucitel_cell = sheet.cell(row=9, column=col).value
                    ucitel = str(ucitel_cell) if ucitel_cell else 'Neurčeno'
                    
                    data.append({
                        'datum': datum,
                        'hodin': hours,
                        'forma': forma,
                        'tema': tema,
                        'ucitel': ucitel
                    })
                    
                    col += 1
                    
            else:
                # Legacy format with List1 sheet
                hours_data = []
                activities = []
                
                # Get hours for each activity (row 10, starting from column C)
                col = 3  # Column C
                while True:
                    cell_value = sheet.cell(row=10, column=col).value
                    if cell_value is None or cell_value == 0:
                        break
                    hours_data.append(int(cell_value))
                    activities.append(f"Aktivita {col-2}")  # Activity 1, 2, 3...
                    col += 1
                
                # Create DataFrame with activity data  
                current_date = datetime.now()
                data = []
                for i, (activity, hours) in enumerate(zip(activities, hours_data)):
                    # Use sequential dates starting from today
                    activity_date = current_date.replace(day=1) + pd.Timedelta(days=i*7)  # Weekly intervals
                    data.append({
                        'datum': activity_date.strftime('%d.%m.%Y'),
                        'hodin': hours,
                        'forma': 'Neurčeno',
                        'tema': activity,
                        'ucitel': 'Neurčeno'
                    })
            
            df = pd.DataFrame(data)
            
            # Calculate total hours
            self.hours_total = df['hodin'].sum()
            self.add_info(f"Celkem hodin: {self.hours_total}")
            
            wb.close()
            return df
            
        except Exception as e:
            self.add_error(f"Chyba při čtení 32 hodinových dat: {str(e)}")
            return None
            
    def _optimize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data by removing duplicates"""
        original_count = len(df)
        df = df.drop_duplicates()
        removed_count = original_count - len(df)
        
        if removed_count > 0:
            self.add_info(f"Odstraněno {removed_count} duplicitních řádků")
            
        return df
        
    def _normalize_filename(self, filename: str) -> str:
        """
        Normalize filename: remove diacritics, replace spaces with underscores
        
        Args:
            filename: Original filename
            
        Returns:
            Normalized filename without diacritics and spaces
        """
        # Remove file extension if present (only .xlsx, .xls at the end)
        if filename.lower().endswith(('.xlsx', '.xls')):
            name_without_ext = filename.rsplit('.', 1)[0]
        else:
            name_without_ext = filename
        
        # Remove diacritics (Czech characters like á, č, ě, etc.)
        normalized = unicodedata.normalize('NFD', name_without_ext)
        ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        
        # Replace problematic characters with underscores
        # Keep only alphanumeric and underscore, replace everything else
        clean_text = re.sub(r'[^\w]', '_', ascii_text)
        
        # Remove multiple consecutive underscores
        clean_text = re.sub(r'_+', '_', clean_text)
        
        # Remove leading/trailing underscores
        clean_text = clean_text.strip('_')
        
        return clean_text
        
    def _fix_incomplete_dates(self, date_series: pd.Series) -> pd.Series:
        """
        Fix incomplete dates by inferring missing years from context
        
        Examples:
        - 14.5.2024, 16.6.2024, 17.6., 19.7.2024 → 17.6.2024
        - 24.1.2025, 15.2., 20.3.2025 → 15.2.2025
        
        Args:
            date_series: Series with date values (strings or datetime objects)
            
        Returns:
            Series with fixed dates
        """
        fixed_dates = []
        uncertain_fixes = []
        
        # Convert to string series for processing
        date_strings = date_series.astype(str)
        
        for i, date_str in enumerate(date_strings):
            original_date = date_str
            
            # Skip if already a proper datetime or NaN
            if pd.isna(date_str) or date_str == 'nan':
                fixed_dates.append(date_str)
                continue
                
            # If it's already a datetime object converted to string, skip processing
            original_value = date_series.iloc[i]
            if pd.api.types.is_datetime64_any_dtype(pd.Series([original_value])):
                fixed_dates.append(date_str)
                continue
                
            # Clean up common issues
            date_str = str(date_str).strip()
            
            # Remove extra spaces: "24 .1.2025" → "24.1.2025"
            date_str = re.sub(r'\s+\.', '.', date_str)
            date_str = re.sub(r'\.\s+', '.', date_str)
            
            # Check if date is incomplete (missing year)
            parts = date_str.split('.')
            
            
            if len(parts) == 2:  # DD.MM format - missing year
                day, month = parts
                inferred_year = self._infer_missing_year(i, date_strings, day, month)
                
                if inferred_year['confidence'] == 'high':
                    fixed_date = f"{day}.{month}.{inferred_year['year']}"
                    fixed_dates.append(fixed_date)
                    self.add_info(f"Doplněn rok {inferred_year['year']} pro datum {original_date} → {fixed_date}")
                elif inferred_year['confidence'] == 'medium':
                    fixed_date = f"{day}.{month}.{inferred_year['year']}"
                    fixed_dates.append(fixed_date)
                    uncertain_fixes.append(f"{original_date} → {fixed_date}")
                else:
                    # Low confidence - add current year as fallback
                    current_year = datetime.now().year
                    fixed_date = f"{day}.{month}.{current_year}"
                    fixed_dates.append(fixed_date)
                    uncertain_fixes.append(f"{original_date} → {fixed_date} (neistý)")
                    
            elif len(parts) == 3:  # DD.MM.YYYY format - check if year is empty
                day, month, year = parts
                if not year or year.strip() == "":  # Empty year part
                    inferred_year = self._infer_missing_year(i, date_strings, day, month)
                    
                    if inferred_year['confidence'] == 'high':
                        fixed_date = f"{day}.{month}.{inferred_year['year']}"
                        fixed_dates.append(fixed_date)
                        self.add_info(f"Doplněn rok {inferred_year['year']} pro datum {original_date} → {fixed_date}")
                    elif inferred_year['confidence'] == 'medium':
                        fixed_date = f"{day}.{month}.{inferred_year['year']}"
                        fixed_dates.append(fixed_date)
                        uncertain_fixes.append(f"{original_date} → {fixed_date}")
                    else:
                        # Low confidence - add current year as fallback
                        current_year = datetime.now().year
                        fixed_date = f"{day}.{month}.{current_year}"
                        fixed_dates.append(fixed_date)
                        uncertain_fixes.append(f"{original_date} → {fixed_date} (neistý)")
                else:
                    # Complete date
                    fixed_dates.append(date_str)
            else:
                # Invalid format
                fixed_dates.append(date_str)
                self.add_warning(f"Nerozpoznaný formát data: {original_date}")
        
        # Report uncertain fixes
        if uncertain_fixes:
            self.add_warning("Následující data byla opravena s nejistotou:")
            for fix in uncertain_fixes:
                self.add_warning(f"  {fix}")
            self.add_warning("Zkontrolujte správnost a případně soubor opravte a spusťte znovu")
            
        return pd.Series(fixed_dates)
        
    def _infer_missing_year(self, index: int, date_strings: pd.Series, day: str, month: str) -> dict:
        """
        Infer missing year from neighboring dates
        
        Args:
            index: Current position in series
            date_strings: All date strings
            day: Day part of incomplete date
            month: Month part of incomplete date
            
        Returns:
            Dict with 'year' and 'confidence' ('high', 'medium', 'low')
        """
        years_found = []
        
        # Look for complete dates in nearby positions (±3 positions)
        search_range = range(max(0, index-3), min(len(date_strings), index+4))
        
        for i in search_range:
            if i == index:
                continue
                
            date_str = str(date_strings.iloc[i]).strip()
            parts = date_str.split('.')
            
            if len(parts) == 3:  # Complete date DD.MM.YYYY
                try:
                    year = int(parts[2])
                    if 2020 <= year <= 2030:  # Reasonable year range
                        years_found.append(year)
                except ValueError:
                    continue
        
        if not years_found:
            # No nearby years found - use current year
            return {'year': datetime.now().year, 'confidence': 'low'}
            
        # Find most common year
        year_counts = {}
        for year in years_found:
            year_counts[year] = year_counts.get(year, 0) + 1
            
        most_common_year = max(year_counts.keys(), key=lambda y: year_counts[y])
        
        # Determine confidence based on consistency
        if len(set(years_found)) == 1:
            # All nearby years are the same
            confidence = 'high'
        elif year_counts[most_common_year] >= len(years_found) * 0.7:
            # Most common year appears in 70%+ of cases
            confidence = 'medium'
        else:
            # Mixed years
            confidence = 'low'
            
        # Additional logic: check if month sequence makes sense
        try:
            current_month = int(month)
            
            # Look at previous and next complete dates to see if year makes sense
            for i in [index-1, index+1]:
                if 0 <= i < len(date_strings):
                    neighbor_parts = str(date_strings.iloc[i]).strip().split('.')
                    if len(neighbor_parts) == 3:
                        try:
                            neighbor_month = int(neighbor_parts[1])
                            neighbor_year = int(neighbor_parts[2])
                            
                            # If this date's month fits chronologically, increase confidence
                            if i == index-1 and current_month > neighbor_month and most_common_year == neighbor_year:
                                confidence = 'high'
                            elif i == index+1 and current_month < neighbor_month and most_common_year == neighbor_year:
                                confidence = 'high'
                                
                        except ValueError:
                            continue
                            
        except ValueError:
            pass
            
        return {'year': most_common_year, 'confidence': confidence}
        
    def _create_output_filename(self, source_file: str, output_dir: str, 
                               keep_filename: bool) -> str:
        """Create output filename with proper prefix and normalization"""
        if keep_filename:
            # Get original filename without extension
            base_name = os.path.splitext(os.path.basename(source_file))[0]
            
            # Normalize filename (remove diacritics, replace spaces)
            normalized_name = self._normalize_filename(base_name)
            
            # Add version prefix
            version_prefix = f"{self.version}h_inv_"
            output_filename = f"{version_prefix}{normalized_name}_MSMT.xlsx"
            
            return os.path.join(output_dir, output_filename)
        else:
            # Fallback with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_prefix = f"{self.version}h_inv_"
            return os.path.join(output_dir, f"{version_prefix}MSMT_{timestamp}.xlsx")
            
    def _copy_template_with_data(self, template_path: str, output_path: str, 
                                data: pd.DataFrame, source_file: str):
        """Copy template file and fill with data using xlwings - following original approach"""
        try:
            # Following original approach: open template directly, fill data, save as new file
            wb = xw.Book(template_path)
            
            # STEP 1: Write student names to "Seznam účastníků" sheet at B4
            sheet = wb.sheets['Seznam účastníků']
            
            # Unprotect sheet if protected
            try:
                sheet.api.Unprotect()
            except:
                pass  # Sheet might not be protected
            
            # Extract student names from source file (column B, from row 11 until two empty rows)
            student_names = self._extract_student_names_from_data(source_file)
            
            # Write student names starting at B4
            if len(student_names) > 0:
                sheet.range("B4").options(ndim="expand", transpose=True).value = student_names
            
            # Save as new file and close
            wb.save(output_path)
            wb.close()
            
        except Exception as e:
            self.add_error(f"Chyba při kopírování šablony: {str(e)}")
            raise
    
    def _extract_student_names_from_data(self, source_file: str) -> List[str]:
        """Extract student names from source file column B starting from row 11"""
        try:
            wb = load_workbook(source_file, read_only=True)
            sheet_name = "zdroj-dochazka" if "zdroj-dochazka" in wb.sheetnames else wb.sheetnames[0]
            sheet = wb[sheet_name]
            
            student_names = []
            empty_count = 0
            
            # Start from row 11 (0-indexed = 10)
            for row in range(10, sheet.max_row):
                cell_value = sheet.cell(row=row+1, column=2).value  # Column B
                
                if cell_value is None or str(cell_value).strip() == "":
                    empty_count += 1
                    if empty_count >= 2:  # Two consecutive empty rows
                        break
                else:
                    empty_count = 0
                    student_names.append(str(cell_value).strip())
            
            wb.close()
            self.add_info(f"Načteno {len(student_names)} jmen žáků")
            return student_names
            
        except Exception as e:
            self.add_error(f"Chyba při načítání jmen žáků: {str(e)}")
            return []
            
    def process_paths(self, source_files: List[str], template_path: str, 
                     output_dir: str, keep_filename: bool = True,
                     optimize: bool = False) -> Dict[str, Any]:
        """
        Process files using file paths (for testing)
        
        Args:
            source_files: List of source file paths
            template_path: Path to template file
            output_dir: Output directory
            keep_filename: Whether to keep original filename
            optimize: Whether to optimize data
            
        Returns:
            Processing result dictionary
        """
        try:
            self.clear_messages()
            
            # Validate template
            if not self.file_exists(template_path):
                self.add_error(f"Šablona neexistuje: {template_path}")
                return {"success": False, "output_files": []}
                
            # Detect and validate template version
            template_version = self._detect_template_version(template_path)
            if template_version != self.version:
                self.add_error(f"Verze šablony ({template_version}) neodpovídá procesoru ({self.version})")
                return {"success": False, "output_files": []}
                
            # Process files
            output_files = []
            for source_file in source_files:
                if not self.file_exists(source_file):
                    self.add_error(f"Zdrojový soubor neexistuje: {source_file}")
                    continue
                    
                # Validate version match
                if not self._validate_version_match(source_file, template_path):
                    continue
                    
                # Process file
                output_file = self._process_single_file(
                    source_file, template_path, output_dir, 
                    keep_filename, optimize
                )
                
                if output_file:
                    output_files.append(output_file)
                    
            success = len(output_files) > 0 and len(self.errors) == 0
            return {
                "success": success,
                "output_files": output_files,
                "errors": self.errors,
                "warnings": self.warnings,
                "info": self.info_messages
            }
            
        except Exception as e:
            self.add_error(f"Neočekávaná chyba: {str(e)}")
            return {"success": False, "output_files": []}
            
    def clear_messages(self):
        """Clear all messages"""
        self.errors.clear()
        self.warnings.clear()
        self.info_messages.clear()
        
    def file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        return os.path.isfile(filepath)