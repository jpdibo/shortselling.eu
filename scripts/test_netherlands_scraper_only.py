#!/usr/bin/env python3
"""
Test Netherlands Scraper Only
Test script to verify Netherlands scraper functionality without database interaction
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory

def test_netherlands_scraper():
    """Test the Netherlands scraper"""
    print("🇳🇱 Testing Netherlands Scraper")
    print("=" * 50)
    
    try:
        # Create Netherlands scraper
        factory = ScraperFactory()
        netherlands_scraper = factory.create_scraper('NL')
        print(f"✅ Netherlands Scraper created: {netherlands_scraper.country_name}")
        
        # Download and parse data
        print("\n📥 Downloading Netherlands data...")
        data = netherlands_scraper.download_data()
        dataframes = netherlands_scraper.parse_data(data)
        positions = netherlands_scraper.extract_positions(dataframes)
        
        print(f"✅ Extracted {len(positions)} positions from Netherlands")
        
        if not positions:
            print("❌ No positions found")
            return
        
        # Analyze the data
        print(f"\n📊 Data Analysis:")
        print(f"   Total positions: {len(positions)}")
        
        # Check date ranges
        dates = [pos['date'] for pos in positions if pos['date']]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            print(f"   Date range: {min_date} to {max_date}")
        
        # Check position size distribution
        position_sizes = [pos['position_size'] for pos in positions if pos['position_size'] > 0]
        if position_sizes:
            avg_size = sum(position_sizes) / len(position_sizes)
            max_size = max(position_sizes)
            min_size = min(position_sizes)
            print(f"   Position size - Avg: {avg_size:.2f}%, Max: {max_size:.2f}%, Min: {min_size:.2f}%")
        
        # Check unique managers and companies
        managers = set(pos['manager_name'] for pos in positions if pos['manager_name'])
        companies = set(pos['company_name'] for pos in positions if pos['company_name'])
        print(f"   Unique managers: {len(managers)}")
        print(f"   Unique companies: {len(companies)}")
        
        # Show sample positions
        print(f"\n📋 Sample Positions:")
        for i, pos in enumerate(positions[:5]):
            print(f"   {i+1}. {pos['manager_name']} -> {pos['company_name']} ({pos['position_size']:.2f}%) - {pos['date']}")
        
        # Check for current vs historical data
        current_positions = [pos for pos in positions if pos.get('is_current', False)]
        historical_positions = [pos for pos in positions if not pos.get('is_current', False)]
        
        print(f"\n📈 Data Types:")
        print(f"   Current positions: {len(current_positions)}")
        print(f"   Historical positions: {len(historical_positions)}")
        
        # Simulate incremental logic
        print(f"\n🔄 Simulating Incremental Logic:")
        if dates:
            latest_date = max(dates)
            print(f"   Latest date in data: {latest_date}")
            print(f"   Would only add positions after: {latest_date}")
        
        print(f"\n✅ Netherlands scraper test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Netherlands scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_netherlands_scraper()
