#!/usr/bin/env python3
"""
Test InvVzd processor with missing date file
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor
from logger import init_logging
import json

def test_missing_dates():
    """Test processing file with missing dates"""
    
    # Initialize logging
    _, tool_logger = init_logging()
    
    # Create processor
    processor = InvVzdProcessor(logger=tool_logger)
    
    # Test file with missing date
    test_files = [
        "/root/vyvoj_sw/electron_app/test_32h_missing_dates.xlsx"
    ]
    
    # Options
    options = {
        "template": "/root/vyvoj_sw/electron_app/template_32_hodin.xlsx",
        "courseType": "32",
        "keep_filename": True,
        "optimize": False
    }
    
    print("Testing InvVzd processor with file that has missing date in D6...\n")
    
    # Process
    result = processor.process(test_files, options)
    
    # Print result with pretty formatting
    print("Full Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")
    
    # Summary
    print("SUMMARY:")
    print(f"Success: {result['success']}")
    print(f"Errors: {len(result.get('errors', []))}")
    print(f"Warnings: {len(result.get('warnings', []))}")
    print(f"Info: {len(result.get('info', []))}")
    
    if result.get('errors'):
        print("\nERRORS:")
        for error in result['errors']:
            print(f"  ❌ {error}")
            
    if result.get('warnings'):
        print("\nWARNINGS:")
        for warning in result['warnings']:
            print(f"  ⚠️ {warning}")
            
    if result.get('info'):
        print("\nINFO:")
        for info in result['info']:
            print(f"  ℹ️ {info}")
            
    # Check data field
    if result.get('data'):
        print(f"\nDATA FIELD PRESENT: Yes")
        print(f"  - processed_files: {len(result['data'].get('processed_files', []))}")
    else:
        print(f"\nDATA FIELD PRESENT: No")
        
    print("\n" + "="*60 + "\n")
    
    # Simulate what UI would see
    print("UI WOULD SEE:")
    if result.get('status') in ['success', 'partial'] or (result.get('data') and result.get('info')):
        print("✓ Detailed report with errors would be displayed")
    else:
        print("✗ Generic error message would be shown")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_missing_dates())