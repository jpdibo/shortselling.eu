#!/usr/bin/env python3
"""
Diagnose Belgium files and database connection
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition

def diagnose_belgium():
    """Diagnose Belgium files and database"""
    print("🔍 Diagnosing Belgium files and database...")
    
    base_path = Path("C:/shortselling.eu/excel_files")
    current_file = base_path / "Belgium" / "de-shortselling.csv"
    history_file = base_path / "Belgium" / "de-shortselling-history.csv"
    
    # Check files
    print(f"\n📁 File check:")
    print(f"   Current file exists: {current_file.exists()}")
    print(f"   History file exists: {history_file.exists()}")
    
    if current_file.exists():
        print(f"   Current file size: {current_file.stat().st_size / 1024:.1f} KB")
        try:
            df = pd.read_csv(current_file, encoding='utf-8')
            print(f"   Current file rows: {len(df)}")
            print(f"   Current file columns: {list(df.columns)}")
            print(f"   First row: {dict(df.iloc[0])}")
        except Exception as e:
            print(f"   ❌ Error reading current file: {e}")
    
    if history_file.exists():
        print(f"   History file size: {history_file.stat().st_size / 1024:.1f} KB")
        try:
            df = pd.read_csv(history_file, encoding='utf-8')
            print(f"   History file rows: {len(df)}")
            print(f"   History file columns: {list(df.columns)}")
            print(f"   First row: {dict(df.iloc[0])}")
        except Exception as e:
            print(f"   ❌ Error reading history file: {e}")
    
    # Check database connection
    print(f"\n🗄️ Database check:")
    try:
        db = next(get_db())
        print("   ✅ Database connection successful")
        
        # Check existing data
        country_count = db.query(Country).count()
        company_count = db.query(Company).count()
        manager_count = db.query(Manager).count()
        position_count = db.query(ShortPosition).count()
        
        print(f"   Countries in DB: {country_count}")
        print(f"   Companies in DB: {company_count}")
        print(f"   Managers in DB: {manager_count}")
        print(f"   Positions in DB: {position_count}")
        
        # Check if Belgium exists
        belgium = db.query(Country).filter(Country.name == 'Belgium').first()
        if belgium:
            print(f"   ✅ Belgium country exists in DB (ID: {belgium.id})")
        else:
            print(f"   ❌ Belgium country not found in DB")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_belgium()
