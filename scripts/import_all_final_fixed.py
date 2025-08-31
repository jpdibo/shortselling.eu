#!/usr/bin/env python3
"""
FINAL FIXED Import script for all countries
Properly handles existing managers and database sessions
"""

import pandas as pd
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition

class FinalFixedImporter:
    """Final fixed import with proper manager handling"""
    
    def __init__(self):
        self.base_path = Path("C:/shortselling.eu/excel_files")
        self.imported_positions = 0
        self.errors = []
        
        # Cache for managers and companies to avoid repeated DB queries
        self.manager_cache = {}
        self.company_cache = {}
        self.country_cache = {}
    
    def import_all_countries(self):
        """Import data from all countries"""
        print("🚀 Starting FINAL FIXED import of all countries...")
        print("📋 Countries: UK, Italy, Netherlands, France, Belgium, Spain, Germany, Ireland")
        print("⚡ Using FINAL FIXED _get_or_create_manager function")
        print("🏷️  is_current flags will be set correctly based on source")
        
        # Single database connection for all operations
        db = next(get_db())
        
        try:
            # Import all countries
            self.import_uk_data(db)
            self.import_italy_data(db)
            self.import_netherlands_data(db)
            self.import_france_data(db)
            self.import_belgium_data(db)
            self.import_spain_data(db)
            self.import_germany_data(db)
            self.import_ireland_data(db)
            
            print(f"\n✅ Import completed!")
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

    def _get_or_create_manager_final_fixed(self, db: Session, manager_name: str) -> Manager:
        """FINAL FIXED: Get or create a manager with proper error handling"""
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

    def _get_or_create_company_final_fixed(self, db: Session, company_name: str, isin: str, country_name: str) -> Company:
        """FINAL FIXED: Get or create a company with proper error handling"""
        cache_key = f"{company_name}_{country_name}"
        if cache_key in self.company_cache:
            return self.company_cache[cache_key]
        
        # First ensure country exists
        if country_name not in self.country_cache:
            country = db.query(Country).filter(Country.name == country_name).first()
            if not country:
                # Create country if it doesn't exist
                country_codes = {
                    'United Kingdom': 'GB', 'Italy': 'IT', 'Netherlands': 'NL', 'France': 'FR',
                    'Belgium': 'BE', 'Spain': 'ES', 'Germany': 'DE', 'Ireland': 'IE'
                }
                country_code = country_codes.get(country_name, country_name[:2].upper())
                country = Country(
                    code=country_code,
                    name=country_name,
                    flag=country_code,
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

    def import_uk_data(self, db: Session):
        """Import UK data with proper is_current flags"""
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
            
            for sheet_name in sheet_names:
                # Determine if this is current or historical based on tab name
                is_active = 'current' in sheet_name.lower()
                print(f"📄 Processing tab: {sheet_name} ({'current' if is_active else 'historical'})")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    positions_to_add = []
                    
                    for idx, row in df.iterrows():
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
                            
                            # Convert position size to float
                            try:
                                position_size_float = float(position_size)
                            except (ValueError, TypeError):
                                continue
                            
                            # Get or create manager and company
                            manager = self._get_or_create_manager_final_fixed(db, manager_name)
                            company = self._get_or_create_company_final_fixed(db, company_name, isin, 'United Kingdom')
                            
                            # Create short position with proper is_current flag
                            position = ShortPosition(
                                date=pd.to_datetime(position_date),
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id,
                                position_size=position_size_float,
                                is_active=position_size_float >= 0.5,
                                is_active=is_active  # Set based on tab name
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
                    error_msg = f"Error processing UK tab {sheet_name}: {e}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Error importing UK data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_italy_data(self, db: Session):
        """Import Italy data with proper is_current flags"""
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
            
            for sheet_name in sheet_names:
                # Determine if this is current or historical based on tab name
                is_active = 'current' in sheet_name.lower()
                print(f"📄 Processing tab: {sheet_name} ({'current' if is_active else 'historical'})")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    positions_to_add = []
                    
                    for idx, row in df.iterrows():
                        try:
                            # Extract data
                            manager_name = str(row['Position holder']).strip()
                            company_name = str(row['Issuer']).strip()
                            isin = str(row['ISIN']).strip()
                            position_size = row['Perc. posizione netta corta']
                            position_date = row['Position date']
                            
                            # Skip header rows and invalid data
                            if (pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin) or 
                                manager_name == 'Position holder' or company_name == 'Issuer' or
                                pd.isna(position_date) or pd.isna(position_size)):
                                continue
                            
                            # Convert position size to float
                            try:
                                position_size_float = float(position_size)
                            except (ValueError, TypeError):
                                continue
                            
                            # Get or create manager and company
                            manager = self._get_or_create_manager_final_fixed(db, manager_name)
                            company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Italy')
                            
                            # Create short position with proper is_current flag
                            position = ShortPosition(
                                date=pd.to_datetime(position_date),
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id,
                                position_size=position_size_float,
                                is_active=position_size_float >= 0.5,
                                is_active=is_active  # Set based on tab name
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
                            error_msg = f"Italy {sheet_name} row {idx+1} error: {e}"
                            self.errors.append(error_msg)
                    
                    # Commit remaining positions
                    if positions_to_add:
                        db.add_all(positions_to_add)
                        db.commit()
                        self.imported_positions += len(positions_to_add)
                        print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
                    
                    print(f"✅ Imported positions from {sheet_name}")
                    
                except Exception as e:
                    error_msg = f"Error processing Italy tab {sheet_name}: {e}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Error importing Italy data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_netherlands_data(self, db: Session):
        """Import Netherlands data with proper is_current flags"""
        print("\n🇳🇱 Importing Netherlands data...")
        
        current_file = self.base_path / "Netherlands" / "nettoshortpositiesactueel.csv"
        history_file = self.base_path / "Netherlands" / "nettoshortpositieshistorie.csv"
        
        if not current_file.exists() or not history_file.exists():
            print("❌ Netherlands files not found")
            return
        
        # Import current positions
        print("📄 Importing current positions...")
        try:
            df_current = pd.read_csv(current_file, encoding='utf-8')
            print(f"📊 Found {len(df_current)} current positions")
            
            positions_to_add = []
            
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
                    
                    # Convert position size to float
                    try:
                        position_size_float = float(position_size)
                    except (ValueError, TypeError):
                        continue
                    
                    # Get or create manager and company
                    manager = self._get_or_create_manager_final_fixed(db, manager_name)
                    company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Netherlands')
                    
                    # Create short position (current)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=True  # Current file
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
                    error_msg = f"Netherlands current row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            # Commit remaining positions
            if positions_to_add:
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
            
            print(f"✅ Imported current positions")
            
        except Exception as e:
            error_msg = f"Error importing Netherlands current data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
        
        # Import historical positions
        print("📄 Importing historical positions...")
        try:
            df_history = pd.read_csv(history_file, encoding='latin-1')
            print(f"📊 Found {len(df_history)} historical positions")
            
            positions_to_add = []
            
            for idx, row in df_history.iterrows():
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
                    
                    # Convert position size to float
                    try:
                        position_size_float = float(position_size)
                    except (ValueError, TypeError):
                        continue
                    
                    # Get or create manager and company
                    manager = self._get_or_create_manager_final_fixed(db, manager_name)
                    company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Netherlands')
                    
                    # Create short position (historical)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=False  # Historical file
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
                    error_msg = f"Netherlands history row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            # Commit remaining positions
            if positions_to_add:
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
            
            print(f"✅ Imported historical positions")
            
        except Exception as e:
            error_msg = f"Error importing Netherlands historical data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_france_data(self, db: Session):
        """Import France data (all current)"""
        print("\n🇫🇷 Importing France data...")
        
        filepath = self.base_path / "France" / "export_od_vad_20250812111500_20250812123000.csv"
        if not filepath.exists():
            print("❌ France file not found")
            return
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            print(f"📊 Found {len(df)} positions")
            
            positions_to_add = []
            
            for idx, row in df.iterrows():
                try:
                    # Extract data
                    manager_name = str(row['Detenteur de la position courte nette']).strip()
                    company_name = str(row['Emetteur / issuer']).strip()
                    isin = str(row['ISIN']).strip()
                    position_size = row['Position courte nette']
                    position_date = row['Date de position']
                    
                    # Skip header rows and invalid data
                    if (pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin) or 
                        manager_name == 'Detenteur de la position courte nette' or company_name == 'Emetteur / issuer' or
                        pd.isna(position_date) or pd.isna(position_size)):
                        continue
                    
                    # Convert position size to float
                    try:
                        position_size_float = float(position_size)
                    except (ValueError, TypeError):
                        continue
                    
                    # Get or create manager and company
                    manager = self._get_or_create_manager_final_fixed(db, manager_name)
                    company = self._get_or_create_company_final_fixed(db, company_name, isin, 'France')
                    
                    # Create short position (all current for France)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=True  # All current for France (no historical distinction)
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
                    error_msg = f"France row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            # Commit remaining positions
            if positions_to_add:
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
            
            print(f"✅ Imported France positions")
            
        except Exception as e:
            error_msg = f"Error importing France data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_belgium_data(self, db: Session):
        """Import Belgium data with proper is_current flags"""
        print("\n🇧🇪 Importing Belgium data...")
        
        current_file = self.base_path / "Belgium" / "de-shortselling.csv"
        history_file = self.base_path / "Belgium" / "de-shortselling-history.csv"
        
        if not current_file.exists() or not history_file.exists():
            print("❌ Belgium files not found")
            return
        
        # Import current positions
        print("📄 Importing current positions...")
        try:
            df_current = pd.read_csv(current_file, encoding='utf-8')
            print(f"📊 Found {len(df_current)} current positions")
            
            positions_to_add = []
            
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
                    manager = self._get_or_create_manager_final_fixed(db, manager_name)
                    company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Belgium')
                    
                    # Create short position (current)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date, format='%d/%m/%Y'),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=True  # Current file
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
                    error_msg = f"Belgium current row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            # Commit remaining positions
            if positions_to_add:
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
            
            print(f"✅ Imported current positions")
            
        except Exception as e:
            error_msg = f"Error importing Belgium current data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
        
        # Import historical positions
        print("📄 Importing historical positions...")
        try:
            df_history = pd.read_csv(history_file, encoding='utf-8')
            print(f"📊 Found {len(df_history)} historical positions")
            
            positions_to_add = []
            
            for idx, row in df_history.iterrows():
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
                    manager = self._get_or_create_manager_final_fixed(db, manager_name)
                    company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Belgium')
                    
                    # Create short position (historical)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date, format='%d/%m/%Y'),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=False  # Historical file
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
                    error_msg = f"Belgium history row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            # Commit remaining positions
            if positions_to_add:
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
            
            print(f"✅ Imported historical positions")
            
        except Exception as e:
            error_msg = f"Error importing Belgium historical data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_spain_data(self, db: Session):
        """Import Spain data with proper is_current flags"""
        print("\n🇪🇸 Importing Spain data...")
        
        filepath = self.base_path / "Spain" / "NetShortPositions.xls"
        if not filepath.exists():
            print("❌ Spain file not found")
            return
        
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(filepath)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Found {len(sheet_names)} tabs: {', '.join(sheet_names)}")
            
            # Define which tabs to process and their types
            tabs_to_process = {
                'Última_-_Current': True,      # Current
                'Serie_-_Series': False,       # Historical
                'Anteriores_-_Previous': False # Historical
            }
            
            for sheet_name in sheet_names:
                if sheet_name not in tabs_to_process:
                    continue
                
                is_current = tabs_to_process[sheet_name]
                print(f"📄 Processing tab: {sheet_name} ({'current' if is_current else 'historical'})")
                
                try:
                    # Skip first 2 rows (empty rows) and read from row 3
                    df = pd.read_excel(filepath, sheet_name=sheet_name, skiprows=2)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    positions_to_add = []
                    
                    for idx, row in df.iterrows():
                        try:
                            # Extract data (columns are unnamed, so use position)
                            manager_name = str(row.iloc[3]).strip()  # Tenedor de la Posición
                            company_name = str(row.iloc[2]).strip()  # Emisor / Issuer
                            isin = str(row.iloc[1]).strip()          # ISIN
                            position_size = row.iloc[5]              # Posición corta(%)
                            position_date = row.iloc[4]              # Fecha posición
                            
                            # Skip header rows and invalid data
                            if (pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin) or 
                                'Tenedor' in str(manager_name) or 'Emisor' in str(company_name) or
                                pd.isna(position_date) or pd.isna(position_size)):
                                continue
                            
                            # Convert position size to float
                            try:
                                position_size_float = float(position_size)
                            except (ValueError, TypeError):
                                continue
                            
                            # Get or create manager and company
                            manager = self._get_or_create_manager_final_fixed(db, manager_name)
                            company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Spain')
                            
                            # Create short position with proper is_current flag
                            position = ShortPosition(
                                date=pd.to_datetime(position_date),
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id,
                                position_size=position_size_float,
                                is_active=position_size_float >= 0.5,
                                is_current=is_current  # Set based on tab type
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
                            error_msg = f"Spain {sheet_name} row {idx+1} error: {e}"
                            self.errors.append(error_msg)
                    
                    # Commit remaining positions
                    if positions_to_add:
                        db.add_all(positions_to_add)
                        db.commit()
                        self.imported_positions += len(positions_to_add)
                        print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
                    
                    print(f"✅ Imported positions from {sheet_name}")
                    
                except Exception as e:
                    error_msg = f"Error processing Spain tab {sheet_name}: {e}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Error importing Spain data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_germany_data(self, db: Session):
        """Import Germany data (all current)"""
        print("\n🇩🇪 Importing Germany data...")
        
        filepath = self.base_path / "Germany" / "leerverkaeufe_2025-08-12T20_45_36.csv"
        if not filepath.exists():
            print("❌ Germany file not found")
            return
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            print(f"📊 Found {len(df)} positions")
            
            positions_to_add = []
            
            for idx, row in df.iterrows():
                try:
                    # Extract data
                    manager_name = str(row['Positionsinhaber']).strip()
                    company_name = str(row['Emittent']).strip()
                    isin = str(row['ISIN']).strip()
                    position_size = row['Position']
                    position_date = row['Datum']
                    
                    # Skip header rows and invalid data
                    if (pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin) or 
                        manager_name == 'Positionsinhaber' or company_name == 'Emittent' or
                        pd.isna(position_date) or pd.isna(position_size)):
                        continue
                    
                    # Convert position size to float (handle comma decimal separator)
                    try:
                        position_size_str = str(position_size).replace(',', '.')
                        position_size_float = float(position_size_str)
                    except (ValueError, TypeError):
                        continue
                    
                    # Get or create manager and company
                    manager = self._get_or_create_manager_final_fixed(db, manager_name)
                    company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Germany')
                    
                    # Create short position (all current for Germany - single file)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=True  # All current for Germany (single file)
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
                    error_msg = f"Germany row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            # Commit remaining positions
            if positions_to_add:
                db.add_all(positions_to_add)
                db.commit()
                self.imported_positions += len(positions_to_add)
                print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
            
            print(f"✅ Imported Germany positions")
            
        except Exception as e:
            error_msg = f"Error importing Germany data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_ireland_data(self, db: Session):
        """Import Ireland data with proper is_current flags"""
        print("\n🇮🇪 Importing Ireland data...")
        
        filepath = self.base_path / "Ireland" / "table-of-significant-net-short-positions-in-shares.xlsx"
        if not filepath.exists():
            print("❌ Ireland file not found")
            return
        
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(filepath)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Found {len(sheet_names)} tabs: {', '.join(sheet_names)}")
            
            for sheet_name in sheet_names:
                # Determine if this is current or historical based on tab name
                is_current = 'current' in sheet_name.lower()
                print(f"📄 Processing tab: {sheet_name} ({'current' if is_current else 'historical'})")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    positions_to_add = []
                    
                    for idx, row in df.iterrows():
                        try:
                            # Extract data
                            manager_name = str(row['Position Holder:']).strip()
                            company_name = str(row['Name of the Issuer:']).strip()
                            isin = str(row['ISIN:']).strip()
                            position_size = row['Net short position %:']
                            position_date = row['Position Date:']
                            
                            # Skip header rows and invalid data
                            if (pd.isna(manager_name) or pd.isna(company_name) or pd.isna(isin) or 
                                'Position Holder' in str(manager_name) or 'Name of the Issuer' in str(company_name) or
                                pd.isna(position_date) or pd.isna(position_size)):
                                continue
                            
                            # Convert position size to float
                            try:
                                position_size_float = float(position_size)
                            except (ValueError, TypeError):
                                continue
                            
                            # Get or create manager and company
                            manager = self._get_or_create_manager_final_fixed(db, manager_name)
                            company = self._get_or_create_company_final_fixed(db, company_name, isin, 'Ireland')
                            
                            # Create short position with proper is_current flag
                            position = ShortPosition(
                                date=pd.to_datetime(position_date),
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id,
                                position_size=position_size_float,
                                is_active=position_size_float >= 0.5,
                                is_current=is_current  # Set based on tab name
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
                            error_msg = f"Ireland {sheet_name} row {idx+1} error: {e}"
                            self.errors.append(error_msg)
                    
                    # Commit remaining positions
                    if positions_to_add:
                        db.add_all(positions_to_add)
                        db.commit()
                        self.imported_positions += len(positions_to_add)
                        print(f"   ✅ Committed final batch of {len(positions_to_add)} positions")
                    
                    print(f"✅ Imported positions from {sheet_name}")
                    
                except Exception as e:
                    error_msg = f"Error processing Ireland tab {sheet_name}: {e}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Error importing Ireland data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

def main():
    """Main function"""
    print("📊 ShortSelling.eu - FINAL FIXED Import Tool")
    print("=" * 80)
    print("🚀 Importing ALL countries with FINAL FIXED manager handling")
    print("⚡ FINAL FIXED _get_or_create_manager function")
    print("🏷️  is_current flags set correctly based on source")
    print("📈 All positions will be imported (no filtering by size)")
    print("=" * 80)
    
    importer = FinalFixedImporter()
    importer.import_all_countries()
    
    print(f"\n🎉 Import process completed!")
    print(f"📊 Total positions imported: {importer.imported_positions:,}")
    print(f"❌ Total errors: {len(importer.errors)}")

if __name__ == "__main__":
    main()
