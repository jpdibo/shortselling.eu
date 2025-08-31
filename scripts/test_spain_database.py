#!/usr/bin/env python3
"""
Test Spain Scraper with Database
Tests the Spain scraper with the database to show incremental update logic
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scrapers.scraper_factory import ScraperFactory
from app.services.daily_scraping_service import DailyScrapingService
from app.db.models import Country, ShortPosition
from app.db.database import get_db
from sqlalchemy.orm import Session

async def test_spain_with_database():
    """Test Spain scraper with database integration"""
    print("🇪🇸 Testing Spain Scraper with Database")
    print("=" * 60)
    
    try:
        # Get current Spain data from database
        db = next(get_db())
        
        # Get Spain country
        spain_country = db.query(Country).filter(Country.code == 'ES').first()
        if not spain_country:
            print("❌ Spain country not found in database")
            return
        
        # Get latest Spain position date
        latest_position = db.query(ShortPosition)\
            .filter(ShortPosition.country_id == spain_country.id)\
            .order_by(ShortPosition.date.desc())\
            .first()
        
        latest_date = latest_position.date if latest_position else None
        total_positions = db.query(ShortPosition)\
            .filter(ShortPosition.country_id == spain_country.id)\
            .count()
        
        print(f"📊 Current Spain data in database:")
        print(f"   - Total positions: {total_positions:,}")
        print(f"   - Latest date: {latest_date.strftime('%Y-%m-%d') if latest_date else 'None'}")
        
        # Test the scraper
        print(f"\n🔍 Testing Spain scraper...")
        factory = ScraperFactory()
        spain_scraper = factory.create_scraper('ES')
        
        # Download and parse data
        data = spain_scraper.download_data()
        dataframes = spain_scraper.parse_data(data)
        positions = spain_scraper.extract_positions(dataframes)
        
        print(f"✅ Scraper extracted {len(positions):,} positions")
        
        # Analyze the scraped data
        if positions:
            dates = [pos['date'] for pos in positions]
            min_date = min(dates)
            max_date = max(dates)
            
            print(f"📅 Scraped data range: {min_date.date()} to {max_date.date()}")
            
            # Count positions from latest_date onwards
            if latest_date:
                new_positions = [pos for pos in positions if pos['date'] >= latest_date]
                print(f"📈 Positions from {latest_date.strftime('%Y-%m-%d')} onwards: {len(new_positions):,}")
                
                # Show recent dates
                from collections import Counter
                date_counts = Counter([pos['date'].date() for pos in new_positions])
                
                print(f"📊 Recent new positions:")
                for date, count in sorted(date_counts.items())[-5:]:
                    print(f"   {date}: {count:,} positions")
            else:
                print(f"📈 All {len(positions):,} positions are new (no existing data)")
        
        # Test with DailyScrapingService
        print(f"\n🔄 Testing with DailyScrapingService...")
        scraping_service = DailyScrapingService()
        
        # Run the service for Spain only
        result = await scraping_service.run_daily_update()
        
        print(f"✅ DailyScrapingService completed")
        print(f"📊 Results:")
        print(f"   - Total positions added: {result['statistics']['total_positions_added']}")
        print(f"   - Countries processed: {result['statistics']['countries_processed']}")
        print(f"   - Errors: {result['statistics']['total_errors']}")
        
        # Check final database state
        db = next(get_db())
        final_total = db.query(ShortPosition)\
            .filter(ShortPosition.country_id == spain_country.id)\
            .count()
        
        final_latest = db.query(ShortPosition)\
            .filter(ShortPosition.country_id == spain_country.id)\
            .order_by(ShortPosition.date.desc())\
            .first()
        
        print(f"\n📊 Final Spain data in database:")
        print(f"   - Total positions: {final_total:,}")
        print(f"   - Latest date: {final_latest.date.strftime('%Y-%m-%d') if final_latest else 'None'}")
        print(f"   - Positions added: {final_total - total_positions}")
        
        db.close()
        
        print("\n✅ Spain scraper database test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Spain scraper database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_spain_with_database())
