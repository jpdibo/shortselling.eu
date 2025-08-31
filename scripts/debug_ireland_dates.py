#!/usr/bin/env python3
"""
Debug Ireland date parsing
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.ireland_scraper import IrelandScraper
import pandas as pd
from datetime import datetime

def debug_ireland_dates():
    """Debug Ireland date parsing"""
    print("🔍 Debugging Ireland Date Parsing")
    print("=" * 50)
    
    try:
        # Create scraper
        scraper = IrelandScraper()
        
        # Download and parse data
        print("📥 Downloading Ireland data...")
        data = scraper.download_data()
        df = scraper.parse_data(data)
        
        print(f"📊 Total rows: {len(df)}")
        print(f"📅 Current date: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Check the raw date column
        if 'Position Date:' in df.columns:
            raw_dates = df['Position Date:'].dropna()
            print(f"\n📋 Raw date column sample (first 10):")
            for i, date in enumerate(raw_dates.head(10)):
                print(f"   {i+1}. {date} (type: {type(date)})")
            
            print(f"\n📋 Raw date column sample (last 10):")
            for i, date in enumerate(raw_dates.tail(10)):
                print(f"   {i+1}. {date} (type: {type(date)})")
        
        # Check parsed dates
        print(f"\n🔍 Checking parsed dates...")
        
        # Try to parse dates manually
        if 'Position Date:' in df.columns:
            parsed_dates = []
            for idx, row in df.iterrows():
                try:
                    raw_date = row['Position Date:']
                    if pd.notna(raw_date):
                        parsed_date = pd.to_datetime(raw_date)
                        parsed_dates.append(parsed_date)
                except Exception as e:
                    print(f"   Error parsing date at row {idx}: {raw_date} - {e}")
            
            if parsed_dates:
                parsed_dates.sort()
                print(f"\n📅 Parsed dates range:")
                print(f"   Earliest: {min(parsed_dates)}")
                print(f"   Latest: {max(parsed_dates)}")
                print(f"   Total unique dates: {len(set(parsed_dates))}")
                
                # Show recent dates
                recent_dates = sorted(set(parsed_dates))[-10:]
                print(f"\n📅 Most recent 10 dates:")
                for date in recent_dates:
                    print(f"   {date.strftime('%Y-%m-%d')}")
        
        # Check if there are any dates in 2025-08
        if parsed_dates:
            august_2025_dates = [d for d in parsed_dates if d.year == 2025 and d.month == 8]
            if august_2025_dates:
                print(f"\n✅ Found {len(august_2025_dates)} dates in August 2025:")
                for date in sorted(set(august_2025_dates)):
                    print(f"   {date.strftime('%Y-%m-%d')}")
            else:
                print(f"\n❌ No dates found in August 2025")
        
        print(f"\n🎯 Debug completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ireland_dates()
