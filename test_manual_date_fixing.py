#!/usr/bin/env python3
"""
Test date fixing with manually created test data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

import pandas as pd
from tools.inv_vzd_processor import InvVzdProcessor

def test_manual_date_fixing():
    """Test date fixing with manually created incomplete dates"""
    print("=== Testing Manual Date Fixing ===")
    
    processor = InvVzdProcessor("16")
    
    # Create test DataFrame with incomplete dates
    test_data = {
        'poradi': [1, 2, 3, 4, 5],
        'datum': ["14.5.2024", "16.6.2024", "17.6.", "19.7.2024", "20.8."], 
        'cas': ["8:00", "9:00", "10:00", "11:00", "12:00"],
        'hodin': [2, 3, 2, 1, 2],
        'forma': ["Prezenční", "Prezenční", "Online", "Prezenční", "Online"],
        'tema': ["Téma 1", "Téma 2", "Téma 3", "Téma 4", "Téma 5"],
        'ucitel': ["Jan Novák", "Marie Svobodová", "Petr Dvořák", "Jana Krásná", "Pavel Horný"]
    }
    
    df = pd.DataFrame(test_data)
    
    print("Original dates:")
    for i, date in enumerate(df['datum']):
        print(f"  {i}: {date}")
    
    print(f"\nData types before processing:")
    print(f"  datum column type: {df['datum'].dtype}")
    print(f"  First few values: {df['datum'].head().tolist()}")
    
    # Clear processor messages
    processor.clear_messages()
    
    # Apply date fixing
    fixed_dates = processor._fix_incomplete_dates(df['datum'])
    
    print(f"\nFixed dates:")
    for i, date in enumerate(fixed_dates):
        print(f"  {i}: {date}")
    
    # Show processor messages
    if processor.info_messages:
        print("\nInfo messages:")
        for info in processor.info_messages:
            print(f"  ℹ️ {info}")
            
    if processor.warnings:
        print("\nWarning messages:")
        for warning in processor.warnings:
            print(f"  ⚠️ {warning}")

def test_spaces_in_dates():
    """Test fixing dates with extra spaces"""
    print("\n=== Testing Spaces in Dates ===")
    
    processor = InvVzdProcessor("16")
    
    # Test dates with spaces
    dates_with_spaces = ["24 .1.2025", "15 . 2.", "20.3.2025", "10. 4.", "5.5 .2025"]
    
    print("Original dates with spaces:")
    for i, date in enumerate(dates_with_spaces):
        print(f"  {i}: '{date}'")
    
    processor.clear_messages()
    
    # Apply date fixing
    fixed_dates = processor._fix_incomplete_dates(pd.Series(dates_with_spaces))
    
    print(f"\nCleaned and fixed dates:")
    for i, date in enumerate(fixed_dates):
        print(f"  {i}: '{date}'")
        
    # Show messages
    if processor.info_messages:
        print("\nInfo messages:")
        for info in processor.info_messages:
            print(f"  ℹ️ {info}")
            
    if processor.warnings:
        print("\nWarning messages:")
        for warning in processor.warnings:
            print(f"  ⚠️ {warning}")

def test_confidence_levels():
    """Test different confidence levels in year inference"""
    print("\n=== Testing Confidence Levels ===")
    
    processor = InvVzdProcessor("16")
    
    test_scenarios = [
        {
            "name": "High confidence (all neighbors same year)",
            "dates": ["15.1.2024", "20.2.2024", "25.3.", "30.4.2024", "5.5.2024"]
        },
        {
            "name": "Medium confidence (mostly same year)",
            "dates": ["15.1.2024", "20.2.2024", "25.3.", "30.4.2024", "5.5.2023"]
        },
        {
            "name": "Low confidence (mixed years)",
            "dates": ["15.1.2022", "20.2.2023", "25.3.", "30.4.2024", "5.5.2025"]
        },
        {
            "name": "No context (all incomplete)",
            "dates": ["15.1.", "20.2.", "25.3.", "30.4.", "5.5."]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Input: {scenario['dates']}")
        
        processor.clear_messages()
        fixed_dates = processor._fix_incomplete_dates(pd.Series(scenario['dates']))
        
        print(f"Fixed: {fixed_dates.tolist()}")
        
        if processor.info_messages:
            for info in processor.info_messages:
                print(f"  ℹ️ {info}")
                
        if processor.warnings:
            for warning in processor.warnings:
                print(f"  ⚠️ {warning}")

if __name__ == "__main__":
    test_manual_date_fixing()
    test_spaces_in_dates()
    test_confidence_levels()