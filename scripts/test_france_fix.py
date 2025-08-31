#!/usr/bin/env python3
"""
Test France Scraper Fix
"""
import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.scraper_factory import ScraperFactory

def test_france_scraper():
    """Test the fixed France scraper"""
    print("🧪 Testing Fixed France Scraper")
    print("=" * 50)
    
    try:
        # Create scraper
        factory = ScraperFactory()
        scraper = factory.create_scraper('FR')
        print(f"✅ Scraper created: {scraper.__class__.__name__}")
        
        # Test download
        print(f"\n📥 Testing download...")
        data = scraper.download_data()
        print(f"✅ Download successful: {len(data)} items")
        
        # Test parsing
        print(f"\n📊 Testing parsing...")
        df = scraper.parse_data(data)
        print(f"✅ Parsing successful: {len(df)} rows")
        
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
        
        print(f"\n🎉 France scraper: FIXED AND WORKING ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ France scraper: STILL FAILED ❌")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    test_france_scraper()

