#!/usr/bin/env python3
"""
Import Excel data from all countries into the database - CORRECTED VERSION
Handles all tabs and imports ALL positions
"""

import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelImporter:
    """Import Excel data from different countries"""
    
    def __init__(self):
        self.base_path = Path("C:/shortselling.eu/excel_files")
        self.imported_count = 0
        self.errors = []
    
    async def import_all_countries(self):
        """Import data from all available countries"""
        print("🚀 Starting Excel data import...")
        
        # Import each country
        await self.import_uk_data()
        await self.import_italy_data()
        await self.import_netherlands_data()
        await self.import_france_data()
        
        print(f"\n✅ Import completed!")
        print(f"📊 Total positions imported: {self.imported_count}")
        if self.errors:
            print(f"❌ Errors encountered: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
    
    async def import_uk_data(self):
        """Import UK data from both current and historic tabs"""
        print("\n🇬🇧 Importing UK data...")
        
        filepath = self.base_path / "United Kingdom" / "short-positions-daily-update.xlsx"
        if not filepath.exists():
            print("❌ UK file not found")
            return
        
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(filepath)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Found {len(sheet_names)} tabs: {', '.join(sheet_names)}")
            
            db = next(get_db())
            
            for sheet_name in sheet_names:
                print(f"📄 Processing tab: {sheet_name}")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} positions in tab '{sheet_name}'")
                    
                    for _, row in df.iterrows():
                        try:
                            # Extract data
                            manager_name = str(row['Position Holder']).strip()
                            company_name = str(row['Name of Share Issuer']).strip()
                            isin = str(row['ISIN']).strip()
                            position_size = float(row['Net Short Position (%)'])
                            position_date = pd.to_datetime(row['Position Date']).date()
                            
                            # Skip empty rows
                            if pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin):
                                continue
                            
                            # Get or create manager
                            manager = self._get_or_create_manager(db, manager_name)
                            
                            # Get or create company
                            company = self._get_or_create_company(db, company_name, isin, 'GB')
                            
                            # Create position - IMPORT ALL POSITIONS (no filtering by size)
                            position = ShortPosition(
                                date=position_date,
                                position_size=position_size,
                                is_active=position_size >= 0.5,  # This is for analytics, not filtering
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id
                            )
                            
                            db.add(position)
                            self.imported_count += 1
                            
                        except Exception as e:
                            self.errors.append(f"UK {sheet_name} row error: {e}")
                            continue
                    
                    print(f"✅ Tab '{sheet_name}': Processed {len(df)} positions")
                    
                except Exception as e:
                    print(f"❌ Error processing tab {sheet_name}: {e}")
                    self.errors.append(f"UK tab {sheet_name} error: {e}")
            
            db.commit()
            print(f"✅ UK: Total imported {self.imported_count} positions")
            
        except Exception as e:
            print(f"❌ Error importing UK data: {e}")
            self.errors.append(f"UK import error: {e}")
    
    async def import_italy_data(self):
        """Import Italy data from both current and historic tabs"""
        print("\n🇮🇹 Importing Italy data...")
        
        filepath = self.base_path / "Italy" / "PncPubbl.xlsx"
        if not filepath.exists():
            print("❌ Italy file not found")
            return
        
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(filepath)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Found {len(sheet_names)} tabs: {', '.join(sheet_names)}")
            
            db = next(get_db())
            
            for sheet_name in sheet_names:
                # Skip the publication date tab
                if "Pubb" in sheet_name:
                    print(f"⏭️  Skipping tab: {sheet_name} (publication info)")
                    continue
                
                print(f"📄 Processing tab: {sheet_name}")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} positions in tab '{sheet_name}'")
                    
                    for _, row in df.iterrows():
                        try:
                            # Extract data
                            manager_name = str(row['Detentore']).strip()
                            company_name = str(row['Emittente']).strip()
                            isin = str(row['ISIN']).strip()
                            position_size = float(row['Perc. posizione netta corta'])
                            position_date = pd.to_datetime(row['Data della posizione']).date()
                            
                            # Skip empty rows
                            if pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin):
                                continue
                            
                            # Get or create manager
                            manager = self._get_or_create_manager(db, manager_name)
                            
                            # Get or create company
                            company = self._get_or_create_company(db, company_name, isin, 'IT')
                            
                            # Create position - IMPORT ALL POSITIONS (no filtering by size)
                            position = ShortPosition(
                                date=position_date,
                                position_size=position_size,
                                is_active=position_size >= 0.5,  # This is for analytics, not filtering
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id
                            )
                            
                            db.add(position)
                            self.imported_count += 1
                            
                        except Exception as e:
                            self.errors.append(f"Italy {sheet_name} row error: {e}")
                            continue
                    
                    print(f"✅ Tab '{sheet_name}': Processed {len(df)} positions")
                    
                except Exception as e:
                    print(f"❌ Error processing tab {sheet_name}: {e}")
                    self.errors.append(f"Italy tab {sheet_name} error: {e}")
            
            db.commit()
            print(f"✅ Italy: Total imported {self.imported_count} positions")
            
        except Exception as e:
            print(f"❌ Error importing Italy data: {e}")
            self.errors.append(f"Italy import error: {e}")
    
    async def import_netherlands_data(self):
        """Import Netherlands data from both current and historic files"""
        print("\n🇳🇱 Importing Netherlands data...")
        
        current_file = self.base_path / "Netherlands" / "nettoshortpositiesactueel.csv"
        history_file = self.base_path / "Netherlands" / "nettoshortpositieshistorie.csv"
        
        if not current_file.exists() or not history_file.exists():
            print("❌ Netherlands files not found")
            return
        
        try:
            db = next(get_db())
            
            # Process current positions
            print(f"📄 Processing current positions...")
            df_current = pd.read_csv(current_file, sep=';', encoding='utf-8')
            print(f"📊 Found {len(df_current)} current positions")
            
            for _, row in df_current.iterrows():
                try:
                    # Extract data
                    manager_name = str(row['Position holder']).strip()
                    company_name = str(row['Name of the issuer']).strip()
                    isin = str(row['ISIN']).strip()
                    position_size = float(row['Net short position'])
                    position_date = pd.to_datetime(row['Position date']).date()
                    
                    # Skip empty rows
                    if pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin):
                        continue
                    
                    # Get or create manager
                    manager = self._get_or_create_manager(db, manager_name)
                    
                    # Get or create company
                    company = self._get_or_create_company(db, company_name, isin, 'NL')
                    
                    # Create position - IMPORT ALL POSITIONS (no filtering by size)
                    position = ShortPosition(
                        date=position_date,
                        position_size=position_size,
                        is_active=position_size >= 0.5,  # This is for analytics, not filtering
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id
                    )
                    
                    db.add(position)
                    self.imported_count += 1
                    
                except Exception as e:
                    self.errors.append(f"Netherlands current row error: {e}")
                    continue
            
            print(f"✅ Current positions: Processed {len(df_current)} positions")
            
            # Process historical positions with proper encoding
            print(f"📄 Processing historical positions...")
            try:
                # Try different encodings for the history file
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        df_history = pd.read_csv(history_file, sep=';', encoding=encoding)
                        print(f"✅ Successfully read history file with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print("❌ Could not read history file with any encoding")
                    return
                
                print(f"📊 Found {len(df_history)} historical positions")
                
                for _, row in df_history.iterrows():
                    try:
                        # Extract data
                        manager_name = str(row['Position holder']).strip()
                        company_name = str(row['Name of the issuer']).strip()
                        isin = str(row['ISIN']).strip()
                        position_size = float(row['Net short position'])
                        position_date = pd.to_datetime(row['Position date']).date()
                        
                        # Skip empty rows
                        if pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin):
                            continue
                        
                        # Get or create manager
                        manager = self._get_or_create_manager(db, manager_name)
                        
                        # Get or create company
                        company = self._get_or_create_company(db, company_name, isin, 'NL')
                        
                        # Create position - IMPORT ALL POSITIONS (no filtering by size)
                        position = ShortPosition(
                            date=position_date,
                            position_size=position_size,
                            is_active=position_size >= 0.5,  # This is for analytics, not filtering
                            company_id=company.id,
                            manager_id=manager.id,
                            country_id=company.country_id
                        )
                        
                        db.add(position)
                        self.imported_count += 1
                        
                    except Exception as e:
                        self.errors.append(f"Netherlands history row error: {e}")
                        continue
                
                print(f"✅ Historical positions: Processed {len(df_history)} positions")
                
            except Exception as e:
                print(f"❌ Error processing historical data: {e}")
                self.errors.append(f"Netherlands history error: {e}")
            
            db.commit()
            print(f"✅ Netherlands: Total imported {self.imported_count} positions")
            
        except Exception as e:
            print(f"❌ Error importing Netherlands data: {e}")
            self.errors.append(f"Netherlands import error: {e}")
    
    async def import_france_data(self):
        """Import France data"""
        print("\n🇫🇷 Importing France data...")
        
        filepath = self.base_path / "France" / "export_od_vad_20250812111500_20250812123000.csv"
        if not filepath.exists():
            print("❌ France file not found")
            return
        
        try:
            df = pd.read_csv(filepath, sep=';', encoding='utf-8')
            print(f"📊 Found {len(df)} positions in France file")
            
            db = next(get_db())
            
            for _, row in df.iterrows():
                try:
                    # Extract data
                    manager_name = str(row['Detenteur de la position courte nette']).strip()
                    company_name = str(row['Emetteur / issuer']).strip()
                    isin = str(row['code ISIN']).strip()
                    position_size = float(row['Ratio'])
                    position_date = pd.to_datetime(row['Date de debut de publication position']).date()
                    
                    # Skip empty rows
                    if pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin):
                        continue
                    
                    # Get or create manager
                    manager = self._get_or_create_manager(db, manager_name)
                    
                    # Get or create company
                    company = self._get_or_create_company(db, company_name, isin, 'FR')
                    
                    # Create position - IMPORT ALL POSITIONS (no filtering by size)
                    position = ShortPosition(
                        date=position_date,
                        position_size=position_size,
                        is_active=position_size >= 0.5,  # This is for analytics, not filtering
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id
                    )
                    
                    db.add(position)
                    self.imported_count += 1
                    
                except Exception as e:
                    self.errors.append(f"France row error: {e}")
                    continue
            
            db.commit()
            print(f"✅ France: Total imported {self.imported_count} positions")
            
        except Exception as e:
            print(f"❌ Error importing France data: {e}")
            self.errors.append(f"France import error: {e}")
    
    def _get_or_create_manager(self, db: Session, name: str) -> Manager:
        """Get or create a manager"""
        # Clean the name
        name = name.strip()
        
        # Check if manager exists
        manager = db.query(Manager).filter(Manager.name == name).first()
        if manager:
            return manager
        
        # Create new manager
        manager = Manager(name=name)
        db.add(manager)
        db.flush()  # Get the ID
        return manager
    
    def _get_or_create_company(self, db: Session, name: str, isin: str, country_code: str) -> Company:
        """Get or create a company"""
        # Clean the data
        name = name.strip()
        isin = isin.strip() if isin else None
        
        # Get country first
        country = db.query(Country).filter(Country.code == country_code).first()
        if not country:
            # Create country if it doesn't exist
            country = Country(
                code=country_code,
                name=self._get_country_name(country_code),
                flag=country_code,
                priority='high',
                url=''
            )
            db.add(country)
            db.flush()
        
        # Check if company exists by ISIN first
        if isin:
            company = db.query(Company).filter(Company.isin == isin).first()
            if company:
                return company
        
        # Check by name and country
        company = db.query(Company).filter(
            Company.name == name,
            Company.country_id == country.id
        ).first()
        if company:
            return company
        
        # Create new company
        company = Company(
            name=name,
            isin=isin,
            country_id=country.id
        )
        db.add(company)
        db.flush()  # Get the ID
        return company
    
    def _get_country_name(self, country_code: str) -> str:
        """Get country name from code"""
        country_names = {
            'GB': 'United Kingdom',
            'IT': 'Italy',
            'NL': 'Netherlands',
            'FR': 'France',
            'DE': 'Germany',
            'ES': 'Spain',
            'DK': 'Denmark',
            'NO': 'Norway',
            'SE': 'Sweden',
            'FI': 'Finland',
            'BE': 'Belgium',
            'IE': 'Ireland',
            'PL': 'Poland',
            'AT': 'Austria',
            'GR': 'Greece',
            'PT': 'Portugal',
            'LU': 'Luxembourg'
        }
        return country_names.get(country_code, country_code)

def check_conda_env():
    """Check if we're in the correct conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'short_selling':
        print("❌ Error: Please activate the 'short_selling' conda environment first:")
        print("   conda activate short_selling")
        return False
    print(f"✅ Using conda environment: {conda_env}")
    return True

async def main():
    """Main function"""
    print("📊 ShortSelling.eu - Excel Data Import Tool (CORRECTED)")
    print("=" * 60)
    print("✅ Will import ALL positions from ALL tabs")
    print("✅ No filtering by position size")
    print("=" * 60)
    
    # Check conda environment
    if not check_conda_env():
        sys.exit(1)
    
    # Create importer and run import
    importer = ExcelImporter()
    await importer.import_all_countries()
    
    print(f"\n🎉 Import process completed!")
    print(f"📈 Total positions imported: {importer.imported_count}")

if __name__ == "__main__":
    asyncio.run(main())
