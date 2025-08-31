#!/usr/bin/env python3
"""
Script to examine Excel files and understand their structure
"""

import pandas as pd
import os
import sys
from pathlib import Path

def examine_file(filepath, country_name):
    """Examine a single file and print its structure"""
    print(f"\n{'='*60}")
    print(f"📊 {country_name.upper()}")
    print(f"📁 File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        # Try to read the file
        if filepath.endswith('.csv'):
            # Try different encodings for CSV files
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, nrows=5)
                    print(f"✅ Successfully read CSV with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print("❌ Could not read CSV file with any encoding")
                return
        else:
            df = pd.read_excel(filepath, nrows=5)
            print("✅ Successfully read Excel file")
        
        # Print basic info
        print(f"📋 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"📅 Columns:")
        
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Show first few rows
        print(f"\n📊 First 3 rows:")
        print(df.head(3).to_string())
        
        # Show data types
        print(f"\n🔍 Data types:")
        for col, dtype in df.dtypes.items():
            print(f"   {col}: {dtype}")
        
        # Check for missing values
        print(f"\n❓ Missing values:")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            for col, count in missing.items():
                if count > 0:
                    print(f"   {col}: {count} missing values")
        else:
            print("   No missing values found")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main function to examine all files"""
    print("🔍 ShortSelling.eu - Excel File Structure Analysis")
    print("=" * 60)
    
    # Define the base path
    base_path = Path("C:/shortselling.eu/excel_files")
    
    # Define countries with their files
    countries = {
        "United Kingdom": ["short-positions-daily-update.xlsx"],
        "Italy": ["PncPubbl.xlsx"],
        "Netherlands": ["nettoshortpositiesactueel.csv", "nettoshortpositieshistorie.csv"],
        "France": ["export_od_vad_20250812111500_20250812123000.csv"]
    }
    
    for country, files in countries.items():
        country_path = base_path / country
        if country_path.exists():
            for filename in files:
                filepath = country_path / filename
                if filepath.exists():
                    examine_file(str(filepath), country)
                else:
                    print(f"❌ File not found: {filepath}")
        else:
            print(f"❌ Country folder not found: {country_path}")
    
    print(f"\n{'='*60}")
    print("✅ Analysis complete!")
    print("💡 Next step: Create importers based on the column mappings")

if __name__ == "__main__":
    main()
