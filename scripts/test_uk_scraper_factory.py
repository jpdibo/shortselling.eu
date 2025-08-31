#!/usr/bin/env python3
"""
Test UK Scraper Only (No Database)
Tests the UK scraper functionality without any database operations
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory

def test_uk_scraper_only():
    """Test UK scraper without any database operations"""
    print("🇬🇧 Testing UK Scraper Only (No Database)")
    print("=" * 60)
    
    try:
        # Create UK scraper
        factory = ScraperFactory()
        uk_scraper = factory.create_scraper('GB')
        
        print(f"✅ UK Scraper created: {uk_scraper.country_name}")
        print(f"📍 Data URL: {uk_scraper.get_data_url()}")
        
        # Test downloading data
        print("\n📥 Testing data download...")
        data = uk_scraper.download_data()
        print(f"✅ Data downloaded successfully")
        
        # Test parsing data
        print("📊 Testing data parsing...")
        dataframes = uk_scraper.parse_data(data)
        print(f"✅ Parsed {len(dataframes)} sheets")
        
        for sheet_name, df in dataframes.items():
            print(f"   - {sheet_name}: {len(df)} rows")
        
        # Test extracting positions
        print("🔍 Testing position extraction...")
        positions = uk_scraper.extract_positions(dataframes)
        print(f"✅ Extracted {len(positions)} positions")
        
        if positions:
            # Analyze date distribution
            dates = [pos['date'] for pos in positions]
            min_date = min(dates)
            max_date = max(dates)
            
            print(f"\n📅 Date range: {min_date.date()} to {max_date.date()}")
            
            # Group by date to see distribution
            from collections import Counter
            date_counts = Counter([pos['date'].date() for pos in positions])
            
            print(f"📊 Recent date distribution:")
            for date, count in sorted(date_counts.items())[-5:]:  # Show last 5 dates
                print(f"   {date}: {count:,} positions")
            
            # Show sample position
            sample_position = positions[0]
            print(f"\n📋 Sample position:")
            print(f"   - Manager: {sample_position['manager_name']}")
            print(f"   - Company: {sample_position['company_name']}")
            print(f"   - Position Size: {sample_position['position_size']}%")
            print(f"   - Date: {sample_position['date']}")
            print(f"   - Current: {sample_position['is_current']}")
            
            # Test incremental logic simulation
            print(f"\n🔄 Testing incremental logic simulation...")
            
            # Simulate different cutoff dates
            test_dates = [
                datetime(2025, 8, 10),
                datetime(2025, 8, 12),
                datetime(2025, 8, 14)
            ]
            
            for cutoff_date in test_dates:
                new_positions = [pos for pos in positions if pos['date'] >= cutoff_date]
                print(f"   - If latest DB date is {cutoff_date.strftime('%Y-%m-%d')}: {len(new_positions):,} positions would be added")
        
        print("\n✅ UK scraper test completed (NO DATABASE OPERATIONS)!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ UK scraper test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_uk_scraper_only()
