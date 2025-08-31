#!/usr/bin/env python3
"""
Add Netherlands and Italy as new countries to the database
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from app.db.database import get_db
from app.db.models import Country

def add_netherlands_italy():
    """Add Netherlands and Italy as new countries"""
    print("🌍 Adding Netherlands and Italy to database...")
    
    try:
        db = next(get_db())
        
        # Check existing countries
        existing_countries = db.query(Country).all()
        existing_codes = [c.code for c in existing_countries]
        
        print(f"Current countries: {existing_codes}")
        
        # Add Netherlands if not exists
        if 'NL' not in existing_codes:
            netherlands = Country(
                code='NL',
                name='Netherlands',
                flag='NL',
                priority='high',
                url='https://www.afm.nl/en/sector/registers/meldingenregisters/netto-shortposities-historie',
                is_active=True
            )
            db.add(netherlands)
            print("✅ Added Netherlands")
        else:
            print("⚠️ Netherlands already exists")
        
        # Add Italy if not exists
        if 'IT' not in existing_codes:
            italy = Country(
                code='IT',
                name='Italy',
                flag='IT',
                priority='high',
                url='https://www.consob.it/web/site-en/short-selling',
                is_active=True
            )
            db.add(italy)
            print("✅ Added Italy")
        else:
            print("⚠️ Italy already exists")
        
        # Commit changes
        db.commit()
        
        # Verify
        updated_countries = db.query(Country).all()
        print(f"\n📊 Updated countries: {[c.code for c in updated_countries]}")
        
        db.close()
        print("🎉 Countries added successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    add_netherlands_italy()
