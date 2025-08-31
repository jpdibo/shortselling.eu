#!/usr/bin/env python3
"""
Test Updated Ireland Scraper
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.ireland_scraper import IrelandScraper
import pandas as pd

def test_ireland_scraper():
    """Test the updated Ireland scraper"""
    print("🇮🇪 Testing Updated Ireland Scraper")
    print("=" * 50)
    
    try:
        # Create scraper
        scraper = IrelandScraper()
        print(f"✅ Ireland Scraper created: {scraper.country_name}")
        
        # Test URLs
        print(f"\n🔗 Data URLs:")
        print(f"   Main URL: {scraper.get_data_url()}")
        print(f"   Excel URL: {scraper.get_excel_url()}")
        
        # Download data
        print("\n📥 Downloading Ireland data...")
        data = scraper.download_data()
        print(f"✅ Downloaded {len(data['excel_content'])} bytes")
        
        # Parse data
        print("\n📊 Parsing Ireland data...")
        df = scraper.parse_data(data)
        
        print(f"   Total rows: {len(df)}")
        if len(df) > 0:
            print(f"   Columns: {list(df.columns)}")
            print(f"   Sheets found: {df['sheet_name'].unique() if 'sheet_name' in df.columns else 'N/A'}")
            print(f"   Sample data:")
            print(df.head(3))
            print()
        
        print(f"✅ Parsed {len(df)} total rows")
        
        # Extract positions
        print("\n🔍 Extracting positions...")
        positions = scraper.extract_positions(df)
        print(f"✅ Extracted {len(positions)} positions from Ireland")
        
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
        
        print("\n🎉 Ireland scraper test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Ireland scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ireland_scraper()
