#!/usr/bin/env python3
"""
Final fix for France data encoding issues
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from app.scrapers.france_scraper import FranceScraper
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

def reimport_france_data_final():
    """Re-import France data with final encoding fixes"""
    print("🇫🇷 Final France Data Import with Encoding Fixes")
    print("=" * 60)
    
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
        
        # Clear existing France data
        print("\n🗑️ Clearing existing France data...")
        existing_count = db.query(ShortPosition).filter(ShortPosition.country_id == france.id).count()
        print(f"   Found {existing_count} existing France positions")
        
        # Delete existing France positions
        db.query(ShortPosition).filter(ShortPosition.country_id == france.id).delete()
        db.commit()
        print("   ✅ Cleared existing France positions")
        
        # Add all positions with final encoding fixes
        print(f"\n📊 Adding {len(positions)} positions with final encoding fixes...")
        added_count = 0
        errors = 0
        
        for pos_data in positions:
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
        total_positions = db.query(ShortPosition).filter(ShortPosition.country_id == france.id).count()
        
        print(f"\n🎉 France data import completed!")
        print(f"✅ Added {added_count} positions")
        print(f"⚠️ Errors: {errors}")
        print(f"📊 Total France positions in database: {total_positions:,}")
        
        if errors == 0:
            print("🎯 Perfect! No encoding errors!")
        else:
            print(f"⚠️ {errors} positions had encoding issues (skipped)")
        
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
    reimport_france_data_final()
