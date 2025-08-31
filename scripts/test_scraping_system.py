#!/usr/bin/env python3
"""
Test Scraping System
Tests the scraping system to ensure it works correctly
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.daily_scraping_service import DailyScrapingService
from app.scrapers.scraper_factory import ScraperFactory

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_scraping_system():
    """Test the complete scraping system"""
    print("🧪 Testing Scraping System")
    print("=" * 60)
    
    # Test 1: Scraper Factory
    print("1. Testing Scraper Factory...")
    factory = ScraperFactory()
    
    # Check available countries
    countries = factory.get_available_countries()
    print(f"   ✅ Available countries: {countries}")
    
    # Test each country
    for country_code in countries:
        print(f"   Testing {country_code}...")
        try:
            scraper = factory.create_scraper(country_code)
            print(f"   ✅ {country_code} scraper created successfully")
        except Exception as e:
            print(f"   ❌ {country_code} scraper failed: {e}")
    
    # Test 2: Daily Scraping Service
    print("\n2. Testing Daily Scraping Service...")
    scraping_service = DailyScrapingService()
    
    # Test getting countries to scrape
    try:
        countries_to_scrape = scraping_service._get_countries_to_scrape()
        print(f"   ✅ Found {len(countries_to_scrape)} countries to scrape")
        for country in countries_to_scrape:
            print(f"      - {country.name} ({country.code})")
    except Exception as e:
        print(f"   ❌ Failed to get countries: {e}")
    
    # Test 3: Scraping Status
    print("\n3. Testing Scraping Status...")
    try:
        status = scraping_service.get_scraping_status()
        print(f"   ✅ Status retrieved successfully")
        print(f"      - Recent logs: {len(status['recent_logs'])}")
        print(f"      - Country stats: {len(status['country_statistics'])}")
    except Exception as e:
        print(f"   ❌ Failed to get status: {e}")
    
    # Test 4: Individual Country Scrapers (without actually scraping)
    print("\n4. Testing Individual Country Scrapers...")
    for country_code in ['GB', 'DE', 'ES', 'BE', 'IE']:
        print(f"   Testing {country_code} scraper...")
        try:
            scraper = factory.create_scraper(country_code)
            
            # Test URL generation
            url = scraper.get_data_url()
            print(f"      ✅ URL: {url}")
            
            # Test scraper initialization
            print(f"      ✅ Scraper initialized: {scraper.country_name}")
            
        except Exception as e:
            print(f"      ❌ {country_code} failed: {e}")
    
    print("\n✅ Scraping system test completed!")
    print("=" * 60)

def test_uk_scraper_specifically():
    """Test UK scraper specifically since we know it works"""
    print("\n🔬 Testing UK Scraper Specifically...")
    
    try:
        factory = ScraperFactory()
        uk_scraper = factory.create_scraper('GB')
        
        print(f"   ✅ UK Scraper created: {uk_scraper.country_name}")
        print(f"   📍 Data URL: {uk_scraper.get_data_url()}")
        
        # Test downloading data (this will actually download)
        print("   📥 Testing data download...")
        data = uk_scraper.download_data()
        print(f"   ✅ Data downloaded successfully")
        
        # Test parsing data
        print("   📊 Testing data parsing...")
        dataframes = uk_scraper.parse_data(data)
        print(f"   ✅ Parsed {len(dataframes)} sheets")
        
        for sheet_name, df in dataframes.items():
            print(f"      - {sheet_name}: {len(df)} rows")
        
        # Test extracting positions
        print("   🔍 Testing position extraction...")
        positions = uk_scraper.extract_positions(dataframes)
        print(f"   ✅ Extracted {len(positions)} positions")
        
        if positions:
            sample_position = positions[0]
            print(f"   📋 Sample position:")
            print(f"      - Manager: {sample_position['manager_name']}")
            print(f"      - Company: {sample_position['company_name']}")
            print(f"      - Position Size: {sample_position['position_size']}%")
            print(f"      - Date: {sample_position['date']}")
            print(f"      - Current: {sample_position['is_current']}")
        
    except Exception as e:
        print(f"   ❌ UK scraper test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_scraping_system())
    
    # Run the specific UK test
    test_uk_scraper_specifically()
