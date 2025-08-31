#!/usr/bin/env python3
"""
Show clear summary of position types:
- Current vs Historical (based on source tab/file)
- Active vs Inactive (based on position size >= 0.5%)
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.db.models import ShortPosition

def show_position_summary():
    """Show clear summary of position types"""
    print("📊 ShortSelling.eu - Position Summary")
    print("=" * 80)
    print("🔍 Clear distinction between position types:")
    print("   📈 Current vs Historical: Based on source tab/file")
    print("   ✅ Active vs Inactive: Based on position size (≥0.5% vs <0.5%)")
    print("=" * 80)
    
    db = next(get_db())
    
    # Overall summary
    total_positions = db.query(ShortPosition).count()
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"   Total positions: {total_positions:,}")
    
    # Current vs Historical
    current_positions = db.query(ShortPosition).filter(ShortPosition.is_current == True).count()
    historical_positions = db.query(ShortPosition).filter(ShortPosition.is_current == False).count()
    
    print(f"\n📈 CURRENT vs HISTORICAL (by source):")
    print(f"   📈 Current positions: {current_positions:,} ({current_positions/total_positions*100:.1f}%)")
    print(f"   📚 Historical positions: {historical_positions:,} ({historical_positions/total_positions*100:.1f}%)")
    
    # Active vs Inactive
    active_positions = db.query(ShortPosition).filter(ShortPosition.is_active == True).count()
    inactive_positions = db.query(ShortPosition).filter(ShortPosition.is_active == False).count()
    
    print(f"\n✅ ACTIVE vs INACTIVE (by size):")
    print(f"   ✅ Active positions (≥0.5%): {active_positions:,} ({active_positions/total_positions*100:.1f}%)")
    print(f"   ⏸️  Inactive positions (<0.5%): {inactive_positions:,} ({inactive_positions/total_positions*100:.1f}%)")
    
    # Cross-tabulation
    print(f"\n🔍 CROSS-TABULATION:")
    current_active = db.query(ShortPosition).filter(
        ShortPosition.is_current == True,
        ShortPosition.is_active == True
    ).count()
    
    current_inactive = db.query(ShortPosition).filter(
        ShortPosition.is_current == True,
        ShortPosition.is_active == False
    ).count()
    
    historical_active = db.query(ShortPosition).filter(
        ShortPosition.is_current == False,
        ShortPosition.is_active == True
    ).count()
    
    historical_inactive = db.query(ShortPosition).filter(
        ShortPosition.is_current == False,
        ShortPosition.is_active == False
    ).count()
    
    print(f"   📈 Current + ✅ Active: {current_active:,}")
    print(f"   📈 Current + ⏸️  Inactive: {current_inactive:,}")
    print(f"   📚 Historical + ✅ Active: {historical_active:,}")
    print(f"   📚 Historical + ⏸️  Inactive: {historical_inactive:,}")
    
    # By country
    print(f"\n📈 BREAKDOWN BY COUNTRY:")
    countries_query = text("""
        SELECT 
            co.name,
            COUNT(*) as total,
            COUNT(CASE WHEN sp.is_current = TRUE THEN 1 END) as current,
            COUNT(CASE WHEN sp.is_current = FALSE THEN 1 END) as historical,
            COUNT(CASE WHEN sp.is_active = TRUE THEN 1 END) as active,
            COUNT(CASE WHEN sp.is_active = FALSE THEN 1 END) as inactive
        FROM short_positions sp
        JOIN companies c ON sp.company_id = c.id
        JOIN countries co ON c.country_id = co.id
        GROUP BY co.id, co.name
        ORDER BY co.name
    """)
    
    countries = db.execute(countries_query).fetchall()
    for country in countries:
        print(f"\n   🇺🇳 {country.name}:")
        print(f"      📊 Total: {country.total:,}")
        print(f"      📈 Current: {country.current:,} | 📚 Historical: {country.historical:,}")
        print(f"      ✅ Active: {country.active:,} | ⏸️  Inactive: {country.inactive:,}")
    
    # Sample data for verification
    print(f"\n🔍 SAMPLE DATA VERIFICATION:")
    
    # Sample current active positions
    print(f"\n   📈 Sample Current + ✅ Active positions:")
    sample_query = text("""
        SELECT 
            c.name as company_name,
            co.name as country_name,
            m.name as manager_name,
            sp.position_size
        FROM short_positions sp
        JOIN companies c ON sp.company_id = c.id
        JOIN countries co ON c.country_id = co.id
        JOIN managers m ON sp.manager_id = m.id
        WHERE sp.is_current = TRUE AND sp.is_active = TRUE
        LIMIT 3
    """)
    
    sample_current_active = db.execute(sample_query).fetchall()
    for row in sample_current_active:
        print(f"      - {row.company_name} ({row.country_name}): {row.manager_name} - {row.position_size}%")
    
    # Sample historical active positions
    print(f"\n   📚 Sample Historical + ✅ Active positions:")
    sample_query = text("""
        SELECT 
            c.name as company_name,
            co.name as country_name,
            m.name as manager_name,
            sp.position_size
        FROM short_positions sp
        JOIN companies c ON sp.company_id = c.id
        JOIN countries co ON c.country_id = co.id
        JOIN managers m ON sp.manager_id = m.id
        WHERE sp.is_current = FALSE AND sp.is_active = TRUE
        LIMIT 3
    """)
    
    sample_historical_active = db.execute(sample_query).fetchall()
    for row in sample_historical_active:
        print(f"      - {row.company_name} ({row.country_name}): {row.manager_name} - {row.position_size}%")
    
    print(f"\n✅ Position summary completed!")

if __name__ == "__main__":
    show_position_summary()
