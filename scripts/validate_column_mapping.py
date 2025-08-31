#!/usr/bin/env python3
"""
Validate column mappings between Excel files and database schema
"""

import pandas as pd
import os
import sys
from pathlib import Path

def validate_uk_mapping(filepath):
    """Validate UK file column mapping"""
    print(f"\n🇬🇧 UK COLUMN MAPPING VALIDATION")
    print("=" * 50)
    
    try:
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names
        
        for sheet_name in sheet_names:
            print(f"\n📄 Tab: {sheet_name}")
            print("-" * 30)
            
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=3)
            
            # Expected mappings
            expected_mappings = {
                'Position Holder': 'Manager Name',
                'Name of Share Issuer': 'Company Name', 
                'ISIN': 'ISIN Code',
                'Net Short Position (%)': 'Position Size',
                'Position Date': 'Disclosure Date'
            }
            
            print("📋 Column Mapping Validation:")
            for excel_col, db_col in expected_mappings.items():
                if excel_col in df.columns:
                    print(f"   ✅ {excel_col} → {db_col}")
                else:
                    print(f"   ❌ {excel_col} → {db_col} (NOT FOUND)")
            
            # Check for unexpected columns
            unexpected = [col for col in df.columns if col not in expected_mappings]
            if unexpected:
                print(f"\n⚠️  Unexpected columns found:")
                for col in unexpected:
                    print(f"   - {col}")
            
            # Show sample data
            print(f"\n📊 Sample Data Validation:")
            for _, row in df.iterrows():
                if pd.notna(row['Position Holder']) and pd.notna(row['Name of Share Issuer']):
                    print(f"   Manager: {row['Position Holder']}")
                    print(f"   Company: {row['Name of Share Issuer']}")
                    print(f"   ISIN: {row['ISIN']}")
                    print(f"   Position: {row['Net Short Position (%)']}%")
                    print(f"   Date: {row['Position Date']}")
                    print(f"   ---")
                    break
                    
    except Exception as e:
        print(f"❌ Error validating UK file: {e}")

def validate_italy_mapping(filepath):
    """Validate Italy file column mapping"""
    print(f"\n🇮🇹 ITALY COLUMN MAPPING VALIDATION")
    print("=" * 50)
    
    try:
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names
        
        for sheet_name in sheet_names:
            if "Pubb" in sheet_name:
                continue
                
            print(f"\n📄 Tab: {sheet_name}")
            print("-" * 30)
            
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=3)
            
            # Expected mappings
            expected_mappings = {
                'Detentore': 'Manager Name',
                'Emittente': 'Company Name',
                'ISIN': 'ISIN Code', 
                'Perc. posizione netta corta': 'Position Size',
                'Data della posizione': 'Disclosure Date'
            }
            
            print("📋 Column Mapping Validation:")
            for excel_col, db_col in expected_mappings.items():
                if excel_col in df.columns:
                    print(f"   ✅ {excel_col} → {db_col}")
                else:
                    print(f"   ❌ {excel_col} → {db_col} (NOT FOUND)")
            
            # Check for unexpected columns
            unexpected = [col for col in df.columns if col not in expected_mappings]
            if unexpected:
                print(f"\n⚠️  Unexpected columns found:")
                for col in unexpected:
                    print(f"   - {col}")
            
            # Show sample data
            print(f"\n📊 Sample Data Validation:")
            for _, row in df.iterrows():
                if pd.notna(row['Detentore']) and pd.notna(row['Emittente']):
                    print(f"   Manager: {row['Detentore']}")
                    print(f"   Company: {row['Emittente']}")
                    print(f"   ISIN: {row['ISIN']}")
                    print(f"   Position: {row['Perc. posizione netta corta']}%")
                    print(f"   Date: {row['Data della posizione']}")
                    print(f"   ---")
                    break
                    
    except Exception as e:
        print(f"❌ Error validating Italy file: {e}")

