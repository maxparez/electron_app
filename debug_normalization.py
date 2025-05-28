#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor
import unicodedata
import re

def debug_normalization(text):
    print(f"Debugging: '{text}'")
    
    # Step by step
    name_without_ext = os.path.splitext(text)[0]
    print(f"1. Without ext: '{name_without_ext}'")
    
    normalized = unicodedata.normalize('NFD', name_without_ext)
    print(f"2. NFD normalized: '{normalized}'")
    
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    print(f"3. Without diacritics: '{ascii_text}'")
    
    clean_text = re.sub(r'[^\w]', '_', ascii_text)
    print(f"4. Replace non-word: '{clean_text}'")
    
    clean_text = re.sub(r'_+', '_', clean_text)
    print(f"5. Remove multiple _: '{clean_text}'")
    
    clean_text = clean_text.strip('_')
    print(f"6. Strip underscores: '{clean_text}'")
    
    print()

if __name__ == "__main__":
    debug_normalization("docházka MŠ 1. pololetí 24-25")