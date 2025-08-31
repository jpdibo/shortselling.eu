#!/usr/bin/env python3
"""
Remove duplicate short positions from the database
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition

def remove_duplicates():
    """Remove duplicate short positions"""
    print("🧹 Removing duplicate short positions...")
    
    db = next(get_db())
    
    # Get initial count
    initial_count = db.query(ShortPosition).count()
    print(f"📊 Initial positions: {initial_count:,}")
    
    # Find duplicates using raw SQL for better performance
    print("🔍 Finding duplicates...")
    
    # Method 1: Find exact duplicates (same company, manager, date, size)
    duplicate_query = text("""
        SELECT company_id, manager_id, date, position_size, COUNT(*) as count
        FROM short_positions 
        GROUP BY company_id, manager_id, date, position_size 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicates = db.execute(duplicate_query).fetchall()
    
    if not duplicates:
        print("✅ No exact duplicates found!")
        return
    
    print(f"📋 Found {len(duplicates)} groups of duplicates:")
    total_duplicates = 0
    
    for dup in duplicates[:10]:  # Show first 10
        print(f"   - {dup.company_id}, {dup.manager_id}, {dup.date}, {dup.position_size}%: {dup.count} times")
        total_duplicates += dup.count - 1  # -1 because we keep one
    
    if len(duplicates) > 10:
        print(f"   ... and {len(duplicates) - 10} more duplicate groups")
    
    print(f"📊 Total duplicate positions to remove: {total_duplicates:,}")
    
    # Remove duplicates
    print("🗑️  Removing duplicates...")
    
    # Use a more efficient approach - keep the first occurrence of each duplicate group
    remove_query = text("""
        DELETE FROM short_positions 
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY company_id, manager_id, date, position_size 
                           ORDER BY id
                       ) as rn
                FROM short_positions
            ) t
            WHERE t.rn > 1
        )
    """)
    
    result = db.execute(remove_query)
    db.commit()
    
    # Get final count
    final_count = db.query(ShortPosition).count()
    removed_count = initial_count - final_count
    
    print(f"✅ Removed {removed_count:,} duplicate positions")
    print(f"📊 Final positions: {final_count:,}")
    print(f"📈 Reduction: {removed_count/initial_count*100:.1f}%")
    
    # Show breakdown by country
    print(f"\n📈 Positions by Country (after deduplication):")
    countries = db.query(Country).all()
    for country in countries:
        count = db.query(ShortPosition).filter(ShortPosition.country_id == country.id).count()
        active_count = db.query(ShortPosition).filter(
            ShortPosition.country_id == country.id,
            ShortPosition.is_active == True
        ).count()
        print(f"   {country.name}: {count:,} total ({active_count:,} active)")

if __name__ == "__main__":
    remove_duplicates()
