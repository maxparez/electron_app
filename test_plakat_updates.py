#!/usr/bin/env python3
"""
Test updated plakat generator functionality
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/python'))

from tools.plakat_generator import PlakatGenerator

def test_filename_generation():
    """Test the new filename generation logic"""
    gen = PlakatGenerator()
    
    test_cases = [
        ("CZ.02.3.68/0.0/0.0/20_083/0021933", "21933_plakat.pdf"),  # Remove leading zeros
        ("CZ.02.3.68/0.0/0.0/20_083/0021930", "21930_plakat.pdf"),  # Keep trailing zero
        ("CZ.02.3.68/0.0/0.0/20_083/0021945", "21945_plakat.pdf"),  # Full number
        ("CZ.02.3.68/0.0/0.0/20_083/0021900", "21900_plakat.pdf"),  # Keep trailing zeros
        ("CZ.02.3.68/0.0/0.0/20_083/0000001", "1_plakat.pdf"),     # All leading zeros
    ]
    
    print("Testing filename generation:")
    for project_id, expected in test_cases:
        result = gen._generate_filename(project_id)
        status = "✅" if result == expected else "❌"
        print(f"{status} {project_id} -> {result} (expected: {expected})")

def test_project_parsing():
    """Test parsing projects with semicolon separator"""
    test_input = """CZ.02.3.68/0.0/0.0/20_083/0021933;Modernizace učeben
CZ.02.3.68/0.0/0.0/20_083/0021934;Digitalizace výuky
CZ.02.3.68/0.0/0.0/20_083/0021935	Vybavení laboratoří"""
    
    print("\nTesting project parsing (semicolon and tab):")
    lines = test_input.strip().split('\n')
    for line in lines:
        if ';' in line:
            parts = line.split(';', 2)
            print(f"Semicolon: {parts[0]} -> {parts[1]}")
        elif '\t' in line:
            parts = line.split('\t', 2)
            print(f"Tab: {parts[0]} -> {parts[1]}")

if __name__ == "__main__":
    test_filename_generation()
    test_project_parsing()
    print("\nNote: Project name only appears on poster, ID is used only for filename")