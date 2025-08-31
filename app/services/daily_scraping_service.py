#!/usr/bin/env python3
"""
Daily Scraping Service for ShortSelling.eu
Automatically updates database with fresh data from all countries.

UPDATED INGESTION LOGIC (important):
- We always re-ingest a recent rolling window (default 30 days) from the regulator.
- This avoids missing closures (including 0.00) that might be older than the country's max date for another issuer.
- Duplicates are avoided by an exact-match check before insert (you can also add a unique index for full idempotency).
"""

import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.database import get_db
from app.db.models import Country, Company, Manager, ShortPosition, ScrapingLog
from app.scrapers.scraper_factory import ScraperFactory


# ========================================
# CENTRALIZED MANAGER NORMALIZATION LOGIC
# ========================================

def normalize_manager_name(raw_name: str) -> str:
    """
    Normalize manager name to prevent duplicates across ALL scrapers.
    
    Rules:
    1. Strip whitespace
    2. Convert to Title Case (Marshall Wace Llp)
    3. Handle common abbreviations correctly
    4. Clean up spacing
    5. Transliterate non-Latin scripts for WIN1252 compatibility
    
    Args:
        raw_name: Raw manager name from any scraper
        
    Returns:
        Normalized manager name
    """
    if not raw_name or not raw_name.strip():
        return ""
    
    # Strip and basic cleanup
    name = raw_name.strip()
    
    # Transliterate Arabic text only for database compatibility
    try:
        # Check if it contains Arabic characters specifically
        if any(0x0600 <= ord(char) <= 0x06FF for char in name):  # Arabic Unicode block
            # Simple Arabic to Latin transliteration for key names
            arabic_to_latin = {
                'ميلينيوم كابيتال (دي اي اف سي) ليميتد': 'Millennium Capital (DIFC) Limited',
                'شركة': 'Company',
                'كابيتال': 'Capital',
                'ليميتد': 'Limited',
                'ميلينيوم': 'Millennium'
            }
            for arabic, latin in arabic_to_latin.items():
                if arabic in name:
                    name = name.replace(arabic, latin)
                    break
            # If still has Arabic characters, use unidecode as fallback
            if any(0x0600 <= ord(char) <= 0x06FF for char in name):
                try:
                    import unidecode
                    name = unidecode.unidecode(name)
                except ImportError:
                    # Final fallback: remove Arabic characters only
                    name = ''.join(char for char in name if not (0x0600 <= ord(char) <= 0x06FF))
    except Exception:
        pass
    
    
    # Convert to Title Case (Unicode-aware with proper accent handling)
    def unicode_title_case(text):
        """Custom title case that properly handles accented characters"""
        return ''.join(char.upper() if i == 0 or text[i-1].isspace() 
                      else char.lower() for i, char in enumerate(text))
    
    name = unicode_title_case(name)
    
    # Fix common abbreviations that shouldn't be title-cased
    abbreviations = {
        'Llc': 'LLC',
        'Llp': 'LLP', 
        'Lp': 'LP',
        'Ltd': 'Ltd',
        'Inc': 'Inc',
        'Corp': 'Corp',
        'Plc': 'PLC',
        'As': 'AS',  # Norwegian companies
        'Asa': 'ASA',  # Norwegian companies
        'Gmbh': 'GmbH',  # German companies
        'Sa': 'SA',  # French/Spanish companies
        'Sas': 'SAS',  # French companies
        'Bv': 'BV',  # Dutch companies
        'Nv': 'NV',  # Dutch companies
        'Ab': 'AB',  # Swedish companies
        'Oy': 'OY',  # Finnish companies
    }
    
    for wrong, correct in abbreviations.items():
        # Match word boundaries to avoid partial replacements
        name = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, name)
    
    # Clean up extra spaces
    name = ' '.join(name.split())
    
    return name


def generate_manager_slug(normalized_name: str) -> str:
    """Generate a clean URL slug for the manager."""
    if not normalized_name:
        return ""
    
    # Convert to lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', normalized_name.lower()).strip('-')
    return slug


