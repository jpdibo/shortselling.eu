#!/usr/bin/env python3
"""
Test UK scraper with direct FCA data download
"""

import sys
import os
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.db.models import ShortPosition, Country
from sqlalchemy import func

def get_latest_uk_date():
    """Get the most recent date for UK positions in our database"""
    try:
        db = next(get_db())
        
        # Get UK country
        uk_country = db.query(Country).filter(Country.code == 'GB').first()
        if not uk_country:
            print("❌ UK country not found in database")
            return None
        
        # Get the most recent date for UK positions
        latest_date = db.query(func.max(ShortPosition.date))\
                       .filter(ShortPosition.country_id == uk_country.id)\
                       .scalar()
        
        if latest_date:
            print(f"✅ Latest UK date in database: {latest_date}")
            return latest_date
        else:
            print("⚠️  No UK positions found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error getting latest UK date: {e}")
        return None
    finally:
        db.close()

def download_uk_data():
    """Download UK FCA data directly"""
    url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    try:
        print(f"📥 Downloading UK data from: {url}")
        
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
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        temp_file = "temp_uk_data.xlsx"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Read the Excel file
        df = pd.read_excel(temp_file)
        
        # Clean up temp file
        os.remove(temp_file)
        
        print(f"✅ Downloaded successfully!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Show first few rows
        print(f"\n📊 First 3 rows:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ Error downloading UK data: {e}")
        return None

def analyze_uk_data(df):
    """Analyze the UK data structure"""
    print(f"\n🔍 Analyzing UK data structure...")
    
    # Check for date column
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    print(f"   Date columns found: {date_columns}")
    
    # Check for position holder/manager column
    manager_columns = [col for col in df.columns if any(word in col.lower() for word in ['holder', 'manager', 'position'])]
    print(f"   Manager columns found: {manager_columns}")
    
    # Check for issuer/company column
    company_columns = [col for col in df.columns if any(word in col.lower() for word in ['issuer', 'company', 'emitter'])]
    print(f"   Company columns found: {company_columns}")
    
    # Check for position size column
    size_columns = [col for col in df.columns if any(word in col.lower() for word in ['position', 'size', 'net', 'short'])]
    print(f"   Position size columns found: {size_columns}")
    
    # Check for ISIN column
    isin_columns = [col for col in df.columns if 'isin' in col.lower()]
    print(f"   ISIN columns found: {isin_columns}")
    
    return {
        'date_col': date_columns[0] if date_columns else None,
        'manager_col': manager_columns[0] if manager_columns else None,
        'company_col': company_columns[0] if company_columns else None,
        'size_col': size_columns[0] if size_columns else None,
        'isin_col': isin_columns[0] if isin_columns else None
    }

def filter_new_positions(df, column_mapping, latest_db_date):
    """Filter positions that are newer than our latest database date"""
    if not latest_db_date:
        print("⚠️  No latest date from database, will process all positions")
        return df
    
    date_col = column_mapping['date_col']
    if not date_col:
        print("❌ No date column found")
        return None
    
    # Convert date column to datetime
    df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Filter for dates after our latest database date
    new_positions = df[df['date_parsed'] > latest_db_date]
    
    print(f"📅 Date filtering results:")
    print(f"   Total positions in file: {len(df)}")
    print(f"   Positions after {latest_db_date}: {len(new_positions)}")
    print(f"   New positions to add: {len(new_positions)}")
    
    if len(new_positions) > 0:
        print(f"\n📊 Sample of new positions:")
        print(new_positions.head(3).to_string())
    
    return new_positions

def main():
    """Main test function"""
    print("🇬🇧 UK FCA Data Analysis")
    print("=" * 50)
    
    # Step 1: Get latest date from database
    latest_date = get_latest_uk_date()
    
    # Step 2: Download UK data
    df = download_uk_data()
    if df is None:
        return
    
    # Step 3: Analyze data structure
    column_mapping = analyze_uk_data(df)
    
    # Step 4: Filter new positions
    new_positions = filter_new_positions(df, column_mapping, latest_date)
    
    if new_positions is not None and len(new_positions) > 0:
        print(f"\n✅ Found {len(new_positions)} new UK positions to add!")
        print(f"   Date range: {new_positions['date_parsed'].min()} to {new_positions['date_parsed'].max()}")
    else:
        print(f"\nℹ️  No new UK positions found")

if __name__ == "__main__":
    main()
