#!/usr/bin/env python3
"""
Check countries in database
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from sqlalchemy import create_engine
import pandas as pd

def check_countries():
    """Check what countries are in the database"""
    try:
        # Database connection
        DATABASE_URL = "postgresql://jpdib@localhost:5432/shortselling"
        engine = create_engine(DATABASE_URL)
        
        # Query countries
        query = "SELECT * FROM countries ORDER BY name"
        df = pd.read_sql(query, engine)
        
        print("🌍 Countries in Database:")
        print("=" * 40)
        
        for idx, row in df.iterrows():
            print(f"{idx+1}. {row['name']} ({row['code']})")
        
        print(f"\n📊 Total countries: {len(df)}")
        
        # Check if Netherlands is missing
        netherlands = df[df['code'] == 'NL']
        if netherlands.empty:
            print("\n❌ Netherlands (NL) is NOT in the database!")
            print("   We need to create the Netherlands scraper and add the data.")
        else:
            print("\n✅ Netherlands (NL) is in the database!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_countries()

