#!/usr/bin/env python3
"""Test folder selection with template validation"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_folder_validation():
    processor = InvVzdProcessor()
    
    # Test without template (should find all files)
    print("=== Test 1: Without template ===")
    processor.version = None
    result = processor.select_folder("tests/test1")
    print(f"Result: {result['message']}")
    print(f"Files found: {len(result.get('files', []))}")
    
    # Test with 16h template (should filter only 16h files)
    print("\n=== Test 2: With 16h template ===")
    processor.version = "16"
    processor.config = {"hours": 16}
    result = processor.select_folder("tests/test1")
    print(f"Result: {result['message']}")
    print(f"Files found: {len(result.get('files', []))}")
    for file in result.get('files', []):
        print(f"  - {file['name']} ({file['version']})")
    
    # Test with 32h template (should filter only 32h files)
    print("\n=== Test 3: With 32h template ===")
    processor.version = "32"
    processor.config = {"hours": 32}
    result = processor.select_folder("tests/test1")
    print(f"Result: {result['message']}")
    print(f"Files found: {len(result.get('files', []))}")
    for file in result.get('files', []):
        print(f"  - {file['name']} ({file['version']})")
    
    # Test with regression test folder
    print("\n=== Test 4: Regression folder with mixed versions ===")
    processor.version = "16"
    processor.config = {"hours": 16}
    result = processor.select_folder("tests/regression/inputs/16h")
    print(f"Result: {result['message']}")
    print(f"Files found: {len(result.get('files', []))}")
    for file in result.get('files', []):
        print(f"  - {file['name']} ({file['version']})")

if __name__ == "__main__":
    test_folder_validation()