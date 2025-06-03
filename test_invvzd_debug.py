#!/usr/bin/env python3
"""
Test script to debug InvVzd processing with verbose logging
"""

import os
import sys
import json

# Add src/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor
from logger import init_logging

def test_invvzd_debug():
    """Test InvVzd processing with debug logging"""
    print("=== INVVZD DEBUG TEST ===")
    
    # Initialize logging
    server_logger, tool_logger = init_logging()
    
    # Create processor
    processor = InvVzdProcessor(logger=tool_logger)
    
    # Test files - using WSL paths
    legacy_dir = "/root/vyvoj_sw/electron_app/legacy_code/inv"
    output_dir = "/root/vyvoj_sw/electron_app/tests/test1"
    
    # Source file and template
    source_file = os.path.join(legacy_dir, "source.xlsx")
    template_file = os.path.join(legacy_dir, "32_hodin_inovativniho_vzdelavani_sablona.xlsx")
    
    print(f"Source file: {source_file}")
    print(f"Template file: {template_file}")
    
    # Check if files exist
    print(f"Source exists: {os.path.exists(source_file)}")
    print(f"Template exists: {os.path.exists(template_file)}")
    
    # Process files
    options = {
        'template': template_file,
        'output_dir': output_dir,
        'keep_filename': True,
        'optimize': False
    }
    
    print("\n--- Starting processing ---")
    result = processor.process([source_file], options)
    
    print("\n--- Processing Result ---")
    print(f"Success: {result.get('success')}")
    print(f"Errors: {result.get('errors', [])}")
    print(f"Warnings: {result.get('warnings', [])}")
    print(f"Info: {result.get('info', [])}")
    
    if result.get('success') and 'data' in result:
        print(f"\nProcessed files:")
        for pf in result['data'].get('processed_files', []):
            print(f"  - Source: {pf['source']}")
            print(f"    Output: {pf['output']}")
            print(f"    Hours: {pf['hours']}")

if __name__ == "__main__":
    test_invvzd_debug()