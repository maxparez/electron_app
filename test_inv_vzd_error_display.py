#!/usr/bin/env python3
"""
Test InvVzd processor to show how errors are handled
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
    
    # Test files
    test_files = [
        "/root/vyvoj_sw/electron_app/tests/test1/32_hodin_inovativniho_vzdelavani_MS_ZS_SDP.xlsx"
    ]
    
    # Options
    options = {
        "template": "/root/vyvoj_sw/electron_app/template_32_hodin.xlsx",
        "courseType": "32",
        "keep_filename": True,
        "optimize": False
    }
    
    print("Testing InvVzd processor with file that has missing dates...\n")
    
    # Process
    result = processor.process(test_files, options)
    
    # Print result
    print("Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60 + "\n")
    
    # Analyze result
    print("Analysis:")
    print(f"- Success: {result['success']}")
    print(f"- Errors: {len(result.get('errors', []))}")
    print(f"- Warnings: {len(result.get('warnings', []))}")
    print(f"- Info messages: {len(result.get('info', []))}")
    
    if result.get('errors'):
        print("\nErrors found:")
        for error in result['errors']:
            print(f"  • {error}")
            
    if result.get('info'):
        print("\nInfo messages:")
        for info in result['info']:
            print(f"  • {info}")
            
    # Check if data is present
    if result.get('data'):
        print(f"\nData present: {list(result['data'].keys())}")
        if 'processed_files' in result['data']:
            print(f"Files processed: {len(result['data']['processed_files'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_missing_dates())