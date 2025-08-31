#!/usr/bin/env python3
"""
Debug script to test import process step by step
"""

import pandas as pd
import os
import sys
from pathlib import Path
import time

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from app.core.config import settings

def test_uk_import_step_by_step():
    """Test UK import step by step to find the issue"""
    print("🔍 Debugging UK Import Process")
    print("=" * 50)
    
    filepath = Path("C:/shortselling.eu/excel_files/United Kingdom/short-positions-daily-update.xlsx")
    
    if not filepath.exists():
        print("❌ UK file not found")
        return
    
    try:
        # Step 1: Read Excel file
        print("📄 Step 1: Reading Excel file...")
        start_time = time.time()
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names
        print(f"✅ Excel file read in {time.time() - start_time:.2f}s")
        print(f"📋 Found tabs: {sheet_names}")
        
        # Step 2: Read first tab
        print(f"\n📄 Step 2: Reading first tab '{sheet_names[0]}'...")
        start_time = time.time()
        df = pd.read_excel(filepath, sheet_name=sheet_names[0])
        print(f"✅ Tab read in {time.time() - start_time:.2f}s")
        print(f"📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Step 3: Test database connection
        print(f"\n🗄️ Step 3: Testing database connection...")
        start_time = time.time()
        db = next(get_db())
        print(f"✅ Database connection in {time.time() - start_time:.2f}s")
        
        # Step 4: Test first row processing
        print(f"\n🔧 Step 4: Testing first row processing...")
        start_time = time.time()
        
        first_row = df.iloc[0]
        print(f"📋 First row data:")
        print(f"   Manager: {first_row['Position Holder']}")
        print(f"   Company: {first_row['Name of Share Issuer']}")
        print(f"   ISIN: {first_row['ISIN']}")
        print(f"   Position: {first_row['Net Short Position (%)']}%")
        print(f"   Date: {first_row['Position Date']}")
        
        # Test manager creation
        print(f"\n👤 Testing manager creation...")
        manager_name = str(first_row['Position Holder']).strip()
        manager = db.query(Manager).filter(Manager.name == manager_name).first()
        if not manager:
            print(f"   Creating new manager: {manager_name}")
            manager = Manager(name=manager_name)
            db.add(manager)
            db.flush()
            print(f"   ✅ Manager created with ID: {manager.id}")
        else:
            print(f"   ✅ Manager found with ID: {manager.id}")
        
        # Test company creation
        print(f"\n🏢 Testing company creation...")
        company_name = str(first_row['Name of Share Issuer']).strip()
        isin = str(first_row['ISIN']).strip()
        
        # Get country first
        country = db.query(Country).filter(Country.code == 'GB').first()
        if not country:
            print(f"   ❌ Country GB not found, creating it...")
            country = Country(
                code='GB',
                name='United Kingdom',
                flag='GB',
                priority='high',
                url='https://www.fca.org.uk/markets/short-selling/notification-disclosure-net-short-positions'
            )
            db.add(country)
            db.flush()
            print(f"   ✅ Country created with ID: {country.id}")
        
        company = db.query(Company).filter(Company.isin == isin).first()
        if not company:
            company = db.query(Company).filter(
                Company.name == company_name,
                Company.country_id == country.id
            ).first()
        
        if not company:
            print(f"   Creating new company: {company_name}")
            company = Company(
                name=company_name,
                isin=isin,
                country_id=country.id
            )
            db.add(company)
            db.flush()
            print(f"   ✅ Company created with ID: {company.id}")
        else:
            print(f"   ✅ Company found with ID: {company.id}")
        
        # Test position creation
        print(f"\n📊 Testing position creation...")
        position_size = float(first_row['Net Short Position (%)'])
        position_date = pd.to_datetime(first_row['Position Date']).date()
        
        position = ShortPosition(
            date=position_date,
            position_size=position_size,
            is_active=position_size >= 0.5,
            company_id=company.id,
            manager_id=manager.id,
            country_id=country.id
        )
        db.add(position)
        db.commit()
        print(f"   ✅ Position created with ID: {position.id}")
        
        total_time = time.time() - start_time
        print(f"\n✅ First row processed in {total_time:.2f}s")
        
        # Step 5: Test processing multiple rows
        print(f"\n🔄 Step 5: Testing multiple rows...")
        start_time = time.time()
        
        processed_count = 0
        for idx, row in df.head(5).iterrows():
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
                manager = db.query(Manager).filter(Manager.name == manager_name).first()
                if not manager:
                    manager = Manager(name=manager_name)
                    db.add(manager)
                    db.flush()
                
                # Get or create company
                company = db.query(Company).filter(Company.isin == isin).first()
                if not company:
                    # Get country first
                    country = db.query(Country).filter(Country.code == 'GB').first()
                    if country:
                        company = db.query(Company).filter(
                            Company.name == company_name,
                            Company.country_id == country.id
                        ).first()
                    if not company:
                        # Get country first
                        country = db.query(Country).filter(Country.code == 'GB').first()
                        if country:
                            company = Company(
                                name=company_name,
                                isin=isin,
                                country_id=country.id
                            )
                        db.add(company)
                        db.flush()
                
                # Create position
                position = ShortPosition(
                    date=position_date,
                    position_size=position_size,
                    is_active=position_size >= 0.5,
                    company_id=company.id,
                    manager_id=manager.id,
                    country_id=country.id
                )
                db.add(position)
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing row {idx}: {e}")
                break
        
        db.commit()
        total_time = time.time() - start_time
        print(f"✅ Processed {processed_count} rows in {total_time:.2f}s")
        print(f"📊 Average time per row: {total_time/processed_count:.3f}s")
        
        # Estimate total time
        total_rows = len(df)
        estimated_time = (total_time/processed_count) * total_rows
        print(f"⏱️ Estimated time for {total_rows} rows: {estimated_time/60:.1f} minutes")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    print("🔍 ShortSelling.eu - Import Debug Tool")
    print("=" * 50)
    
    test_uk_import_step_by_step()
    
    print(f"\n{'='*50}")
    print("✅ Debug complete!")

if __name__ == "__main__":
    main()
