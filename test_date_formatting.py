#!/usr/bin/env python3
"""
Test date formatting in processed data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_date_formatting():
    """Test that dates are properly formatted in processed data"""
    print("=== Testing Date Formatting ===")
    
    # Test 16-hour file processing
    file_path = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx"
    
    if os.path.exists(file_path):
        processor = InvVzdProcessor("16")
        
        print(f"Processing: {os.path.basename(file_path)}")
        data = processor._read_source_data(file_path)
        
        if data is not None:
            print(f"\nProcessed data shape: {data.shape}")
            print(f"Columns: {list(data.columns)}")
            
            print("\nFirst 5 rows of date data:")
            for i, row in data.head().iterrows():
                print(f"  Row {i}: Datum={row['datum']}, Hodiny={row['hodin']}, Téma={row['tema']}")
                
            print(f"\nDate format validation:")
            for i, date_str in enumerate(data['datum'].head()):
                # Check if date is in DD.MM.YYYY format
                try:
                    parts = date_str.split('.')
                    if len(parts) == 3 and len(parts[2]) == 4:
                        print(f"  ✅ Row {i}: {date_str} (valid DD.MM.YYYY format)")
                    else:
                        print(f"  ❌ Row {i}: {date_str} (invalid format)")
                except:
                    print(f"  ❌ Row {i}: {date_str} (parse error)")
                    
        else:
            print("Failed to process data")
            for error in processor.errors:
                print(f"  Error: {error}")
    else:
        print(f"File not found: {file_path}")

def test_32_hour_dates():
    """Test 32-hour file date formatting"""
    print("\n=== Testing 32-Hour Date Formatting ===")
    
    file_path = "/root/vyvoj_sw/electron_app/legacy_code/inv/source.xlsx"
    
    if os.path.exists(file_path):
        processor = InvVzdProcessor("32")
        
        print(f"Processing: {os.path.basename(file_path)}")
        data = processor._read_source_data(file_path)
        
        if data is not None:
            print(f"\nProcessed data shape: {data.shape}")
            
            print("\nFirst 5 rows of generated date data:")
            for i, row in data.head().iterrows():
                print(f"  Row {i}: Datum={row['datum']}, Hodiny={row['hodin']}, Téma={row['tema']}")
                
        else:
            print("Failed to process 32-hour data")
            for error in processor.errors:
                print(f"  Error: {error}")
    else:
        print(f"File not found: {file_path}")

if __name__ == "__main__":
    test_date_formatting()
    test_32_hour_dates()