#!/usr/bin/env python3
"""Debug script for 16h attendance processing issue"""

import sys
import os
import json
import logging
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.python.tools.inv_vzd_processor_refactored import InvVzdProcessor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def debug_process_file(source_file, template_file, output_dir):
    """Debug processing of a single file"""
    print(f"\n=== DEBUGGING 16H PROCESSING ===")
    print(f"Source: {source_file}")
    print(f"Template: {template_file}")
    print(f"Output dir: {output_dir}")
    
    # Check if files exist
    if not os.path.exists(source_file):
        print(f"ERROR: Source file not found: {source_file}")
        return
        
    if not os.path.exists(template_file):
        print(f"ERROR: Template file not found: {template_file}")
        return
    
    # Create processor
    processor = InvVzdProcessor()
    
    # Enable debug logging
    processor.logger.setLevel(logging.DEBUG)
    
    try:
        # Process the file
        print("\n--- Starting processing ---")
        result = processor.process(
            files=[source_file],
            options={
                'template': template_file,
                'output_dir': output_dir
            }
        )
        
        print("\n--- Processing result ---")
        # Convert numpy types to regular types for JSON serialization
        try:
            import numpy as np
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                return obj
                
            result_json = convert_numpy(result)
            print(json.dumps(result_json, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Could not serialize to JSON: {e}")
            print(f"Result structure: {result}")
        
        # Check specific file result
        if result.get('results'):
            file_result = result['results'][0]
            print(f"\nFile status: {file_result.get('status')}")
            print(f"Output file: {file_result.get('output')}")
            
            # Check if output file was created
            if file_result.get('output'):
                if os.path.exists(file_result['output']):
                    print(f"✓ Output file created successfully")
                    print(f"  Size: {os.path.getsize(file_result['output'])} bytes")
                else:
                    print(f"✗ Output file NOT found at: {file_result['output']}")
            else:
                print("✗ No output file path in result")
                
        # Print all messages
        if result.get('errors'):
            print("\n--- ERRORS ---")
            for err in result['errors']:
                print(f"  {err}")
                
        if result.get('warnings'):
            print("\n--- WARNINGS ---")
            for warn in result['warnings']:
                print(f"  {warn}")
                
        if result.get('info'):
            print("\n--- INFO ---")
            for info in result['info']:
                print(f"  {info}")
                
    except Exception as e:
        print(f"\n!!! EXCEPTION CAUGHT !!!")
        print(f"Error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()

def main():
    # Test with the legacy file
    source_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/dochazka_16h.xlsx"
    template_file = "/root/vyvoj_sw/electron_app/template_16_hodin.xlsx"
    output_dir = "/root/vyvoj_sw/electron_app/tests/regression/outputs"
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    debug_process_file(source_file, template_file, output_dir)
    
    # Also test with test1 file if it exists
    test1_file = "/root/vyvoj_sw/electron_app/tests/test1/dochazka_16h_test.xlsx"
    if os.path.exists(test1_file):
        print("\n\n" + "="*60)
        print("Testing with test1 file...")
        debug_process_file(test1_file, template_file, output_dir)

if __name__ == "__main__":
    main()