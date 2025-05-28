#!/usr/bin/env python3
"""Test script to read attendance data and display DataFrame structure"""

import sys
import os
import pandas as pd

# Add project path to sys.path
sys.path.insert(0, '/root/vyvoj_sw/electron_app/src/python')

from tools.inv_vzd_processor import InvVzdProcessor

def test_read_attendance():
    """Test reading attendance data from the specified file"""
    
    # Initialize processor for 32h version
    processor = InvVzdProcessor(version="32")
    
    # Source file path
    source_file = "/mnt/d/TEMP/bobrovniky/inv_vzd/Lettovska.xlsx"
    
    print(f"Testing file: {source_file}")
    print("-" * 80)
    
    # Check if file exists
    if not os.path.exists(source_file):
        print(f"ERROR: File not found: {source_file}")
        return
        
    # Detect source version
    detected_version = processor._detect_source_version(source_file)
    print(f"Detected source version: {detected_version}h")
    print("-" * 80)
    
    # Read source data
    df = processor._read_source_data(source_file)
    
    if df is None:
        print("ERROR: Failed to read data")
        print("Errors:", processor.errors)
        return
        
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Total hours: {processor.hours_total}")
    
    print("\nDataFrame columns:")
    print(df.columns.tolist())
    
    print("\nDataFrame info:")
    print(df.info())
    
    print("\nFirst 10 rows of data:")
    print(df.head(10).to_string())
    
    print("\nData that would be exported to 'Seznam aktivit':")
    # For 32h version, export_columns should be ["datum","hodin","forma","tema","ucitel"]
    export_columns = ["datum", "hodin", "forma", "tema", "ucitel"]
    
    if all(col in df.columns for col in export_columns):
        export_df = df[export_columns]
        print(f"\nExport DataFrame shape: {export_df.shape}")
        print("\nExport data:")
        print(export_df.to_string())
    else:
        print(f"WARNING: Not all export columns found. Available: {df.columns.tolist()}")
        print("Full DataFrame:")
        print(df.to_string())
    
    print("\nProcessor messages:")
    print("Info:", processor.info_messages)
    print("Warnings:", processor.warnings)
    print("Errors:", processor.errors)

if __name__ == "__main__":
    test_read_attendance()