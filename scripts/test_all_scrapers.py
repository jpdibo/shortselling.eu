#!/usr/bin/env python3
"""
Test All Scrapers
Comprehensive test of all country scrapers to identify which ones work
"""
import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.scraper_factory import ScraperFactory
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraper(country_code: str, country_name: str):
    """Test a single scraper"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing {country_name} ({country_code}) Scraper")
    print(f"{'='*60}")
    
    try:
        # Create scraper
        factory = ScraperFactory()
        scraper = factory.create_scraper(country_code)
        print(f"✅ Scraper created: {scraper.__class__.__name__}")
        print(f"📍 Data URL: {scraper.get_data_url()}")
        
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
        
        print(f"\n🎉 {country_name} scraper: WORKING ✅")
        return True, len(positions)
        
    except Exception as e:
        print(f"\n❌ {country_name} scraper: FAILED ❌")
        print(f"   Error: {e}")
        return False, 0

def main():
    """Test all scrapers"""
    print("🧪 COMPREHENSIVE SCRAPER TEST")
    print("=" * 60)
    print("Testing all country scrapers to identify which ones work...")
    
    # Define all countries to test
    countries = [
        ('GB', 'United Kingdom'),
        ('DE', 'Germany'),
        ('ES', 'Spain'),
        ('IT', 'Italy'),
        ('FR', 'France'),
        ('BE', 'Belgium'),
        ('IE', 'Ireland'),
        ('NL', 'Netherlands'),
        ('FI', 'Finland')
    ]
    
    results = {}
    
    for country_code, country_name in countries:
        success, position_count = test_scraper(country_code, country_name)
        results[country_code] = {
            'name': country_name,
            'success': success,
            'position_count': position_count
        }
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    working_count = 0
    total_positions = 0
    
    for country_code, result in results.items():
        status = "✅ WORKING" if result['success'] else "❌ FAILED"
        positions = result['position_count'] if result['success'] else 0
        print(f"{status} {result['name']} ({country_code}): {positions:,} positions")
        
        if result['success']:
            working_count += 1
            total_positions += positions
    
    print(f"\n📈 SUMMARY:")
    print(f"   - Working scrapers: {working_count}/{len(countries)}")
    print(f"   - Total positions found: {total_positions:,}")
    
    # Recommendations
    print(f"\n🔧 RECOMMENDATIONS:")
    
    failed_countries = [code for code, result in results.items() if not result['success']]
    if failed_countries:
        print(f"   - Fix these scrapers: {', '.join(failed_countries)}")
    
    working_countries = [code for code, result in results.items() if result['success']]
    if working_countries:
        print(f"   - Keep these scrapers: {', '.join(working_countries)}")
    
    # Check for duplicate scrapers
    print(f"\n🔍 DUPLICATE SCRAPER CHECK:")
    scraper_files = [
        'uk_scraper.py',
        'germany_scraper.py', 
        'spain_scraper.py',
        'italy_scraper.py',
        'italy_selenium_scraper.py',  # This is a duplicate!
        'france_scraper.py',
        'belgium_scraper.py',
        'ireland_scraper.py',
        'netherlands_scraper.py'
    ]
    
    print(f"   - Found duplicate: italy_selenium_scraper.py")
    print(f"   - Recommendation: DELETE italy_selenium_scraper.py and keep italy_scraper.py")

if __name__ == "__main__":
    main()
