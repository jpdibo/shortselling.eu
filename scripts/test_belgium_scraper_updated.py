#!/usr/bin/env python3
"""
Test Updated Belgium Scraper
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.belgium_scraper import BelgiumScraper
import pandas as pd

def test_belgium_scraper():
    """Test the updated Belgium scraper"""
    print("🇧🇪 Testing Updated Belgium Scraper")
    print("=" * 50)
    
    try:
        # Create scraper
        scraper = BelgiumScraper()
        print(f"✅ Belgium Scraper created: {scraper.country_name}")
        
        # Test URLs
        print(f"\n🔗 Data URLs:")
        print(f"   Main URL: {scraper.get_data_url()}")
        print(f"   Current CSV: {scraper.get_current_csv_url()}")
        print(f"   Historical CSV: {scraper.get_historical_csv_url()}")
        
        # Download data
        print("\n📥 Downloading Belgium data...")
        data = scraper.download_data()
        print(f"✅ Downloaded {len(data['current_csv'])} bytes (current) and {len(data['historical_csv'])} bytes (historical)")
        
        # Parse data
        print("\n📊 Parsing Belgium data...")
        df = scraper.parse_data(data)
        
        print(f"   Total rows: {len(df)}")
        if len(df) > 0:
            print(f"   Columns: {list(df.columns)}")
            print(f"   Sample data:")
            print(df.head(3))
            print()
        
        print(f"✅ Parsed {len(df)} total rows")
        
        # Extract positions
        print("\n🔍 Extracting positions...")
        positions = scraper.extract_positions(df)
        print(f"✅ Extracted {len(positions)} positions from Belgium")
        
        if positions:
            # Show statistics
            print("\n📊 Data Analysis:")
            print(f"   Total positions: {len(positions)}")
            
            # Date range
            dates = [pos['date'] for pos in positions if pos['date']]
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                print(f"   Date range: {min_date} to {max_date}")
            
            # Position size statistics
            sizes = [pos['position_size'] for pos in positions if pos['position_size'] > 0]
            if sizes:
                avg_size = sum(sizes) / len(sizes)
                max_size = max(sizes)
                min_size = min(sizes)
                print(f"   Position size - Avg: {avg_size:.2f}%, Max: {max_size:.2f}%, Min: {min_size:.2f}%")
            
            # Unique managers and companies
            managers = set(pos['manager_name'] for pos in positions)
            companies = set(pos['company_name'] for pos in positions)
            print(f"   Unique managers: {len(managers)}")
            print(f"   Unique companies: {len(companies)}")
            
            # Show sample positions
            print("\n📋 Sample positions:")
            for i, pos in enumerate(positions[:5]):
                print(f"   {i+1}. {pos['manager_name']} -> {pos['company_name']} ({pos['isin']}) - {pos['position_size']:.2f}% - {pos['date']}")
        
        print("\n🎉 Belgium scraper test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Belgium scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_belgium_scraper()
