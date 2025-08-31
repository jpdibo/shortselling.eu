import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition, Subscription, ScrapingLog
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CSVManager:
    """Manager for CSV export/import operations"""
    
    def __init__(self, export_dir: str = "data/exports"):
        self.export_dir = export_dir
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        """Ensure the export directory exists"""
        os.makedirs(self.export_dir, exist_ok=True)
    
    async def export_all_data(self, include_timestamp: bool = True) -> Dict[str, str]:
        """Export all data to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        
        exported_files = {}
        
        try:
            async with get_db() as db:
                # Export countries
                countries_file = await self._export_countries(db, timestamp)
                exported_files['countries'] = countries_file
                
                # Export companies
                companies_file = await self._export_companies(db, timestamp)
                exported_files['companies'] = companies_file
                
                # Export managers
                managers_file = await self._export_managers(db, timestamp)
                exported_files['managers'] = managers_file
                
                # Export short positions
                positions_file = await self._export_positions(db, timestamp)
                exported_files['positions'] = positions_file
                
                # Export subscriptions
                subscriptions_file = await self._export_subscriptions(db, timestamp)
                exported_files['subscriptions'] = subscriptions_file
                
                # Export scraping logs
                logs_file = await self._export_scraping_logs(db, timestamp)
                exported_files['scraping_logs'] = logs_file
                
                # Create consolidated file
                consolidated_file = await self._create_consolidated_file(db, timestamp)
                exported_files['consolidated'] = consolidated_file
                
            logger.info(f"Successfully exported {len(exported_files)} CSV files")
            return exported_files
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise
    
    async def _export_countries(self, db: Session, timestamp: str) -> str:
        """Export countries data"""
        countries = db.query(Country).all()
        
        data = []
        for country in countries:
            data.append({
                'id': country.id,
                'code': country.code,
                'name': country.name,
                'flag': country.flag,
                'priority': country.priority,
                'url': country.url,
                'is_active': country.is_active,
                'created_at': country.created_at,
                'updated_at': country.updated_at
            })
        
        filename = f"countries{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def _export_companies(self, db: Session, timestamp: str) -> str:
        """Export companies data"""
        companies = db.query(Company).all()
        
        data = []
        for company in companies:
            data.append({
                'id': company.id,
                'name': company.name,
                'isin_code': company.isin_code,
                'country_code': company.country_code,
                'created_at': company.created_at,
                'updated_at': company.updated_at
            })
        
        filename = f"companies{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def _export_managers(self, db: Session, timestamp: str) -> str:
        """Export managers data"""
        managers = db.query(Manager).all()
        
        data = []
        for manager in managers:
            data.append({
                'id': manager.id,
                'name': manager.name,
                'slug': manager.slug,
                'created_at': manager.created_at,
                'updated_at': manager.updated_at
            })
        
        filename = f"managers{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def _export_positions(self, db: Session, timestamp: str) -> str:
        """Export short positions data"""
        positions = db.query(ShortPosition).all()
        
        data = []
        for position in positions:
            data.append({
                'id': position.id,
                'disclosure_date': position.disclosure_date,
                'position_size': position.position_size,
                'is_active': position.is_active,
                'is_historical': position.is_historical,
                'company_id': position.company_id,
                'manager_id': position.manager_id,
                'created_at': position.created_at,
                'updated_at': position.updated_at
            })
        
        filename = f"positions{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def _export_subscriptions(self, db: Session, timestamp: str) -> str:
        """Export subscriptions data"""
        subscriptions = db.query(Subscription).all()
        
        data = []
        for subscription in subscriptions:
            data.append({
                'id': subscription.id,
                'email': subscription.email,
                'first_name': subscription.first_name,
                'frequency': subscription.frequency,
                'countries': subscription.countries,
                'is_active': subscription.is_active,
                'created_at': subscription.created_at,
                'updated_at': subscription.updated_at
            })
        
        filename = f"subscriptions{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def _export_scraping_logs(self, db: Session, timestamp: str) -> str:
        """Export scraping logs data"""
        logs = db.query(ScrapingLog).all()
        
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'country_code': log.country_code,
                'success_count': log.success_count,
                'error_count': log.error_count,
                'last_success': log.last_success,
                'last_error': log.last_error,
                'created_at': log.created_at,
                'updated_at': log.updated_at
            })
        
        filename = f"scraping_logs{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def _create_consolidated_file(self, db: Session, timestamp: str) -> str:
        """Create a consolidated CSV with all position data including company and manager names"""
        # Get positions with company and manager information
        positions = db.query(
            ShortPosition, Company, Manager, Country
        ).join(
            Company, ShortPosition.company_id == Company.id
        ).join(
            Manager, ShortPosition.manager_id == Manager.id
        ).join(
            Country, Company.country_code == Country.code
        ).all()
        
        data = []
        for position, company, manager, country in positions:
            data.append({
                'disclosure_date': position.disclosure_date,
                'company_name': company.name,
                'company_isin': company.isin_code,
                'manager_name': manager.name,
                'country_name': country.name,
                'country_code': country.code,
                'country_flag': country.flag,
                'position_size': position.position_size,
                'is_active': position.is_active,
                'is_historical': position.is_historical
            })
        
        filename = f"consolidated_positions{'_' + timestamp if timestamp else ''}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        return filepath
    
    async def import_from_csv(self, filepath: str, table_name: str) -> bool:
        """Import data from CSV file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return False
            
            df = pd.read_csv(filepath)
            
            async with get_db() as db:
                if table_name == 'countries':
                    await self._import_countries(db, df)
                elif table_name == 'companies':
                    await self._import_companies(db, df)
                elif table_name == 'managers':
                    await self._import_managers(db, df)
                elif table_name == 'positions':
                    await self._import_positions(db, df)
                elif table_name == 'subscriptions':
                    await self._import_subscriptions(db, df)
                else:
                    logger.error(f"Unknown table: {table_name}")
                    return False
            
            logger.info(f"Successfully imported data from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
    
    async def _import_countries(self, db: Session, df: pd.DataFrame):
        """Import countries data"""
        for _, row in df.iterrows():
            country = Country(
                code=row['code'],
                name=row['name'],
                flag=row['flag'],
                priority=row['priority'],
                url=row['url'],
                is_active=row['is_active']
            )
            db.add(country)
        await db.commit()
    
    async def _import_companies(self, db: Session, df: pd.DataFrame):
        """Import companies data"""
        for _, row in df.iterrows():
            company = Company(
                name=row['name'],
                isin_code=row.get('isin_code'),
                country_code=row['country_code']
            )
            db.add(company)
        await db.commit()
    
    async def _import_managers(self, db: Session, df: pd.DataFrame):
        """Import managers data"""
        for _, row in df.iterrows():
            manager = Manager(
                name=row['name'],
                slug=row['slug']
            )
            db.add(manager)
        await db.commit()
    
    async def _import_positions(self, db: Session, df: pd.DataFrame):
        """Import positions data"""
        for _, row in df.iterrows():
            position = ShortPosition(
                disclosure_date=pd.to_datetime(row['disclosure_date']),
                position_size=row['position_size'],
                is_active=row['is_active'],
                is_historical=row['is_historical'],
                company_id=row['company_id'],
                manager_id=row['manager_id']
            )
            db.add(position)
        await db.commit()
    
    async def _import_subscriptions(self, db: Session, df: pd.DataFrame):
        """Import subscriptions data"""
        for _, row in df.iterrows():
            subscription = Subscription(
                email=row['email'],
                first_name=row['first_name'],
                frequency=row['frequency'],
                countries=row.get('countries'),
                is_active=row['is_active']
            )
            db.add(subscription)
        await db.commit()
    
    def get_export_summary(self) -> Dict[str, Any]:
        """Get summary of exported files"""
        if not os.path.exists(self.export_dir):
            return {}
        
        files = os.listdir(self.export_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
        
        summary = {
            'export_dir': self.export_dir,
            'total_files': len(csv_files),
            'files': []
        }
        
        for file in csv_files:
            filepath = os.path.join(self.export_dir, file)
            size = os.path.getsize(filepath)
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            summary['files'].append({
                'name': file,
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'modified': modified.isoformat()
            })
        
        return summary
