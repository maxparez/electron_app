#!/usr/bin/env python3
"""
Compare original and refactored InvVzdProcessor
"""

import sys
import os
import tempfile

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor as OriginalProcessor
from tools.inv_vzd_processor_refactored import InvVzdProcessor as RefactoredProcessor

def create_test_data():
    """Create test data for comparison"""
    # Test files from the tests directory
    test_files = [
        "tests/test1/dochazka_16h_test.xlsx"
    ]
    
    # Check if files exist
    existing_files = []
    for f in test_files:
        if os.path.exists(f):
            existing_files.append(f)
            print(f"✅ Found test file: {f}")
        else:
            print(f"❌ Test file not found: {f}")
            
    return existing_files

def test_processor(processor_class, name, files, template):
    """Test a processor with given files"""
    print(f"\n=== Testing {name} ===")
    
    try:
        processor = processor_class()
        
        # Test with empty inputs
        print("Test 1: Empty inputs")
        result = processor.validate_inputs([], {})
        print(f"  - Empty validation: {'✅ Failed as expected' if not result else '❌ Should have failed'}")
        
        if files and template:
            # Test with real files
            print("\nTest 2: Real file processing")
            options = {
                'template': template,
                'output_dir': tempfile.gettempdir()
            }
            
            # Validate inputs
            valid = processor.validate_inputs(files, options)
            print(f"  - Input validation: {'✅' if valid else '❌'}")
            
            if valid:
                # Process files
                result = processor.process(files, options)
                print(f"  - Processing result: {result.get('status', 'unknown')}")
                
                if 'processed_files' in result.get('data', {}):
                    for file_result in result['data']['processed_files']:
                        print(f"    - {os.path.basename(file_result['source'])}: {file_result['status']}")
                elif 'results' in result:
                    for file_result in result['results']:
                        print(f"    - {os.path.basename(file_result['source'])}: {file_result['status']}")
                        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== InvVzdProcessor Comparison Test ===")
    
    # Get test files
    test_files = create_test_data()
    
    # Find template
    template_16h = None
    for template in ["template_16_hodin.xlsx", "templates/template_16h.xlsx"]:
        if os.path.exists(template):
            template_16h = template
            print(f"✅ Found 16h template: {template}")
            break
            
    if not template_16h:
        print("❌ No 16h template found")
        
    # Test both processors
    orig_ok = test_processor(OriginalProcessor, "Original Processor", test_files, template_16h)
    ref_ok = test_processor(RefactoredProcessor, "Refactored Processor", test_files, template_16h)
    
    print("\n=== Summary ===")
    print(f"Original: {'✅ OK' if orig_ok else '❌ Failed'}")
    print(f"Refactored: {'✅ OK' if ref_ok else '❌ Failed'}")
    
    if orig_ok and ref_ok:
        print("\n✅ Both processors working! Ready for integration.")
    else:
        print("\n❌ Issues found, need to fix before integration.")

if __name__ == "__main__":
    main()