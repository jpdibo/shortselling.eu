#!/usr/bin/env python3
"""
Create New Data Backup
Creates a fresh backup of all database data in a new folder with today's date
"""

import sys
import os
import pandas as pd
from datetime import datetime
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection using environment variables"""
    try:
        # PostgreSQL connection
        DATABASE_URL = "postgresql://jpdib@localhost:5432/shortselling"
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def create_backup_folder():
    """Create backup folder with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use absolute path to project directory
    project_dir = r"C:\shortselling.eu"
    backup_folder = os.path.join(project_dir, "data_backup", f"backup_{timestamp}")
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
        logger.info(f"Created backup folder: {backup_folder}")
    
    return backup_folder

def backup_table(engine, table_name, backup_folder):
    """Backup a single table to CSV"""
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        
        csv_path = os.path.join(backup_folder, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        
        logger.info(f"✅ Backed up {table_name}: {len(df)} rows -> {csv_path}")
        return len(df)
        
    except Exception as e:
        logger.error(f"❌ Failed to backup {table_name}: {e}")
        return 0

def create_consolidated_backup(backup_folder):
    """Create consolidated CSV with all short positions"""
    try:
        engine = get_database_connection()
        
        # Query to get all short positions with related data
        query = """
        SELECT 
            c.name as country_name,
            c.code as country_code,
            m.name as manager_name,
            m.slug as manager_slug,
            comp.name as company_name,
            comp.isin as company_isin,
            sp.position_size,
            sp.date,
            sp.created_at,
            sp.updated_at
        FROM short_positions sp
        JOIN countries c ON sp.country_id = c.id
        JOIN managers m ON sp.manager_id = m.id
        JOIN companies comp ON sp.company_id = comp.id
        ORDER BY sp.date DESC, c.name, m.name
        """
        
        df = pd.read_sql(query, engine)
        
        consolidated_path = os.path.join(backup_folder, "consolidated_short_positions.csv")
        df.to_csv(consolidated_path, index=False)
        
        logger.info(f"✅ Created consolidated backup: {len(df)} positions -> {consolidated_path}")
        
        # Create summary statistics
        summary_stats = {
            'total_positions': len(df),
            'countries': df['country_name'].nunique(),
            'managers': df['manager_name'].nunique(),
            'companies': df['company_name'].nunique(),
            'date_range': f"{df['date'].min()} to {df['date'].max()}",
            'backup_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save summary
        summary_path = os.path.join(backup_folder, "backup_summary.txt")
        with open(summary_path, 'w') as f:
            f.write("SHORT SELLING DATA BACKUP SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Backup Date: {summary_stats['backup_date']}\n")
            f.write(f"Total Positions: {summary_stats['total_positions']:,}\n")
            f.write(f"Countries: {summary_stats['countries']}\n")
            f.write(f"Managers: {summary_stats['managers']}\n")
            f.write(f"Companies: {summary_stats['companies']}\n")
            f.write(f"Date Range: {summary_stats['date_range']}\n\n")
            
            # Country breakdown
            f.write("POSITIONS BY COUNTRY:\n")
            f.write("-" * 30 + "\n")
            country_counts = df['country_name'].value_counts()
            for country, count in country_counts.items():
                f.write(f"{country}: {count:,} positions\n")
            
            f.write(f"\nLATEST POSITIONS BY COUNTRY:\n")
            f.write("-" * 30 + "\n")
            latest_by_country = df.groupby('country_name')['date'].max().sort_values(ascending=False)
            for country, latest_date in latest_by_country.items():
                f.write(f"{country}: {latest_date.strftime('%Y-%m-%d')}\n")
        
        logger.info(f"✅ Created backup summary: {summary_path}")
        
        return summary_stats
        
    except Exception as e:
        logger.error(f"❌ Failed to create consolidated backup: {e}")
        raise

def main():
    """Main backup process"""
    print("🔄 Creating New Data Backup")
    print("=" * 50)
    
    try:
        # Create backup folder
        backup_folder = create_backup_folder()
        
        # Get database connection
        engine = get_database_connection()
        
        # Backup individual tables
        tables = ['countries', 'managers', 'companies', 'short_positions']
        total_rows = 0
        
        for table in tables:
            rows = backup_table(engine, table, backup_folder)
            total_rows += rows
        
        # Create consolidated backup
        summary_stats = create_consolidated_backup(backup_folder)
        
        print(f"\n🎉 Backup completed successfully!")
        print(f"📁 Backup location: {backup_folder}")
        print(f"📊 Total rows backed up: {total_rows:,}")
        print(f"📈 Consolidated positions: {summary_stats['total_positions']:,}")
        print(f"🌍 Countries: {summary_stats['countries']}")
        print(f"👥 Managers: {summary_stats['managers']}")
        print(f"🏢 Companies: {summary_stats['companies']}")
        print(f"📅 Date range: {summary_stats['date_range']}")
        
        # List backup files
        print(f"\n📋 Backup files created:")
        for file in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, file)
            file_size = os.path.getsize(file_path)
            print(f"   {file} ({file_size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        logger.error(f"Backup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
