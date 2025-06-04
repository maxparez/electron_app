#!/usr/bin/env python3
"""Test processing with refactored processor"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_processing():
    print("=== Testing file processing with refactored processor ===")
    
    processor = InvVzdProcessor()
    
    # Test files
    test_file = "tests/test1/dochazka_16h_test.xlsx"
    template_16h = "template_16_hodin.xlsx"
    
    # Process file
    print("\nProcessing 16h file...")
    result = processor.process(
        [test_file],
        {
            'template': template_16h,
            'output_dir': 'tests/output'
        }
    )
    
    print(f"\nResult structure:")
    print(f"  status: {result.get('status')}")
    print(f"  has results: {'results' in result}")
    print(f"  number of results: {len(result.get('results', []))}")
    
    if 'results' in result and result['results']:
        for i, file_result in enumerate(result['results']):
            print(f"\n  File {i+1}:")
            print(f"    source: {os.path.basename(file_result.get('source', 'N/A'))}")
            print(f"    output: {os.path.basename(file_result.get('output', 'N/A')) if file_result.get('output') else 'None'}")
            print(f"    status: {file_result.get('status')}")
            print(f"    hours: {file_result.get('hours', 0)}")
            print(f"    errors: {len(file_result.get('errors', []))}")
            
    print(f"\nGlobal messages:")
    print(f"  info: {len(result.get('info', []))}")
    print(f"  warnings: {len(result.get('warnings', []))}")
    print(f"  errors: {len(result.get('errors', []))}")

if __name__ == "__main__":
    test_processing()