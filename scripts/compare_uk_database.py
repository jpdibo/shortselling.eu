#!/usr/bin/env python3
"""
Compare UK Excel data line by line with database to ensure no positions are missed
"""

import sys
import os
import pandas as pd
import requests
from datetime import datetime
import tempfile

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.db.models import ShortPosition, Country, Manager, Company
from sqlalchemy import func

def download_uk_excel_data():
    """Download UK Excel data and extract all positions"""
    url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    try:
        print(f"📥 Downloading UK data from: {url}")
        
        # Create session
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
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        try:
            # Read both sheets
            excel_file = pd.ExcelFile(temp_file_path)
            all_positions = []
            
            print(f"📊 Processing {len(excel_file.sheet_names)} sheets: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                print(f"   Processing sheet: {sheet_name}")
                
                # Read the sheet
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                print(f"     Rows: {len(df)}")
                
                # Determine if current or historical
                is_current = 'current' in sheet_name.lower()
                
                # Extract positions
                column_mapping = {
                    'manager': 'Position Holder',
                    'company': 'Name of Share Issuer',
                    'isin': 'ISIN',
                    'position_size': 'Net Short Position (%)',
                    'date': 'Position Date'
                }
                
                for idx, row in df.iterrows():
                    try:
                        # Skip header rows
                        if _is_header_row(row):
                            continue
                        
                        position = {
                            'manager_name': str(row[column_mapping['manager']]).strip(),
                            'company_name': str(row[column_mapping['company']]).strip(),
                            'isin': str(row[column_mapping['isin']]).strip() if pd.notna(row[column_mapping['isin']]) else None,
                            'position_size': float(row[column_mapping['position_size']]),
                            'date': pd.to_datetime(row[column_mapping['date']]),
                            'is_current': is_current,
                            'sheet_name': sheet_name,
                            'row_index': idx
                        }
                        
                        all_positions.append(position)
                        
                    except Exception as e:
                        print(f"     ⚠️  Error processing row {idx}: {e}")
                        continue
            
            print(f"✅ Extracted {len(all_positions)} positions from Excel")
            return all_positions
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error downloading UK data: {e}")
        return None

def get_database_uk_positions():
    """Get all UK positions from database"""
    try:
        db = next(get_db())
        
        # Get UK country
        uk_country = db.query(Country).filter(Country.code == 'GB').first()
        if not uk_country:
            print("❌ UK country not found in database")
            return []
        
        # Get all UK positions
        positions = db.query(ShortPosition).filter(ShortPosition.country_id == uk_country.id).all()
        
        db_positions = []
        for pos in positions:
            # Get manager and company names
            manager = db.query(Manager).filter(Manager.id == pos.manager_id).first()
            company = db.query(Company).filter(Company.id == pos.company_id).first()
            
            db_positions.append({
                'manager_name': manager.name if manager else 'Unknown',
                'company_name': company.name if company else 'Unknown',
                'isin': company.isin if company else None,
                'position_size': pos.position_size,
                'date': pos.date,
                'is_current': pos.is_current,
                'db_id': pos.id
            })
        
        print(f"✅ Found {len(db_positions)} positions in database")
        return db_positions
        
    except Exception as e:
        print(f"❌ Error getting database positions: {e}")
        return []
    finally:
        db.close()

def compare_positions(excel_positions, db_positions):
    """Compare Excel positions with database positions"""
    print(f"\n🔍 Comparing {len(excel_positions)} Excel positions with {len(db_positions)} database positions")
    
    # Create lookup keys for database positions
    db_lookup = {}
    for pos in db_positions:
        key = (
            pos['manager_name'].lower().strip(),
            pos['company_name'].lower().strip(),
            pos['date'].date(),
            pos['position_size'],
            pos['is_current']
        )
        db_lookup[key] = pos
    
    # Check each Excel position
    missing_positions = []
    matching_positions = []
    
    for excel_pos in excel_positions:
        key = (
            excel_pos['manager_name'].lower().strip(),
            excel_pos['company_name'].lower().strip(),
            excel_pos['date'].date(),
            excel_pos['position_size'],
            excel_pos['is_current']
        )
        
        if key in db_lookup:
            matching_positions.append(excel_pos)
        else:
            missing_positions.append(excel_pos)
    
    print(f"\n📊 Comparison Results:")
    print(f"   ✅ Matching positions: {len(matching_positions)}")
    print(f"   ❌ Missing positions: {len(missing_positions)}")
    
    if missing_positions:
        print(f"\n🔍 Missing positions (first 10):")
        for i, pos in enumerate(missing_positions[:10]):
            print(f"   {i+1}. {pos['manager_name']} - {pos['company_name']} - {pos['date'].strftime('%Y-%m-%d')} - {pos['position_size']}% - {'Current' if pos['is_current'] else 'Historical'}")
        
        # Group by date
        print(f"\n📅 Missing positions by date:")
        date_groups = {}
        for pos in missing_positions:
            date_str = pos['date'].strftime('%Y-%m-%d')
            if date_str not in date_groups:
                date_groups[date_str] = []
            date_groups[date_str].append(pos)
        
        for date_str in sorted(date_groups.keys(), reverse=True):
            count = len(date_groups[date_str])
            print(f"   {date_str}: {count} positions")
    
    return missing_positions, matching_positions

def _is_header_row(row) -> bool:
    """Check if row is a header row"""
    value = str(row.iloc[0]).lower()
    return 'position holder' in value or 'name of share issuer' in value

def main():
    """Main comparison function"""
    print("🔍 UK Database vs Excel Comparison")
    print("=" * 60)
    
    # Step 1: Download Excel data
    excel_positions = download_uk_excel_data()
    if excel_positions is None:
        return
    
    # Step 2: Get database positions
    db_positions = get_database_uk_positions()
    
    # Step 3: Compare positions
    missing_positions, matching_positions = compare_positions(excel_positions, db_positions)
    
    # Step 4: Summary
    print(f"\n📋 Summary:")
    print(f"   Excel positions: {len(excel_positions)}")
    print(f"   Database positions: {len(db_positions)}")
    print(f"   Matching: {len(matching_positions)}")
    print(f"   Missing: {len(missing_positions)}")
    
    if missing_positions:
        print(f"\n⚠️  ACTION NEEDED: {len(missing_positions)} positions need to be added to database!")
    else:
        print(f"\n✅ PERFECT MATCH: All Excel positions are already in database!")
    
    print(f"\n✅ Comparison complete!")

if __name__ == "__main__":
    main()
