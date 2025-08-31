#!/usr/bin/env python3
"""
Add France as a new country to the database
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.db.database import get_db
from app.db.models import Country

def add_france():
    """Add France as a new country"""
    print("🇫🇷 Adding France to database...")
    
    try:
        db = next(get_db())
        
        # Check existing countries
        existing_countries = db.query(Country).all()
        existing_codes = [c.code for c in existing_countries]
        
        print(f"Current countries: {existing_codes}")
        
        # Add France if not exists
        if 'FR' not in existing_codes:
            france = Country(
                code='FR',
                name='France',
                flag='FR',
                priority='high',
                url='https://www.data.gouv.fr/datasets/historique-des-positions-courtes-nettes-sur-actions-rendues-publiques-depuis-le-1er-novembre-2012/',
                is_active=True
            )
            db.add(france)
            print("✅ Added France")
        else:
            print("⚠️ France already exists")
        
        # Commit changes
        db.commit()
        
        # Verify
        updated_countries = db.query(Country).all()
        print(f"\n📊 Updated countries: {[c.code for c in updated_countries]}")
        
        db.close()
        print("🎉 France added successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    add_france()
