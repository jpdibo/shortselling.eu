#!/usr/bin/env python3
"""
Add France short-selling data to the database
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from app.scrapers.france_scraper import FranceScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_france_data():
    """Add France short-selling data to database"""
    print("🇫🇷 Adding France Data to Database")
    print("=" * 50)
    
    try:
        # Create scraper
        scraper = FranceScraper()
        print(f"✅ France Scraper created: {scraper.country_name}")
        
        # Download and parse data
        print("\n📥 Downloading France data...")
        data = scraper.download_data()
        df = scraper.parse_data(data)
        positions = scraper.extract_positions(df)
        
        print(f"✅ Extracted {len(positions)} positions from France")
        
        # Get database session
        db = next(get_db())
        
        # Get France country
        france = db.query(Country).filter(Country.code == 'FR').first()
        if not france:
            print("❌ France country not found in database")
            return
        
        print(f"✅ Found France country: {france.name}")
        
        # Get latest date in database for France
        latest_position = db.query(ShortPosition).filter(
            ShortPosition.country_id == france.id
        ).order_by(ShortPosition.date.desc()).first()
        
        latest_date = latest_position.date if latest_position else None
        print(f"📅 Latest date in database: {latest_date}")
        
        # Filter for new positions
        new_positions = []
        if latest_date:
            for pos in positions:
                if pos['date'] > latest_date:
                    new_positions.append(pos)
        else:
            new_positions = positions
        
        print(f"📊 Found {len(new_positions)} new positions after {latest_date}")
        
        if not new_positions:
            print("✅ No new positions to add")
            return
        
        # Add new positions
        added_count = 0
        errors = 0
        
        for pos_data in new_positions:
            try:
                # Get or create manager
                manager_name = pos_data['manager_name']
                
                # Handle encoding issues with Arabic/Unicode characters
                try:
                    # Try to create a clean slug
                    slug = manager_name.lower().replace(' ', '-').replace('.', '').replace(',', '').replace('&', '-and-')
                    # Remove any non-ASCII characters that might cause encoding issues
                    import re
                    slug = re.sub(r'[^\x00-\x7F]+', '', slug)  # Remove non-ASCII characters
                    slug = re.sub(r'[^a-z0-9\-]', '', slug)    # Keep only alphanumeric and hyphens
                    
                    # If slug is empty after cleaning, create a fallback
                    if not slug:
                        slug = f"manager-{hash(manager_name) % 1000000}"
                    
                except Exception as e:
                    # Fallback slug creation
                    slug = f"manager-{hash(manager_name) % 1000000}"
                
                manager = db.query(Manager).filter(Manager.slug == slug).first()
                if not manager:
                    manager = Manager(name=manager_name, slug=slug)
                    db.add(manager)
                    db.flush()
                
                # Get or create company
                company_name = pos_data['company_name']
                isin = pos_data['isin']
                
                # Clean company name and ISIN
                try:
                    company_name = str(company_name).strip()
                    isin = str(isin).strip()
                    
                    # Skip if invalid data
                    if not company_name or company_name == 'nan' or not isin or isin == 'nan':
                        continue
                        
                except Exception as e:
                    logger.warning(f"Error cleaning company data: {e}")
                    continue
                
                company = db.query(Company).filter(Company.isin == isin).first()
                if not company:
                    company = Company(
                        name=company_name,
                        isin=isin,
                        country_id=france.id
                    )
                    db.add(company)
                    db.flush()
                
                # Create short position
                position = ShortPosition(
                    manager_id=manager.id,
                    company_id=company.id,
                    country_id=france.id,
                    position_size=pos_data['position_size'],
                    date=pos_data['date']
                )
                
                db.add(position)
                added_count += 1
                
                if added_count % 1000 == 0:
                    print(f"   Added {added_count} positions...")
                
            except Exception as e:
                logger.warning(f"Error processing position: {e}")
                errors += 1
                continue
        
        # Commit changes
        db.commit()
        
        # Get total count
        total_positions = db.query(ShortPosition).filter(ShortPosition.country_id == france.id).count()
        
        print(f"\n🎉 France data import completed!")
        print(f"✅ Added {added_count} new positions")
        print(f"⚠️ Errors: {errors}")
        print(f"📊 Total France positions in database: {total_positions:,}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    add_france_data()
