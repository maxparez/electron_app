#!/usr/bin/env python3
"""
Debug date formats in Excel files
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

import pandas as pd
from openpyxl import load_workbook
from datetime import datetime

def debug_dates_in_file(filepath):
    """Debug date formats in Excel file"""
    print(f"=== Debugging dates in {os.path.basename(filepath)} ===")
    
    try:
        # Read with pandas
        df = pd.read_excel(filepath, sheet_name="Seznam aktivit", header=0)
        
        print("Raw data from pandas:")
        date_column = df.iloc[:, 2]  # Column C (index 2) should be dates
        
        for i, value in enumerate(date_column.head(10)):
            print(f"  Row {i}: {value} (type: {type(value)})")
            
        print("\nChecking with openpyxl:")
        wb = load_workbook(filepath)
        sheet = wb["Seznam aktivit"]
        
        # Check first 10 rows in column C (dates)
        for row in range(1, 11):
            cell = sheet[f"C{row}"]
            print(f"  C{row}: {cell.value} (type: {type(cell.value)}, number_format: {cell.number_format})")
            
        wb.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    file_path = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx"
    debug_dates_in_file(file_path)