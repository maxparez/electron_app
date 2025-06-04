#!/usr/bin/env python3
"""Test to compare refactored vs original processor on Windows with xlwings"""

import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor as RefactoredProcessor
from tools.inv_vzd_processor_original import InvVzdProcessor as OriginalProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_processor(processor_class, name, source_file, template, is_refactored=False):
    """Test a processor"""
    print(f"\n=== Testing {name} ===")
    
    output_dir = f"tests/output/{name.lower()}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create processor
    processor = processor_class(logger=logger)
    
    # Process file using appropriate method
    if is_refactored:
        # Use new API for refactored processor
        result = processor.process(
            files=[source_file],
            options={
                'template': template,
                'output_dir': output_dir
            }
        )
    else:
        # Use old API for original processor
        result = processor.process_paths(
            source_files=[source_file],
            template_path=template,
            output_dir=output_dir,
            keep_filename=True,
            optimize=False
        )
    
    print(f"Success: {result['success']}")
    if result.get('output_files'):
        print(f"Output files: {result['output_files']}")
    if result.get('errors'):
        print(f"Errors: {result['errors']}")
    if result.get('warnings'):
        print(f"Warnings: {result['warnings']}")
    if result.get('info'):
        print(f"Info: {result['info']}")
        
    return result

def main():
    # Test file
    source_file = "tests/test1/dochazka_16h_test.xlsx"
    template = "template_16_hodin.xlsx"
    
    # Check if files exist
    if not os.path.exists(source_file):
        print(f"Source file not found: {source_file}")
        return
    if not os.path.exists(template):
        print(f"Template not found: {template}")
        return
    
    # Test both processors
    print("Testing refactored vs original processor...")
    
    # Test original
    orig_result = test_processor(OriginalProcessor, "Original", source_file, template, is_refactored=False)
    
    # Test refactored  
    ref_result = test_processor(RefactoredProcessor, "Refactored", source_file, template, is_refactored=True)
    
    # Compare results
    print("\n=== Comparison ===")
    print(f"Original success: {orig_result['success']}")
    print(f"Refactored success: {ref_result['success']}")
    
    # Check xlwings availability
    try:
        import xlwings as xw
        print(f"\nxlwings available: YES")
        print(f"Platform should support full functionality")
    except ImportError:
        print(f"\nxlwings available: NO")
        print(f"Running in basic mode - full test requires Windows with Excel")

if __name__ == "__main__":
    main()