def find_existing_manager(db: Session, normalized_name: str) -> Optional[Manager]:
    """
    Find existing manager using multiple lookup strategies to avoid duplicates.
    
    Strategies:
    1. Exact match on normalized name
    2. Case-insensitive match  
    3. Slug-based match
    """
    if not normalized_name:
        return None
    
    # Strategy 1: Exact match on normalized name
    manager = db.query(Manager).filter(Manager.name == normalized_name).first()
    if manager:
        return manager
    
    # Strategy 2: Case-insensitive match
    manager = db.query(Manager).filter(
        func.upper(Manager.name) == func.upper(normalized_name)
    ).first()
    if manager:
        return manager
    
    # Strategy 3: Slug-based match (in case name has slight variations)
    target_slug = generate_manager_slug(normalized_name)
    if target_slug:
        manager = db.query(Manager).filter(Manager.slug == target_slug).first()
    
    return manager


def get_or_create_normalized_manager(db: Session, raw_manager_name: str, logger=None) -> Optional[Manager]:
    """
    Get existing manager or create new one with proper normalization.
    
    This is the main function that ALL scrapers should use for manager handling.
    
    Args:
        db: Database session
        raw_manager_name: Raw manager name from any scraper
        logger: Optional logger for debugging
        
    Returns:
        Manager instance or None if invalid name
    """
    if not raw_manager_name or not raw_manager_name.strip():
        return None
    
    # Normalize the name
    normalized_name = normalize_manager_name(raw_manager_name)
    if not normalized_name:
        return None
    
    # Try to find existing manager
    manager = find_existing_manager(db, normalized_name)
    if manager:
        if logger:
            logger.debug(f"Found existing manager: '{raw_manager_name}' -> '{manager.name}'")
        return manager
    
    # Create new manager
    try:
        slug = generate_manager_slug(normalized_name)
        
        # Ensure slug uniqueness
        base_slug = slug
        counter = 1
        while db.query(Manager).filter(Manager.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        manager = Manager(name=normalized_name, slug=slug)
        db.add(manager)
        db.flush()  # Get the ID
        
        if logger:
            logger.info(f"Created new manager: '{raw_manager_name}' -> '{normalized_name}' (ID: {manager.id})")
        
        return manager
        
    except Exception as e:
        # Handle race conditions
        db.rollback()
        
        if logger:
            logger.warning(f"Failed to create manager '{normalized_name}', trying to find again: {e}")
        
        # Try to find again after rollback
        manager = find_existing_manager(db, normalized_name)
        if manager:
            return manager
        
        if logger:
            logger.error(f"Could not create or find manager '{normalized_name}': {e}")
        
        return None


def normalize_company_name(raw_name: str) -> str:
    """Normalize company name to prevent duplicates across ALL scrapers."""
    if not raw_name or not raw_name.strip():
        return ""
    
    # Basic cleanup
    name = raw_name.strip()
    
    
    # Convert to Title Case for consistency (Unicode-aware with proper accent handling)
    def unicode_title_case(text):
        """Custom title case that properly handles accented characters"""
        return ''.join(char.upper() if i == 0 or text[i-1].isspace() 
                      else char.lower() for i, char in enumerate(text))
    
    name = unicode_title_case(name)
    
    # Fix common company abbreviations that get messed up by title case
    company_abbreviations = {
        'Ab': 'AB',           # Swedish: Aktiebolag
        'Asa': 'ASA',         # Norwegian: Allmennaksjeselskap  
        'As': 'AS',           # Norwegian: Aksjeselskap
        'Plc': 'PLC',         # Public Limited Company
        'Ltd': 'Ltd',         # Limited
        'Llc': 'LLC',         # Limited Liability Company
        'Inc': 'Inc',         # Incorporated
        'Corp': 'Corp',       # Corporation
        'Co': 'Co',           # Company
        'Sa': 'SA',           # Société Anonyme
        'Spa': 'SpA',         # Società per Azioni
        'Srl': 'SRL',         # Società a Responsabilità Limitata
        'Nv': 'NV',           # Naamloze Vennootschap
        'Bv': 'BV',           # Besloten Vennootschap
        'Gmbh': 'GmbH',       # Gesellschaft mit beschränkter Haftung
        'Ag': 'AG',           # Aktiengesellschaft
        'Se': 'SE',           # Societas Europaea
        'Oy': 'OY',           # Finnish: Osakeyhtiö
        'Oyj': 'OYJ',         # Finnish: Julkinen osakeyhtiö
        'A/s': 'A/S',         # Danish: Aktieselskab
        'Publ': '(publ)',     # Swedish: publicly traded indicator
        'Public': '(publ)',   # English equivalent
    }
    
    for wrong, correct in company_abbreviations.items():
        # Use word boundary regex to avoid partial replacements
        name = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, name)
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name


