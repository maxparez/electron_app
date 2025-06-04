#!/usr/bin/env python3
"""
Regression test for Windows - compare original vs refactored processor
"""

import sys
import os
import shutil
import tempfile
from datetime import datetime

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

def test_with_processor(processor_module_name, test_name):
    """Test with specific processor version"""
    print(f"\n{'='*60}")
    print(f"Testing with {test_name}")
    print('='*60)
    
    # Import the processor
    if processor_module_name == "original":
        from tools.inv_vzd_processor_original import InvVzdProcessor
    else:
        from tools.inv_vzd_processor import InvVzdProcessor
    
    # Test files
    source_file = "tests/test1/dochazka_16h_test.xlsx"
    template_file = "template_16_hodin.xlsx"
    
    # Check if files exist
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False
        
    if not os.path.exists(template_file):
        print(f"❌ Template file not found: {template_file}")
        return False
        
    print(f"✅ Source file: {source_file}")
    print(f"✅ Template file: {template_file}")
    
    # Create processor
    processor = InvVzdProcessor()
    
    # Create output directory
    output_dir = tempfile.mkdtemp(prefix=f"test_{processor_module_name}_")
    print(f"📁 Output directory: {output_dir}")
    
    try:
        # Test detection
        print("\n1. Testing version detection:")
        version = processor._detect_source_version(source_file)
        print(f"   Detected version: {version}")
        
        # Test processing
        print("\n2. Testing file processing:")
        options = {
            'template': template_file,
            'output_dir': output_dir
        }
        
        result = processor.process([source_file], options)
        
        print(f"\n3. Results:")
        print(f"   Status: {result.get('status')}")
        
        if 'data' in result and 'processed_files' in result['data']:
            for file_result in result['data']['processed_files']:
                print(f"\n   File: {os.path.basename(file_result['source'])}")
                print(f"   Status: {file_result['status']}")
                print(f"   Output: {file_result.get('output', 'None')}")
                print(f"   Hours: {file_result.get('hours', 0)}")
                
                if file_result['errors']:
                    print("   Errors:")
                    for error in file_result['errors']:
                        print(f"     ❌ {error}")
                        
                if file_result['info']:
                    print("   Info:")
                    for info in file_result['info']:
                        print(f"     ℹ️ {info}")
        
        # Check if output file was created
        output_files = os.listdir(output_dir)
        if output_files:
            print(f"\n4. Output files created: {output_files}")
            return True
        else:
            print("\n4. ❌ No output files created")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(output_dir, ignore_errors=True)

def main():
    print("REGRESSION TEST - InvVzdProcessor")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {sys.platform}")
    
    # First check if we have the original processor
    original_path = "src/python/tools/inv_vzd_processor_original.py"
    if not os.path.exists(original_path):
        print(f"\n❌ Original processor not found: {original_path}")
        print("Creating backup of current processor...")
        
        current_path = "src/python/tools/inv_vzd_processor.py"
        if os.path.exists(current_path):
            shutil.copy2(current_path, original_path)
            print(f"✅ Created backup: {original_path}")
        else:
            print("❌ Cannot create backup - no current processor found")
            return
    
    # Test both versions
    original_ok = test_with_processor("original", "ORIGINAL PROCESSOR")
    refactored_ok = test_with_processor("refactored", "REFACTORED PROCESSOR")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Original processor: {'✅ PASS' if original_ok else '❌ FAIL'}")
    print(f"Refactored processor: {'✅ PASS' if refactored_ok else '❌ FAIL'}")
    
    if original_ok and not refactored_ok:
        print("\n⚠️ REGRESSION DETECTED! Refactored version is not working correctly.")
        print("Consider reverting to original processor:")
        print("  copy src\\python\\tools\\inv_vzd_processor_original.py src\\python\\tools\\inv_vzd_processor.py")
    elif original_ok and refactored_ok:
        print("\n✅ Both versions working! No regression detected.")
    elif not original_ok and not refactored_ok:
        print("\n❌ Both versions failing! Check test data and xlwings.")

if __name__ == "__main__":
    main()