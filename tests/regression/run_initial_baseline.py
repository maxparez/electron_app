#!/usr/bin/env python3
"""
Create Initial Baseline for Regression Tests

This script runs all test cases and saves the outputs as expected results.
Run this once with a known-good version of the application.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from test_regression import RegressionTester


class BaselineCreator(RegressionTester):
    """Extended tester that saves all outputs as expected results"""
    
    def compare_output(self, test_name: str, version: str, result: Dict) -> bool:
        """Override to always save output as expected"""
        expected_base = self.expected_dir / version / f"{test_name}_output"
        
        # Ensure expected directory exists
        expected_base.parent.mkdir(parents=True, exist_ok=True)
        
        # For error cases, save JSON
        if test_name.startswith("error_"):
            expected_json = expected_base.with_suffix(".json")
            self.save_expected_error(result, expected_json)
            print(f"      📁 Saved error baseline: {expected_json.name}")
            
        # For valid cases, save Excel
        else:
            actual_xlsx = self.outputs_dir / version / f"{test_name}_output.xlsx"
            expected_xlsx = expected_base.with_suffix(".xlsx")
            
            if actual_xlsx.exists():
                shutil.copy2(actual_xlsx, expected_xlsx)
                print(f"      📁 Saved output baseline: {expected_xlsx.name}")
            else:
                print(f"      ⚠️  No output file created")
                
        return True  # Always return True for baseline creation


def main():
    """Create baseline outputs"""
    print("=" * 60)
    print("CREATING REGRESSION TEST BASELINE")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This will process all test inputs and save outputs as expected results.")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
        
    # Get base directory
    base_dir = Path(__file__).parent
    
    # Create baseline creator
    creator = BaselineCreator(base_dir)
    
    # Run all tests
    creator.run_all_tests()
    
    print()
    print("✅ Baseline created successfully!")
    print()
    print("Expected outputs saved to:")
    print(f"  {creator.expected_dir}")
    print()
    print("You can now run regression tests with: python test_regression.py")


if __name__ == "__main__":
    main()