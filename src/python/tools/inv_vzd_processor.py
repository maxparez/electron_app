"""
Refactored InvVzd Processor - Process innovative education attendance files

This is a cleaner, more maintainable version using helper modules.
"""

import pandas as pd
import numpy as np
import os
import warnings
from typing import Dict, Any, List, Optional, Tuple
import platform

from .base_tool import BaseTool
from .date_utils import DateParser
from .excel_utils import ExcelHelper
from .inv_vzd_constants import VERSIONS, VALIDATION_CELLS, ERROR_MESSAGES, INFO_MESSAGES
from .error_handler import ErrorHandler, ToolError
from .validation_utils import FileValidator, ExcelValidator, DataValidator
from .logger_utils import ToolLogger, log_execution_time
from datetime import datetime
import re
import traceback

# Check xlwings availability
try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False

warnings.filterwarnings('ignore')


class InvVzdProcessor(BaseTool):
    """Refactored processor for innovative education attendance (16/32 hours)"""
    
    def __init__(self, version: Optional[str] = None, logger=None):
        super().__init__(logger)
        self.hours_total = 0
        self.version = version
        self.config = VERSIONS.get(version) if version else None
        self.date_parser = DateParser()
        self.excel_helper = ExcelHelper()
        self.error_handler = ErrorHandler(self.logger)
        self.tool_logger = ToolLogger(self.logger, "INVVZD")
        self.file_validator = FileValidator()
        self.excel_validator = ExcelValidator()
        self.data_validator = DataValidator()
        
    def validate_inputs(self, files: List[str], options: Dict[str, Any]) -> bool:
        """Validate input files and options"""
        self.clear_messages()
        self.logger.info(f"[INVVZD] Validating inputs: {len(files)} files")
        
        # Check if files provided
        if not files:
            self._add_error('no_files')
            return False
            
        # Check if template provided
        template = options.get('template')
        if not template:
            self._add_error('no_template')
            return False
            
        # Check if template exists
        if not self.file_exists(template):
            self._add_error('file_not_found', file=template)
            return False
            
        # Validate all source files exist
        for file in files:
            if not self.file_exists(file):
                self._add_error('file_not_found', file=file)
                return False
                
        # Detect template version
        template_version = self._detect_template_version(template)
        if not template_version:
            self._add_error('invalid_template')
            return False
            
        self.version = template_version
        self.config = VERSIONS[template_version]
        
        return True
        
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Process attendance files"""
        self.logger.info(f"[INVVZD] Processing {len(files)} files")
        
        if not self.validate_inputs(files, options):
            return self.get_result(False)
            
        try:
            template = options.get('template')
            output_dir = options.get('output_dir', os.path.dirname(files[0]))
            
            results = []
            
            for source_file in files:
                self.logger.info(f"[INVVZD] Processing: {source_file}")
                
                # Clear messages for this file
                self.clear_file_messages()
                
                # Process single file
                result = self._process_single_file(
                    source_file, 
                    template, 
                    output_dir
                )
                results.append(result)
                
            # Return combined results in expected format
            success = all(r.get('status') == 'success' for r in results)
            
            # Format data for compatibility with original API
            data = {"processed_files": results}
            
            # Create result with get_result method for consistency
            if success:
                return self.get_result(True, data)
            else:
                return self.get_result(False, data)
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Process error: {str(e)}")
            self._add_error('read_error', error=str(e))
            return self.get_result(False)
            
    def _process_single_file(self, source_file: str, template_file: str, 
                           output_dir: str) -> Dict[str, Any]:
        """Process a single attendance file"""
        try:
            # Store source file for xlwings to use
            self._current_source_file = source_file
            
            # Validate version match
            if not self._validate_version_match(source_file, template_file):
                return self._create_file_result(source_file, None, "error")
                
            # Read and process data
            if self.version == "16":
                processed_data = self._process_16h_file(source_file, template_file)
            else:
                processed_data = self._process_32h_file(source_file, template_file)
                
            if not processed_data:
                return self._create_file_result(source_file, None, "error")
                
            # Generate output filename
            output_file = self._generate_output_filename(source_file, output_dir)
            
            # Write output
            if self._write_output(template_file, output_file, processed_data):
                self._add_info('file_complete', file=os.path.basename(output_file))
                return self._create_file_result(source_file, output_file, "success", 
                                              self.hours_total)
            else:
                return self._create_file_result(source_file, None, "error")
                
        except Exception as e:
            self.logger.error(f"[INVVZD] Error processing {source_file}: {str(e)}")
            self._add_error('read_error', error=str(e))
            return self._create_file_result(source_file, None, "error")
            
    @log_execution_time("INVVZD")
    def _process_16h_file(self, source_file: str, template_file: str) -> Optional[Dict[str, pd.DataFrame]]:
        """Process 16-hour attendance file"""
        try:
            # Validate Excel file
            valid, msg = self.excel_validator.validate_excel_file(source_file)
            if not valid:
                self._add_error('invalid_excel', error=msg)
                return None
                
            # Read source data - try zdroj-dochazka first, then fall back to first sheet
            try:
                df = pd.read_excel(source_file, sheet_name='zdroj-dochazka')
                self.logger.info(f"[INVVZD] Using sheet: zdroj-dochazka")
            except ValueError:
                # Fall back to first sheet
                df = pd.read_excel(source_file, sheet_name=0)
                excel_file = pd.ExcelFile(source_file)
                sheet_name = excel_file.sheet_names[0]
                self.logger.info(f"[INVVZD] Using first sheet: {sheet_name}")
            
            # Validate DataFrame structure
            valid, msg = self.data_validator.validate_dataframe(
                df, min_rows=5, min_cols=10
            )
            if not valid:
                self._add_error('invalid_data', error=msg)
                return None
            
            # Get configuration
            config = self.config
            
            # Find dates row
            dates = self._extract_dates_16h(df)
            if not dates:
                return None
                
            # Process attendance data
            attendance_data = self._process_attendance_16h(df, dates)
            
            return attendance_data
            
        except Exception as e:
            self.error_handler.handle_exception(e, "_process_16h_file")
            return None
            
    @log_execution_time("INVVZD")
    def _process_32h_file(self, source_file: str, template_file: str) -> Optional[Dict[str, pd.DataFrame]]:
        """Process 32-hour attendance file"""
        try:
            # Validate Excel file
            valid, msg = self.excel_validator.validate_excel_file(source_file)
            if not valid:
                self._add_error('invalid_excel', error=msg)
                return None
                
            # Read source data - try zdroj-dochazka first, then fall back to first sheet
            try:
                df = pd.read_excel(source_file, sheet_name='zdroj-dochazka')
                self.logger.info(f"[INVVZD] Using sheet: zdroj-dochazka")
            except ValueError:
                # Fall back to first sheet
                df = pd.read_excel(source_file, sheet_name=0)
                excel_file = pd.ExcelFile(source_file)
                sheet_name = excel_file.sheet_names[0]
                self.logger.info(f"[INVVZD] Using first sheet: {sheet_name}")
            
            # Validate DataFrame structure
            valid, msg = self.data_validator.validate_dataframe(
                df, min_rows=5, min_cols=10
            )
            if not valid:
                self._add_error('invalid_data', error=msg)
                return None
            
            # Get configuration
            config = self.config
            
            # Find dates row
            dates = self._extract_dates_32h(df)
            if not dates:
                return None
                
            # Process attendance data
            attendance_data = self._process_attendance_32h(df, dates)
            
            return attendance_data
            
        except Exception as e:
            self.error_handler.handle_exception(e, "_process_32h_file")
            return None
            
    def _extract_dates_16h(self, df: pd.DataFrame) -> Optional[List]:
        """Extract dates from 16h format"""
        config = self.config
        dates_row = config['dates_row']
        
        try:
            # Get date values
            date_values = df.iloc[dates_row, config['data_start_col']:].tolist()
            
            # Filter out empty values
            raw_dates = []
            for date_val in date_values:
                if pd.isna(date_val) or str(date_val).strip() == '':
                    break
                raw_dates.append(date_val)
                
            if not raw_dates:
                self._add_error('no_dates', error="Nenalezeny žádné datumy")
                return None
                
            # Fix incomplete dates
            fixed_dates = self._fix_incomplete_dates(raw_dates, dates_row)
            
            # Check for None values (failed parsing)
            missing_dates = []
            valid_dates = []
            
            for i, date in enumerate(fixed_dates):
                if date is None:
                    col_letter = chr(ord('A') + config['data_start_col'] + i)
                    cell = f"{col_letter}{dates_row + 1}"
                    missing_dates.append(cell)
                else:
                    valid_dates.append(date)
                    
            # Report missing dates
            for cell in missing_dates:
                self._add_error('missing_date', cell=cell)
                
            return valid_dates if len(valid_dates) > 0 else None
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Date extraction error: {str(e)}")
            return None
            
    def _extract_dates_32h(self, df: pd.DataFrame) -> Optional[List]:
        """Extract dates from 32h format"""
        # Similar implementation to 16h
        return self._extract_dates_16h(df)
        
    def _create_file_result(self, source: str, output: Optional[str], 
                          status: str, hours: float = 0) -> Dict[str, Any]:
        """Create result dictionary for a single file"""
        return {
            "source": source,
            "output": output,
            "hours": hours,
            "status": status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "info": list(self.info_messages)
        }
        
    def _add_error(self, error_key: str, **kwargs):
        """Add error message from constants"""
        message = ERROR_MESSAGES.get(error_key, error_key)
        if kwargs:
            message = message.format(**kwargs)
        self.add_error(message)
        self.logger.error(f"[INVVZD] ERROR: {message}")
        
    def _add_info(self, info_key: str, **kwargs):
        """Add info message from constants"""
        message = INFO_MESSAGES.get(info_key, info_key)
        if kwargs:
            message = message.format(**kwargs)
        self.add_info(message)
        self.logger.info(f"[INVVZD] INFO: {message}")
        
    def _detect_template_version(self, template_path: str) -> Optional[str]:
        """Detect template version using excel helper"""
        return self.excel_helper.detect_version_from_template(template_path)
        
    def _detect_source_version(self, source_file: str) -> Optional[str]:
        """Detect version from source content"""
        self.logger.info(f"[INVVZD] === DETECT SOURCE VERSION START ===")
        self.logger.info(f"[INVVZD] Source file: {source_file}")
        
        try:
            from openpyxl import load_workbook
            wb = load_workbook(source_file, read_only=True)
            sheet_names = wb.sheetnames
            self.logger.info(f"[INVVZD] Sheet names in file: {sheet_names}")
            
            # Priority 1: Check for "zdroj-dochazka" sheet (preferred format)
            if "zdroj-dochazka" in sheet_names:
                self.logger.info(f"[INVVZD] Found 'zdroj-dochazka' sheet")
                sheet = wb["zdroj-dochazka"]
                b7_value = sheet["B7"].value
                self.logger.info(f"[INVVZD] B7 value in zdroj-dochazka: '{b7_value}'")
                
                # If B7 contains "čas zahájení" then it's 16h version
                if b7_value and "čas zahájení" in str(b7_value).lower():
                    wb.close()
                    self.logger.info(f"[INVVZD] Detected version: 16h (found 'čas zahájení' in B7)")
                    return "16"
                else:
                    # If zdroj-dochazka exists but no "čas zahájení" in B7, it's 32h
                    wb.close()
                    self.logger.info(f"[INVVZD] Detected version: 32h (zdroj-dochazka exists but no 'čas zahájení')") 
                    return "32"
            
            # Priority 2: If no "zdroj-dochazka", use first sheet and check B5/B6/B7
            if sheet_names:
                self.logger.info(f"[INVVZD] No 'zdroj-dochazka' sheet, checking first sheet: {sheet_names[0]}")
                sheet = wb[sheet_names[0]]  # Take first sheet regardless of name
                b5_value = sheet["B5"].value
                b6_value = sheet["B6"].value
                b7_value = sheet["B7"].value
                self.logger.info(f"[INVVZD] B5 value: '{b5_value}'")
                self.logger.info(f"[INVVZD] B6 value: '{b6_value}'")
                self.logger.info(f"[INVVZD] B7 value: '{b7_value}'")
                
                # Check if B5 contains "datum aktivity" (16h format)
                if b5_value and "datum aktivity" in str(b5_value).lower():
                    self.logger.info(f"[INVVZD] Found 'datum aktivity' in B5")
                    # If B6 contains "čas zahájení" then 16h, otherwise 32h
                    if b6_value and "čas zahájení" in str(b6_value).lower():
                        wb.close()
                        self.logger.info(f"[INVVZD] Detected version: 16h (found 'čas zahájení' in B6)")
                        return "16"
                    else:
                        wb.close()
                        self.logger.info(f"[INVVZD] Detected version: 32h (B5 has 'datum aktivity' but no 'čas zahájení' in B6)")
                        return "32"
                
                # Check if B6 contains "datum aktivity" (32h format)
                elif b6_value and "datum aktivity" in str(b6_value).lower():
                    self.logger.info(f"[INVVZD] Found 'datum aktivity' in B6")
                    # Check B7 for "Forma výuky" to confirm 32h
                    if b7_value and "forma výuky" in str(b7_value).lower():
                        wb.close()
                        self.logger.info(f"[INVVZD] Detected version: 32h (found 'datum aktivity' in B6 and 'Forma výuky' in B7)")
                        return "32"
            
            # Fallback: Check legacy formats
            self.logger.info(f"[INVVZD] Checking legacy formats...")
            # Check for 16 hour version (complex sheet structure)
            if "Seznam aktivit" in sheet_names:
                self.logger.info(f"[INVVZD] Found 'Seznam aktivit' sheet")
                sheet = wb["Seznam aktivit"]
                b2_value = sheet["B2"].value
                self.logger.info(f"[INVVZD] B2 value in Seznam aktivit: '{b2_value}'")
                
                if b2_value and "pořadové číslo aktivity" in str(b2_value).lower():
                    wb.close()
                    self.logger.info(f"[INVVZD] Detected version: 16h (found 'pořadové číslo aktivity' in Seznam aktivit B2)")
                    return "16"
                    
            wb.close()
            self.logger.warning(f"[INVVZD] Could not detect version - no matching patterns found")
            return None
        except Exception as e:
            self.logger.error(f"[INVVZD] Exception in _detect_source_version: {str(e)}")
            import traceback
            self.logger.error(f"[INVVZD] Traceback: {traceback.format_exc()}")
            return None
        
    def _validate_version_match(self, source_file: str, template_file: str) -> bool:
        """Validate that source file matches template version"""
        # Implementation would check if source file structure matches template
        # For now, return True
        return True
        
    def _generate_output_filename(self, source_file: str, output_dir: str) -> str:
        """Generate output filename"""
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        
        # Normalize if needed
        normalized = self.excel_helper.normalize_filename(base_name)
        
        # Add prefix
        prefix = self.config['short_prefix']
        output_name = f"{prefix}_{normalized}.xlsx"
        
        return os.path.join(output_dir, output_name)
        
    def _write_output(self, template_file: str, output_file: str, 
                     data: Dict[str, pd.DataFrame]) -> bool:
        """Write output file with activities data"""
        try:
            # Get activities data
            activities_df = data.get('activities')
            if activities_df is None or activities_df.empty:
                self._add_error('no_data', error="Žádná data k zápisu")
                return False
                
            # Check platform for xlwings
            if platform.system() != 'Windows' or not XLWINGS_AVAILABLE:
                self.logger.warning("[INVVZD] xlwings not available, using basic copy")
                # Basic implementation - just save the data
                activities_df.to_excel(output_file, index=False)
                return True
                
            # Use xlwings for formatting preservation
            # For InvVzd, we need to write to specific sheet/location
            return self._copy_with_xlwings_invvzd(
                template_file, 
                output_file, 
                activities_df
            )
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Write error: {str(e)}")
            self._add_error('write_error', error=str(e))
            return False
            
    def _copy_with_xlwings_invvzd(self, template_file: str, output_file: str,
                                 activities_df: pd.DataFrame) -> bool:
        """Special xlwings copy for InvVzd format - writes to 3 sheets"""
        try:
            import xlwings as xw
            import shutil
            
            # Copy template first
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            shutil.copy2(template_file, output_file)
            
            self.logger.info(f"[INVVZD] Opening Excel application...")
            # Open with xlwings - visible=True like original
            app = xw.App(visible=True)
            try:
                self.logger.info(f"[INVVZD] Loading template workbook...")
                wb = app.books.open(output_file)
                
                # Get source file path from activities data metadata
                source_file = getattr(activities_df, '_source_file', None)
                if not source_file:
                    # Try to get from processing context
                    source_file = getattr(self, '_current_source_file', None)
                
                # STEP 1: Write student names to "Seznam účastníků" sheet at B4
                self.logger.info(f"[INVVZD] STEP 1: Writing student names...")
                if 'Seznam účastníků' in [s.name for s in wb.sheets]:
                    sheet = wb.sheets['Seznam účastníků']
                    
                    # Extract student names from source file
                    student_names = self._extract_student_names(source_file) if source_file else []
                    self.logger.info(f"[INVVZD] Extracted {len(student_names)} student names")
                    
                    # Write student names exactly like original
                    if len(student_names) > 0:
                        sheet.range("B4").options(ndim="expand", transpose=True).value = student_names
                
                # STEP 2: Write activities to "Seznam aktivit" sheet at C3
                self.logger.info(f"[INVVZD] STEP 2: Writing activities...")
                if 'Seznam aktivit' in [s.name for s in wb.sheets]:
                    sheet = wb.sheets['Seznam aktivit']
                    
                    # Prepare activities data for export
                    if not activities_df.empty:
                        # For 16h version include time column, for 32h version exclude it
                        if self.version == "16":
                            export_columns = ["datum", "cas", "hodin", "forma", "tema", "ucitel"]
                        else:
                            export_columns = ["datum", "hodin", "forma", "tema", "ucitel"]
                        
                        # Select only needed columns in correct order
                        if all(col in activities_df.columns for col in export_columns):
                            activities_data = activities_df[export_columns]
                        else:
                            activities_data = activities_df
                            
                        self.add_info(f"Zapisuji {len(activities_data)} aktivit do Seznam aktivit")
                        sheet.range("C3").options(ndim="expand").value = activities_data.values
                
                # STEP 3: Write overview to "Přehled" sheet at C3
                self.logger.info(f"[INVVZD] STEP 3: Writing overview...")
                if 'Přehled' in [s.name for s in wb.sheets]:
                    sheet = wb.sheets['Přehled']
                    
                    # Create overview data (student-activity combinations)
                    overview_data = self._create_overview(student_names, activities_df)
                    if len(overview_data) > 0:
                        self.add_info(f"Zapisuji {len(overview_data)} záznamů do Přehled")
                        sheet.range("C3").options(ndim="expand").value = overview_data
                else:
                    self.logger.warning(f"[INVVZD] Sheet 'Přehled' not found in template")
                
                # STEP 4: Control check - verify SDP sums match activities total
                self.logger.info(f"[INVVZD] STEP 4: Verifying SDP sums...")
                self._verify_sdp_sums(wb)
                
                # Save and close
                self.logger.info(f"[INVVZD] Saving output file: {output_file}")
                wb.save()
                self.logger.info(f"[INVVZD] Closing workbook...")
                wb.close()
                self.logger.info(f"[INVVZD] === COPY TEMPLATE SUCCESS ===")
                return True
                
            finally:
                self.logger.info(f"[INVVZD] Quitting Excel application...")
                app.quit()
                
        except Exception as e:
            self.logger.error(f"[INVVZD] xlwings error: {str(e)}")
            self.logger.error(f"[INVVZD] Traceback: {traceback.format_exc()}")
            self._add_error('write_error', error=str(e))
            # Try to close Excel if still open
            try:
                if 'wb' in locals():
                    wb.close()
                if 'app' in locals():
                    app.quit()
            except:
                pass
            return False
            
    def _process_attendance_16h(self, df: pd.DataFrame, dates: List) -> Dict[str, pd.DataFrame]:
        """Process 16h attendance data - reads activities not participants"""
        config = self.config
        
        try:
            self.logger.info(f"[INVVZD] _process_attendance_16h: Starting with {len(dates)} dates")
            self.logger.info(f"[INVVZD] Config: data_start_col={config['data_start_col']}, hours_row={config['hours_row']}")
            
            # 16h format reads activities/dates, not participants
            # Structure: dates in row 6, data in columns
            activities = []
            
            # Process each date/activity column
            col = config['data_start_col']  # Start from column C (index 2)
            
            # Read activities while there are hours in columns
            for i in range(len(dates)):
                if i < len(dates):
                    # Read activity data from column
                    activity = self._extract_activity_16h(df, col + i, dates[i])
                    if activity:
                        activities.append(activity)
                        self.logger.info(f"[INVVZD] Added activity {i+1}: {activity['datum']}, {activity['hodin']}h")
                    
            # Create DataFrame from activities
            if activities:
                activities_df = pd.DataFrame(activities)
                self.hours_total = activities_df['hodin'].sum()
                self._add_info('file_complete', file=f"{len(activities)} aktivit, {self.hours_total} hodin")
                return {'activities': activities_df}
            else:
                self._add_error('no_activities', error="Nenalezena žádná data aktivit")
                return {}
                
        except Exception as e:
            self.logger.error(f"[INVVZD] Processing error: {str(e)}")
            self._add_error('processing_error', error=str(e))
            return {}
            
    def _process_attendance_32h(self, df: pd.DataFrame, dates: List) -> Dict[str, pd.DataFrame]:
        """Process 32h attendance data - reads activities not participants"""
        config = self.config
        
        try:
            # 32h format also reads activities/dates, not participants
            activities = []
            
            # Process each date/activity column
            col = config['data_start_col']  # Start from column C
            activity_num = 0
            
            while activity_num < len(dates):
                # Read activity data from column
                activity = self._extract_activity_32h(df, col, dates[activity_num])
                if activity:
                    activities.append(activity)
                    col += 1
                    activity_num += 1
                else:
                    break
                    
            # Create DataFrame from activities
            if activities:
                activities_df = pd.DataFrame(activities)
                self.hours_total = activities_df['hodin'].sum()
                self._add_info('file_complete', file=f"{len(activities)} aktivit, {self.hours_total} hodin")
                return {'activities': activities_df}
            else:
                self._add_error('no_activities', error="Nenalezena žádná data aktivit")
                return {}
                
        except Exception as e:
            self.logger.error(f"[INVVZD] Processing error: {str(e)}")
            self._add_error('processing_error', error=str(e))
            return {}
            
    def _find_data_end_row(self, df: pd.DataFrame, start_row: int) -> int:
        """Find the last row with participant data"""
        for i in range(start_row, len(df)):
            # Check if name column is empty
            if pd.isna(df.iloc[i, 1]) or str(df.iloc[i, 1]).strip() == '':
                return i
        return len(df)
        
    def _extract_activity_16h(self, df: pd.DataFrame, col_idx: int, 
                            date_value: Any) -> Optional[Dict[str, Any]]:
        """Extract activity data for 16h version from a column"""
        config = self.config
        
        try:
            self.logger.info(f"[INVVZD] _extract_activity_16h: col_idx={col_idx}, date_value={date_value}")
            # 16h structure (0-based indices):
            # Row 5: dates (Excel row 6)
            # Row 6: times (Excel row 7 - čas zahájení)
            # Row 7: forms (Excel row 8 - forma výuky)
            # Row 8: topics (Excel row 9 - téma výuky)
            # Row 9: teachers (Excel row 10 - jméno pedagoga)
            # Row 10: hours (Excel row 11 - počet hodin)
            
            # Get hours first to check if column has data
            hours_val = df.iloc[config['hours_row'], col_idx]
            if pd.isna(hours_val) or str(hours_val).strip() == '':
                return None
                
            try:
                hours = int(float(str(hours_val)))
                if hours <= 0:
                    return None
            except:
                return None
                
            # Format date
            if hasattr(date_value, 'strftime'):
                datum = date_value.strftime('%d.%m.%Y')
            else:
                datum = str(date_value).strip()
                
            # Get other fields using correct indices from config
            time_val = df.iloc[config.get('time_row', 6), col_idx]
            cas = str(time_val) if not pd.isna(time_val) else ''
            
            forma_val = df.iloc[config.get('form_row', 7), col_idx]
            forma = str(forma_val) if not pd.isna(forma_val) else 'Neurčeno'
            
            tema_val = df.iloc[config.get('topic_row', 8), col_idx]
            tema = str(tema_val) if not pd.isna(tema_val) else 'Neurčeno'
            
            ucitel_val = df.iloc[config.get('teacher_row', 9), col_idx]
            ucitel = str(ucitel_val) if not pd.isna(ucitel_val) else 'Neurčeno'
            
            return {
                'datum': datum,
                'cas': cas,
                'hodin': hours,
                'forma': forma,
                'tema': tema,
                'ucitel': ucitel
            }
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Activity extraction error: {str(e)}")
            return None
            
    def _extract_activity_32h(self, df: pd.DataFrame, col_idx: int, 
                            date_value: Any) -> Optional[Dict[str, Any]]:
        """Extract activity data for 32h version from a column"""
        # 32h has similar structure but different row indices
        # Reuse 16h logic with adjusted config
        return self._extract_activity_16h(df, col_idx, date_value)
        
    def clear_file_messages(self):
        """Clear messages but keep version info"""
        # Keep only version detection message
        version_msg = None
        for msg in self.info_messages:
            if "Detekována verze" in msg:
                version_msg = msg
                break
                
        self.errors = []
        self.warnings = []
        self.info_messages = [version_msg] if version_msg else []
        
    def _fix_incomplete_dates(self, dates: List, start_row: int = 6) -> List:
        """Fix incomplete dates by inferring missing years"""
        fixed_dates = []
        
        for i, date_val in enumerate(dates):
            if hasattr(date_val, 'year'):
                # Already a datetime object
                fixed_dates.append(date_val)
            else:
                # Try to parse using DateParser
                parsed = self.date_parser.parse_date(date_val)
                if parsed:
                    fixed_dates.append(parsed)
                else:
                    # Try to infer year if missing
                    date_str = str(date_val).strip()
                    parts = date_str.split('.')
                    
                    if len(parts) == 2:  # DD.MM format
                        # Infer year from context
                        year = self._infer_year_from_context(i, dates)
                        fixed_date_str = f"{parts[0]}.{parts[1]}.{year}"
                        parsed = self.date_parser.parse_date(fixed_date_str)
                        if parsed:
                            fixed_dates.append(parsed)
                            col_letter = chr(ord('A') + self.config['data_start_col'] + i)
                            self._add_info('date_fixed', cell=f"{col_letter}{start_row + 1}", 
                                         original=date_str, fixed=fixed_date_str)
                        else:
                            fixed_dates.append(None)
                    else:
                        fixed_dates.append(None)
                        
        return fixed_dates
        
    def _infer_year_from_context(self, index: int, dates: List) -> int:
        """Infer missing year from surrounding dates"""
        current_year = datetime.now().year
        
        # Look at surrounding dates that have years
        for i in range(max(0, index - 3), min(len(dates), index + 3)):
            if i == index:
                continue
                
            date_val = dates[i]
            if hasattr(date_val, 'year'):
                return date_val.year
            else:
                # Try to extract year from string
                date_str = str(date_val)
                parts = date_str.split('.')
                if len(parts) >= 3 and parts[2].strip():
                    try:
                        year = int(parts[2].strip())
                        if 2020 <= year <= 2030:  # Reasonable range
                            return year
                    except:
                        pass
                        
        # Default to current year
        return current_year
        
    def _extract_student_names(self, source_file: str) -> List[str]:
        """Extract student names from source file column B"""
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(source_file, read_only=True)
            sheet_name = "zdroj-dochazka" if "zdroj-dochazka" in wb.sheetnames else wb.sheetnames[0]
            sheet = wb[sheet_name]
            
            student_names = []
            empty_count = 0
            
            # Start from row 11 for 16h version, row 10 for 32h version (0-indexed)
            start_row = 11 if self.version == "16" else 10  # 0-indexed
            for row in range(start_row, sheet.max_row):
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
            self.logger.error(f"[INVVZD] Error extracting student names: {str(e)}")
            self._add_error('read_error', error=f"Chyba při načítání jmen žáků: {str(e)}")
            return []
            
    def _create_overview(self, student_names: List[str], activities_df: pd.DataFrame) -> List[List]:
        """Create overview data combining students with activity numbers"""
        try:
            # Following original logic from create_orginal_file
            overview_result = []
            
            # For each activity (numbered 1, 2, 3...)
            for activity_num, (_, activity) in enumerate(activities_df.iterrows(), 1):
                # Add all students for this activity
                for student_name in student_names:
                    overview_result.append([activity_num, student_name])
            
            self.add_info(f"Vytvořen přehled: {len(activities_df)} aktivit × {len(student_names)} žáků = {len(overview_result)} záznamů")
            return overview_result
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Error creating overview: {str(e)}")
            self._add_error('processing_error', error=f"Chyba při vytváření přehledu: {str(e)}")
            return []
            
    def _verify_sdp_sums(self, wb):
        """Verify SDP sums match total hours - following original control logic"""
        try:
            # Calculate activities total (Seznam aktivit column depends on version)
            aktivit_sheet = wb.sheets['Seznam aktivit']
            activities_total = 0
            row = 3
            
            # For 16h version, hours are in column E (includes time column)
            # For 32h version, hours are in column D  
            hours_column = "E" if self.version == "16" else "D"
            
            while True:
                cell_value = aktivit_sheet.range(f"{hours_column}{row}").value
                if cell_value is None or str(cell_value).strip() == '':
                    break
                try:
                    activities_total += int(float(str(cell_value)))
                except:
                    pass
                row += 1
            
            # Check SDP sheet sums
            sdp_sheet = wb.sheets['SDP']
            
            # Sum C4:C10 (forma range)
            sdp_forma_total = 0
            for row in range(4, 11):  # C4 to C10
                cell_value = sdp_sheet.range(f"C{row}").value
                if cell_value is not None:
                    try:
                        sdp_forma_total += int(float(str(cell_value)))
                    except:
                        pass
            
            # Sum C12:C28 (tema range) 
            sdp_tema_total = 0
            for row in range(12, 29):  # C12 to C28
                cell_value = sdp_sheet.range(f"C{row}").value
                if cell_value is not None:
                    try:
                        sdp_tema_total += int(float(str(cell_value)))
                    except:
                        pass
            
            # Compare and report with detailed logging
            self.logger.info(f"[INVVZD] === SDP VERIFICATION ===")
            self.logger.info(f"[INVVZD] Activities total: {activities_total} hours")
            self.logger.info(f"[INVVZD] SDP forma total (C4-C10): {sdp_forma_total} hours")
            self.logger.info(f"[INVVZD] SDP tema total (C12-C28): {sdp_tema_total} hours")
            
            self.add_info(f"Kontrola součtů:")
            self.add_info(f"  Aktivity: {activities_total}h")
            self.add_info(f"  SDP forma: {sdp_forma_total}h")
            self.add_info(f"  SDP téma: {sdp_tema_total}h")
            
            if activities_total == sdp_forma_total == sdp_tema_total:
                self.logger.info(f"[INVVZD] All sums match!")
                self.add_info(f"✅ Všechny součty souhlasí")
            else:
                self.logger.error(f"[INVVZD] ❌ SUMS DO NOT MATCH!")
                self.logger.error(f"[INVVZD] Activities: {activities_total}, Forma: {sdp_forma_total}, Tema: {sdp_tema_total}")
                
                self._add_error('sum_mismatch', error=f"❌ NESOUHLASÍ součty v SDP!")
                self._add_error('sum_details', error=f"Aktivity: {activities_total}h, SDP forma: {sdp_forma_total}h, SDP téma: {sdp_tema_total}h")
                self.add_warning("ZKONTROLUJTE výsledný soubor - aktivity na listu 'Seznam aktivit'")
                
        except Exception as e:
            self.logger.error(f"[INVVZD] Error verifying SDP sums: {str(e)}")
            self._add_error('verification_error', error=f"Chyba při kontrole SDP součtů: {str(e)}")
            
    def select_folder(self, folder_path: str) -> Dict[str, Any]:
        """Scan folder for attendance files and filter them"""
        self.logger.info(f"[INVVZD] === SELECT FOLDER START ===")
        self.logger.info(f"[INVVZD] Folder path: {folder_path}")
        
        result = {"success": False, "files": [], "message": ""}
        
        try:
            # Check if folder exists
            if not os.path.exists(folder_path):
                self.logger.error(f"[INVVZD] Folder does not exist: {folder_path}")
                result["message"] = f"Složka neexistuje: {folder_path}"
                return result
                
            # List all files in folder
            all_files = os.listdir(folder_path)
            self.logger.info(f"[INVVZD] All files in folder: {all_files}")
            
            attendance_files = []
            
            # Scan for Excel files
            for file in all_files:
                if file.endswith(('.xlsx', '.xls')) and not file.startswith('~$'):
                    full_path = os.path.join(folder_path, file)
                    self.logger.info(f"[INVVZD] Checking Excel file: {file}")
                    
                    # Skip output files (already processed)
                    if file.startswith(('32h_inv_', '16h_inv_', '32_hodin_inovativniho_vzdelavani_', '16_hodin_inovativniho_vzdelavani_')):
                        self.logger.info(f"[INVVZD] Skipping output file: {file}")
                        continue
                    
                    # Skip template files
                    if 'sablona' in file.lower() or 'template' in file.lower():
                        self.logger.info(f"[INVVZD] Skipping template file: {file}")
                        continue
                    
                    # Try to detect version from content
                    self.logger.info(f"[INVVZD] Detecting version for: {full_path}")
                    version = self._detect_source_version(full_path)
                    self.logger.info(f"[INVVZD] Detected version: {version}")
                    
                    if version:
                        self.logger.info(f"[INVVZD] Valid attendance file found: {file} (version {version}h)")
                        attendance_files.append({
                            "path": full_path,
                            "name": file,
                            "version": f"{version} hodin"
                        })
                    else:
                        self.logger.info(f"[INVVZD] Not an attendance file: {file}")
                        
            self.logger.info(f"[INVVZD] Total attendance files found: {len(attendance_files)}")
            
            if attendance_files:
                result["success"] = True
                result["files"] = attendance_files
                result["message"] = f"Nalezeno {len(attendance_files)} souborů s docházkou"
                self.logger.info(f"[INVVZD] SUCCESS: {result['message']}")
            else:
                result["message"] = "Ve složce nebyly nalezeny žádné soubory s docházkou"
                self.logger.warning(f"[INVVZD] WARNING: {result['message']}")
                
        except Exception as e:
            result["message"] = f"Chyba při procházení složky: {str(e)}"
            self.logger.error(f"[INVVZD] ERROR: {result['message']}")
            import traceback
            self.logger.error(f"[INVVZD] Traceback: {traceback.format_exc()}")
            
        self.logger.info(f"[INVVZD] === SELECT FOLDER END ===")
        self.logger.info(f"[INVVZD] Result: {result}")
        return result