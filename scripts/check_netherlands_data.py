#!/usr/bin/env python3
"""
Check Netherlands data in database
"""

import sys
import os
sys.path.append(r'C:\shortselling.eu')

from sqlalchemy import create_engine
import pandas as pd

def check_netherlands_data():
    """Check Netherlands data in database"""
    try:
        # Database connection
        DATABASE_URL = "postgresql://jpdib@localhost:5432/shortselling"
        engine = create_engine(DATABASE_URL)
        
        # Query Netherlands data
        query = """
        SELECT 
            c.name as country_name,
            COUNT(sp.id) as position_count,
            MIN(sp.date) as earliest_date,
            MAX(sp.date) as latest_date
        FROM countries c
        LEFT JOIN short_positions sp ON c.id = sp.country_id
        WHERE c.code = 'NL'
        GROUP BY c.id, c.name
        """
        
        df = pd.read_sql(query, engine)
        
        print("🇳🇱 Netherlands Data Check:")
        print("=" * 40)
        
        if not df.empty:
            row = df.iloc[0]
            print(f"Country: {row['country_name']}")
            print(f"Position Count: {row['position_count']:,}")
            
            if row['position_count'] > 0:
                print(f"Date Range: {row['earliest_date']} to {row['latest_date']}")
                print("✅ Netherlands has data!")
            else:
                print("❌ Netherlands has NO data (0 positions)")
                print("   We need to create the Netherlands scraper and import data.")
        else:
            print("❌ Netherlands not found in database")
        
        # Check all countries for comparison
        print(f"\n📊 All Countries Data Summary:")
        print("-" * 40)
        
        all_countries_query = """
        SELECT 
            c.name as country_name,
            c.code as country_code,
            COUNT(sp.id) as position_count,
            MIN(sp.date) as earliest_date,
            MAX(sp.date) as latest_date
        FROM countries c
        LEFT JOIN short_positions sp ON c.id = sp.country_id
        GROUP BY c.id, c.name, c.code
        ORDER BY position_count DESC
        """
        
        all_df = pd.read_sql(all_countries_query, engine)
        
        for idx, row in all_df.iterrows():
            status = "✅" if row['position_count'] > 0 else "❌"
            print(f"{status} {row['country_name']} ({row['country_code']}): {row['position_count']:,} positions")
            if row['position_count'] > 0:
                print(f"    Date range: {row['earliest_date']} to {row['latest_date']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_netherlands_data()

