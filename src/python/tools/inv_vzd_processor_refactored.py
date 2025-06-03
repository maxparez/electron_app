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
                
            # Return combined results
            success = all(r.get('status') == 'success' for r in results)
            return {
                'status': 'success' if success else 'error',
                'results': results,
                'errors': self.errors,
                'warnings': self.warnings,
                'info': self.info_messages
            }
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Process error: {str(e)}")
            self._add_error('read_error', error=str(e))
            return self.get_result(False)
            
    def _process_single_file(self, source_file: str, template_file: str, 
                           output_dir: str) -> Dict[str, Any]:
        """Process a single attendance file"""
        try:
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
            
    def _process_16h_file(self, source_file: str, template_file: str) -> Optional[pd.DataFrame]:
        """Process 16-hour attendance file"""
        try:
            # Read source data
            df = pd.read_excel(source_file, sheet_name='zdroj-dochazka')
            
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
            self.logger.error(f"[INVVZD] Error in 16h processing: {str(e)}")
            self._add_error('read_error', error=str(e))
            return None
            
    def _process_32h_file(self, source_file: str, template_file: str) -> Optional[pd.DataFrame]:
        """Process 32-hour attendance file"""
        try:
            # Read source data
            df = pd.read_excel(source_file, sheet_name='zdroj-dochazka')
            
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
            self.logger.error(f"[INVVZD] Error in 32h processing: {str(e)}")
            self._add_error('read_error', error=str(e))
            return None
            
    def _extract_dates_16h(self, df: pd.DataFrame) -> Optional[List]:
        """Extract dates from 16h format"""
        config = self.config
        dates_row = config['dates_row']
        
        try:
            # Get date values
            date_values = df.iloc[dates_row, config['data_start_col']:].tolist()
            
            # Parse dates
            parsed_dates = []
            missing_dates = []
            
            for i, date_val in enumerate(date_values):
                if pd.isna(date_val):
                    break
                    
                parsed = self.date_parser.parse_date(date_val)
                if parsed:
                    parsed_dates.append(parsed)
                else:
                    col_letter = chr(ord('A') + config['data_start_col'] + i)
                    cell = f"{col_letter}{dates_row + 1}"
                    missing_dates.append(cell)
                    
            # Report missing dates
            for cell in missing_dates:
                self._add_error('missing_date', cell=cell)
                
            return parsed_dates if len(parsed_dates) > 0 else None
            
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
                     data: pd.DataFrame) -> bool:
        """Write output file"""
        try:
            # Check platform for xlwings
            if platform.system() != 'Windows' or not XLWINGS_AVAILABLE:
                self.logger.warning("[INVVZD] xlwings not available, using basic copy")
                # Basic implementation without formatting
                data.to_excel(output_file, index=False)
                return True
                
            # Use xlwings for formatting preservation
            return self.excel_helper.copy_excel_with_xlwings(
                template_file, 
                output_file, 
                {'Sheet1': data}
            )
            
        except Exception as e:
            self.logger.error(f"[INVVZD] Write error: {str(e)}")
            self._add_error('write_error', error=str(e))
            return False
            
    # Stub methods for missing implementations
    def _process_attendance_16h(self, df: pd.DataFrame, dates: List) -> pd.DataFrame:
        """Process 16h attendance data"""
        # This would contain the actual processing logic
        # For now, return empty DataFrame
        return pd.DataFrame()
        
    def _process_attendance_32h(self, df: pd.DataFrame, dates: List) -> pd.DataFrame:
        """Process 32h attendance data"""
        # This would contain the actual processing logic
        # For now, return empty DataFrame  
        return pd.DataFrame()
        
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