#!/usr/bin/env python3
"""
Test France Scraper Only
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.france_scraper import FranceScraper
import pandas as pd

def test_france_scraper():
    """Test the France scraper"""
    print("🇫🇷 Testing France Scraper")
    print("=" * 50)
    
    try:
        # Create scraper
        scraper = FranceScraper()
        print(f"✅ France Scraper created: {scraper.country_name}")
        
        # Download data
        print("\n📥 Downloading France data...")
        data = scraper.download_data()
        print(f"✅ Downloaded {len(data['csv_data'])} bytes")
        
        # Parse data
        print("\n📊 Parsing France data...")
        df = scraper.parse_data(data)
        print(f"✅ Parsed {len(df)} rows")
        
        # Show sample data
        print("\n📋 Sample data:")
        print(df.head())
        print(f"\nColumns: {list(df.columns)}")
        
        # Extract positions
        print("\n🔍 Extracting positions...")
        positions = scraper.extract_positions(df)
        print(f"✅ Extracted {len(positions)} positions from France")
        
        if positions:
            # Show statistics
            print("\n📊 Data Analysis:")
            print(f"   Total positions: {len(positions)}")
            
            # Date range
            dates = [pos['date'] for pos in positions if pos['date']]
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                print(f"   Date range: {min_date} to {max_date}")
            
            # Position size statistics
            sizes = [pos['position_size'] for pos in positions if pos['position_size'] > 0]
            if sizes:
                avg_size = sum(sizes) / len(sizes)
                max_size = max(sizes)
                min_size = min(sizes)
                print(f"   Position size - Avg: {avg_size:.2f}%, Max: {max_size:.2f}%, Min: {min_size:.2f}%")
            
            # Unique managers and companies
            managers = set(pos['manager_name'] for pos in positions)
            companies = set(pos['company_name'] for pos in positions)
            print(f"   Unique managers: {len(managers)}")
            print(f"   Unique companies: {len(companies)}")
            
            # Show sample positions
            print("\n📋 Sample positions:")
            for i, pos in enumerate(positions[:5]):
                print(f"   {i+1}. {pos['manager_name']} -> {pos['company_name']} ({pos['isin']}) - {pos['position_size']:.2f}% - {pos['date']}")
        
        print("\n🎉 France scraper test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing France scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_france_scraper()