def find_existing_company(db: Session, normalized_name: str, country_id: int) -> Optional[Company]:
    """
    Find existing company using multiple lookup strategies to avoid duplicates.
    
    Strategies:
    1. Exact match on normalized name + country
    2. Case-insensitive match + country
    3. ISIN-based match (if available)
    """
    if not normalized_name:
        return None
    
    # Strategy 1: Exact match on normalized name + country
    company = db.query(Company).filter(
        Company.name == normalized_name,
        Company.country_id == country_id
    ).first()
    if company:
        return company
    
    # Strategy 2: Case-insensitive match + country
    company = db.query(Company).filter(
        func.upper(Company.name) == func.upper(normalized_name),
        Company.country_id == country_id
    ).first()
    if company:
        return company
    
    return None


def get_or_create_normalized_company(db: Session, raw_company_name: str, country_id: int, isin: str = None, logger=None) -> Optional[Company]:
    """
    Get existing company or create new one with proper normalization.
    
    This is the main function that ALL scrapers should use for company handling.
    
    Args:
        db: Database session
        raw_company_name: Raw company name from any scraper
        country_id: Country ID for the company
        isin: Optional ISIN code
        logger: Optional logger for debugging
        
    Returns:
        Company instance or None if invalid name
    """
    if not raw_company_name or not raw_company_name.strip():
        return None
    
    # Normalize the name
    normalized_name = normalize_company_name(raw_company_name)
    if not normalized_name:
        return None
    
    # Try to find existing company
    company = find_existing_company(db, normalized_name, country_id)
    if company:
        if logger:
            logger.debug(f"Found existing company: '{raw_company_name}' -> '{normalized_name}' (ID: {company.id})")
        return company
    
    # Create new company
    try:
        company = Company(
            name=normalized_name,
            country_id=country_id,
            isin=isin if isin and isin.strip() else None
        )
        
        db.add(company)
        db.flush()  # Get the ID without committing
        
        if logger:
            logger.info(f"Created new company: '{raw_company_name}' -> '{normalized_name}' (ID: {company.id})")
        
        return company
        
    except Exception as e:
        # Handle race conditions
        db.rollback()
        
        if logger:
            logger.warning(f"Failed to create company '{normalized_name}', trying to find again: {e}")
        
        # Try to find again after rollback
        company = find_existing_company(db, normalized_name, country_id)
        if company:
            return company
        
        if logger:
            logger.error(f"Could not create or find company '{normalized_name}': {e}")
        
        return None


