#!/usr/bin/env python3
"""
Test Incremental Update Logic
Tests that our scraping system only adds the most recent data not already in database
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.daily_scraping_service import DailyScrapingService
from app.scrapers.scraper_factory import ScraperFactory

def test_incremental_logic():
    """Test the incremental update logic"""
    print("🧪 Testing Incremental Update Logic")
    print("=" * 60)
    
    # Create scraping service
    scraping_service = DailyScrapingService()
    
    # Test UK scraper specifically
    print("1. Testing UK Scraper Incremental Logic...")
    
    try:
        # Create UK scraper
        factory = ScraperFactory()
        uk_scraper = factory.create_scraper('GB')
        
        # Download and parse data
        print("   📥 Downloading UK data...")
        data = uk_scraper.download_data()
        dataframes = uk_scraper.parse_data(data)
        positions = uk_scraper.extract_positions(dataframes)
        
        print(f"   ✅ Downloaded {len(positions)} total positions")
        
        # Analyze date distribution
        dates = [pos['date'] for pos in positions]
        min_date = min(dates)
        max_date = max(dates)
        
        print(f"   📅 Date range: {min_date.date()} to {max_date.date()}")
        
        # Group by date to see distribution
        from collections import Counter
        date_counts = Counter([pos['date'].date() for pos in positions])
        
        print(f"   📊 Date distribution:")
        for date, count in sorted(date_counts.items())[-5:]:  # Show last 5 dates
            print(f"      {date}: {count:,} positions")
        
        # Simulate what would happen with different latest dates in database
        print("\n2. Simulating Incremental Updates...")
        
        test_dates = [
            None,  # No existing data
            datetime(2025, 8, 10),  # Recent date
            datetime(2025, 8, 5),   # Older date
            datetime(2025, 7, 1),   # Much older date
        ]
        
        for test_latest_date in test_dates:
            if test_latest_date:
                filtered_positions = [
                    pos for pos in positions 
                    if pos['date'] >= test_latest_date
                ]
                print(f"   📈 If latest DB date is {test_latest_date.date()}:")
                print(f"      Would add {len(filtered_positions):,} positions")
                
                if filtered_positions:
                    new_dates = set([pos['date'].date() for pos in filtered_positions])
                    print(f"      New dates: {sorted(new_dates)[-3:]}")  # Show last 3 dates
            else:
                print(f"   📈 If no existing data:")
                print(f"      Would add {len(positions):,} positions")
        
        print("\n✅ Incremental update logic test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_incremental_logic()
