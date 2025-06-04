#!/usr/bin/env python3
"""Test folder selection with template filtering"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_folder_selection():
    print("=== Testing folder selection with template filtering ===")
    
    processor = InvVzdProcessor()
    
    # Test with no template - should find all files
    print("\n1. No template provided:")
    result = processor.select_folder("tests/test1")
    print(f"   Found {len(result.get('files', []))} files")
    print(f"   Message: {result.get('message', 'No message')}")
    
    # Test with 16h template 
    print("\n2. With 16h template:")
    template_16h = "template_16_hodin.xlsx"
    result = processor.select_folder("tests/test1", template_16h)
    print(f"   Found {len(result.get('files', []))} files")
    print(f"   Message: {result.get('message', 'No message')}")
    
    # Show file details
    for file in result.get('files', []):
        print(f"   - {file['name']} ({file.get('version', 'unknown')})")
    
    # Test with 32h template
    print("\n3. With 32h template:")
    template_32h = "template_32_hodin.xlsx"
    result = processor.select_folder("tests/test1", template_32h)
    print(f"   Found {len(result.get('files', []))} files")
    print(f"   Message: {result.get('message', 'No message')}")
    
    # Show file details
    for file in result.get('files', []):
        print(f"   - {file['name']} ({file.get('version', 'unknown')})")

if __name__ == "__main__":
    test_folder_selection()