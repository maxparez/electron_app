#!/usr/bin/env python3
"""
Test student count with 16+ hours by school type
"""

import sys
import os
import pandas as pd

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.zor_spec_dat_processor import ZorSpecDatProcessor

def test_students_16plus_calculation():
    """Test calculation of students with 16+ hours by school type"""
    print("=== Testing Students 16+ Hours Calculation ===\n")

    processor = ZorSpecDatProcessor()

    # Create test data
    # Scenario:
    # - Student A in ZŠ: 20 hours total (should count)
    # - Student B in ZŠ: 10 hours (should NOT count)
    # - Student C in MŠ: 18 hours (should count)
    # - Student D in ŠD: 8 hours (should NOT count)
    # - Student A in MŠ: 16 hours (should count - same student, different school!)
    # Total expected: MŠ=2, ZŠ=1, ŠD=0

    test_data = pd.DataFrame({
        'ca': ['ca1', 'ca1', 'ca1', 'ca1', 'ca2', 'ca2', 'ca3', 'ca3', 'ca4', 'ca5', 'ca5'],
        'jmena': ['Student A', 'Student A', 'Student A', 'Student B', 'Student B', 'Student B',
                  'Student C', 'Student C', 'Student D', 'Student A', 'Student A'],
        'sablona': ['ZŠ První'] * 4 + ['ZŠ První'] * 2 + ['MŠ Sluníčko'] * 2 +
                   ['ŠD Radost'] * 1 + ['MŠ Pohádka'] * 2,
        'pocet_hodin': [8, 6, 4, 2, 5, 5, 10, 8, 8, 8, 8],
        'datum': ['15.09.2024'] * 11,
        'forma': ['prezenční'] * 11,
        'tema': ['čtenářská pre/gramotnost'] * 11
    })

    # Add hash_jmena
    test_data['hash_jmena'] = test_data['jmena'].apply(processor._custom_hash)

    print("📊 Test Data:")
    print("\nStudent hours by school (ca + jmena):")
    student_hours = test_data.groupby(['ca', 'jmena', 'sablona'])['pocet_hodin'].sum()
    for (ca, student, school), hours in student_hours.items():
        marker = "✅" if hours >= 16 else "❌"
        print(f"  {marker} {student} at {school}: {hours}h")

    # Calculate stats
    result = processor._calculate_students_16plus_by_type(test_data)

    print("\n📈 Calculated Results:")
    print(result.to_string(index=False))

    # Verify
    print("\n🔍 Verification:")
    expected = {'MŠ': 2, 'ZŠ': 1, 'ŠD': 0}

    all_correct = True
    for typ, expected_count in expected.items():
        actual = int(result[typ].values[0])
        status = "✅" if actual == expected_count else "❌"
        print(f"{status} {typ}: {actual} students (expected: {expected_count})")
        if actual != expected_count:
            all_correct = False

    return all_correct

def test_edge_cases():
    """Test edge cases for student counting"""
    print("\n=== Testing Edge Cases ===\n")

    processor = ZorSpecDatProcessor()

    # Test 1: Empty dataframe
    print("Test 1: Empty DataFrame")
    empty_df = pd.DataFrame(columns=['ca', 'jmena', 'sablona', 'pocet_hodin'])
    result = processor._calculate_students_16plus_by_type(empty_df)
    print(f"  Result: {result.to_dict('records')[0]}")
    assert result['MŠ'].values[0] == 0
    assert result['ZŠ'].values[0] == 0
    assert result['ŠD'].values[0] == 0
    print("  ✅ PASS\n")

    # Test 2: Exactly 16 hours
    print("Test 2: Exactly 16 hours (should count)")
    df_16h = pd.DataFrame({
        'ca': ['ca1', 'ca1'],
        'jmena': ['Student X', 'Student X'],
        'sablona': ['ZŠ Test', 'ZŠ Test'],
        'pocet_hodin': [8, 8]
    })
    result = processor._calculate_students_16plus_by_type(df_16h)
    assert result['ZŠ'].values[0] == 1
    print(f"  Result: ZŠ={result['ZŠ'].values[0]}")
    print("  ✅ PASS\n")

    # Test 3: Multiple students in same school
    print("Test 3: Multiple students in same school")
    df_multi = pd.DataFrame({
        'ca': ['ca1'] * 4 + ['ca1'] * 4,
        'jmena': ['Student 1'] * 4 + ['Student 2'] * 4,
        'sablona': ['MŠ Test'] * 8,
        'pocet_hodin': [5, 5, 3, 3, 6, 6, 2, 2]
    })
    result = processor._calculate_students_16plus_by_type(df_multi)
    # Student 1: 16h, Student 2: 16h -> both count
    assert result['MŠ'].values[0] == 2
    print(f"  Result: MŠ={result['MŠ'].values[0]} (expected 2)")
    print("  ✅ PASS\n")

    # Test 4: Same student, different schools (should count twice)
    print("Test 4: Same student in different schools")
    df_diff_schools = pd.DataFrame({
        'ca': ['ca1'] * 4 + ['ca2'] * 4,
        'jmena': ['Student Y'] * 8,
        'sablona': ['ZŠ One'] * 4 + ['MŠ Two'] * 4,
        'pocet_hodin': [4, 4, 4, 4, 5, 5, 3, 3]
    })
    result = processor._calculate_students_16plus_by_type(df_diff_schools)
    # Student Y at ZŠ One: 16h -> count
    # Student Y at MŠ Two: 16h -> count
    # Total: MŠ=1, ZŠ=1
    assert result['ZŠ'].values[0] == 1
    assert result['MŠ'].values[0] == 1
    print(f"  Result: MŠ={result['MŠ'].values[0]}, ZŠ={result['ZŠ'].values[0]}")
    print("  ✅ PASS\n")

    print("✅ All edge cases passed!")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("TESTING: Student Count with 16+ Hours by School Type")
        print("=" * 60 + "\n")

        result1 = test_students_16plus_calculation()
        test_edge_cases()

        print("\n" + "=" * 60)
        if result1:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
