#!/usr/bin/env python3
"""
Database initialization script for ShortSelling.eu
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, init_db
from app.db.models import Country
from app.core.config import settings


def init_countries():
    """Initialize countries in the database"""
    db = SessionLocal()
    
    try:
        # Check if countries already exist
        existing_countries = db.query(Country).count()
        if existing_countries > 0:
            print("Countries already exist in database. Skipping initialization.")
            return
        
        # Add countries from settings
        for country_data in settings.countries:
            country = Country(
                code=country_data['code'],
                name=country_data['name'],
                flag=country_data['flag'],
                priority=country_data['priority'],
                url=country_data['url'],
                is_active=True
            )
            db.add(country)
        
        db.commit()
        print(f"Successfully initialized {len(settings.countries)} countries")
        
    except Exception as e:
        print(f"Error initializing countries: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("Initializing ShortSelling.eu database...")
    
    # Create tables
    print("Creating database tables...")
    init_db()
    
    # Initialize countries
    print("Initializing countries...")
    init_countries()
    
    print("Database initialization complete!")


if __name__ == "__main__":
    main()
