#!/usr/bin/env python3
"""
Detailed analysis of Excel file structures for import mapping
"""

import pandas as pd
import os
import sys
from pathlib import Path

def analyze_uk_file(filepath):
    """Analyze UK file structure"""
    print(f"\n🇬🇧 UK FILE ANALYSIS")
    print("=" * 50)
    
    try:
        df = pd.read_excel(filepath)
        print(f"✅ Successfully read UK file")
        print(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Show column mapping
        print(f"\n📋 Column Mapping:")
        print(f"   Position Holder → Manager Name")
        print(f"   Name of Share Issuer → Company Name")
        print(f"   ISIN → ISIN Code")
        print(f"   Net Short Position (%) → Position Size")
        print(f"   Position Date → Disclosure Date")
        
        # Show sample data
        print(f"\n📊 Sample Data:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading UK file: {e}")
        return None

def analyze_italy_file(filepath):
    """Analyze Italy file structure"""
    print(f"\n🇮🇹 ITALY FILE ANALYSIS")
    print("=" * 50)
    
    try:
        df = pd.read_excel(filepath)
        print(f"✅ Successfully read Italy file")
        print(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Show column mapping
        print(f"\n📋 Column Mapping:")
        print(f"   Detentore → Manager Name")
        print(f"   LEI del Detentore → Manager LEI")
        print(f"   Emittente → Company Name")
        print(f"   LEI dell'Emittente → Company LEI")
        print(f"   ISIN → ISIN Code")
        print(f"   Perc. posizione netta corta → Position Size")
        print(f"   Data della posizione → Disclosure Date")
        
        # Show sample data
        print(f"\n📊 Sample Data:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading Italy file: {e}")
        return None

def analyze_netherlands_files(filepath_current, filepath_history):
    """Analyze Netherlands files structure"""
    print(f"\n🇳🇱 NETHERLANDS FILE ANALYSIS")
    print("=" * 50)
    
    try:
        # Read current positions
        df_current = pd.read_csv(filepath_current, sep=';', encoding='utf-8')
        print(f"✅ Successfully read Netherlands current file")
        print(f"📊 Current Shape: {df_current.shape[0]} rows, {df_current.shape[1]} columns")
        
        # Read historical positions
        df_history = pd.read_csv(filepath_history, sep=';', encoding='utf-8')
        print(f"✅ Successfully read Netherlands history file")
        print(f"📊 History Shape: {df_history.shape[0]} rows, {df_history.shape[1]} columns")
        
        # Show column mapping
        print(f"\n📋 Column Mapping:")
        print(f"   Position holder → Manager Name")
        print(f"   Name of the issuer → Company Name")
        print(f"   ISIN → ISIN Code")
        print(f"   Net short position → Position Size")
        print(f"   Position date → Disclosure Date")
        
        # Show sample data
        print(f"\n📊 Current Sample Data:")
        print(df_current.head(3).to_string())
        
        print(f"\n📊 History Sample Data:")
        print(df_history.head(3).to_string())
        
        return df_current, df_history
        
    except Exception as e:
        print(f"❌ Error reading Netherlands files: {e}")
        return None, None

def analyze_france_file(filepath):
    """Analyze France file structure"""
    print(f"\n🇫🇷 FRANCE FILE ANALYSIS")
    print("=" * 50)
    
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
        print(f"✅ Successfully read France file")
        print(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Show column mapping
        print(f"\n📋 Column Mapping:")
        print(f"   Detenteur de la position courte nette → Manager Name")
        print(f"   Legal Entity Identifier detenteur → Manager LEI")
        print(f"   Emetteur / issuer → Company Name")
        print(f"   Ratio → Position Size")
        print(f"   code ISIN → ISIN Code")
        print(f"   Date de debut position → Position Start Date")
        print(f"   Date de debut de publication position → Disclosure Date")
        print(f"   Date de fin de publication position → Publication End Date")
        
        # Show sample data
        print(f"\n📊 Sample Data:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading France file: {e}")
        return None

def main():
    """Main analysis function"""
    print("🔍 ShortSelling.eu - Detailed Excel Structure Analysis")
    print("=" * 60)
    
    # Define file paths
    base_path = Path("C:/shortselling.eu/excel_files")
    
    # Analyze each country's files
    uk_file = base_path / "United Kingdom" / "short-positions-daily-update.xlsx"
    italy_file = base_path / "Italy" / "PncPubbl.xlsx"
    netherlands_current = base_path / "Netherlands" / "nettoshortpositiesactueel.csv"
    netherlands_history = base_path / "Netherlands" / "nettoshortpositieshistorie.csv"
    france_file = base_path / "France" / "export_od_vad_20250812111500_20250812123000.csv"
    
    # Analyze each file
    uk_data = analyze_uk_file(uk_file) if uk_file.exists() else None
    italy_data = analyze_italy_file(italy_file) if italy_file.exists() else None
    netherlands_current_data, netherlands_history_data = analyze_netherlands_files(
        netherlands_current, netherlands_history
    ) if netherlands_current.exists() and netherlands_history.exists() else (None, None)
    france_data = analyze_france_file(france_file) if france_file.exists() else None
    
    print(f"\n{'='*60}")
    print("✅ Analysis complete!")
    print("\n💡 Next steps:")
    print("   1. Create importers for each country")
    print("   2. Map columns to database fields")
    print("   3. Test data import")

if __name__ == "__main__":
    main()
