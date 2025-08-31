#!/usr/bin/env python3
"""
Debug Spain Data Structure
Examines the actual structure of Spanish CNMV data
"""

import sys
import os
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory

def debug_spain_data():
    """Debug the Spain data structure"""
    print("🔍 Debugging Spain Data Structure")
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
            print(f"\n📋 Sheet: {sheet_name}")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            
            # Show column names
            print(f"   Column names:")
            for i, col in enumerate(df.columns):
                print(f"     {i}: '{col}'")
            
            # Show first few rows
            print(f"   First 5 rows:")
            for i in range(min(5, len(df))):
                row = df.iloc[i]
                print(f"     Row {i}: {list(row.values)}")
            
            # Check for header-like rows
            print(f"   Checking for header rows...")
            header_count = 0
            for i in range(min(20, len(df))):  # Check first 20 rows
                row = df.iloc[i]
                if spain_scraper._is_header_row(row):
                    header_count += 1
                    print(f"     Row {i} is header: {list(row.values)}")
            
            print(f"   Header rows found: {header_count}")
            
            # Show some sample data rows
            print(f"   Sample data rows (after headers):")
            data_rows = 0
            for i in range(len(df)):
                row = df.iloc[i]
                if not spain_scraper._is_header_row(row):
                    print(f"     Row {i}: {list(row.values)}")
                    data_rows += 1
                    if data_rows >= 3:  # Show 3 data rows
                        break
        
        print("\n✅ Debug completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_spain_data()
