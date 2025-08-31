#!/usr/bin/env python3
"""
Fixed Italy Data Import
Handles manual import of Italy CONSOB data files with proper duplicate handling
"""
import sys
import os
import pandas as pd
import re
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scrapers.italy_scraper import ItalyScraper
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text_for_database(text):
    """Clean text for database compatibility"""
    if not text: return ""
    try:
        text = str(text).strip()
        text = re.sub(r'[^\x00-\x7F]+', '', text) # Remove non-ASCII
        text = re.sub(r'[^\w\s\-\.&]', '', text) # Remove other problematic chars
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logger.warning(f"Error cleaning text '{text}': {e}")
        return "Unknown"

def create_safe_slug(text):
    """Create a safe slug for database"""
    try:
        clean_text = clean_text_for_database(text)
        slug = clean_text.lower()
        slug = re.sub(r'[^\w\-]', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        if not slug:
            slug = f"manager-{abs(hash(text)) % 1000000}"
        return slug
    except Exception as e:
        logger.warning(f"Error creating slug for '{text}': {e}")
        return f"manager-{abs(hash(text)) % 1000000}"

def import_italy_data_fixed(file_path: str):
    """Import Italy data with proper duplicate handling"""
    print("🇮🇹 Fixed Italy Data Import")
    print("=" * 50)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📁 Importing file: {file_path}")
    
    try:
        # Create a mock data structure that the scraper expects
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Create mock data structure
        mock_data = {
            'excel_content': file_content,
            'source_url': f'manual_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
        
        # Use the Italy scraper to parse the data
        italy_scraper = ItalyScraper('IT', 'Italy')
        
        print("📊 Parsing file...")
        dataframes = italy_scraper.parse_data(mock_data)
        
        print("🔍 Extracting positions...")
        positions = italy_scraper.extract_positions(dataframes)
        
        if not positions:
            print("❌ No positions found in file")
            return False
        
        print(f"✅ Found {len(positions)} positions")
        
        # Show sample data
        if positions:
            sample = positions[0]
            print(f"\n📋 Sample position:")
            print(f"   - Manager: {sample['manager_name']}")
            print(f"   - Company: {sample['company_name']}")
            print(f"   - ISIN: {sample['isin']}")
            print(f"   - Position Size: {sample['position_size']}%")
            print(f"   - Date: {sample['date']}")
            print(f"   - Current: {sample['is_current']}")
        
        # Import into database
        print("💾 Importing into database...")
        db = next(get_db())
        
        try:
            # Get Italy country
            italy = db.query(Country).filter(Country.code == 'IT').first()
            if not italy:
                print("❌ Italy country not found in database")
                return False
            
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            for i, position_data in enumerate(positions):
                try:
                    # Clean and validate data
                    company_name = clean_text_for_database(position_data['company_name'])
                    manager_name = clean_text_for_database(position_data['manager_name'])
                    isin = clean_text_for_database(position_data['isin'])
                    
                    if not company_name or not manager_name or not isin:
                        skipped_count += 1
                        continue
                    
                    # Find or create company
                    company = db.query(Company).filter(
                        Company.name == company_name,
                        Company.country_id == italy.id
                    ).first()
                    
                    if not company:
                        company = Company(
                            name=company_name,
                            isin=isin,
                            country_id=italy.id
                        )
                        db.add(company)
                        db.flush()  # Get the ID
                    
                    # Find or create manager with proper slug handling
                    manager_slug = create_safe_slug(manager_name)
                    manager = db.query(Manager).filter(Manager.slug == manager_slug).first()
                    
                    if not manager:
                        manager = Manager(
                            name=manager_name,
                            slug=manager_slug
                        )
                        db.add(manager)
                        db.flush()  # Get the ID
                    
                    # Check if position already exists
                    existing = db.query(ShortPosition).filter(
                        ShortPosition.date == position_data['date'],
                        ShortPosition.company_id == company.id,
                        ShortPosition.manager_id == manager.id,
                        ShortPosition.country_id == italy.id
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Create new position
                    position = ShortPosition(
                        date=position_data['date'],
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=italy.id,
                        position_size=position_data['position_size'],
                        is_active=position_data['position_size'] >= 0.5,
                        is_current=position_data['is_current']
                    )
                    
                    db.add(position)
                    imported_count += 1
                    
                    # Periodic commit to avoid large transactions
                    if imported_count % 100 == 0:
                        db.commit()
                        print(f"   ✅ Imported {imported_count} positions...")
                    
                except Exception as e:
                    error_count += 1
                    logger.warning(f"Error importing position {i}: {e}")
                    db.rollback()  # Rollback on error
                    continue
            
            # Final commit
            db.commit()
            
            print(f"\n✅ Import completed successfully!")
            print(f"   - Imported: {imported_count} positions")
            print(f"   - Skipped: {skipped_count} positions (duplicates)")
            print(f"   - Errors: {error_count} positions")
            
            # Show updated statistics
            total_positions = db.query(ShortPosition).filter(ShortPosition.country_id == italy.id).count()
            print(f"   - Total Italy positions in database: {total_positions:,}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Database error: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🇮🇹 Fixed Italy Data Import Tool")
    print("=" * 50)
    print("This tool imports CONSOB data files with proper duplicate handling.")
    print("=" * 50)
    
    # Check if file path provided as argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Use the default Italy file
        file_path = r"C:\shortselling.eu\excel_files\Italy\PncPubbl.xlsx"
    
    if not file_path:
        print("❌ No file path provided")
        return
    
    # Remove quotes if present
    file_path = file_path.strip('"\'')
    
    success = import_italy_data_fixed(file_path)
    
    if success:
        print("\n🎉 Italy data imported successfully!")
        print("You can now run daily updates to include Italy data.")
    else:
        print("\n❌ Import failed. Please check the file and try again.")

if __name__ == "__main__":
    main()
