#!/usr/bin/env python3
"""
Analyze all tabs in Excel files to understand complete structure
"""

import pandas as pd
import os
import sys
from pathlib import Path

def analyze_excel_tabs(filepath, country_name):
    """Analyze all tabs in an Excel file"""
    print(f"\n{'='*60}")
    print(f"📊 {country_name.upper()}")
    print(f"📁 File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        # Read all sheet names
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names
        
        print(f"📋 Found {len(sheet_names)} tabs:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"   {i}. {sheet}")
        
        # Analyze each tab
        for sheet_name in sheet_names:
            print(f"\n📄 TAB: {sheet_name}")
            print("-" * 40)
            
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                print(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Show columns
                print(f"📅 Columns:")
                for i, col in enumerate(df.columns, 1):
                    print(f"   {i:2d}. {col}")
                
                # Show first few rows
                print(f"\n📊 First 3 rows:")
                print(df.head(3).to_string())
                
                # Check for missing values
                missing = df.isnull().sum()
                if missing.sum() > 0:
                    print(f"\n❓ Missing values:")
                    for col, count in missing.items():
                        if count > 0:
                            print(f"   {col}: {count} missing values")
                
            except Exception as e:
                print(f"❌ Error reading tab {sheet_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def analyze_csv_file(filepath, country_name):
    """Analyze CSV file structure"""
    print(f"\n{'='*60}")
    print(f"📊 {country_name.upper()}")
    print(f"📁 File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(filepath, sep=';', encoding=encoding, nrows=5)
                print(f"✅ Successfully read CSV with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("❌ Could not read CSV file with any encoding")
            return
        
        # Get full file info
        df_full = pd.read_csv(filepath, sep=';', encoding=encoding)
        print(f"📊 Shape: {df_full.shape[0]} rows, {df_full.shape[1]} columns")
        
        # Show columns
        print(f"📅 Columns:")
        for i, col in enumerate(df_full.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Show first few rows
        print(f"\n📊 First 3 rows:")
        print(df_full.head(3).to_string())
        
        # Check for missing values
        missing = df_full.isnull().sum()
        if missing.sum() > 0:
            print(f"\n❓ Missing values:")
            for col, count in missing.items():
                if count > 0:
                    print(f"   {col}: {count} missing values")
                    
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main function to analyze all files"""
    print("🔍 ShortSelling.eu - Complete Excel Tab Analysis")
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
                    if filepath.suffix.lower() == '.xlsx':
                        analyze_excel_tabs(str(filepath), country)
                    else:
                        analyze_csv_file(str(filepath), country)
                else:
                    print(f"❌ File not found: {filepath}")
        else:
            print(f"❌ Country folder not found: {country_path}")
    
    print(f"\n{'='*60}")
    print("✅ Analysis complete!")
    print("💡 Next step: Create importers that handle all tabs and import ALL positions")

if __name__ == "__main__":
    main()
