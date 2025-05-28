import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import os
import warnings
from typing import Dict, Any, List, Optional, Tuple
import xlwings as xw
from datetime import datetime

from .base_tool import BaseTool

warnings.filterwarnings('ignore')

# Version-specific constants
VERSIONS = {
    "32": {
        "hours": 32,
        "template": {
            "B1": "32 hodin"
        },
        "output_prefix": "32_hodin_inovativniho_vzdelavani",
        "short_prefix": "32_inv",
        "sheet": "List1",
        "cells": {
            "B6": "datum aktivity",
        },
        "skiprows": 9,
        "hours_cell": "C10",
        "hours_total_cell": "A10",
        "version_identifier": "I",
        "column_head_names": ["to_drop", "datum", "forma", "tema", "ucitel", "hodin"],
        "export_columns": ["datum", "hodin", "forma", "tema", "ucitel"]
    },
    "16": {
        "hours": 16,
        "template": {
            "B1": "16 hodin"
        },
        "output_prefix": "16_hodin_inovativniho_vzdelavani",
        "short_prefix": "16_inv",
        "sheet": "zdroj-dochazka",
        "cells": {
            "B6": "datum aktivity",
            "B7": "čas zahájení"
        },
        "skiprows": 10,
        "hours_cell": "C11",
        "hours_total_cell": "A11",
        "version_identifier": "II",
        "column_head_names": ["to_drop", "datum", "cas", "forma", "tema", "ucitel", "hodin"],
        "export_columns": ["datum", "cas", "hodin", "forma", "tema", "ucitel"]
    }
}


class InvVzdProcessor(BaseTool):
    """Processor for innovative education attendance (16/32 hours)"""
    
    def __init__(self, logger=None):
        super().__init__(logger)
        self.hours_total = 0
        self.version = None
        self.config = None
        
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
            sheet = wb.worksheets[0]
            
            for version, config in VERSIONS.items():
                match = True
                for cell, expected_value in config["cells"].items():
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
                template_path, output_file, source_data
            )
            
            self.add_info(f"Vytvořen výstupní soubor: {os.path.basename(output_file)}")
            return output_file
            
        except Exception as e:
            self.add_error(f"Chyba při zpracování souboru {os.path.basename(source_file)}: {str(e)}")
            return None
            
    def _read_source_data(self, source_file: str) -> Optional[pd.DataFrame]:
        """Read and process source data"""
        try:
            # Read Excel file
            df = pd.read_excel(
                source_file,
                sheet_name=self.config["sheet"],
                skiprows=self.config["skiprows"],
                names=self.config["column_head_names"],
                usecols=range(len(self.config["column_head_names"]))
            )
            
            # Clean data
            df = df.dropna(axis='index', how='all')
            df = df[df['datum'].notna()]
            
            # Calculate total hours
            self.hours_total = df['hodin'].sum()
            self.add_info(f"Celkem hodin: {self.hours_total}")
            
            # Select export columns
            df = df[self.config["export_columns"]]
            
            return df
            
        except Exception as e:
            self.add_error(f"Chyba při čtení zdrojových dat: {str(e)}")
            return None
            
    def _optimize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data by removing duplicates"""
        original_count = len(df)
        df = df.drop_duplicates()
        removed_count = original_count - len(df)
        
        if removed_count > 0:
            self.add_info(f"Odstraněno {removed_count} duplicitních řádků")
            
        return df
        
    def _create_output_filename(self, source_file: str, output_dir: str, 
                               keep_filename: bool) -> str:
        """Create output filename"""
        if keep_filename:
            base_name = os.path.splitext(os.path.basename(source_file))[0]
            return os.path.join(output_dir, f"{base_name}_MSMT.xlsx")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = self.config["output_prefix"]
            return os.path.join(output_dir, f"{prefix}_MSMT_{timestamp}.xlsx")
            
    def _copy_template_with_data(self, template_path: str, output_path: str, 
                                data: pd.DataFrame):
        """Copy template file and fill with data using xlwings"""
        try:
            # Use xlwings to preserve all Excel features
            app = xw.App(visible=False)
            
            # Open template
            wb_template = app.books.open(template_path)
            
            # Save as new file
            wb_template.save(output_path)
            wb_template.close()
            
            # Open the new file
            wb = app.books.open(output_path)
            sheet = wb.sheets[0]
            
            # Write data starting from appropriate row
            start_row = self.config["skiprows"] + 2  # +2 for header row and 0-based index
            start_col = 2  # Column B
            
            # Write data
            if len(data) > 0:
                sheet.range((start_row, start_col)).value = data.values
                
            # Update total hours cell
            hours_cell = self.config["hours_total_cell"]
            sheet.range(hours_cell).value = f"Celkem {self.hours_total} hodin"
            
            # Save and close
            wb.save()
            wb.close()
            app.quit()
            
        except Exception as e:
            self.add_error(f"Chyba při kopírování šablony: {str(e)}")
            raise