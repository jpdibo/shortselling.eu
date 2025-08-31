#!/usr/bin/env python3
"""
Test UK Excel column names to identify the mismatch
"""

import sys
import os
import pandas as pd
import requests
import tempfile

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_uk_column_names():
    """Check the actual column names in UK Excel file"""
    url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    try:
        print(f"📥 Downloading UK data from: {url}")
        
        # Create session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })
        
        # Download the file
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        try:
            # Read both sheets
            excel_file = pd.ExcelFile(temp_file_path)
            
            print(f"\n📊 Excel file structure:")
            print(f"   Sheets: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                print(f"\n📄 Sheet: {sheet_name}")
                
                # Read the sheet
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {list(df.columns)}")
                
                # Show first few rows
                print(f"   First 3 rows:")
                print(df.head(3).to_string())
                
                # Check what the import script expects vs what we have
                expected_columns = {
                    'Position holder': 'Position Holder',
                    'Issuer': 'Name of Share Issuer', 
                    'ISIN': 'ISIN',
                    'Net short position': 'Net Short Position (%)',
                    'Position date': 'Position Date'
                }
                
                print(f"\n🔍 Column name comparison:")
                for expected, actual in expected_columns.items():
                    if actual in df.columns:
                        print(f"   ✅ Expected: '{expected}' -> Found: '{actual}'")
                    else:
                        print(f"   ❌ Expected: '{expected}' -> NOT FOUND!")
                        print(f"      Available columns: {list(df.columns)}")
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔍 UK Column Names Test")
    print("=" * 50)
    
    check_uk_column_names()
    
    print(f"\n✅ Test complete!")

if __name__ == "__main__":
    main()