class DailyScrapingService:
    """Service for daily scraping and database updates"""
    
    def __init__(self):
        self.logger = logging.getLogger("daily_scraping")
        self.scraper_factory = ScraperFactory()
        
        # Cache for managers and companies to avoid repeated DB queries
        self.manager_cache: Dict[str, Manager] = {}
        self.company_cache: Dict[str, Company] = {}
        self.country_cache: Dict[str, Country] = {}
        
        # Statistics
        self.stats: Dict[str, Any] = {
            'total_positions_found': 0,
            'total_positions_added': 0,
            'total_errors': 0,
            'countries_processed': 0,
            'countries_failed': 0
        }
    
    async def run_daily_update(self) -> Dict[str, Any]:
        """Run daily update for all countries"""
        self.logger.info("🚀 Starting daily scraping update")
        start_time = datetime.now()
        
        # Reset statistics
        self.stats = {
            'total_positions_found': 0,
            'total_positions_added': 0,
            'total_errors': 0,
            'countries_processed': 0,
            'countries_failed': 0
        }
        
        # Get list of countries to scrape
        countries = self._get_countries_to_scrape()
        
        self.logger.info(f"📋 Found {len(countries)} countries to process")
        
        # Process each country
        for country in countries:
            try:
                await self._process_country(country)
                self.stats['countries_processed'] += 1
            except Exception as e:
                self.logger.error(f"❌ Failed to process {country.name}: {e}")
                self.stats['countries_failed'] += 1
                await self._log_scraping_error(country.code, str(e))
        
        # Calculate duration
        duration = datetime.now() - start_time
        
        # Log final statistics
        self.logger.info(f"Daily scraping completed in {duration}")
        self.logger.info(f"Statistics: {self.stats}")
        
        return {
            'success': True,
            'duration': str(duration),
            'statistics': self.stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_countries_to_scrape(self) -> List[Country]:
        """Get list of countries that have scrapers available"""
        db = next(get_db())
        try:
            # Get all 12 European countries that have scrapers available
            countries = db.query(Country).filter(
                Country.code.in_([
                    'GB', 'DE', 'ES', 'BE', 'IE',  # Original 5
                    'FR', 'IT', 'NL',              # Additional 3
                    'FI', 'SE', 'NO', 'DK'         # Nordic 4
                ])
            ).all()
            
            self.logger.info(f"Found {len(countries)} countries with scrapers")
            return countries
            
        finally:
            db.close()
    
    def _get_scraper(self, country_code: str):
        """Get scraper for a country code"""
        return self.scraper_factory.create_scraper(country_code)

    async def _process_country(self, country: Country):
        """Process a single country"""
        self.logger.info(f"Processing {country.name} ({country.code})")
        
        try:
            # Get scraper for this country
            scraper = self._get_scraper(country.code)
            if not scraper:
                self.logger.error(f"No scraper found for {country.code}")
                return
            
            # Scrape data
            positions = scraper.scrape()
            self.logger.info(f"Found {len(positions)} positions for {country.name}")
            
            # Update database
            added_count = await self._update_database(country, positions)
            self.logger.info(f"Added {added_count} new positions for {country.name}")
            
            # Log success
            await self._log_scraping_success(country.code, len(positions), added_count)
            
        except Exception as e:
            self.logger.error(f"Error processing {country.name}: {e}")
            await self._log_scraping_error(country.code, str(e))
            self.stats['total_errors'] += 1
    
    async def _update_database(self, country: Country, positions: List[Dict]) -> int:
        """Update database with new positions using a rolling time window, 
        with optional full backfill for specific countries (e.g. UK)."""
        db = next(get_db())
        added_count = 0

        try:
            # Get the most recent date we have for this country (for logging only now)
            latest_date = db.query(func.max(ShortPosition.date)).filter(
                ShortPosition.country_id == country.id
            ).scalar()

            # Get existing count for this country
            existing_count = db.query(ShortPosition).filter(
                ShortPosition.country_id == country.id
            ).count()

            self.logger.info(f"Latest date in database for {country.name}: {latest_date}")
            self.logger.info(f"Existing positions for {country.name}: {existing_count}")

            # Update statistics
            self.stats['total_positions_found'] += len(positions)

            # --- BEGIN BACKFILL/ROLLING WINDOW LOGIC ---
            # One-off full backfill for UK (GB), otherwise rolling window.
            FORCE_FULL_BACKFILL = {'GB': False}  # set to False/remove after UK backfill is done
            ROLLING_DAYS = 30

            if positions:
                # Normalize scraped dates to `date` objects
                for pos in positions:
                    if hasattr(pos['date'], 'date'):
                        pos['date'] = pos['date'].date()

                if FORCE_FULL_BACKFILL.get(country.code, False):
                    filtered_positions = positions  # take *all* FCA rows, including 2020 zeros
                    self.logger.info(
                        f"[Backfill] Forcing FULL import for {country.code}: "
                        f"{len(filtered_positions)} rows"
                    )
                else:
                    most_recent_scraped = max(pos['date'] for pos in positions)
                    cutoff_date = most_recent_scraped - timedelta(days=ROLLING_DAYS)

                    if existing_count < 100:
                        filtered_positions = positions
                        self.logger.info(
                            f"Very little existing data ({existing_count}), "
                            f"keeping ALL {len(filtered_positions)} rows for {country.name}"
                        )
                    else:
                        filtered_positions = [
                            pos for pos in positions if pos['date'] >= cutoff_date
                        ]
                        self.logger.info(
                            f"Rolling window: keeping {len(filtered_positions)} rows "
                            f"from {cutoff_date} to {most_recent_scraped} for {country.name}"
                        )
            else:
                filtered_positions = []
                self.logger.info("No positions found in scraped data")
            # --- END BACKFILL/ROLLING WINDOW LOGIC ---

            batch_size = 100  # Commit every 100 positions for better performance
            batch_count = 0
            
            for position_data in filtered_positions:
                try:
                    # Get or create manager and company
                    manager = self._get_or_create_manager(
                        db,
                        position_data['manager_name']
                    )
                    company = self._get_or_create_company(
                        db,
                        position_data['company_name'],
                        position_data.get('isin'),
                        country.name
                    )
                    
                    # Check if position already exists (exact match)
                    existing = db.query(ShortPosition).filter(
                        and_(
                            ShortPosition.date == position_data['date'],
                            ShortPosition.position_size == position_data['position_size'],
                            ShortPosition.company_id == company.id,
                            ShortPosition.manager_id == manager.id,
                            ShortPosition.country_id == country.id,
                        )
                    ).first()

                    if existing:
                        continue  # Position already exists

                    # Create new position
                    new_position = ShortPosition(
                        date=position_data['date'],
                        company_id=company.id,
                        manager_id=manager.id,
                        country_id=country.id,
                        position_size=position_data['position_size'],
                        is_active=position_data.get('is_active', True)
                    )

                    db.add(new_position)
                    added_count += 1
                    batch_count += 1
                    
                    # Commit in batches for better performance
                    if batch_count >= batch_size:
                        db.commit()
                        batch_count = 0
                        if added_count % 1000 == 0:  # Log progress every 1000 positions
                            self.logger.info(f"Processed {added_count} positions so far...")

                except Exception as e:
                    self.logger.warning(f"Error processing position: {e}")
                    self.stats['total_errors'] += 1
                    db.rollback()  # Rollback failed transaction
                    batch_count = 0  # Reset batch count after rollback
                    continue
            
            # Commit any remaining positions in the final batch
            if batch_count > 0:
                db.commit()

            # Update statistics
            self.stats['total_positions_added'] += added_count

            # Commit all changes
            db.commit()

        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()

        return added_count

    async def run_for_country_codes(self, codes: list[str]) -> dict:
        """Run scraping only for the provided country codes (e.g., ['GB'] or ['GB','DE'])."""
        start_time = datetime.now()
        self.stats = {
            'total_positions_found': 0,
            'total_positions_added': 0,
            'total_errors': 0,
            'countries_processed': 0,
            'countries_failed': 0
        }

        # fetch only requested countries
        db = next(get_db())
        try:
            countries = db.query(Country).filter(Country.code.in_(codes)).all()
        finally:
            db.close()

        for country in countries:
            try:
                await self._process_country(country)
                self.stats['countries_processed'] += 1
            except Exception as e:
                self.logger.error(f"❌ Failed to process {country.name}: {e}")
                self.stats['countries_failed'] += 1
                await self._log_scraping_error(country.code, str(e))

        duration = datetime.now() - start_time
        return {
            'success': True,
            'duration': str(duration),
            'statistics': self.stats,
            'timestamp': datetime.now().isoformat(),
            'countries': codes,
        }


    
    def _get_or_create_manager(self, db: Session, manager_name: str) -> Manager:
        """Get or create a manager using centralized normalization logic"""
        # Use the centralized normalization function
        manager = get_or_create_normalized_manager(db, manager_name, self.logger)
        
        if not manager:
            raise Exception(f"Failed to create or find manager: '{manager_name}'")
        
        # Cache the result using the normalized name as key
        normalized_name = normalize_manager_name(manager_name)
        self.manager_cache[normalized_name] = manager
        return manager
    
    def _get_or_create_company(self, db: Session, company_name: str, isin: Optional[str], country_name: str) -> Company:
        """Get or create a company with caching and normalization"""
        def clean_text(text: Optional[str]) -> str:
            if not text:
                return ""
            text_str = str(text).strip()
            text_str = text_str.replace('\x9c', 'o').replace('\x9d', 'o').replace('\x9e', 'o')
            text_str = (text_str
                        .replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                        .replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue'))
            return text_str
        
        # Clean and normalize the company name
        cleaned_company_name = clean_text(company_name)
        normalized_company_name = normalize_company_name(cleaned_company_name)
        
        cache_key = f"{normalized_company_name}_{country_name}"
        
        if cache_key in self.company_cache:
            return self.company_cache[cache_key]
        
        if country_name not in self.country_cache:
            country = db.query(Country).filter(Country.name == country_name).first()
            self.country_cache[country_name] = country
        
        country = self.country_cache[country_name]
        
        # Use the centralized normalized company function
        company = get_or_create_normalized_company(
            db=db,
            raw_company_name=cleaned_company_name,
            country_id=country.id,
            isin=isin,
            logger=self.logger
        )
        
        if not company:
            self.logger.error(f"Failed to create or find company '{cleaned_company_name}' in country '{country_name}'")
            raise Exception(f"Could not create company: {cleaned_company_name}")
        
        self.company_cache[cache_key] = company
        return company
    
    async def _log_scraping_success(self, country_code: str, positions_found: int, positions_added: int):
        """Log successful scraping"""
        db = next(get_db())
        try:
            country = db.query(Country).filter(Country.code == country_code).first()
            if not country:
                return
            
            log_entry = ScrapingLog(
                country_id=country.id,
                status="success",
                records_scraped=positions_found,
                error_message=None,
                completed_at=datetime.now()
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()
    
    async def _log_scraping_error(self, country_code: str, error_message: str):
        """Log scraping error"""
        db = next(get_db())
        try:
            country = db.query(Country).filter(Country.code == country_code).first()
            if not country:
                return
            
            log_entry = ScrapingLog(
                country_id=country.id,
                status="error",
                records_scraped=0,
                error_message=error_message,
                completed_at=datetime.now()
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()
    
    def get_scraping_status(self) -> Dict[str, Any]:
        """Get current scraping status and statistics"""
        db = next(get_db())
        try:
            recent_logs = db.query(ScrapingLog).filter(
                ScrapingLog.started_at >= datetime.now() - timedelta(days=7)
            ).order_by(ScrapingLog.started_at.desc()).all()
            
            country_stats = db.query(
                Country.name,
                Country.code,
                func.count(ShortPosition.id).label('total_positions')
            ).join(ShortPosition).group_by(Country.name, Country.code).all()
            
            return {
                'recent_logs': [
                    {
                        'country_code': log.country.code if getattr(log, 'country', None) else 'Unknown',
                        'status': log.status,
                        'positions_found': log.records_scraped,
                        'positions_added': log.records_scraped,  # not tracked separately here
                        'error_message': log.error_message,
                        'created_at': log.started_at.isoformat() if getattr(log, 'started_at', None) else None
                    }
                    for log in recent_logs
                ],
                'country_statistics': [
                    {
                        'country_name': stat.name,
                        'country_code': stat.code,
                        'total_positions': stat.total_positions
                    }
                    for stat in country_stats
                ],
                'last_update': datetime.now().isoformat()
            }
        finally:
            db.close()

