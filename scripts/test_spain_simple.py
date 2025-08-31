#!/usr/bin/env python3
"""
Simple Spain Data Test
Tests the Spain data structure without complex logic
"""

import sys
import os
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory

def test_spain_simple():
    """Simple test of Spain data"""
    print("🔍 Simple Spain Data Test")
    print("=" * 60)
    
    try:
        # Create Spain scraper
        factory = ScraperFactory()
        spain_scraper = factory.create_scraper('ES')
        
        # Download data
        print("📥 Downloading Spain data...")
        data = spain_scraper.download_data()
        
        # Parse data
        print("📊 Parsing data...")
        dataframes = spain_scraper.parse_data(data)
        
        print(f"✅ Found {len(dataframes)} sheets")
        
        for sheet_name, df in dataframes.items():
            if len(df) == 0:
                continue
                
            print(f"\n📋 Sheet: {sheet_name}")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            
            # Show column names
            print(f"   Column names:")
            for i, col in enumerate(df.columns):
                print(f"     {i}: '{col}'")
            
            # Show first few rows
            print(f"   First 3 rows:")
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                print(f"     Row {i}: {list(row.values)}")
            
            # Test column mapping
            column_mapping = {
                'manager': 'Tenedor de la Posición / Position holder',
                'company': 'Emisor / Issuer',
                'isin': 'ISIN',
                'position_size': 'Posición corta (%) / Net short position (%)',
                'date': 'Fecha posición / Position date'
            }
            
            print(f"   Testing column mapping:")
            for key, col_name in column_mapping.items():
                if col_name in df.columns:
                    print(f"     ✅ {key}: '{col_name}' found")
                else:
                    print(f"     ❌ {key}: '{col_name}' NOT found")
            
            # Test a few data rows
            print(f"   Testing data extraction:")
            success_count = 0
            for i in range(1, min(5, len(df))):  # Skip first row (header)
                try:
                    row = df.iloc[i]
                    
                    # Check if all required columns exist
                    missing_cols = []
                    for key, col_name in column_mapping.items():
                        if col_name not in df.columns:
                            missing_cols.append(col_name)
                    
                    if missing_cols:
                        print(f"     Row {i}: Missing columns: {missing_cols}")
                        continue
                    
                    # Try to extract data
                    manager = str(row[column_mapping['manager']]).strip()
                    company = str(row[column_mapping['company']]).strip()
                    isin = str(row[column_mapping['isin']]).strip() if pd.notna(row[column_mapping['isin']]) else None
                    position_size = float(row[column_mapping['position_size']])
                    date = pd.to_datetime(row[column_mapping['date']])
                    
                    print(f"     Row {i}: ✅ {manager} -> {company} ({position_size}%) on {date}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"     Row {i}: ❌ Error: {e}")
            
            print(f"   Successfully processed: {success_count} rows")
        
        print("\n✅ Simple test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spain_simple()
