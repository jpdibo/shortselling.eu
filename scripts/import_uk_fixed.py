#!/usr/bin/env python3
"""
FIXED UK Import Script - Uses correct column names
Imports ALL 97,115 positions from both Current and Historic sheets
"""

import sys
import os
import pandas as pd
import requests
import tempfile
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition

class FixedUKImporter:
    """Fixed UK importer with correct column names"""
    
    def __init__(self):
        self.url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
        self.imported_positions = 0
        self.errors = []
        
        # Cache for managers and companies to avoid repeated DB queries
        self.manager_cache = {}
        self.company_cache = {}
        self.country_cache = {}
    
    def download_uk_data(self):
        """Download UK Excel data directly from FCA"""
        try:
            print(f"📥 Downloading UK data from: {self.url}")
            
            # Create session with proper headers
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Download the file
            response = session.get(self.url, timeout=30)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            print(f"❌ Error downloading UK data: {e}")
            return None
    
    def import_uk_data(self):
        """Import UK data with correct column names"""
        print("🇬🇧 Starting FIXED UK import...")
        print("🔧 Using CORRECT column names:")
        print("   - 'Position Holder' (not 'Position holder')")
        print("   - 'Name of Share Issuer' (not 'Issuer')")
        print("   - 'Net Short Position (%)' (not 'Net short position')")
        
        # Download data
        excel_content = self.download_uk_data()
        if not excel_content:
            return
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(excel_content)
            temp_file_path = temp_file.name
        
        try:
            # Single database connection for all operations
            db = next(get_db())
            
            try:
                # Read both sheets
                excel_file = pd.ExcelFile(temp_file_path)
                sheet_names = excel_file.sheet_names
                
                print(f"📋 Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
                
                for sheet_name in sheet_names:
                    # Determine if this is current or historical based on sheet name
                    is_current = 'current' in sheet_name.lower()
                    print(f"\n📄 Processing sheet: {sheet_name} ({'current' if is_current else 'historical'})")
                    
                    try:
                        df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                        print(f"📊 Found {len(df)} rows in sheet '{sheet_name}'")
                        
                        # Use CORRECT column names
                        column_mapping = {
                            'manager': 'Position Holder',
                            'company': 'Name of Share Issuer',
                            'isin': 'ISIN',
                            'position_size': 'Net Short Position (%)',
                            'date': 'Position Date'
                        }
                        
                        positions_to_add = []
                        
                        for idx, row in df.iterrows():
                            try:
                                # Extract data using CORRECT column names
                                manager_name = str(row[column_mapping['manager']]).strip()
                                company_name = str(row[column_mapping['company']]).strip()
                                isin = str(row[column_mapping['isin']]).strip() if pd.notna(row[column_mapping['isin']]) else None
                                position_size = row[column_mapping['position_size']]
                                position_date = row[column_mapping['date']]
                                
                                # Skip header rows and invalid data
                                if (pd.isna(manager_name) or pd.isna(company_name) or 
                                    manager_name == 'Position Holder' or company_name == 'Name of Share Issuer' or
                                    pd.isna(position_date) or pd.isna(position_size)):
                                    continue
                                
                                # Convert position size to float
                                try:
                                    position_size_float = float(position_size)
                                except (ValueError, TypeError):
                                    continue
                                
                                # Get or create manager and company
                                manager = self._get_or_create_manager(db, manager_name)
                                company = self._get_or_create_company(db, company_name, isin, 'United Kingdom')
                                
                                # Create short position with proper is_current flag
                                position = ShortPosition(
                                    date=pd.to_datetime(position_date),
                                    company_id=company.id,
                                    manager_id=manager.id,
                                    country_id=company.country_id,
                                    position_size=position_size_float,
                                    is_active=position_size_float >= 0.5,
                                    is_current=is_current  # Set based on sheet name
                                )
                                
                                positions_to_add.append(position)
                                
                                # Batch commit every 1000 positions
                                if len(positions_to_add) >= 1000:
                                    db.add_all(positions_to_add)
                                    db.commit()
                                    self.imported_positions += len(positions_to_add)
                                    print(f"   ✅ Committed batch of {len(positions_to_add)} positions")
                                    positions_to_add = []
                                
                            except Exception as e:
                                error_msg = f"UK {sheet_name} row {idx+1} error: {e}"
                                self.errors.append(error_msg)
                        
                        # Commit remaining positions
                        if positions_to_add:
                            db.add_all(positions_to_add)
                            db.commit()
                            self.imported_positions += len(positions_to_add)
                            print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
                        
                        print(f"✅ Imported positions from {sheet_name}")
                        
                    except Exception as e:
                        error_msg = f"Error processing UK sheet {sheet_name}: {e}"
                        self.errors.append(error_msg)
                        print(f"❌ {error_msg}")
                
                print(f"\n✅ UK import completed!")
                print(f"📊 Total positions imported: {self.imported_positions:,}")
                print(f"❌ Total errors: {len(self.errors)}")
                
                if self.errors:
                    print(f"\n🔍 Errors encountered:")
                    for error in self.errors[:10]:  # Show first 10 errors
                        print(f"   - {error}")
                    if len(self.errors) > 10:
                        print(f"   ... and {len(self.errors) - 10} more errors")
                
            finally:
                db.close()
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def _get_or_create_manager(self, db: Session, manager_name: str) -> Manager:
        """Get or create a manager with proper error handling"""
        if manager_name in self.manager_cache:
            return self.manager_cache[manager_name]
        
        # First try to find existing manager by name
        manager = db.query(Manager).filter(Manager.name == manager_name).first()
        
        if not manager:
            # Create slug from manager name
            slug = manager_name.lower().replace(' ', '-').replace('.', '').replace(',', '').replace('&', '-and-')
            
            # Check if slug already exists
            existing_manager = db.query(Manager).filter(Manager.slug == slug).first()
            if existing_manager:
                # Use existing manager with same slug
                manager = existing_manager
            else:
                # Create new manager
                manager = Manager(name=manager_name, slug=slug)
                db.add(manager)
                db.flush()  # Get the ID
        
        self.manager_cache[manager_name] = manager
        return manager
    
    def _get_or_create_company(self, db: Session, company_name: str, isin: str, country_name: str) -> Company:
        """Get or create a company with proper error handling"""
        cache_key = f"{company_name}_{country_name}"
        if cache_key in self.company_cache:
            return self.company_cache[cache_key]
        
        # First ensure country exists
        if country_name not in self.country_cache:
            country = db.query(Country).filter(Country.name == country_name).first()
            if not country:
                print(f"❌ Country not found: {country_name}")
                return None
            self.country_cache[country_name] = country
        
        country = self.country_cache[country_name]
        
        # Try to find existing company by name and country
        company = db.query(Company).filter(
            Company.name == company_name,
            Company.country_id == country.id
        ).first()
        
        if not company:
            # Create new company
            company = Company(
                name=company_name,
                isin=isin,
                country_id=country.id
            )
            db.add(company)
            db.flush()  # Get the ID
        
        self.company_cache[cache_key] = company
        return company

def main():
    """Main function"""
    print("🚀 FIXED UK Import Script")
    print("=" * 60)
    print("🔧 This script uses CORRECT column names to import ALL UK data")
    print("📊 Expected: 97,115 total positions (353 current + 96,762 historical)")
    print("=" * 60)
    
    importer = FixedUKImporter()
    importer.import_uk_data()
    
    print(f"\n✅ Import complete!")

if __name__ == "__main__":
    main()
