#!/usr/bin/env python3
"""
Import ONLY the new countries (Belgium, Spain, Germany, Ireland)
Skip existing countries that are already in the database
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

class NewCountryImporter:
    """Import ONLY new countries (Belgium, Spain, Germany, Ireland)"""
    
    def __init__(self):
        self.base_path = Path("C:/shortselling.eu/excel_files")
        self.imported_positions = 0
        self.errors = []
    
    def import_new_countries_only(self):
        """Import data from ONLY the new countries"""
        print("🚀 Starting import of NEW countries only...")
        print("📋 Countries: Belgium, Spain, Germany, Ireland")
        print("⏭️  Skipping: UK, Italy, Netherlands, France (already imported)")
        
        # Import only new countries
        self.import_belgium_data()
        self.import_spain_data()
        self.import_germany_data()
        self.import_ireland_data()
        
        print(f"\n✅ Import completed!")
        print(f"📊 Total positions imported: {self.imported_positions:,}")
        print(f"❌ Total errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n🔍 Errors encountered:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")

    def _get_or_create_manager(self, db: Session, manager_name: str) -> Manager:
        """Get or create a manager"""
        manager = db.query(Manager).filter(Manager.name == manager_name).first()
        if not manager:
            # Create slug from manager name
            slug = manager_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
            manager = Manager(name=manager_name, slug=slug)
            db.add(manager)
            db.flush()  # Get the ID
        return manager

    def _get_or_create_company(self, db: Session, company_name: str, isin: str, country_name: str) -> Company:
        """Get or create a company"""
        # First ensure country exists
        country = db.query(Country).filter(Country.name == country_name).first()
        if not country:
            # Create country if it doesn't exist
            country_codes = {
                'Belgium': 'BE', 'Spain': 'ES', 'Germany': 'DE', 'Ireland': 'IE'
            }
            country_code = country_codes.get(country_name, country_name[:2].upper())
            country = Country(
                code=country_code,
                name=country_name,
                flag=country_code,  # Use country code instead of emoji to avoid encoding issues
                priority="high",
                url=""
            )
            db.add(country)
            db.flush()
        
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
        
        return company

    def import_belgium_data(self):
        """Import Belgium data from CSV files"""
        print("\n🇧🇪 Importing Belgium data...")
        
        current_file = self.base_path / "Belgium" / "de-shortselling.csv"
        history_file = self.base_path / "Belgium" / "de-shortselling-history.csv"
        
        if not current_file.exists() or not history_file.exists():
            print("❌ Belgium files not found")
            return
        
        db = next(get_db())
        
        # Import current positions
        print("📄 Importing current positions...")
        try:
            df_current = pd.read_csv(current_file, encoding='utf-8')
            print(f"📊 Found {len(df_current)} current positions")
            
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
                    manager = self._get_or_create_manager(db, manager_name)
                    company = self._get_or_create_company(db, company_name, isin, 'Belgium')
                    
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
                    
                    db.add(position)
                    self.imported_positions += 1
                    
                except Exception as e:
                    error_msg = f"Belgium current row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            db.commit()
            print(f"✅ Imported {len(df_current)} current positions")
            
        except Exception as e:
            error_msg = f"Error importing Belgium current data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
        
        # Import historical positions
        print("📄 Importing historical positions...")
        try:
            df_history = pd.read_csv(history_file, encoding='utf-8')
            print(f"📊 Found {len(df_history)} historical positions")
            
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
                    manager = self._get_or_create_manager(db, manager_name)
                    company = self._get_or_create_company(db, company_name, isin, 'Belgium')
                    
                    # Create short position (historical)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date, format='%d/%m/%Y'),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=False
                    )
                    
                    db.add(position)
                    self.imported_positions += 1
                    
                except Exception as e:
                    error_msg = f"Belgium history row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            db.commit()
            print(f"✅ Imported {len(df_history)} historical positions")
            
        except Exception as e:
            error_msg = f"Error importing Belgium historical data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_spain_data(self):
        """Import Spain data from Excel file with multiple tabs"""
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
            
            db = next(get_db())
            
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
                            manager = self._get_or_create_manager(db, manager_name)
                            company = self._get_or_create_company(db, company_name, isin, 'Spain')
                            
                            # Create short position
                            position = ShortPosition(
                                date=pd.to_datetime(position_date),
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id,
                                position_size=position_size_float,
                                is_active=position_size_float >= 0.5,
                                is_current=is_current
                            )
                            
                            db.add(position)
                            self.imported_positions += 1
                            
                        except Exception as e:
                            error_msg = f"Spain {sheet_name} row {idx+1} error: {e}"
                            self.errors.append(error_msg)
                    
                    db.commit()
                    print(f"✅ Imported positions from {sheet_name}")
                    
                except Exception as e:
                    error_msg = f"Error processing Spain tab {sheet_name}: {e}"
                    self.errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Error importing Spain data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_germany_data(self):
        """Import Germany data from CSV file"""
        print("\n🇩🇪 Importing Germany data...")
        
        filepath = self.base_path / "Germany" / "leerverkaeufe_2025-08-12T20_45_36.csv"
        if not filepath.exists():
            print("❌ Germany file not found")
            return
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            print(f"📊 Found {len(df)} positions")
            
            db = next(get_db())
            
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
                    manager = self._get_or_create_manager(db, manager_name)
                    company = self._get_or_create_company(db, company_name, isin, 'Germany')
                    
                    # Create short position (all current for Germany - single file)
                    position = ShortPosition(
                        date=pd.to_datetime(position_date),
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=company.country_id,
                        position_size=position_size_float,
                        is_active=position_size_float >= 0.5,
                        is_current=True
                    )
                    
                    db.add(position)
                    self.imported_positions += 1
                    
                except Exception as e:
                    error_msg = f"Germany row {idx+1} error: {e}"
                    self.errors.append(error_msg)
            
            db.commit()
            print(f"✅ Imported {len(df)} positions")
            
        except Exception as e:
            error_msg = f"Error importing Germany data: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    def import_ireland_data(self):
        """Import Ireland data from Excel file with multiple tabs"""
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
            
            db = next(get_db())
            
            for sheet_name in sheet_names:
                print(f"📄 Processing tab: {sheet_name}")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    # Determine if this is current or historical based on row count
                    is_current = len(df) < 100  # Current tab has fewer rows
                    
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
                            manager = self._get_or_create_manager(db, manager_name)
                            company = self._get_or_create_company(db, company_name, isin, 'Ireland')
                            
                            # Create short position
                            position = ShortPosition(
                                date=pd.to_datetime(position_date),
                                company_id=company.id,
                                manager_id=manager.id,
                                country_id=company.country_id,
                                position_size=position_size_float,
                                is_active=position_size_float >= 0.5,
                                is_current=is_current
                            )
                            
                            db.add(position)
                            self.imported_positions += 1
                            
                        except Exception as e:
                            error_msg = f"Ireland {sheet_name} row {idx+1} error: {e}"
                            self.errors.append(error_msg)
                    
                    db.commit()
                    print(f"✅ Imported {len(df)} positions from {sheet_name}")
                    
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
    print("📊 ShortSelling.eu - NEW Countries Import Tool")
    print("=" * 80)
    print("🚀 Importing ONLY new countries: Belgium, Spain, Germany, Ireland")
    print("⏭️  Skipping existing countries: UK, Italy, Netherlands, France")
    print("📈 All positions will be imported (no filtering by size)")
    print("🏷️  Current/Historical flags will be set based on source")
    print("=" * 80)
    
    importer = NewCountryImporter()
    importer.import_new_countries_only()
    
    print(f"\n🎉 Import process completed!")
    print(f"📊 Total positions imported: {importer.imported_positions:,}")
    print(f"❌ Total errors: {len(importer.errors)}")

if __name__ == "__main__":
    main()
