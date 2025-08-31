#!/usr/bin/env python3
"""
TEST - Import ONLY Belgium data with aggressive optimizations
To identify and fix the performance bottleneck
"""

import pandas as pd
import sys
import os
from datetime import datetime
from pathlib import Path
import time

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition

class BelgiumTestImporter:
    """Test import of Belgium only with aggressive optimizations"""
    
    def __init__(self):
        self.base_path = Path("C:/shortselling.eu/excel_files")
        self.imported_positions = 0
        self.errors = []
        self.batch_size = 5000  # Much larger batch size
        
        # Cache for managers and companies to avoid repeated DB queries
        self.manager_cache = {}
        self.company_cache = {}
        self.country_cache = {}
    
    def test_belgium_only(self):
        """Test import of Belgium data only"""
        print("🧪 TESTING Belgium import only...")
        print(f"⚡ Using batch size: {self.batch_size}")
        print(f"📁 Base path: {self.base_path}")
        
        # Single database connection for all operations
        db = next(get_db())
        
        try:
            # Test Belgium only
            self.import_belgium_test(db)
            
            print(f"\n✅ Test completed!")
            print(f"📊 Total positions imported: {self.imported_positions:,}")
            print(f"❌ Total errors: {len(self.errors)}")
            
            if self.errors:
                print(f"\n🔍 Errors encountered:")
                for error in self.errors[:5]:  # Show first 5 errors
                    print(f"   - {error}")
                    
        finally:
            db.close()

    def _get_or_create_manager_test(self, db: Session, manager_name: str) -> Manager:
        """Get or create a manager with caching"""
        if manager_name in self.manager_cache:
            return self.manager_cache[manager_name]
        
        manager = db.query(Manager).filter(Manager.name == manager_name).first()
        if not manager:
            # Create slug from manager name
            slug = manager_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
            manager = Manager(name=manager_name, slug=slug)
            db.add(manager)
            db.flush()  # Get the ID
        
        self.manager_cache[manager_name] = manager
        return manager

    def _get_or_create_company_test(self, db: Session, company_name: str, isin: str, country_name: str) -> Company:
        """Get or create a company with caching"""
        cache_key = f"{company_name}_{country_name}"
        if cache_key in self.company_cache:
            return self.company_cache[cache_key]
        
        # First ensure country exists
        if country_name not in self.country_cache:
            country = db.query(Country).filter(Country.name == country_name).first()
            if not country:
                # Create country if it doesn't exist
                country = Country(
                    code='BE',
                    name=country_name,
                    flag='BE',
                    priority="high",
                    url=""
                )
                db.add(country)
                db.flush()
            self.country_cache[country_name] = country
        
        country = self.country_cache[country_name]
        
        # Look for company by name and country
        company = db.query(Company).filter(
            Company.name == company_name,
            Company.country_id == country.id
        ).first()
        
        if not company:
            company = Company(
                name=company_name,
                isin=isin if pd.notna(isin) else None,
                country_id=country.id
            )
            db.add(company)
            db.flush()
        
        self.company_cache[cache_key] = company
        return company

    def import_belgium_test(self, db: Session):
        """Import Belgium data with aggressive optimizations"""
        print("\n🇧🇪 Testing Belgium import...")
        
        current_file = self.base_path / "Belgium" / "de-shortselling.csv"
        history_file = self.base_path / "Belgium" / "de-shortselling-history.csv"
        
        if not current_file.exists():
            print(f"❌ Current file not found: {current_file}")
            return
        if not history_file.exists():
            print(f"❌ History file not found: {history_file}")
            return
        
        print(f"✅ Found files:")
        print(f"   📄 Current: {current_file}")
        print(f"   📄 History: {history_file}")
        
        # Test current positions first
        print("\n📄 Testing current positions...")
        start_time = time.time()
        
        try:
            df_current = pd.read_csv(current_file, encoding='utf-8')
            print(f"📊 Found {len(df_current)} current positions")
            print(f"📋 Columns: {list(df_current.columns)}")
            
            # Show first few rows
            print(f"🔍 First 3 rows:")
            for i in range(min(3, len(df_current))):
                row = df_current.iloc[i]
                print(f"   Row {i+1}: {dict(row)}")
            
            positions_to_add = []
            processed_count = 0
            
            for idx, row in df_current.iterrows():
                try:
                    # Extract data
                    manager_name = str(row['Position holder']).strip()
                    company_name = str(row['Issuer']).strip()
                    isin = str(row['ISIN']).strip()
                    position_size = row['Net short position']
                    position_date = row['Position date']
                    
                    # Skip header rows and invalid data
                    if (pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin) or 
                        manager_name == 'Position holder' or company_name == 'Issuer' or
                        pd.isna(position_date) or pd.isna(position_size)):
                        continue
                    
                    # Convert position size to float (handle comma decimal separator)
                    try:
                        position_size_str = str(position_size).replace(',', '.')
                        position_size_float = float(position_size_str)
                    except (ValueError, TypeError):
                        continue
                    
                    # Get or create manager and company
                    manager = self._get_or_create_manager_test(db, manager_name)
                    company = self._get_or_create_company_test(db, company_name, isin, 'Belgium')
                    
                    # Create short position (current)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date, format='%d/%m/%Y'),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=True
                    )
                    
                    positions_to_add.append(position)
                    processed_count += 1
                    
                    # Progress update every 100 rows
                    if processed_count % 100 == 0:
                        elapsed = time.time() - start_time
                        print(f"   ⏱️  Processed {processed_count} rows in {elapsed:.1f}s")
                    
                    # Batch commit
                    if len(positions_to_add) >= self.batch_size:
                        print(f"   💾 Committing batch of {len(positions_to_add)} positions...")
                        db.add_all(positions_to_add)
                        db.commit()
                        self.imported_positions += len(positions_to_add)
                        print(f"   ✅ Committed batch successfully")
                        positions_to_add = []
                    
                except Exception as e:
                    error_msg = f"Belgium current row {idx+1} error: {e}"
                    self.errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
                    if len(self.errors) >= 10:  # Stop after 10 errors
                        print("   ⚠️  Stopping due to too many errors")
                        break
            
            # Commit remaining positions
            if positions_to_add:
                print(f"   💾 Committing final batch of {len(positions_to_add)} positions...")
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch successfully")
            
            elapsed = time.time() - start_time
            print(f"✅ Current positions completed in {elapsed:.1f}s")
            print(f"📊 Processed: {processed_count} rows")
            print(f"📊 Imported: {self.imported_positions} positions")
            
        except Exception as e:
            error_msg = f"Error importing Belgium current data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    print("🧪 ShortSelling.eu - Belgium Import Test")
    print("=" * 80)
    print("🧪 Testing Belgium import only with aggressive optimizations")
    print("⚡ Large batch sizes and detailed progress tracking")
    print("🔍 Detailed error reporting")
    print("=" * 80)
    
    importer = BelgiumTestImporter()
    importer.test_belgium_only()
    
    print(f"\n🎉 Test completed!")
    print(f"📊 Total positions imported: {importer.imported_positions:,}")
    print(f"❌ Total errors: {len(importer.errors)}")

if __name__ == "__main__":
    main()
