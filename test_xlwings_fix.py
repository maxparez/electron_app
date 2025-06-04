#!/usr/bin/env python3
"""Test script to verify xlwings fix in refactored InvVzdProcessor"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_16h_processing():
    """Test 16h version processing"""
    print("\n=== Testing 16h Version ===")
    
    # Setup paths
    source_file = "tests/test1/dochazka_16h_test.xlsx"
    template = "template_16_hodin.xlsx"
    output_dir = "tests/output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create processor
    processor = InvVzdProcessor(logger=logger)
    
    # Process files
    result = processor.process(
        files=[source_file],
        options={
            'template': template,
            'output_dir': output_dir
        }
    )
    
    # Check result
    print(f"Success: {result['success']}")
    if result.get('data'):
        for file_result in result['data']['processed_files']:
            print(f"File: {file_result['source']}")
            print(f"Output: {file_result['output']}")
            print(f"Hours: {file_result['hours']}")
            print(f"Status: {file_result['status']}")
            
            if file_result['errors']:
                print(f"Errors: {file_result['errors']}")
            if file_result['warnings']:
                print(f"Warnings: {file_result['warnings']}")
            if file_result['info']:
                print(f"Info: {file_result['info']}")
    
    return result['success']

def test_32h_processing():
    """Test 32h version processing"""
    print("\n=== Testing 32h Version ===")
    
    # Setup paths - use files from regression test
    source_file = "tests/regression/inputs/32h/valid_basic.xlsx"
    template = "template_32_hodin.xlsx"
    output_dir = "tests/output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create processor
    processor = InvVzdProcessor(logger=logger)
    
    # Process files
    result = processor.process(
        files=[source_file],
        options={
            'template': template,
            'output_dir': output_dir
        }
    )
    
    # Check result
    print(f"Success: {result['success']}")
    if result.get('data'):
        for file_result in result['data']['processed_files']:
            print(f"File: {file_result['source']}")
            print(f"Output: {file_result['output']}")
            print(f"Hours: {file_result['hours']}")
            print(f"Status: {file_result['status']}")
            
            if file_result['errors']:
                print(f"Errors: {file_result['errors']}")
            if file_result['warnings']:
                print(f"Warnings: {file_result['warnings']}")
            if file_result['info']:
                print(f"Info: {file_result['info']}")
    
    return result['success']

def check_output_sheets(output_file):
    """Check if output file has all required sheets with data"""
    try:
        import xlwings as xw
        app = xw.App(visible=False)
        try:
            wb = app.books.open(output_file)
            
            # Check Seznam účastníků
            if 'Seznam účastníků' in [s.name for s in wb.sheets]:
                sheet = wb.sheets['Seznam účastníků']
                student_count = 0
                row = 4
                while True:
                    value = sheet.range(f"B{row}").value
                    if value is None or str(value).strip() == '':
                        break
                    student_count += 1
                    row += 1
                print(f"  Seznam účastníků: {student_count} students")
            else:
                print("  Seznam účastníků: NOT FOUND")
            
            # Check Seznam aktivit
            if 'Seznam aktivit' in [s.name for s in wb.sheets]:
                sheet = wb.sheets['Seznam aktivit']
                activity_count = 0
                row = 3
                while True:
                    value = sheet.range(f"C{row}").value
                    if value is None or str(value).strip() == '':
                        break
                    activity_count += 1
                    row += 1
                print(f"  Seznam aktivit: {activity_count} activities")
            else:
                print("  Seznam aktivit: NOT FOUND")
            
            # Check Přehled
            if 'Přehled' in [s.name for s in wb.sheets]:
                sheet = wb.sheets['Přehled']
                overview_count = 0
                row = 3
                while True:
                    value = sheet.range(f"C{row}").value
                    if value is None or str(value).strip() == '':
                        break
                    overview_count += 1
                    row += 1
                print(f"  Přehled: {overview_count} records")
            else:
                print("  Přehled: NOT FOUND")
                
            wb.close()
        finally:
            app.quit()
            
    except ImportError:
        print("  xlwings not available - cannot check sheets")
    except Exception as e:
        print(f"  Error checking output: {e}")

if __name__ == "__main__":
    # Check platform
    import platform
    print(f"Platform: {platform.system()}")
    
    # Test both versions
    success_16h = test_16h_processing()
    success_32h = test_32h_processing()
    
    # Check output files
    print("\n=== Checking Output Files ===")
    output_dir = "tests/output"
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith('.xlsx'):
                print(f"\nFile: {file}")
                check_output_sheets(os.path.join(output_dir, file))
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"16h processing: {'✓ PASSED' if success_16h else '✗ FAILED'}")
    print(f"32h processing: {'✓ PASSED' if success_32h else '✗ FAILED'}")
    
    sys.exit(0 if success_16h and success_32h else 1)