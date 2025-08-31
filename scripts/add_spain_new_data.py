#!/usr/bin/env python3
"""
Add New Spain Data to Database
Safely adds only new Spain data to the existing database using incremental update logic
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

async def add_spain_new_data():
    """Add only new Spain data to the database"""
    print("🇪🇸 Adding New Spain Data to Database")
    print("=" * 60)
    
    try:
        # First, check current Spain data in database
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
        total_positions_before = db.query(ShortPosition)\
            .filter(ShortPosition.country_id == spain_country.id)\
            .count()
        
        print(f"📊 Current Spain data in database:")
        print(f"   - Total positions: {total_positions_before:,}")
        print(f"   - Latest date: {latest_date.strftime('%Y-%m-%d') if latest_date else 'None'}")
        
        db.close()
        
        # Test the scraper to see what new data is available
        print(f"\n🔍 Checking available Spain data...")
        factory = ScraperFactory()
        spain_scraper = factory.create_scraper('ES')
        
        # Download and parse data
        data = spain_scraper.download_data()
        dataframes = spain_scraper.parse_data(data)
        positions = spain_scraper.extract_positions(dataframes)
        
        print(f"✅ Scraper found {len(positions):,} total positions")
        
        # Analyze what would be added
        if positions and latest_date:
            new_positions = [pos for pos in positions if pos['date'] >= latest_date]
            print(f"📈 Positions from {latest_date.strftime('%Y-%m-%d')} onwards: {len(new_positions):,}")
            
            if new_positions:
                # Show what will be added
                from collections import Counter
                date_counts = Counter([pos['date'].date() for pos in new_positions])
                
                print(f"📊 New positions to be added:")
                for date, count in sorted(date_counts.items()):
                    print(f"   {date}: {count:,} positions")
                
                # Confirm with user
                print(f"\n⚠️  About to add {len(new_positions):,} new Spain positions to database")
                print(f"   This will update positions from {latest_date.strftime('%Y-%m-%d')} onwards")
                
                # Use DailyScrapingService to add the data safely
                print(f"\n🔄 Adding new data using DailyScrapingService...")
                scraping_service = DailyScrapingService()
                
                # Run the service (it will only add new data due to incremental logic)
                result = await scraping_service.run_daily_update()
                
                print(f"✅ DailyScrapingService completed")
                print(f"📊 Results:")
                print(f"   - Total positions added: {result['statistics']['total_positions_added']}")
                print(f"   - Countries processed: {result['statistics']['countries_processed']}")
                print(f"   - Errors: {result['statistics']['total_errors']}")
                
                # Check final database state
                db = next(get_db())
                total_positions_after = db.query(ShortPosition)\
                    .filter(ShortPosition.country_id == spain_country.id)\
                    .count()
                
                final_latest = db.query(ShortPosition)\
                    .filter(ShortPosition.country_id == spain_country.id)\
                    .order_by(ShortPosition.date.desc())\
                    .first()
                
                print(f"\n📊 Final Spain data in database:")
                print(f"   - Total positions: {total_positions_after:,}")
                print(f"   - Latest date: {final_latest.date.strftime('%Y-%m-%d') if final_latest else 'None'}")
                print(f"   - Positions added: {total_positions_after - total_positions_before}")
                
                db.close()
                
            else:
                print(f"✅ No new Spain data to add (database is already up to date)")
        else:
            print(f"📈 All {len(positions):,} positions are new (no existing data)")
            
            # Use DailyScrapingService to add all data
            print(f"\n🔄 Adding all Spain data using DailyScrapingService...")
            scraping_service = DailyScrapingService()
            
            result = await scraping_service.run_daily_update()
            
            print(f"✅ DailyScrapingService completed")
            print(f"📊 Results:")
            print(f"   - Total positions added: {result['statistics']['total_positions_added']}")
            print(f"   - Countries processed: {result['statistics']['countries_processed']}")
            print(f"   - Errors: {result['statistics']['total_errors']}")
        
        print("\n✅ Spain data update completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Spain data update failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(add_spain_new_data())
