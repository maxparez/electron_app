#!/usr/bin/env python3
"""Debug script to find why InvVzd shows error despite processing activities"""

import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.python.tools.inv_vzd_processor import InvVzdProcessor

def simulate_api_processing(source_file, template_file):
    """Simulate exactly what the API does"""
    print(f"\n=== SIMULATING API PROCESSING ===")
    print(f"Source: {source_file}")
    print(f"Template: {template_file}")
    
    # Create temp directory like API does
    temp_dir = tempfile.mkdtemp()
    print(f"Temp dir: {temp_dir}")
    
    try:
        # Copy files to temp directory (simulating file upload)
        temp_source = os.path.join(temp_dir, os.path.basename(source_file))
        temp_template = os.path.join(temp_dir, os.path.basename(template_file))
        
        shutil.copy2(source_file, temp_source)
        shutil.copy2(template_file, temp_template)
        
        print(f"Copied source to: {temp_source}")
        print(f"Copied template to: {temp_template}")
        
        # Process with InvVzdProcessor
        processor = InvVzdProcessor()
        
        # Process exactly like API
        options = {
            'template': temp_template,
            'output_dir': temp_dir
        }
        
        result = processor.process([temp_source], options)
        
        print(f"\n--- Result ---")
        print(f"Success: {result.get('success')}")
        print(f"Errors: {result.get('errors')}")
        print(f"Warnings: {result.get('warnings')}")
        print(f"Info: {result.get('info')}")
        
        if result.get('data') and result['data'].get('processed_files'):
            for pf in result['data']['processed_files']:
                print(f"\n--- File Result ---")
                print(f"Source: {pf.get('source')}")
                print(f"Output: {pf.get('output')}")
                print(f"Status: {pf.get('status')}")
                print(f"Hours: {pf.get('hours')}")
                print(f"Info: {pf.get('info')}")
                
                # Check if output file exists
                if pf.get('output'):
                    if os.path.exists(pf['output']):
                        print(f"✓ Output file exists: {os.path.getsize(pf['output'])} bytes")
                    else:
                        print(f"✗ Output file NOT found!")
                        
                # Check what files are in temp directory
                print(f"\nFiles in temp directory:")
                for f in os.listdir(temp_dir):
                    fpath = os.path.join(temp_dir, f)
                    print(f"  {f} ({os.path.getsize(fpath)} bytes)")
        
        return result
        
    except Exception as e:
        print(f"\n!!! EXCEPTION !!!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # List files before cleanup
        print(f"\nFinal temp directory contents:")
        try:
            for f in os.listdir(temp_dir):
                print(f"  {f}")
        except:
            print("  (could not list)")
            
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_direct_processing(source_file, template_file):
    """Test direct processing without temp files"""
    print(f"\n=== DIRECT PROCESSING TEST ===")
    
    output_dir = "/tmp/direct_test"
    os.makedirs(output_dir, exist_ok=True)
    
    processor = InvVzdProcessor()
    result = processor.process(
        files=[source_file],
        options={
            'template': template_file,
            'output_dir': output_dir
        }
    )
    
    print(f"Direct result success: {result.get('success')}")
    if result.get('data') and result['data'].get('processed_files'):
        pf = result['data']['processed_files'][0]
        print(f"Status: {pf.get('status')}")
        print(f"Output: {pf.get('output')}")
        if pf.get('output') and os.path.exists(pf['output']):
            print(f"✓ Output file created: {os.path.getsize(pf['output'])} bytes")
        else:
            print(f"✗ No output file")

def main():
    # Test files
    source_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/dochazka_16h.xlsx"
    template_file = "/root/vyvoj_sw/electron_app/template_16_hodin.xlsx"
    
    # Test direct processing first
    test_direct_processing(source_file, template_file)
    
    # Then simulate API processing
    simulate_api_processing(source_file, template_file)
    
    # Also test with test1 file if exists
    test1_file = "/root/vyvoj_sw/electron_app/tests/test1/dochazka_16h_test.xlsx"
    if os.path.exists(test1_file):
        print("\n" + "="*60)
        print("Testing with test1 file...")
        test_direct_processing(test1_file, template_file)
        simulate_api_processing(test1_file, template_file)

if __name__ == "__main__":
    main()