def validate_netherlands_mapping(current_file, history_file):
    """Validate Netherlands file column mapping"""
    print(f"\n🇳🇱 NETHERLANDS COLUMN MAPPING VALIDATION")
    print("=" * 50)
    
    try:
        # Validate current file
        print(f"\n📄 Current Positions File:")
        print("-" * 30)
        
        df_current = pd.read_csv(current_file, sep=';', encoding='utf-8', nrows=3)
        
        # Expected mappings
        expected_mappings = {
            'Position holder': 'Manager Name',
            'Name of the issuer': 'Company Name',
            'ISIN': 'ISIN Code',
            'Net short position': 'Position Size', 
            'Position date': 'Disclosure Date'
        }
        
        print("📋 Column Mapping Validation:")
        for excel_col, db_col in expected_mappings.items():
            if excel_col in df_current.columns:
                print(f"   ✅ {excel_col} → {db_col}")
            else:
                print(f"   ❌ {excel_col} → {db_col} (NOT FOUND)")
        
        # Check for unexpected columns
        unexpected = [col for col in df_current.columns if col not in expected_mappings]
        if unexpected:
            print(f"\n⚠️  Unexpected columns found:")
            for col in unexpected:
                print(f"   - {col}")
        
        # Show sample data
        print(f"\n📊 Sample Data Validation:")
        for _, row in df_current.iterrows():
            if pd.notna(row['Position holder']) and pd.notna(row['Name of the issuer']):
                print(f"   Manager: {row['Position holder']}")
                print(f"   Company: {row['Name of the issuer']}")
                print(f"   ISIN: {row['ISIN']}")
                print(f"   Position: {row['Net short position']}%")
                print(f"   Date: {row['Position date']}")
                print(f"   ---")
                break
        
        # Validate history file
        print(f"\n📄 Historical Positions File:")
        print("-" * 30)
        
        # Try different encodings for history file
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df_history = pd.read_csv(history_file, sep=';', encoding=encoding, nrows=3)
                print(f"✅ Successfully read with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("❌ Could not read history file with any encoding")
            return
        
        print("📋 Column Mapping Validation:")
        for excel_col, db_col in expected_mappings.items():
            if excel_col in df_history.columns:
                print(f"   ✅ {excel_col} → {db_col}")
            else:
                print(f"   ❌ {excel_col} → {db_col} (NOT FOUND)")
        
        # Check for unexpected columns
        unexpected = [col for col in df_history.columns if col not in expected_mappings]
        if unexpected:
            print(f"\n⚠️  Unexpected columns found:")
            for col in unexpected:
                print(f"   - {col}")
                
    except Exception as e:
        print(f"❌ Error validating Netherlands files: {e}")

def validate_france_mapping(filepath):
    """Validate France file column mapping"""
    print(f"\n🇫🇷 FRANCE COLUMN MAPPING VALIDATION")
    print("=" * 50)
    
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8', nrows=3)
        
        # Expected mappings
        expected_mappings = {
            'Detenteur de la position courte nette': 'Manager Name',
            'Emetteur / issuer': 'Company Name',
            'code ISIN': 'ISIN Code',
            'Ratio': 'Position Size',
            'Date de debut de publication position': 'Disclosure Date'
        }
        
        print("📋 Column Mapping Validation:")
        for excel_col, db_col in expected_mappings.items():
            if excel_col in df.columns:
                print(f"   ✅ {excel_col} → {db_col}")
            else:
                print(f"   ❌ {excel_col} → {db_col} (NOT FOUND)")
        
        # Check for unexpected columns
        unexpected = [col for col in df.columns if col not in expected_mappings]
        if unexpected:
            print(f"\n⚠️  Unexpected columns found:")
            for col in unexpected:
                print(f"   - {col}")
        
        # Show sample data
        print(f"\n📊 Sample Data Validation:")
        for _, row in df.iterrows():
            if pd.notna(row['Detenteur de la position courte nette']) and pd.notna(row['Emetteur / issuer']):
                print(f"   Manager: {row['Detenteur de la position courte nette']}")
                print(f"   Company: {row['Emetteur / issuer']}")
                print(f"   ISIN: {row['code ISIN']}")
                print(f"   Position: {row['Ratio']}%")
                print(f"   Date: {row['Date de debut de publication position']}")
                print(f"   ---")
                break
                
    except Exception as e:
        print(f"❌ Error validating France file: {e}")

def show_database_schema():
    """Show our database schema for reference"""
    print(f"\n🗄️  DATABASE SCHEMA REFERENCE")
    print("=" * 50)
    print("📋 ShortPosition Table Columns:")
    print("   - id (Primary Key)")
    print("   - disclosure_date (Date)")
    print("   - position_size (Float)")
    print("   - is_active (Boolean)")
    print("   - is_historical (Boolean)")
    print("   - company_id (Foreign Key → Company)")
    print("   - manager_id (Foreign Key → Manager)")
    print("   - created_at (DateTime)")
    print("   - updated_at (DateTime)")
    
    print(f"\n📋 Company Table Columns:")
    print("   - id (Primary Key)")
    print("   - name (String)")
    print("   - isin_code (String, Optional)")
    print("   - country_code (String)")
    print("   - created_at (DateTime)")
    print("   - updated_at (DateTime)")
    
    print(f"\n📋 Manager Table Columns:")
    print("   - id (Primary Key)")
    print("   - name (String)")
    print("   - slug (String)")
    print("   - created_at (DateTime)")
    print("   - updated_at (DateTime)")

def main():
    """Main validation function"""
    print("🔍 ShortSelling.eu - Column Mapping Validation")
    print("=" * 60)
    
    # Show database schema first
    show_database_schema()
    
    # Define the base path
    base_path = Path("C:/shortselling.eu/excel_files")
    
    # Validate each country's files
    uk_file = base_path / "United Kingdom" / "short-positions-daily-update.xlsx"
    italy_file = base_path / "Italy" / "PncPubbl.xlsx"
    netherlands_current = base_path / "Netherlands" / "nettoshortpositiesactueel.csv"
    netherlands_history = base_path / "Netherlands" / "nettoshortpositieshistorie.csv"
    france_file = base_path / "France" / "export_od_vad_20250812111500_20250812123000.csv"
    
    # Run validations
    if uk_file.exists():
        validate_uk_mapping(uk_file)
    else:
        print("❌ UK file not found")
    
    if italy_file.exists():
        validate_italy_mapping(italy_file)
    else:
        print("❌ Italy file not found")
    
    if netherlands_current.exists() and netherlands_history.exists():
        validate_netherlands_mapping(netherlands_current, netherlands_history)
    else:
        print("❌ Netherlands files not found")
    
    if france_file.exists():
        validate_france_mapping(france_file)
    else:
        print("❌ France file not found")
    
    print(f"\n{'='*60}")
    print("✅ Column mapping validation complete!")
    print("💡 If all mappings show ✅, the import should work correctly")

if __name__ == "__main__":
    main()
