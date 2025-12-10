#!/usr/bin/env python3
"""
Quick regression tester - runs only first N questions
"""
# Use centralized path utilities
from tests.utils.paths import add_project_root_to_path, REGRESSION_ROOT
add_project_root_to_path()


import csv
import tempfile
import os

try:
    # When run as module: python -m tests.regression.run_quick_regression
    from tests.regression.run_regression import RawCollector
except ModuleNotFoundError:
    # When run as script: python tests/regression/run_quick_regression.py
    from run_regression import RawCollector

def create_limited_csv(original_csv: str, limit: int, output_csv: str):
    """Create a CSV with only the first N questions"""
    with open(original_csv, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    # Take only first N rows
    limited_rows = rows[:limit]
    
    with open(output_csv, 'w', newline='') as outfile:
        if limited_rows:
            fieldnames = limited_rows[0].keys()
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(limited_rows)

def main():
    # Configuration
    LIMIT = 10  # Change this to test more/fewer questions
    original_csv = REGRESSION_ROOT / "test_questions.csv"
    
    # Create temporary limited CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_csv = temp_file.name
    
    try:
        create_limited_csv(original_csv, LIMIT, temp_csv)
        print(f"🔧 Running regression test with first {LIMIT} questions...")
        
        # Environment already loaded by run_regression module
        
        # Run the collector with limited questions
        collector = RawCollector(temp_csv)
        collector.run_collection()
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

if __name__ == "__main__":
    main()
