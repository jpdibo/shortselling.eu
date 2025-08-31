#!/usr/bin/env python3
"""
Test script for all country scrapers
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory

def test_scraper_factory():
    """Test the scraper factory"""
    print("🧪 Testing Scraper Factory...")
    
    # Test available countries
    countries = ScraperFactory.get_available_countries()
    print(f"✅ Available countries: {countries}")
    
    # Test country names
    for country_code in countries:
        country_name = ScraperFactory.get_country_name(country_code)
        print(f"   {country_code}: {country_name}")
    
    # Test scraper creation
    for country_code in countries:
        try:
            scraper = ScraperFactory.create_scraper(country_code)
            print(f"✅ Successfully created scraper for {country_code}")
        except Exception as e:
            print(f"❌ Failed to create scraper for {country_code}: {e}")

def test_single_scraper(country_code: str):
    """Test a single scraper"""
    print(f"\n🧪 Testing {country_code} scraper...")
    
    try:
        scraper = ScraperFactory.create_scraper(country_code)
        
        # Test URL
        url = scraper.get_data_url()
        print(f"   Data URL: {url}")
        
        # Test download (this might fail if no internet or site is down)
        try:
            data = scraper.download_data()
            print(f"   ✅ Download successful")
            
            # Test parsing
            df = scraper.parse_data(data)
            print(f"   ✅ Parsing successful - {len(df)} dataframes")
            
            # Test position extraction
            positions = scraper.extract_positions(df)
            print(f"   ✅ Position extraction successful - {len(positions)} positions")
            
        except Exception as e:
            print(f"   ⚠️  Download/Parsing failed (expected for testing): {e}")
        
    except Exception as e:
        print(f"   ❌ Scraper creation failed: {e}")

def main():
    """Main test function"""
    print("🚀 ShortSelling.eu - Scraper Test Suite")
    print("=" * 50)
    
    # Test factory
    test_scraper_factory()
    
    # Test individual scrapers
    countries = ['GB', 'IT', 'NL', 'FR', 'BE', 'ES', 'DE', 'IE']
    
    for country_code in countries:
        test_single_scraper(country_code)
    
    print("\n✅ Scraper test completed!")

if __name__ == "__main__":
    main()
