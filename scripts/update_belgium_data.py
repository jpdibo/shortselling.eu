#!/usr/bin/env python3
"""
Update Belgium data with the new FSMA scraper
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from app.scrapers.belgium_scraper import BelgiumScraper
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text_for_database(text):
    """Clean text to be safe for database storage"""
    if not text:
        return ""
    
    try:
        # Convert to string and clean
        text = str(text).strip()
        
        # Remove or replace problematic characters
        # Remove non-ASCII characters that cause encoding issues
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # Remove other problematic characters
        text = re.sub(r'[^\w\s\-\.&]', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        logger.warning(f"Error cleaning text '{text}': {e}")
        return "Unknown"

def create_safe_slug(text):
    """Create a safe slug from text"""
    try:
        # Clean the text first
        clean_text = clean_text_for_database(text)
        
        # Create slug
        slug = clean_text.lower()
        slug = re.sub(r'[^\w\-]', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # If slug is empty, create fallback
        if not slug:
            slug = f"manager-{abs(hash(text)) % 1000000}"
        
        return slug
    except Exception as e:
        logger.warning(f"Error creating slug for '{text}': {e}")
        return f"manager-{abs(hash(text)) % 1000000}"

def update_belgium_data():
    """Update Belgium data with the new scraper"""
    print("🇧🇪 Updating Belgium Data with New FSMA Scraper")
    print("=" * 60)
    
    try:
        # Create scraper
        scraper = BelgiumScraper()
        print(f"✅ Belgium Scraper created: {scraper.country_name}")
        
        # Download and parse data
        print("\n📥 Downloading Belgium data...")
        data = scraper.download_data()
        df = scraper.parse_data(data)
        positions = scraper.extract_positions(df)
        
        print(f"✅ Extracted {len(positions)} positions from Belgium")
        
        # Get database session
        db = next(get_db())
        
        # Get Belgium country
        belgium = db.query(Country).filter(Country.code == 'BE').first()
        if not belgium:
            print("❌ Belgium country not found in database")
            return
        
        print(f"✅ Found Belgium country: {belgium.name}")
        
        # Get latest date in database for Belgium
        latest_position = db.query(ShortPosition).filter(
            ShortPosition.country_id == belgium.id
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
                # Clean manager name for database
                manager_name = clean_text_for_database(pos_data['manager_name'])
                if not manager_name or manager_name == "Unknown":
                    continue
                
                # Create safe slug
                slug = create_safe_slug(manager_name)
                
                # Get or create manager
                manager = db.query(Manager).filter(Manager.slug == slug).first()
                if not manager:
                    manager = Manager(name=manager_name, slug=slug)
                    db.add(manager)
                    db.flush()
                
                # Clean company name and ISIN
                company_name = clean_text_for_database(pos_data['company_name'])
                isin = str(pos_data['isin']).strip()
                
                # Skip if invalid data
                if not company_name or company_name == "Unknown" or not isin or isin == 'nan':
                    continue
                
                # Get or create company
                company = db.query(Company).filter(Company.isin == isin).first()
                if not company:
                    company = Company(
                        name=company_name,
                        isin=isin,
                        country_id=belgium.id
                    )
                    db.add(company)
                    db.flush()
                
                # Create short position
                position = ShortPosition(
                    manager_id=manager.id,
                    company_id=company.id,
                    country_id=belgium.id,
                    position_size=pos_data['position_size'],
                    date=pos_data['date']
                )
                
                db.add(position)
                added_count += 1
                
                if added_count % 100 == 0:
                    print(f"   Added {added_count} positions...")
                    # Commit periodically to avoid transaction issues
                    db.commit()
                
            except Exception as e:
                logger.warning(f"Error processing position: {e}")
                errors += 1
                # Rollback and continue
                try:
                    db.rollback()
                except:
                    pass
                continue
        
        # Final commit
        db.commit()
        
        # Get total count
        total_positions = db.query(ShortPosition).filter(ShortPosition.country_id == belgium.id).count()
        
        print(f"\n🎉 Belgium data update completed!")
        print(f"✅ Added {added_count} new positions")
        print(f"⚠️ Errors: {errors}")
        print(f"📊 Total Belgium positions in database: {total_positions:,}")
        
        if errors == 0:
            print("🎯 Perfect! No errors!")
        else:
            print(f"⚠️ {errors} positions had issues (skipped)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db' in locals():
            try:
                db.rollback()
            except:
                pass
            db.close()

if __name__ == "__main__":
    update_belgium_data()
