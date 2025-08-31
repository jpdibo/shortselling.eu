#!/usr/bin/env python3
"""
Test Spain Scraper
Tests the Spain scraper with the direct CNMV URL
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory

def test_spain_scraper():
    """Test the Spain scraper specifically"""
    print("🇪🇸 Testing Spain Scraper")
    print("=" * 60)
    
    try:
        # Create Spain scraper
        factory = ScraperFactory()
        spain_scraper = factory.create_scraper('ES')
        
        print(f"✅ Spain Scraper created: {spain_scraper.country_name}")
        print(f"📍 Data URL: {spain_scraper.get_data_url()}")
        
        # Test downloading data
        print("\n📥 Testing data download...")
        data = spain_scraper.download_data()
        print(f"✅ Data downloaded successfully")
        
        # Test parsing data
        print("📊 Testing data parsing...")
        dataframes = spain_scraper.parse_data(data)
        print(f"✅ Parsed {len(dataframes)} sheets")
        
        for sheet_name, df in dataframes.items():
            print(f"   - {sheet_name}: {len(df)} rows")
        
        # Test extracting positions
        print("🔍 Testing position extraction...")
        positions = spain_scraper.extract_positions(dataframes)
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
        
        print("\n✅ Spain scraper test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Spain scraper test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spain_scraper()
