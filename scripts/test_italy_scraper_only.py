#!/usr/bin/env python3
"""
Test Italy Scraper Only (No Database)
Tests the Italy scraper functionality without any database operations
"""
import sys
import os
from datetime import datetime
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scrapers.scraper_factory import ScraperFactory

def test_italy_scraper_only():
    """Test Italy scraper without any database operations"""
    print("🇮🇹 Testing Italy Scraper Only (No Database)")
    print("=" * 60)
    try:
        factory = ScraperFactory()
        italy_scraper = factory.create_scraper('IT')
        print(f"✅ Italy Scraper created: {italy_scraper.country_name}")
        print(f"📍 Data URL: {italy_scraper.get_data_url()}")
        
        print("\n📥 Testing data download...")
        data = italy_scraper.download_data()
        print(f"✅ Data downloaded successfully")
        print(f"📁 Source URL: {data.get('source_url', 'Unknown')}")
        
        print("📊 Testing data parsing...")
        dataframes = italy_scraper.parse_data(data)
        print(f"✅ Parsed {len(dataframes)} sheets")
        for sheet_name, df in dataframes.items():
            print(f"   - {sheet_name}: {len(df)} rows, columns: {list(df.columns)}")
        
        print("🔍 Testing position extraction...")
        positions = italy_scraper.extract_positions(dataframes)
        print(f"✅ Extracted {len(positions)} positions")
        
        if positions:
            dates = [pos['date'] for pos in positions if pos['date']]
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                print(f"\n📅 Date range: {min_date.date()} to {max_date.date()}")
                
                date_counts = Counter([pos['date'].date() for pos in positions if pos['date']])
                print(f"📊 Recent date distribution:")
                for date, count in sorted(date_counts.items())[-5:]:
                    print(f"   {date}: {count:,} positions")
            
            current_positions = [pos for pos in positions if pos['is_current']]
            historical_positions = [pos for pos in positions if not pos['is_current']]
            print(f"\n📊 Position breakdown:")
            print(f"   - Current positions: {len(current_positions):,}")
            print(f"   - Historical positions: {len(historical_positions):,}")
            
            sample_position = positions[0]
            print(f"\n📋 Sample position:")
            print(f"   - Manager: {sample_position['manager_name']}")
            print(f"   - Company: {sample_position['company_name']}")
            print(f"   - ISIN: {sample_position['isin']}")
            print(f"   - Position Size: {sample_position['position_size']}%")
            print(f"   - Date: {sample_position['date']}")
            print(f"   - Current: {sample_position['is_current']}")
            
            print(f"\n🔄 Testing incremental logic simulation...")
            test_dates = [
                datetime(2025, 8, 10),
                datetime(2025, 8, 12),
                datetime(2025, 8, 14)
            ]
            for cutoff_date in test_dates:
                new_positions = [pos for pos in positions if pos['date'] and pos['date'] >= cutoff_date]
                print(f"   - If latest DB date is {cutoff_date.strftime('%Y-%m-%d')}: {len(new_positions):,} positions would be added")
        
        print("\n✅ Italy scraper test completed (NO DATABASE OPERATIONS)!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Italy scraper test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_italy_scraper_only()
