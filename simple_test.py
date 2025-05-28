#!/usr/bin/env python3
import sys
import os
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def simple_test():
    try:
        print("Creating processor...")
        processor = InvVzdProcessor("16")
        
        print("Testing file detection...")
        file_path = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx"
        version = processor._detect_source_version(file_path)
        print(f"Version detected: {version}")
        
        print("Testing data reading...")
        data = processor._read_source_data(file_path)
        print(f"Data read: {data is not None}")
        
        if data is not None:
            print(f"Shape: {data.shape}")
            print(f"Columns: {list(data.columns)}")
            
        print("Errors:", processor.errors)
        print("Info:", processor.info_messages)
        
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()