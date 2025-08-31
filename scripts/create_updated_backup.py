#!/usr/bin/env python3
"""
Create Updated Backup
Creates a backup of the current database state after daily updates
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition, Subscription, ScrapingLog, AnalyticsCache

def create_backup():
    """Create backup of current database state"""
    print("💾 Creating Updated Database Backup")
    print("=" * 50)
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"C:\\shortselling.eu\\data_backup\\backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📁 Backup directory: {backup_dir}")
    
    db = next(get_db())
    try:
        # Export countries
        print("📊 Exporting countries...")
        countries = db.query(Country).all()
        countries_data = []
        for country in countries:
            countries_data.append({
                'id': country.id,
                'code': country.code,
                'name': country.name,
                'flag': country.flag,
                'priority': country.priority,
                'url': country.url,
                'is_active': country.is_active
            })
        countries_df = pd.DataFrame(countries_data)
        countries_df.to_csv(os.path.join(backup_dir, 'countries.csv'), index=False)
        print(f"   ✅ Exported {len(countries_data)} countries")
        
        # Export companies
        print("📊 Exporting companies...")
        companies = db.query(Company).all()
        companies_data = []
        for company in companies:
            companies_data.append({
                'id': company.id,
                'name': company.name,
                'isin': company.isin,
                'country_id': company.country_id,
                'created_at': company.created_at
            })
        companies_df = pd.DataFrame(companies_data)
        companies_df.to_csv(os.path.join(backup_dir, 'companies.csv'), index=False)
        print(f"   ✅ Exported {len(companies_data)} companies")
        
        # Export managers
        print("📊 Exporting managers...")
        managers = db.query(Manager).all()
        managers_data = []
        for manager in managers:
            managers_data.append({
                'id': manager.id,
                'name': manager.name,
                'slug': manager.slug,
                'created_at': manager.created_at
            })
        managers_df = pd.DataFrame(managers_data)
        managers_df.to_csv(os.path.join(backup_dir, 'managers.csv'), index=False)
        print(f"   ✅ Exported {len(managers_data)} managers")
        
        # Export short positions
        print("📊 Exporting short positions...")
        positions = db.query(ShortPosition).all()
        positions_data = []
        for position in positions:
            positions_data.append({
                'id': position.id,
                'date': position.date,
                'company_id': position.company_id,
                'manager_id': position.manager_id,
                'country_id': position.country_id,
                'position_size': position.position_size,
                'is_active': position.is_active,
                'is_current': position.is_current,
                'created_at': position.created_at
            })
        positions_df = pd.DataFrame(positions_data)
        positions_df.to_csv(os.path.join(backup_dir, 'positions.csv'), index=False)
        print(f"   ✅ Exported {len(positions_data)} positions")
        
        # Export subscriptions
        print("📊 Exporting subscriptions...")
        subscriptions = db.query(Subscription).all()
        subscriptions_data = []
        for subscription in subscriptions:
            subscriptions_data.append({
                'id': subscription.id,
                'email': subscription.email,
                'frequency': subscription.frequency,
                'is_active': subscription.is_active,
                'created_at': subscription.created_at
            })
        subscriptions_df = pd.DataFrame(subscriptions_data)
        subscriptions_df.to_csv(os.path.join(backup_dir, 'subscriptions.csv'), index=False)
        print(f"   ✅ Exported {len(subscriptions_data)} subscriptions")
        
        # Export scraping logs
        print("📊 Exporting scraping logs...")
        logs = db.query(ScrapingLog).all()
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'country_id': log.country_id,
                'status': log.status,
                'records_scraped': log.records_scraped,
                'error_message': log.error_message,
                'started_at': log.started_at,
                'completed_at': log.completed_at
            })
        logs_df = pd.DataFrame(logs_data)
        logs_df.to_csv(os.path.join(backup_dir, 'scraping_logs.csv'), index=False)
        print(f"   ✅ Exported {len(logs_data)} scraping logs")
        
        # Export analytics cache
        print("📊 Exporting analytics cache...")
        cache_entries = db.query(AnalyticsCache).all()
        cache_data = []
        for cache in cache_entries:
            cache_data.append({
                'id': cache.id,
                'cache_key': cache.cache_key,
                'cache_data': cache.cache_data,
                'expires_at': cache.expires_at,
                'created_at': cache.created_at
            })
        cache_df = pd.DataFrame(cache_data)
        cache_df.to_csv(os.path.join(backup_dir, 'analytics_cache.csv'), index=False)
        print(f"   ✅ Exported {len(cache_data)} analytics cache entries")
        
        # Create summary
        print("\n📋 Creating backup summary...")
        summary = {
            'backup_date': timestamp,
            'total_countries': len(countries_data),
            'total_companies': len(companies_data),
            'total_managers': len(managers_data),
            'total_positions': len(positions_data),
            'total_subscriptions': len(subscriptions_data),
            'total_logs': len(logs_data),
            'total_cache': len(cache_data)
        }
        
        # Create summary file
        with open(os.path.join(backup_dir, 'BACKUP_SUMMARY.txt'), 'w') as f:
            f.write("ShortSelling.eu Database Backup Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Backup Date: {timestamp}\n")
            f.write(f"Total Countries: {summary['total_countries']}\n")
            f.write(f"Total Companies: {summary['total_companies']:,}\n")
            f.write(f"Total Managers: {summary['total_managers']:,}\n")
            f.write(f"Total Positions: {summary['total_positions']:,}\n")
            f.write(f"Total Subscriptions: {summary['total_subscriptions']}\n")
            f.write(f"Total Scraping Logs: {summary['total_logs']}\n")
            f.write(f"Total Analytics Cache: {summary['total_cache']}\n")
        
        print(f"\n✅ Backup completed successfully!")
        print(f"📁 Location: {backup_dir}")
        print(f"📊 Total positions backed up: {summary['total_positions']:,}")
        
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def main():
    """Main function"""
    print("💾 Updated Database Backup Creator")
    print("=" * 50)
    print("This script creates a backup of the current database state")
    print("after the daily updates have been applied.")
    print("=" * 50)
    
    backup_dir = create_backup()
    
    if backup_dir:
        print(f"\n🎉 Backup created successfully at: {backup_dir}")
        print("You can now update the CRITICAL_DATABASE_WARNING.md file with this new backup location.")
    else:
        print("\n❌ Backup failed!")

if __name__ == "__main__":
    main()
