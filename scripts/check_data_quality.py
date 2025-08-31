#!/usr/bin/env python3
"""
Check data quality of imported short positions
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition

def check_data_quality():
    """Analyze the quality of imported data"""
    print("🔍 Checking data quality...")
    
    db = next(get_db())
    
    # Basic counts
    total_positions = db.query(ShortPosition).count()
    total_companies = db.query(Company).count()
    total_managers = db.query(Manager).count()
    total_countries = db.query(Country).count()
    
    print(f"\n📊 Database Summary:")
    print(f"   Total Positions: {total_positions:,}")
    print(f"   Total Companies: {total_companies:,}")
    print(f"   Total Managers: {total_managers:,}")
    print(f"   Total Countries: {total_countries}")
    
    # Check for potential issues
    print(f"\n🔍 Data Quality Checks:")
    
    # 1. Check for positions with missing data
    missing_company = db.query(ShortPosition).filter(ShortPosition.company_id.is_(None)).count()
    missing_manager = db.query(ShortPosition).filter(ShortPosition.manager_id.is_(None)).count()
    missing_date = db.query(ShortPosition).filter(ShortPosition.date.is_(None)).count()
    
    print(f"   Positions with missing company: {missing_company}")
    print(f"   Positions with missing manager: {missing_manager}")
    print(f"   Positions with missing date: {missing_date}")
    
    # 2. Check for extreme position sizes
    very_large = db.query(ShortPosition).filter(ShortPosition.position_size > 100).count()
    negative = db.query(ShortPosition).filter(ShortPosition.position_size < 0).count()
    
    print(f"   Positions > 100%: {very_large}")
    print(f"   Negative positions: {negative}")
    
    # 3. Check date ranges
    earliest = db.query(ShortPosition.date).order_by(ShortPosition.date.asc()).first()
    latest = db.query(ShortPosition.date).order_by(ShortPosition.date.desc()).first()
    
    if earliest and latest:
        print(f"   Date range: {earliest[0]} to {latest[0]}")
    
    # 4. Check for duplicate positions (same company, manager, date, size)
    duplicates = db.query(ShortPosition).group_by(
        ShortPosition.company_id,
        ShortPosition.manager_id,
        ShortPosition.date,
        ShortPosition.position_size
    ).having(func.count(ShortPosition.id) > 1).count()
    
    print(f"   Potential duplicates: {duplicates}")
    
    # 5. Check active vs historical positions
    active = db.query(ShortPosition).filter(ShortPosition.is_active == True).count()
    historical = db.query(ShortPosition).filter(ShortPosition.is_active == False).count()
    
    print(f"   Active positions (≥0.5%): {active:,}")
    print(f"   Historical positions (<0.5%): {historical:,}")
    
    # 6. Check by country
    print(f"\n📈 Positions by Country:")
    countries = db.query(Country).all()
    for country in countries:
        count = db.query(ShortPosition).filter(ShortPosition.country_id == country.id).count()
        active_count = db.query(ShortPosition).filter(
            ShortPosition.country_id == country.id,
            ShortPosition.is_active == True
        ).count()
        print(f"   {country.name}: {count:,} total ({active_count:,} active)")
    
    # 7. Check for companies with many positions
    print(f"\n🏢 Top Companies by Position Count:")
    top_companies = db.query(Company, func.count(ShortPosition.id).label('count')).join(ShortPosition).group_by(Company.id).order_by(func.count(ShortPosition.id).desc()).limit(10).all()
    
    for company, count in top_companies:
        country = db.query(Country).filter(Country.id == company.country_id).first()
        print(f"   {company.name} ({country.code}): {count:,} positions")
    
    # 8. Check for managers with many positions
    print(f"\n👥 Top Managers by Position Count:")
    top_managers = db.query(Manager, func.count(ShortPosition.id).label('count')).join(ShortPosition).group_by(Manager.id).order_by(func.count(ShortPosition.id).desc()).limit(10).all()
    
    for manager, count in top_managers:
        print(f"   {manager.name}: {count:,} positions")
    
    print(f"\n✅ Data quality check completed!")

if __name__ == "__main__":
    check_data_quality()
