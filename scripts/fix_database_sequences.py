#!/usr/bin/env python3
"""
Fix Database Sequences
Fixes the auto-increment sequences that got out of sync during data restoration.
This script will reset the sequences to the correct values based on existing data.
"""

import sys
import os
from sqlalchemy import text

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition, Subscription, ScrapingLog, AnalyticsCache

def fix_database_sequences():
    """Fix all database sequences to be in sync with existing data"""
    print("🔧 Fixing Database Sequences")
    print("=" * 50)
    
    db = next(get_db())
    try:
        # Get the database engine
        engine = db.bind
        
        # Fix sequences for each table
        sequences_to_fix = [
            ('countries', 'countries_id_seq'),
            ('companies', 'companies_id_seq'),
            ('managers', 'managers_id_seq'),
            ('short_positions', 'short_positions_id_seq'),
            ('subscriptions', 'subscriptions_id_seq'),
            ('scraping_logs', 'scraping_logs_id_seq'),
            ('analytics_cache', 'analytics_cache_id_seq')
        ]
        
        for table_name, sequence_name in sequences_to_fix:
            try:
                # Get the maximum ID from the table
                result = db.execute(text(f"SELECT MAX(id) FROM {table_name}"))
                max_id = result.scalar()
                
                if max_id is not None:
                    # Set the sequence to the next value after the maximum ID
                    next_val = max_id + 1
                    db.execute(text(f"SELECT setval('{sequence_name}', {next_val}, false)"))
                    print(f"✅ Fixed {sequence_name}: set to {next_val}")
                else:
                    # Table is empty, reset to 1
                    db.execute(text(f"SELECT setval('{sequence_name}', 1, false)"))
                    print(f"✅ Reset {sequence_name}: set to 1 (empty table)")
                    
            except Exception as e:
                print(f"⚠️  Warning: Could not fix {sequence_name}: {e}")
        
        # Commit the changes
        db.commit()
        
        print("\n✅ Database sequences fixed successfully!")
        
        # Verify the fixes
        print("\n🔍 Verifying sequences:")
        for table_name, sequence_name in sequences_to_fix:
            try:
                result = db.execute(text(f"SELECT last_value FROM {sequence_name}"))
                last_value = result.scalar()
                print(f"   {sequence_name}: {last_value}")
            except Exception as e:
                print(f"   {sequence_name}: Error checking - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing sequences: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_sequence_fix():
    """Test that we can now add new records"""
    print("\n🧪 Testing sequence fix...")
    
    db = next(get_db())
    try:
        # Try to add a test position (we'll delete it immediately)
        from datetime import datetime
        
        # Get a valid country, company, and manager
        country = db.query(Country).first()
        company = db.query(Company).first()
        manager = db.query(Manager).first()
        
        if not all([country, company, manager]):
            print("❌ Cannot test: missing required data")
            return False
        
        # Create a test position
        test_position = ShortPosition(
            date=datetime.now(),
            company_id=company.id,
            manager_id=manager.id,
            country_id=country.id,
            position_size=0.1,
            is_active=True,
            is_current=False
        )
        
        db.add(test_position)
        db.commit()
        
        # Get the ID that was assigned
        test_id = test_position.id
        print(f"✅ Test position created with ID: {test_id}")
        
        # Delete the test position
        db.delete(test_position)
        db.commit()
        print(f"✅ Test position deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function"""
    print("🔧 Database Sequence Fixer")
    print("=" * 50)
    print("This script will fix the auto-increment sequences")
    print("that got out of sync during data restoration.")
    print("=" * 50)
    
    # Fix the sequences
    if fix_database_sequences():
        # Test the fix
        if test_sequence_fix():
            print("\n🎉 Database sequences fixed and tested successfully!")
            print("You can now run daily updates without primary key conflicts.")
        else:
            print("\n⚠️  Sequences fixed but test failed. Please investigate.")
    else:
        print("\n❌ Failed to fix sequences.")

if __name__ == "__main__":
    main()
