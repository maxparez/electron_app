#!/usr/bin/env python3
"""
Test refactored InvVzdProcessor
"""

import sys
import os

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

# Test original processor
print("=== Testing Original Processor ===")
try:
    from tools.inv_vzd_processor import InvVzdProcessor as OriginalProcessor
    orig = OriginalProcessor()
    print("✅ Original processor imports successfully")
except Exception as e:
    print(f"❌ Original processor error: {e}")

# Test refactored processor
print("\n=== Testing Refactored Processor ===")
try:
    from tools.inv_vzd_processor_refactored import InvVzdProcessor as RefactoredProcessor
    refactored = RefactoredProcessor()
    print("✅ Refactored processor imports successfully")
    
    # Check if all utility modules load
    print("\nChecking utility modules:")
    print(f"  - DateParser: {'✅' if hasattr(refactored, 'date_parser') else '❌'}")
    print(f"  - ExcelHelper: {'✅' if hasattr(refactored, 'excel_helper') else '❌'}")
    print(f"  - ErrorHandler: {'✅' if hasattr(refactored, 'error_handler') else '❌'}")
    print(f"  - ToolLogger: {'✅' if hasattr(refactored, 'tool_logger') else '❌'}")
    print(f"  - FileValidator: {'✅' if hasattr(refactored, 'file_validator') else '❌'}")
    print(f"  - ExcelValidator: {'✅' if hasattr(refactored, 'excel_validator') else '❌'}")
    print(f"  - DataValidator: {'✅' if hasattr(refactored, 'data_validator') else '❌'}")
    
    # Test basic functionality
    print("\nTesting basic methods:")
    
    # Test validate_inputs
    result = refactored.validate_inputs([], {})
    print(f"  - validate_inputs (empty): {'✅' if not result else '❌'} (expected False)")
    
    # Test error messages
    if refactored.errors:
        print(f"  - Error handling: ✅ ({len(refactored.errors)} errors)")
        print(f"    First error: {refactored.errors[0]}")
    
except Exception as e:
    print(f"❌ Refactored processor error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")