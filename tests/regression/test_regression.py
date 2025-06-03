#!/usr/bin/env python3
"""
Regression Test Suite for InvVzd Tool

This script runs regression tests on the InvVzd tool by:
1. Processing test input files through the API
2. Comparing outputs with expected results
3. Reporting any differences
"""

import os
import sys
import json
import shutil
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add parent directory to path to import tools
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.python.tools.inv_vzd_processor import InvVzdProcessor


class RegressionTester:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.inputs_dir = base_dir / "inputs"
        self.outputs_dir = base_dir / "outputs"
        self.expected_dir = base_dir / "expected"
        
        # Create outputs directory if it doesn't exist
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        (self.outputs_dir / "16h").mkdir(exist_ok=True)
        (self.outputs_dir / "32h").mkdir(exist_ok=True)
        
        self.processor = InvVzdProcessor()
        self.results = []
        
    def run_all_tests(self) -> bool:
        """Run all regression tests"""
        print("=" * 60)
        print("REGRESSION TEST SUITE - InvVzd Tool")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        all_passed = True
        
        # Test 16h version
        print("Testing 16h version...")
        if not self.test_version("16h"):
            all_passed = False
            
        print()
        
        # Test 32h version  
        print("Testing 32h version...")
        if not self.test_version("32h"):
            all_passed = False
            
        # Print summary
        self.print_summary()
        
        return all_passed
        
    def test_version(self, version: str) -> bool:
        """Test specific version (16h or 32h)"""
        version_passed = True
        template_path = self.inputs_dir / "templates" / f"template_{version}.xlsx"
        
        if not template_path.exists():
            print(f"  ❌ Template not found: {template_path}")
            return False
            
        # Get all test files for this version
        test_files = sorted((self.inputs_dir / version).glob("*.xlsx"))
        
        for test_file in test_files:
            print(f"  Testing: {test_file.name}")
            
            try:
                # Process the file
                result = self.process_file(test_file, template_path, version)
                
                # Compare with expected output
                if self.compare_output(test_file.stem, version, result):
                    print(f"    ✅ PASSED")
                    self.results.append((version, test_file.name, "PASSED", None))
                else:
                    print(f"    ❌ FAILED")
                    version_passed = False
                    
            except Exception as e:
                print(f"    ❌ ERROR: {str(e)}")
                self.results.append((version, test_file.name, "ERROR", str(e)))
                version_passed = False
                
        return version_passed
        
    def process_file(self, source_file: Path, template_file: Path, version: str) -> Dict:
        """Process a single test file"""
        # Create output path
        output_file = self.outputs_dir / version / f"{source_file.stem}_output.xlsx"
        
        # Prepare options
        options = {
            'template_path': str(template_file),
            'output_dir': str(self.outputs_dir / version),
            'output_filename': f"{source_file.stem}_output.xlsx"
        }
        
        # Process the file
        result = self.processor.process([str(source_file)], options)
        
        return result
        
    def compare_output(self, test_name: str, version: str, result: Dict) -> bool:
        """Compare actual output with expected output"""
        expected_base = self.expected_dir / version / f"{test_name}_output"
        
        # For error cases, compare JSON error messages
        if test_name.startswith("error_"):
            expected_json = expected_base.with_suffix(".json")
            if expected_json.exists():
                return self.compare_error_output(result, expected_json)
            else:
                print(f"      ⚠️  No expected error file: {expected_json}")
                # First run - save the output as expected
                self.save_expected_error(result, expected_json)
                return True
                
        # For valid cases, compare Excel outputs
        else:
            expected_xlsx = expected_base.with_suffix(".xlsx")
            actual_xlsx = self.outputs_dir / version / f"{test_name}_output.xlsx"
            
            if expected_xlsx.exists():
                return self.compare_excel_output(actual_xlsx, expected_xlsx)
            else:
                print(f"      ⚠️  No expected output file: {expected_xlsx}")
                # First run - save the output as expected
                if actual_xlsx.exists():
                    shutil.copy2(actual_xlsx, expected_xlsx)
                    print(f"      📁 Saved as expected output")
                return True
                
    def compare_error_output(self, result: Dict, expected_file: Path) -> bool:
        """Compare error messages"""
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = json.load(f)
            
        # Compare status
        if result.get('status') != expected.get('status'):
            print(f"      Status mismatch: {result.get('status')} vs {expected.get('status')}")
            return False
            
        # Compare error messages (normalize whitespace)
        actual_errors = sorted([msg.strip() for msg in result.get('errors', [])])
        expected_errors = sorted([msg.strip() for msg in expected.get('errors', [])])
        
        if actual_errors != expected_errors:
            print(f"      Error messages differ:")
            print(f"      Actual: {actual_errors}")
            print(f"      Expected: {expected_errors}")
            return False
            
        return True
        
    def compare_excel_output(self, actual_file: Path, expected_file: Path) -> bool:
        """Compare Excel files (data only, not formatting)"""
        if not actual_file.exists():
            print(f"      Output file not created: {actual_file}")
            return False
            
        try:
            # Read both files
            actual_df = pd.read_excel(actual_file, sheet_name=None)
            expected_df = pd.read_excel(expected_file, sheet_name=None)
            
            # Compare sheet names
            if set(actual_df.keys()) != set(expected_df.keys()):
                print(f"      Sheet names differ")
                return False
                
            # Compare data in each sheet
            for sheet_name in actual_df.keys():
                if not actual_df[sheet_name].equals(expected_df[sheet_name]):
                    print(f"      Data differs in sheet: {sheet_name}")
                    # Show first difference
                    self.show_dataframe_diff(actual_df[sheet_name], expected_df[sheet_name])
                    return False
                    
            return True
            
        except Exception as e:
            print(f"      Error comparing Excel files: {e}")
            return False
            
    def show_dataframe_diff(self, df1: pd.DataFrame, df2: pd.DataFrame):
        """Show first difference between dataframes"""
        # Find first cell that differs
        if df1.shape != df2.shape:
            print(f"        Shape differs: {df1.shape} vs {df2.shape}")
            return
            
        for i in range(min(len(df1), len(df2))):
            for j in range(min(len(df1.columns), len(df2.columns))):
                val1 = df1.iloc[i, j]
                val2 = df2.iloc[i, j]
                if pd.isna(val1) and pd.isna(val2):
                    continue
                if val1 != val2:
                    print(f"        First diff at [{i},{j}]: '{val1}' vs '{val2}'")
                    return
                    
    def save_expected_error(self, result: Dict, output_file: Path):
        """Save error output as expected result"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        error_data = {
            'status': result.get('status'),
            'errors': result.get('errors', []),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
            
        print(f"      📁 Saved error output as expected")
        
    def print_summary(self):
        """Print test summary"""
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for _, _, status, _ in self.results if status == "PASSED")
        failed = sum(1 for _, _, status, _ in self.results if status == "FAILED")
        errors = sum(1 for _, _, status, _ in self.results if status == "ERROR")
        
        print(f"Total tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print()
        
        if failed > 0 or errors > 0:
            print("Failed/Error tests:")
            for version, test_file, status, error in self.results:
                if status in ["FAILED", "ERROR"]:
                    print(f"  - {version}/{test_file}: {status}")
                    if error:
                        print(f"    {error}")
                        
        print()
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main entry point"""
    # Get base directory
    base_dir = Path(__file__).parent
    
    # Create tester
    tester = RegressionTester(base_dir)
    
    # Run tests
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()