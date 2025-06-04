#!/usr/bin/env python3
"""Test select_folder method in refactored processor"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_select_folder():
    processor = InvVzdProcessor()
    
    # Test with test folder
    test_folder = "tests/test1"
    print(f"Testing select_folder with: {test_folder}")
    
    result = processor.select_folder(test_folder)
    print(f"\nResult: {result}")
    
    if result["success"]:
        print(f"\nFound {len(result['files'])} files:")
        for file in result["files"]:
            print(f"  - {file['name']} ({file['version']})")
    else:
        print(f"\nError: {result['message']}")

if __name__ == "__main__":
    test_select_folder()