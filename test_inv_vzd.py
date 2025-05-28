#!/usr/bin/env python3
"""
Test script for InvVzdProcessor with real data
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_file_detection():
    """Test version detection for uploaded files"""
    print("=== Testing File Detection ===")
    
    test_files = [
        ("/root/vyvoj_sw/electron_app/legacy_code/inv/source.xlsx", "32"),
        ("/root/vyvoj_sw/electron_app/legacy_code/inv/source_II.xlsx", "16"),
        ("/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx", "16")
    ]
    
    for file_path, expected_version in test_files:
        if os.path.exists(file_path):
            print(f"\nTesting: {os.path.basename(file_path)}")
            
            # Create processor with correct version
            processor = InvVzdProcessor(expected_version)
            version = processor._detect_source_version(file_path)
            print(f"  Detected version: {version}")
            
            # Test if file can be processed with matching processor
            if version == expected_version:
                try:
                    data = processor._read_source_data(file_path)
                    if data is not None:
                        print(f"  Rows read: {len(data)}")
                        print(f"  Columns: {list(data.columns)}")
                        print(f"  Total hours: {processor.hours_total}")
                    else:
                        print("  Failed to read data")
                        for error in processor.errors:
                            print(f"    Error: {error}")
                except Exception as e:
                    print(f"  Exception: {e}")
            else:
                print(f"  Version mismatch: expected {expected_version}, got {version}")
        else:
            print(f"File not found: {file_path}")

def test_templates():
    """Test template detection"""
    print("\n=== Testing Templates ===")
    
    templates = [
        "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_sablona.xlsx",
        "/root/vyvoj_sw/electron_app/legacy_code/inv/32_hodin_inovativniho_vzdelavani_sablona.xlsx"
    ]
    
    for template_path in templates:
        if os.path.exists(template_path):
            print(f"\nTesting template: {os.path.basename(template_path)}")
            
            processor = InvVzdProcessor("16")
            version = processor._detect_template_version(template_path)
            print(f"  Template version: {version}")
        else:
            print(f"Template not found: {template_path}")

def test_full_processing():
    """Test full processing pipeline"""
    print("\n=== Testing Full Processing ===")
    
    # Test with 16-hour data and template (matching versions)
    source_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx"
    template_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_sablona.xlsx"
    
    if os.path.exists(source_file) and os.path.exists(template_file):
        processor = InvVzdProcessor("16")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                result = processor.process_paths([source_file], template_file, temp_dir)
                
                print(f"Processing result: {result}")
                print(f"Errors: {processor.errors}")
                print(f"Info messages: {processor.info_messages}")
                
                if result["success"]:
                    for output_file in result["output_files"]:
                        if os.path.exists(output_file):
                            print(f"Output file created: {os.path.basename(output_file)}")
                            print(f"File size: {os.path.getsize(output_file)} bytes")
                        
            except Exception as e:
                print(f"Processing exception: {e}")
    else:
        print("Required files not found for full processing test")

if __name__ == "__main__":
    test_file_detection()
    test_templates()
    test_full_processing()