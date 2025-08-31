#!/usr/bin/env python3
"""
Test Finland Scraper
"""
import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.scraper_factory import ScraperFactory

def test_finland_scraper():
    """Test the Finland scraper"""
    print("🧪 Testing Finland Scraper")
    print("=" * 50)
    
    try:
        # Create scraper
        factory = ScraperFactory()
        scraper = factory.create_scraper('FI')
        print(f"✅ Scraper created: {scraper.__class__.__name__}")
        print(f"📍 Data URL: {scraper.get_data_url()}")
        print(f"📍 Current positions URL: {scraper.get_current_positions_url()}")
        print(f"📍 Historic positions URL: {scraper.get_historic_positions_url()}")
        
        # Test download
        print(f"\n📥 Testing download...")
        data = scraper.download_data()
        print(f"✅ Download successful: {len(data)} items")
        print(f"   - Current page: {len(data['current_page'])} bytes")
        print(f"   - Historic page: {len(data['historic_page'])} bytes")
        
        # Test parsing
        print(f"\n📊 Testing parsing...")
        df = scraper.parse_data(data)
        print(f"✅ Parsing successful: {len(df)} rows")
        
        if not df.empty:
            print(f"   - Columns: {list(df.columns)}")
            print(f"   - Data types: {df['data_type'].value_counts().to_dict() if 'data_type' in df.columns else 'N/A'}")
        
        # Test position extraction
        print(f"\n🔍 Testing position extraction...")
        positions = scraper.extract_positions(df)
        print(f"✅ Position extraction successful: {len(positions)} positions")
        
        # Show sample data
        if positions:
            sample = positions[0]
            print(f"\n📋 Sample position:")
            print(f"   - Manager: {sample['manager_name']}")
            print(f"   - Company: {sample['company_name']}")
            print(f"   - ISIN: {sample['isin']}")
            print(f"   - Position Size: {sample['position_size']}%")
            print(f"   - Date: {sample['date']}")
            print(f"   - Current: {sample['is_current']}")
        
        print(f"\n🎉 Finland scraper: WORKING ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ Finland scraper: FAILED ❌")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    test_finland_scraper()

