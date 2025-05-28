#!/usr/bin/env python3
"""
Test intelligent date fixing functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

import pandas as pd
from tools.inv_vzd_processor import InvVzdProcessor

def test_date_fixing():
    """Test the intelligent date fixing logic"""
    print("=== Testing Intelligent Date Fixing ===")
    
    processor = InvVzdProcessor("16")
    
    # Test cases with different scenarios
    test_cases = [
        {
            "name": "Missing year with clear context",
            "dates": ["14.5.2024", "16.6.2024", "17.6.", "19.7.2024", "20.8.2024"],
            "expected_fix": "17.6.2024"
        },
        {
            "name": "Missing year with spaces",
            "dates": ["24.1.2025", "15 .2.", "20.3.2025"],
            "expected_fix": "15.2.2025"
        },
        {
            "name": "Multiple missing years",
            "dates": ["1.1.2024", "15.2.", "20.3.", "25.4.2024"],
            "expected_fixes": ["15.2.2024", "20.3.2024"]
        },
        {
            "name": "Ambiguous year context",
            "dates": ["15.12.2023", "10.1.", "20.2.2025"],
            "expected_fix": "10.1.2025"  # Should prefer closer context
        },
        {
            "name": "No context available",
            "dates": ["15.6.", "20.7.", "25.8."],
            "expected_fix": "current_year"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Input dates: {test_case['dates']}")
        
        # Create test series
        date_series = pd.Series(test_case['dates'])
        
        # Clear processor messages
        processor.clear_messages()
        
        # Apply date fixing
        fixed_dates = processor._fix_incomplete_dates(date_series)
        
        print(f"Fixed dates: {fixed_dates.tolist()}")
        
        # Show processor messages
        if processor.info_messages:
            print("Info messages:")
            for info in processor.info_messages:
                print(f"  ℹ️ {info}")
                
        if processor.warnings:
            print("Warning messages:")
            for warning in processor.warnings:
                print(f"  ⚠️ {warning}")
                
        if processor.errors:
            print("Error messages:")
            for error in processor.errors:
                print(f"  ❌ {error}")

def test_specific_examples():
    """Test with specific real-world examples"""
    print("\n=== Testing Specific Real-World Examples ===")
    
    processor = InvVzdProcessor("16")
    
    # Example 1: Your specific case
    example1 = ["14.5.2024", "16.6.2024", "17.6.", "19.7.2024"]
    print(f"\nExample 1: {example1}")
    processor.clear_messages()
    fixed1 = processor._fix_incomplete_dates(pd.Series(example1))
    print(f"Fixed: {fixed1.tolist()}")
    for info in processor.info_messages:
        print(f"  ℹ️ {info}")
    for warning in processor.warnings:
        print(f"  ⚠️ {warning}")
    
    # Example 2: Spaces issue
    example2 = ["24 .1.2025", "15.2.", "20.3.2025"]
    print(f"\nExample 2: {example2}")
    processor.clear_messages()
    fixed2 = processor._fix_incomplete_dates(pd.Series(example2))
    print(f"Fixed: {fixed2.tolist()}")
    for info in processor.info_messages:
        print(f"  ℹ️ {info}")
    for warning in processor.warnings:
        print(f"  ⚠️ {warning}")
    
    # Example 3: Year transition
    example3 = ["15.11.2024", "20.12.2024", "10.1.", "15.2.2025"]
    print(f"\nExample 3: {example3}")
    processor.clear_messages()
    fixed3 = processor._fix_incomplete_dates(pd.Series(example3))
    print(f"Fixed: {fixed3.tolist()}")
    for info in processor.info_messages:
        print(f"  ℹ️ {info}")
    for warning in processor.warnings:
        print(f"  ⚠️ {warning}")

if __name__ == "__main__":
    test_date_fixing()
    test_specific_examples()