#!/usr/bin/env python3
"""
Test filename normalization for InvVzdProcessor
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_filename_normalization():
    """Test the filename normalization function"""
    print("=== Testing Filename Normalization ===")
    
    # Test cases with Czech diacritics and spaces
    test_cases = [
        # (input, expected_output)
        ("docházka MŠ 1. pololetí 24-25", "dochazka_MS_1_pololeti_24_25"),
        ("Inovativní vzdělávání ZŠ", "Inovativni_vzdelavani_ZS"),
        ("Evidence 16 hodin - třída 2A", "Evidence_16_hodin_trida_2A"),
        ("32 hodin inovativního vzdělávání", "32_hodin_inovativniho_vzdelavani"),
        ("Docházka žáků 2024/2025", "Dochazka_zaku_2024_2025"),
        ("Test - složité čeština ěščřžýáíé", "Test_slozite_cestina_escrzyaie"),
        ("Multiple   spaces   here", "Multiple_spaces_here"),
        ("File@with#special$chars%", "File_with_special_chars_"),
    ]
    
    processor = InvVzdProcessor("16")
    
    for original, expected in test_cases:
        result = processor._normalize_filename(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{original}' -> '{result}'")
        if result != expected:
            print(f"    Expected: '{expected}'")

def test_output_filename_creation():
    """Test complete output filename creation"""
    print("\n=== Testing Output Filename Creation ===")
    
    test_files = [
        ("docházka_MŠ_1_pololetí.xlsx", "16"),
        ("32_hodin_inovativního_vzdělávání.xlsx", "32"),
        ("Evidence žáků - třída 2A.xlsx", "16"),
    ]
    
    output_dir = "/tmp/test_output"
    
    for source_file, version in test_files:
        processor = InvVzdProcessor(version)
        output_path = processor._create_output_filename(source_file, output_dir, True)
        output_filename = os.path.basename(output_path)
        
        print(f"📁 Vstup: {source_file}")
        print(f"   Verze: {version}h")
        print(f"   Výstup: {output_filename}")
        print()

def test_real_files():
    """Test with real uploaded files"""
    print("=== Testing with Real Files ===")
    
    real_files = [
        "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx",
        "/root/vyvoj_sw/electron_app/legacy_code/inv/source.xlsx",
        "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_MŠ_1. pololetí_24_25_7x.xlsx"
    ]
    
    output_dir = "/tmp/test_output"
    
    for file_path in real_files:
        if os.path.exists(file_path):
            # Detect version first
            processor_test = InvVzdProcessor("16")
            detected_version = processor_test._detect_source_version(file_path)
            
            if detected_version:
                processor = InvVzdProcessor(detected_version)
                output_path = processor._create_output_filename(file_path, output_dir, True)
                output_filename = os.path.basename(output_path)
                
                print(f"📄 Vstup: {os.path.basename(file_path)}")
                print(f"   Detekovaná verze: {detected_version}h")
                print(f"   Výstupní název: {output_filename}")
                print()

if __name__ == "__main__":
    test_filename_normalization()
    test_output_filename_creation()
    test_real_files()