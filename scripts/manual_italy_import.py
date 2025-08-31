#!/usr/bin/env python3
"""
Manual Italy Data Import
Handles manual import of Italy CONSOB data files
"""
import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scrapers.italy_scraper import ItalyScraper
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from app.services.daily_scraping_service import DailyScrapingService

def import_manual_italy_file(file_path: str):
    """Import a manually downloaded Italy CONSOB file"""
    print("🇮🇹 Manual Italy Data Import")
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
        
        # Ask user if they want to import
        response = input(f"\n❓ Import {len(positions)} positions into database? (y/N): ")
        if response.lower() != 'y':
            print("❌ Import cancelled")
            return False
        
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
            
            for position_data in positions:
                try:
                    # Find or create company
                    company = db.query(Company).filter(
                        Company.name == position_data['company_name'],
                        Company.country_id == italy.id
                    ).first()
                    
                    if not company:
                        company = Company(
                            name=position_data['company_name'],
                            isin=position_data['isin'],
                            country_id=italy.id
                        )
                        db.add(company)
                        db.flush()  # Get the ID
                    
                    # Find or create manager
                    manager = db.query(Manager).filter(
                        Manager.name == position_data['manager_name']
                    ).first()
                    
                    if not manager:
                        # Generate slug from name
                        slug = position_data['manager_name'].lower().replace(' ', '-').replace('.', '').replace(',', '')
                        manager = Manager(
                            name=position_data['manager_name'],
                            slug=slug
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
                    
                except Exception as e:
                    print(f"⚠️  Error importing position: {e}")
                    skipped_count += 1
                    continue
            
            db.commit()
            
            print(f"\n✅ Import completed successfully!")
            print(f"   - Imported: {imported_count} positions")
            print(f"   - Skipped: {skipped_count} positions (duplicates/errors)")
            
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
    print("🇮🇹 Manual Italy Data Import Tool")
    print("=" * 50)
    print("This tool helps import manually downloaded CONSOB data files.")
    print("Since CONSOB uses bot protection, you need to:")
    print("1. Visit https://www.consob.it/web/consob-and-its-activities/short-selling")
    print("2. Manually download the Excel file")
    print("3. Use this script to import it")
    print("=" * 50)
    
    # Check if file path provided as argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Ask user for file path
        file_path = input("📁 Enter path to CONSOB Excel file: ").strip()
    
    if not file_path:
        print("❌ No file path provided")
        return
    
    # Remove quotes if present
    file_path = file_path.strip('"\'')
    
    success = import_manual_italy_file(file_path)
    
    if success:
        print("\n🎉 Italy data imported successfully!")
        print("You can now run daily updates to include Italy data.")
    else:
        print("\n❌ Import failed. Please check the file and try again.")

if __name__ == "__main__":
    main()
