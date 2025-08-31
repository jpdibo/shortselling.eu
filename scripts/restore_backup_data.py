#!/usr/bin/env python3
"""
Restore Backup Data from CSV Files
Restores the database from the backup CSV files
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import Country, Company, Manager, ShortPosition, Subscription, ScrapingLog, AnalyticsCache

def restore_backup_data():
    """Restore database from CSV backup files"""
    print("🔄 Restoring Database from Backup")
    print("=" * 60)
    
    # Backup directory
    backup_dir = r"C:\shortselling.eu\data_backup\backup_20250815_152658"
    
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return
    
    print(f"📁 Backup directory: {backup_dir}")
    
    db = SessionLocal()
    
    try:
        # 1. Restore Countries
        print("\n🌍 Restoring Countries...")
        countries_file = os.path.join(backup_dir, "countries.csv")
        if os.path.exists(countries_file):
            countries_df = pd.read_csv(countries_file)
            for _, row in countries_df.iterrows():
                # Provide default URLs for countries
                default_urls = {
                    'GB': 'https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx',
                    'IE': 'https://www.centralbank.ie/regulation/industry-sectors/financial-services/securities-markets/short-selling',
                    'BE': 'https://www.fsma.be/en/regulatory-framework/short-selling',
                    'ES': 'https://www.cnmv.es/DocPortal/Posiciones-Cortas/NetShortPositions.xls',
                    'DE': 'https://www.bafin.de/EN/Aufsicht/WertpapiereEmittenten/Leerverkaeufe/leerverkaeufe_node_en.html'
                }
                
                country = Country(
                    id=row['id'],
                    code=row['code'],
                    name=row['name'],
                    flag=row['flag'],
                    priority=row['priority'],
                    url=row['url'] if pd.notna(row['url']) else default_urls.get(row['code'], 'https://example.com'),
                    is_active=True  # Default to True since column doesn't exist
                )
                db.add(country)
            print(f"✅ Restored {len(countries_df)} countries")
        else:
            print("⚠️  countries.csv not found")
        
        # 2. Restore Companies
        print("\n🏢 Restoring Companies...")
        companies_file = os.path.join(backup_dir, "companies.csv")
        if os.path.exists(companies_file):
            companies_df = pd.read_csv(companies_file)
            for _, row in companies_df.iterrows():
                company = Company(
                    id=row['id'],
                    name=row['name'],
                    isin=row['isin'] if pd.notna(row['isin']) else None,
                    country_id=row['country_id'],
                    created_at=pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else datetime.now()
                )
                db.add(company)
            print(f"✅ Restored {len(companies_df)} companies")
        else:
            print("⚠️  companies.csv not found")
        
        # 3. Restore Managers
        print("\n👥 Restoring Managers...")
        managers_file = os.path.join(backup_dir, "managers.csv")
        if os.path.exists(managers_file):
            managers_df = pd.read_csv(managers_file)
            for _, row in managers_df.iterrows():
                manager = Manager(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug'],
                    created_at=pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else datetime.now()
                )
                db.add(manager)
            print(f"✅ Restored {len(managers_df)} managers")
        else:
            print("⚠️  managers.csv not found")
        
        # 4. Restore Short Positions
        print("\n📊 Restoring Short Positions...")
        positions_file = os.path.join(backup_dir, "positions.csv")
        if os.path.exists(positions_file):
            positions_df = pd.read_csv(positions_file)
            
            # Process in batches to avoid memory issues
            batch_size = 1000
            total_positions = len(positions_df)
            
            for i in range(0, total_positions, batch_size):
                batch = positions_df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    position = ShortPosition(
                        id=row['id'],
                        date=pd.to_datetime(row['date']),
                        company_id=row['company_id'],
                        manager_id=row['manager_id'],
                        country_id=row['country_id'],
                        position_size=row['position_size'],
                        is_active=row['is_active'],
                        is_current=row['is_current'],
                        created_at=pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else datetime.now()
                    )
                    db.add(position)
                
                # Commit batch
                db.commit()
                print(f"   Processed {min(i+batch_size, total_positions)}/{total_positions} positions")
            
            print(f"✅ Restored {total_positions} positions")
        else:
            print("⚠️  positions.csv not found")
        
        # 5. Restore Subscriptions
        print("\n📧 Restoring Subscriptions...")
        subscriptions_file = os.path.join(backup_dir, "subscriptions.csv")
        if os.path.exists(subscriptions_file):
            subscriptions_df = pd.read_csv(subscriptions_file)
            for _, row in subscriptions_df.iterrows():
                subscription = Subscription(
                    id=row['id'],
                    email=row['email'],
                    frequency=row['frequency'],
                    is_active=row['is_active'],
                    created_at=pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else datetime.now()
                )
                db.add(subscription)
            print(f"✅ Restored {len(subscriptions_df)} subscriptions")
        else:
            print("⚠️  subscriptions.csv not found")
        
        # 6. Restore Scraping Logs
        print("\n📝 Restoring Scraping Logs...")
        logs_file = os.path.join(backup_dir, "scraping_logs.csv")
        if os.path.exists(logs_file):
            logs_df = pd.read_csv(logs_file)
            for _, row in logs_df.iterrows():
                log = ScrapingLog(
                    id=row['id'],
                    country_id=row['country_id'],
                    status=row['status'],
                    positions_added=row['positions_added'],
                    errors=row['errors'] if pd.notna(row['errors']) else None,
                    started_at=pd.to_datetime(row['started_at']) if pd.notna(row['started_at']) else datetime.now(),
                    completed_at=pd.to_datetime(row['completed_at']) if pd.notna(row['completed_at']) else None
                )
                db.add(log)
            print(f"✅ Restored {len(logs_df)} scraping logs")
        else:
            print("⚠️  scraping_logs.csv not found")
        
        # 7. Restore Analytics Cache
        print("\n📈 Restoring Analytics Cache...")
        cache_file = os.path.join(backup_dir, "analytics_cache.csv")
        if os.path.exists(cache_file):
            cache_df = pd.read_csv(cache_file)
            for _, row in cache_df.iterrows():
                cache = AnalyticsCache(
                    id=row['id'],
                    cache_key=row['cache_key'],
                    data=row['data'],
                    expires_at=pd.to_datetime(row['expires_at']) if pd.notna(row['expires_at']) else None,
                    created_at=pd.to_datetime(row['created_at']) if pd.notna(row['created_at']) else datetime.now()
                )
                db.add(cache)
            print(f"✅ Restored {len(cache_df)} analytics cache entries")
        else:
            print("⚠️  analytics_cache.csv not found")
        
        # Final commit
        db.commit()
        
        # Verify restoration
        print("\n🔍 Verifying Restoration...")
        total_countries = db.query(Country).count()
        total_companies = db.query(Company).count()
        total_managers = db.query(Manager).count()
        total_positions = db.query(ShortPosition).count()
        total_subscriptions = db.query(Subscription).count()
        total_logs = db.query(ScrapingLog).count()
        total_cache = db.query(AnalyticsCache).count()
        
        print(f"📊 Final Database State:")
        print(f"   - Countries: {total_countries}")
        print(f"   - Companies: {total_companies}")
        print(f"   - Managers: {total_managers}")
        print(f"   - Positions: {total_positions:,}")
        print(f"   - Subscriptions: {total_subscriptions}")
        print(f"   - Scraping Logs: {total_logs}")
        print(f"   - Analytics Cache: {total_cache}")
        
        print("\n✅ Database restoration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Database restoration failed: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    restore_backup_data()
