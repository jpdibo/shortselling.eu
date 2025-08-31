#!/usr/bin/env python3
"""
Transfer Norway data from separate Norway database to consolidated database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Norway.database_config import get_norway_db
from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition
from sqlalchemy.orm import sessionmaker
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transfer_norway_data():
    """Transfer all Norway data from separate DB to consolidated DB"""
    
    # Get database connections
    norway_db = next(get_norway_db())
    consolidated_db = next(get_db())
    
    try:
        logger.info("Starting Norway data transfer to consolidated database...")
        
        # Get Norway country record in consolidated DB
        norway_country = consolidated_db.query(Country).filter(Country.code == 'NO').first()
        if not norway_country:
            # Create Norway country if it doesn't exist
            norway_country = Country(
                code='NO',
                name='Norway',
                flag='NO',
                priority='high',
                url='https://ssr.finanstilsynet.no/',
                is_active=True
            )
            consolidated_db.add(norway_country)
            consolidated_db.commit()
            logger.info("Created Norway country record in consolidated database")
        
        # Get all data from Norway database
        norway_companies = norway_db.query(Company).all()
        norway_managers = norway_db.query(Manager).all()
        norway_positions = norway_db.query(ShortPosition).all()
        
        logger.info(f"Found in Norway database: {len(norway_companies)} companies, {len(norway_managers)} managers, {len(norway_positions)} positions")
        
        # Transfer companies
        company_mapping = {}
        for norway_company in norway_companies:
            # Check if company already exists in consolidated DB
            existing_company = consolidated_db.query(Company).filter(
                Company.isin == norway_company.isin
            ).first()
            
            if not existing_company:
                # Create new company
                new_company = Company(
                    name=norway_company.name,
                    isin=norway_company.isin,
                    country_id=norway_country.id
                )
                consolidated_db.add(new_company)
                consolidated_db.flush()
                company_mapping[norway_company.id] = new_company.id
                logger.info(f"Added company: {norway_company.name}")
            else:
                company_mapping[norway_company.id] = existing_company.id
                logger.info(f"Company already exists: {norway_company.name}")
        
        # Transfer managers
        manager_mapping = {}
        for norway_manager in norway_managers:
            # Check if manager already exists in consolidated DB
            existing_manager = consolidated_db.query(Manager).filter(
                Manager.name == norway_manager.name
            ).first()
            
            if not existing_manager:
                # Create new manager with unique slug
                import re
                base_slug = re.sub(r'[^a-z0-9]+', '-', norway_manager.name.lower()).strip('-')
                slug = base_slug
                counter = 1
                while consolidated_db.query(Manager).filter(Manager.slug == slug).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                new_manager = Manager(
                    name=norway_manager.name,
                    slug=slug
                )
                consolidated_db.add(new_manager)
                consolidated_db.flush()
                manager_mapping[norway_manager.id] = new_manager.id
                logger.info(f"Added manager: {norway_manager.name}")
            else:
                manager_mapping[norway_manager.id] = existing_manager.id
                logger.info(f"Manager already exists: {norway_manager.name}")
        
        # Transfer positions
        positions_added = 0
        positions_skipped = 0
        
        for norway_position in norway_positions:
            # Check if position already exists
            existing_position = consolidated_db.query(ShortPosition).filter(
                ShortPosition.company_id == company_mapping[norway_position.company_id],
                ShortPosition.manager_id == manager_mapping[norway_position.manager_id],
                ShortPosition.date == norway_position.date
            ).first()
            
            if not existing_position:
                # Create new position
                new_position = ShortPosition(
                    company_id=company_mapping[norway_position.company_id],
                    manager_id=manager_mapping[norway_position.manager_id],
                    country_id=norway_country.id,
                    position_size=norway_position.position_size,
                    date=norway_position.date
                )
                consolidated_db.add(new_position)
                positions_added += 1
            else:
                positions_skipped += 1
        
        # Commit all changes
        consolidated_db.commit()
        
        logger.info(f"✅ Transfer completed successfully!")
        logger.info(f"   Companies: {len(company_mapping)} processed")
        logger.info(f"   Managers: {len(manager_mapping)} processed") 
        logger.info(f"   Positions: {positions_added} added, {positions_skipped} skipped (duplicates)")
        
        return {
            "success": True,
            "companies": len(company_mapping),
            "managers": len(manager_mapping),
            "positions_added": positions_added,
            "positions_skipped": positions_skipped
        }
        
    except Exception as e:
        consolidated_db.rollback()
        logger.error(f"❌ Transfer failed: {e}")
        raise
    finally:
        norway_db.close()
        consolidated_db.close()

if __name__ == "__main__":
    result = transfer_norway_data()
    print(f"Transfer result: {result}")