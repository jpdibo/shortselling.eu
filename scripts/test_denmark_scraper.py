#!/usr/bin/env python3
"""
Test script for Denmark scraper
Tests download, parsing, and extraction without database interaction
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.scrapers.denmark_scraper import DenmarkScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_denmark_scraper():
    """Test the Denmark scraper functionality"""
    
    print("🇩🇰 Testing Denmark Scraper")
    print("=" * 50)
    
    try:
        # Create scraper instance
        scraper = DenmarkScraper('DK', 'Denmark')
        
        # Test 1: Download data
        print("\n📥 Testing data download...")
        data = scraper.download_data()
        
        if not data:
            print("❌ Download failed")
            return False
        
        print(f"✅ Download successful: {len(data.get('excel_content', b''))} bytes")
        print(f"📄 Source URL: {data.get('source_url')}")
        print(f"🔗 Download URL: {data.get('download_url')}")
        
        # Test 2: Parse data
        print("\n📊 Testing data parsing...")
        df = scraper.parse_data(data)
        
        if df.empty:
            print("❌ Parsing failed - empty DataFrame")
            return False
        
        print(f"✅ Parsing successful: {len(df)} rows, {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show first few rows
        print("\n📋 First 5 rows:")
        print(df.head())
        
        # Test 3: Extract positions
        print("\n🔍 Testing position extraction...")
        positions = scraper.extract_positions(df)
        
        if not positions:
            print("❌ Position extraction failed - no positions found")
            return False
        
        print(f"✅ Position extraction successful: {len(positions)} positions")
        
        # Show first few positions
        print("\n📋 First 5 positions:")
        for i, pos in enumerate(positions[:5]):
            print(f"  {i+1}. {pos.get('company_name', 'N/A')} - {pos.get('manager_name', 'N/A')} - {pos.get('position_size', 0)}%")
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 Denmark Scraper Test Results:")
        print(f"✅ Download: {len(data.get('excel_content', b''))} bytes")
        print(f"✅ Parsing: {len(df)} rows")
        print(f"✅ Extraction: {len(positions)} positions")
        print("✅ All tests passed!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")
        return False

if __name__ == "__main__":
    success = test_denmark_scraper()
    sys.exit(0 if success else 1)
