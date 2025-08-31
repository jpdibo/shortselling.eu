#!/usr/bin/env python3
"""
Daily Scraping Runner Script
Runs the daily scraping service to update database with fresh data

IMPORTANT: This script only adds the most recent data that is not already in our database.
For each country, it:
1. Downloads ALL available data from the regulator
2. Checks the most recent date in our database for that country
3. Only adds positions from that date onwards (inclusive)
4. This prevents re-importing historical data we already have
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.daily_scraping_service import DailyScrapingService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scraping.log'),
        logging.StreamHandler()
    ]
)

async def main():
    """Main function to run daily scraping"""
    print("🚀 Starting Daily Scraping Service")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌍 Countries: UK, Germany, Spain, Belgium, Ireland")
    print("=" * 60)
    
    # Create scraping service
    scraping_service = DailyScrapingService()
    
    try:
        # Run daily update
        result = await scraping_service.run_daily_update()
        
        # Print results
        print(f"\n✅ Daily scraping completed successfully!")
        print(f"⏱️  Duration: {result['duration']}")
        print(f"📊 Statistics:")
        print(f"   - Countries processed: {result['statistics']['countries_processed']}")
        print(f"   - Countries failed: {result['statistics']['countries_failed']}")
        print(f"   - Total positions found: {result['statistics']['total_positions_found']:,}")
        print(f"   - Total positions added: {result['statistics']['total_positions_added']:,}")
        print(f"   - Total errors: {result['statistics']['total_errors']}")
        
        # Get current status
        status = scraping_service.get_scraping_status()
        print(f"\n📈 Current Database Status:")
        for country_stat in status['country_statistics']:
            print(f"   - {country_stat['country_name']}: {country_stat['total_positions']:,} positions")
        
        print(f"\n📋 Recent Scraping Logs:")
        for log in status['recent_logs'][:5]:  # Show last 5 logs
            status_emoji = "✅" if log['status'] == 'success' else "❌"
            print(f"   {status_emoji} {log['country_code']}: {log['positions_found']} found, {log['positions_added']} added")
        
        return result
        
    except Exception as e:
        print(f"❌ Daily scraping failed: {e}")
        logging.error(f"Daily scraping failed: {e}")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
