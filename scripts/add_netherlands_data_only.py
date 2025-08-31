#!/usr/bin/env python3
"""
Add Netherlands Data Only
Adds Netherlands short-selling data to the database, handling duplicate managers properly
"""
import sys
import os
import asyncio
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scrapers.scraper_factory import ScraperFactory
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from sqlalchemy.orm import Session
from sqlalchemy import and_

async def add_netherlands_data():
    """Add Netherlands data to the database"""
    print("🇳🇱 Adding Netherlands Data to Database")
    print("=" * 50)
    
    try:
        # Create Netherlands scraper
        factory = ScraperFactory()
        netherlands_scraper = factory.create_scraper('NL')
        print(f"✅ Netherlands Scraper created: {netherlands_scraper.country_name}")
        
        # Download and parse data
        print("\n📥 Downloading Netherlands data...")
        data = netherlands_scraper.download_data()
        dataframes = netherlands_scraper.parse_data(data)
        positions = netherlands_scraper.extract_positions(dataframes)
        
        print(f"✅ Extracted {len(positions)} positions from Netherlands")
        
        if not positions:
            print("❌ No positions found")
            return
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get Netherlands country
            netherlands = db.query(Country).filter(Country.code == 'NL').first()
            if not netherlands:
                print("❌ Netherlands country not found in database")
                return
            
            print(f"✅ Found Netherlands country: {netherlands.name}")
            
            # Get latest date in database for Netherlands
            latest_position = db.query(ShortPosition).filter(
                ShortPosition.country_id == netherlands.id
            ).order_by(ShortPosition.date.desc()).first()
            
            latest_date = latest_position.date if latest_position else None
            print(f"📅 Latest date in database: {latest_date}")
            
            # Filter positions to only include new ones
            if latest_date:
                new_positions = [pos for pos in positions if pos['date'] and pos['date'] > latest_date]
                print(f"📊 Found {len(new_positions)} new positions after {latest_date}")
            else:
                new_positions = positions
                print(f"📊 No existing data found, adding all {len(new_positions)} positions")
            
            if not new_positions:
                print("✅ No new positions to add")
                return
            
            # Process positions
            added_count = 0
            errors = 0
            
            for i, position_data in enumerate(new_positions):
                try:
                    # Get or create manager
                    manager_name = position_data['manager_name']
                    slug = manager_name.lower().replace(' ', '-').replace('.', '').replace(',', '').replace('&', '-and-')
                    
                    manager = db.query(Manager).filter(Manager.slug == slug).first()
                    if not manager:
                        manager = Manager(name=manager_name, slug=slug)
                        db.add(manager)
                        db.flush()  # Get the ID
                    
                    # Get or create company
                    company_name = position_data['company_name']
                    company = db.query(Company).filter(
                        and_(
                            Company.name == company_name,
                            Company.country_id == netherlands.id
                        )
                    ).first()
                    
                    if not company:
                        company = Company(
                            name=company_name,
                            isin=position_data.get('isin'),
                            country_id=netherlands.id
                        )
                        db.add(company)
                        db.flush()  # Get the ID
                    
                    # Check if position already exists
                    existing_position = db.query(ShortPosition).filter(
                        and_(
                            ShortPosition.date == position_data['date'],
                            ShortPosition.company_id == company.id,
                            ShortPosition.manager_id == manager.id,
                            ShortPosition.country_id == netherlands.id
                        )
                    ).first()
                    
                    if existing_position:
                        continue  # Skip if already exists
                    
                    # Create new position
                    position = ShortPosition(
                        date=position_data['date'],
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=netherlands.id,
                        position_size=position_data['position_size'],
                                        is_active=position_data['is_active']
                    )
                    
                    db.add(position)
                    added_count += 1
                    
                    # Commit every 100 positions to avoid memory issues
                    if added_count % 100 == 0:
                        db.commit()
                        print(f"   ✅ Added {added_count} positions so far...")
                    
                except Exception as e:
                    errors += 1
                    print(f"   ⚠️ Error processing position {i}: {e}")
                    db.rollback()
                    continue
            
            # Final commit
            db.commit()
            
            print(f"\n🎉 Netherlands data import completed!")
            print(f"✅ Added {added_count} new positions")
            print(f"⚠️ Errors: {errors}")
            
            # Get updated statistics
            total_netherlands_positions = db.query(ShortPosition).filter(
                ShortPosition.country_id == netherlands.id
            ).count()
            
            print(f"📊 Total Netherlands positions in database: {total_netherlands_positions:,}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error adding Netherlands data: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    await add_netherlands_data()

if __name__ == "__main__":
    asyncio.run(main())
