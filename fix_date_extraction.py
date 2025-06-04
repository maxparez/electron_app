#!/usr/bin/env python3
"""
Test date extraction in refactored processor
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor
from tools.inv_vzd_constants import VERSIONS
import pandas as pd

# Test file
test_file = "tests/regression/inputs/16h/valid_basic.xlsx"

# Create processor
processor = InvVzdProcessor()
processor.version = "16"
processor.config = VERSIONS["16"]

# Read DataFrame
df = pd.read_excel(test_file, sheet_name='zdroj-dochazka')
print(f"DataFrame shape: {df.shape}")

# Test date extraction
print("\nTesting _extract_dates_16h:")
dates = processor._extract_dates_16h(df)
print(f"Extracted dates: {dates}")

# Check what's in the dates row
dates_row = processor.config['dates_row']
print(f"\nDates row config: {dates_row}")
print(f"Data in row {dates_row}:")
print(df.iloc[dates_row, :10])

# Check manually
print(f"\nManual check - row {dates_row}, columns 2-5:")
for col in range(2, 6):
    val = df.iloc[dates_row, col]
    print(f"  Column {col}: {val} (type: {type(val)})")