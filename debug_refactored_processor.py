#!/usr/bin/env python3
"""
Debug refactored processor to see what's happening
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor
import pandas as pd

def debug_file_reading():
    """Debug what's happening when reading file"""
    
    # Test file
    test_file = "tests/regression/inputs/16h/valid_basic.xlsx"
    if not os.path.exists(test_file):
        test_file = "tests/test1/dochazka_16h_test.xlsx"
    
    print(f"Testing with file: {test_file}")
    
    # Check file structure manually
    print("\n1. Checking file structure with pandas:")
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(test_file)
        print(f"   Sheet names: {excel_file.sheet_names}")
        
        # Read first sheet
        df = pd.read_excel(test_file, sheet_name=0)
        print(f"   DataFrame shape: {df.shape}")
        print(f"   First 15 rows, columns 0-15:")
        print(df.iloc[:15, :15])
        print(f"\n   Row 5 (dates row) all columns:")
        print(df.iloc[4, :])
        
    except Exception as e:
        print(f"   Error reading file: {e}")
        
    # Now test with processor
    print("\n2. Testing with processor:")
    processor = InvVzdProcessor()
    
    # Detect version
    version = processor._detect_source_version(test_file)
    print(f"   Detected version: {version}")
    
    if version:
        from tools.inv_vzd_constants import VERSIONS
        processor.version = version
        processor.config = VERSIONS[version]
        
        # Try to read and process
        print("\n3. Trying to process file:")
        template = "template_16_hodin.xlsx"
        
        try:
            # Try the internal method directly
            result = processor._process_16h_file(test_file, template)
            print(f"   Process result: {result}")
            
            if result and 'activities' in result:
                print(f"   Activities found: {len(result['activities'])}")
                print(f"   Activities data:")
                print(result['activities'])
            else:
                print("   No activities found")
                print(f"   Errors: {processor.errors}")
                
        except Exception as e:
            print(f"   Processing error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_file_reading()