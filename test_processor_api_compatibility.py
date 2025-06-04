#!/usr/bin/env python3
"""Test API compatibility between processors"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.python.tools.inv_vzd_processor import InvVzdProcessor
from src.python.tools.inv_vzd_processor_refactored import InvVzdProcessor as InvVzdProcessorRefactored

def test_processor_output():
    """Test if both processors produce compatible output"""
    
    source_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/dochazka_16h.xlsx"
    template_file = "/root/vyvoj_sw/electron_app/template_16_hodin.xlsx"
    output_dir = "/tmp/test_output"
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir + "_ref", exist_ok=True)
    
    print("=== Testing main InvVzdProcessor ===")
    processor1 = InvVzdProcessor()
    result1 = processor1.process(
        files=[source_file],
        options={
            'template': template_file,
            'output_dir': output_dir
        }
    )
    
    print(f"Success key present: {'success' in result1}")
    print(f"Success value: {result1.get('success')}")
    print(f"Data key present: {'data' in result1}")
    if 'data' in result1:
        print(f"processed_files in data: {'processed_files' in result1['data']}")
        if 'processed_files' in result1['data']:
            pf = result1['data']['processed_files'][0]
            print(f"First file status: {pf.get('status')}")
            print(f"First file output: {pf.get('output')}")
            print(f"First file info: {pf.get('info')}")
    
    print("\n=== Testing refactored processor ===")
    processor2 = InvVzdProcessorRefactored()
    result2 = processor2.process(
        files=[source_file],
        options={
            'template': template_file,
            'output_dir': output_dir + "_ref"
        }
    )
    
    print(f"Result keys: {list(result2.keys())}")
    print(f"Status: {result2.get('status')}")
    print(f"Results in result: {'results' in result2}")
    if 'results' in result2:
        r = result2['results'][0]
        print(f"First file status: {r.get('status')}")
        print(f"First file output: {r.get('output')}")
        print(f"First file info: {r.get('info')}")

if __name__ == "__main__":
    test_processor_output()