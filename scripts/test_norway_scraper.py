#!/usr/bin/env python3
"""
Test Norway Scraper
Tests the Norway scraper without affecting the database
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.norway_scraper import NorwayScraper
import logging

def test_norway_scraper():
    """Test the Norway scraper"""
    print("🧪 TESTING NORWAY SCRAPER")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create scraper instance
        scraper = NorwayScraper()
        print(f"✅ Created Norway scraper for {scraper.country_name}")
        
        # Test data URL
        data_url = scraper.get_data_url()
        api_url = scraper.get_api_url()
        print(f"📡 Data URL: {data_url}")
        print(f"📡 API URL: {api_url}")
        
        # Download data
        print("\n📥 Downloading data...")
        data = scraper.download_data()
        print(f"✅ Downloaded data successfully")
        
        # Show data summary
        print(f"\n📊 Data Summary:")
        print(f"  Current positions: {len(data.get('current_positions', []))}")
        print(f"  API data size: {len(data.get('api_data', b''))} bytes")
        print(f"  Detailed data: {len(data.get('detailed_data', []))} positions")
        
        # Parse data
        print("\n📊 Parsing data...")
        df = scraper.parse_data(data)
        print(f"✅ Parsed {len(df)} rows from Norway data")
        
        if not df.empty:
            print(f"📋 DataFrame columns: {list(df.columns)}")
            print(f"📋 DataFrame shape: {df.shape}")
            
            # Show data types breakdown
            data_types = df['data_type'].value_counts()
            print(f"\n📈 Data types breakdown:")
            for dtype, count in data_types.items():
                print(f"  {dtype}: {count}")
            
            # Extract positions
            print("\n🔍 Extracting positions...")
            positions = scraper.extract_positions(df)
            print(f"✅ Extracted {len(positions)} positions")
            
            if positions:
                # Show sample positions
                print("\n📋 Sample positions:")
                for i, pos in enumerate(positions[:5]):
                    print(f"  {i+1}. {pos['company_name']} - {pos['manager_name']} - {pos['position_size']}% - {pos['date']}")
                
                # Count by data type
                current_count = sum(1 for p in positions if p.get('is_current', False))
                historic_count = len(positions) - current_count
                print(f"\n📈 Position breakdown:")
                print(f"  Current positions: {current_count}")
                print(f"  Historic positions: {historic_count}")
                print(f"  Total positions: {len(positions)}")
            else:
                print("⚠️ No positions extracted")
        else:
            print("⚠️ No data parsed")
        
        print("\n✅ Norway scraper test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Norway scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_norway_scraper()
    sys.exit(0 if success else 1)
