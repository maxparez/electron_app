#!/usr/bin/env python3
"""
Test school type statistics functionality
"""

import sys
import os
import pandas as pd

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.zor_spec_dat_processor import ZorSpecDatProcessor

def test_school_type_identification():
    """Test school type identification from template names"""
    print("=== Testing School Type Identification ===")

    processor = ZorSpecDatProcessor()

    test_cases = [
        ("ZŠ Masarykova", "ZŠ"),
        ("MŠ Sluníčko", "MŠ"),
        ("ŠD při ZŠ Jiráskova", "ŠD"),
        ("Základní škola Komenského", "ZŠ"),
        ("Mateřská škola Pohádka", "MŠ"),
        ("Školní družina u ZŠ", "ŠD"),
        ("Gymnázium Brno", "Jiné"),
        ("Test Template", "Jiné"),
    ]

    for template_name, expected_type in test_cases:
        result = processor._identify_school_type(template_name)
        status = "✅" if result == expected_type else "❌"
        print(f"{status} '{template_name}' -> {result} (expected: {expected_type})")

def test_school_type_stats_calculation():
    """Test calculation of school type statistics"""
    print("\n=== Testing School Type Statistics Calculation ===")

    processor = ZorSpecDatProcessor()

    # Create test dataframe
    test_data = pd.DataFrame({
        'sablona': [
            'ZŠ První',      # 20 hours - should be counted
            'ZŠ První',
            'ZŠ První',
            'MŠ Sluníčko',   # 18 hours - should be counted
            'MŠ Sluníčko',
            'MŠ Sluníčko',
            'ŠD Radost',     # 10 hours - should NOT be counted (< 16)
            'ŠD Radost',
            'ZŠ Druhá',      # 16 hours exactly - should be counted
            'ZŠ Druhá',
            'MŠ Motýlek',    # 8 hours - should NOT be counted
        ],
        'pocet_hodin': [8, 6, 6, 6, 6, 6, 5, 5, 8, 8, 8],
        'jmena': ['Žák ' + str(i) for i in range(11)],
        'ca': [f'ca{i}' for i in range(11)],
        'datum': ['15.09.2024'] * 11,
        'forma': ['prezenční'] * 11,
        'tema': ['čtenářská pre/gramotnost'] * 11
    })

    # Add hash_jmena column
    test_data['hash_jmena'] = test_data['jmena'].apply(processor._custom_hash)

    print(f"Test data created with {len(test_data)} records")
    print("\nSchools and their total hours:")
    school_totals = test_data.groupby('sablona')['pocet_hodin'].sum()
    for school, hours in school_totals.items():
        print(f"  {school}: {hours} hours")

    # Calculate stats
    stats = processor._calculate_school_type_stats(test_data)

    print("\n📊 Calculated Statistics:")
    print(stats.to_string(index=False))

    # Verify results
    print("\n🔍 Verification:")
    expected_counts = {
        'ZŠ': 2,  # ZŠ První (20h) + ZŠ Druhá (16h)
        'MŠ': 1,  # MŠ Sluníčko (18h)
        'ŠD': 0   # ŠD Radost only has 10h
    }

    for typ, expected_count in expected_counts.items():
        row = stats[stats['Typ školy'] == typ]
        if not row.empty:
            actual_count = int(row['Počet škol (≥16h)'].values[0])
            status = "✅" if actual_count == expected_count else "❌"
            print(f"{status} {typ}: {actual_count} schools (expected: {expected_count})")
        else:
            status = "✅" if expected_count == 0 else "❌"
            print(f"{status} {typ}: 0 schools (expected: {expected_count})")

def test_edge_cases():
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===")

    processor = ZorSpecDatProcessor()

    # Test with empty dataframe
    empty_df = pd.DataFrame(columns=['sablona', 'pocet_hodin'])
    try:
        stats = processor._calculate_school_type_stats(empty_df)
        print(f"✅ Empty dataframe handled: {len(stats)} rows returned")
        print(stats.to_string(index=False))
    except Exception as e:
        print(f"❌ Empty dataframe failed: {e}")

    # Test with exactly 16 hours
    df_16h = pd.DataFrame({
        'sablona': ['ZŠ Exact'] * 2,
        'pocet_hodin': [8, 8]
    })
    stats = processor._calculate_school_type_stats(df_16h)
    exact_16_count = int(stats[stats['Typ školy'] == 'ZŠ']['Počet škol (≥16h)'].values[0])
    status = "✅" if exact_16_count == 1 else "❌"
    print(f"{status} Exactly 16 hours: counted = {exact_16_count == 1}")

if __name__ == "__main__":
    try:
        test_school_type_identification()
        test_school_type_stats_calculation()
        test_edge_cases()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
