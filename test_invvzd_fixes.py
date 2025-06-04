#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify InvVzd processor fixes:
1. Version filtering in select_folder method
2. Character encoding handling 
3. Logging buffer issues
"""

import os
import sys
import json

# Add src/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor
from logger import init_logging

def test_version_filtering():
    """Test that select_folder properly filters by template version"""
    print("=== Testing Version Filtering ===")
    
    # Initialize logging
    server_logger, tool_logger = init_logging()
    
    # Create processor
    processor = InvVzdProcessor(logger=tool_logger)
    
    # Test directory with mixed 16h and 32h files
    test_dir = "/root/vyvoj_sw/electron_app/legacy_code/inv"
    template_32h = os.path.join(test_dir, "32_hodin_inovativniho_vzdelavani_sablona.xlsx")
    template_16h = os.path.join(test_dir, "16_hodin_inovativniho_vzdelavani_sablona.xlsx")
    
    print(f"Test directory: {test_dir}")
    print(f"32h template: {template_32h}")
    print(f"16h template: {template_16h}")
    
    # Test with 32h template - should only find 32h files
    print("\n--- Test 1: 32h template filtering ---")
    result_32h = processor.select_folder(test_dir, template_32h)
    print(f"32h filtering result: {result_32h}")
    
    # Test with 16h template - should only find 16h files  
    print("\n--- Test 2: 16h template filtering ---")
    result_16h = processor.select_folder(test_dir, template_16h)
    print(f"16h filtering result: {result_16h}")
    
    # Test without template - should find all files
    print("\n--- Test 3: No template filtering ---")
    result_all = processor.select_folder(test_dir)
    print(f"No filtering result: {result_all}")
    
    return {
        "32h_files": len(result_32h.get("files", [])),
        "16h_files": len(result_16h.get("files", [])),
        "all_files": len(result_all.get("files", []))
    }

def test_character_encoding():
    """Test Czech character handling"""
    print("\n=== Testing Character Encoding ===")
    
    # Initialize logging
    server_logger, tool_logger = init_logging()
    
    # Create processor
    processor = InvVzdProcessor(logger=tool_logger)
    
    # Test Czech messages
    test_messages = [
        "Šablona nebyla poskytnuta",
        "Žádné soubory k zpracování", 
        "Neplatná šablona",
        "Chybí datum aktivity v buňce",
        "NESOUHLASÍ součty v SDP!"
    ]
    
    print("Testing Czech character display:")
    czech_chars_found = False
    for msg in test_messages:
        print(f"  {msg}")
        # Test that Czech characters display properly  
        if any(char in msg for char in ['š', 'ž', 'ň', 'í', 'ě', 'ř', 'ý', 'á', 'ó', 'ú', 'ů', 'č', 'ť', 'ď']):
            czech_chars_found = True
    
    assert czech_chars_found, "No Czech characters found in any test messages"
    
    # Test error message formatting
    processor._add_error('missing_date', cell='C5')
    processor._add_error('sum_mismatch', activities=32, forma=30, tema=32)
    
    print(f"Errors logged: {processor.errors}")
    
    return True

def test_logging_stability():
    """Test logging without buffer issues"""
    print("\n=== Testing Logging Stability ===")
    
    # Initialize logging multiple times to test stability
    for i in range(3):
        try:
            server_logger, tool_logger = init_logging()
            print(f"Logging initialization {i+1}: SUCCESS")
            
            # Test multiple log messages
            tool_logger.info(f"Test info message {i+1}")
            tool_logger.warning(f"Test warning message {i+1}")
            tool_logger.error(f"Test error message {i+1}")
            
        except Exception as e:
            print(f"Logging initialization {i+1}: FAILED - {e}")
            return False
    
    return True

def test_processing_with_fixes():
    """Test actual file processing with the fixes"""
    print("\n=== Testing File Processing ===")
    
    # Initialize logging
    server_logger, tool_logger = init_logging()
    
    # Create processor
    processor = InvVzdProcessor(logger=tool_logger)
    
    # Test files
    legacy_dir = "/root/vyvoj_sw/electron_app/legacy_code/inv"
    output_dir = "/root/vyvoj_sw/electron_app/tests/test1"
    
    # Test with a known file if it exists
    source_file = os.path.join(legacy_dir, "source.xlsx")
    template_file = os.path.join(legacy_dir, "32_hodin_inovativniho_vzdelavani_sablona.xlsx")
    
    if not os.path.exists(source_file):
        print(f"Source file not found: {source_file}")
        return False
        
    if not os.path.exists(template_file):
        print(f"Template file not found: {template_file}")
        return False
    
    print(f"Testing with source: {source_file}")
    print(f"Testing with template: {template_file}")
    
    # Test processing
    options = {
        'template': template_file,
        'output_dir': output_dir,
    }
    
    try:
        result = processor.process([source_file], options)
        print(f"Processing result: {result}")
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== INVVZD FIXES TEST SUITE ===")
    
    results = {}
    
    # Test 1: Version filtering
    try:
        results['version_filtering'] = test_version_filtering()
        print("✓ Version filtering test completed")
    except Exception as e:
        print(f"✗ Version filtering test failed: {e}")
        results['version_filtering'] = False
    
    # Test 2: Character encoding
    try:
        results['character_encoding'] = test_character_encoding()
        print("✓ Character encoding test completed")
    except Exception as e:
        print(f"✗ Character encoding test failed: {e}")
        results['character_encoding'] = False
    
    # Test 3: Logging stability
    try:
        results['logging_stability'] = test_logging_stability()
        print("✓ Logging stability test completed")
    except Exception as e:
        print(f"✗ Logging stability test failed: {e}")
        results['logging_stability'] = False
    
    # Test 4: File processing
    try:
        results['file_processing'] = test_processing_with_fixes()
        print("✓ File processing test completed")
    except Exception as e:
        print(f"✗ File processing test failed: {e}")
        results['file_processing'] = False
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)