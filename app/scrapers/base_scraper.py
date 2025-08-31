#!/usr/bin/env python3
"""
Base scraper class for all country-specific scrapers

IMPORTANT: Each scraper downloads ALL available data from its respective regulator.
The DailyScrapingService then filters this data to only add the most recent data
that is not already in our database, preventing duplicate imports.
"""

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import time
import random

class BaseScraper(ABC):
    """Abstract base class for all country scrapers"""
    
    def __init__(self, country_code: str, country_name: str):
        self.country_code = country_code
        self.country_name = country_name
        self.session = requests.Session()
        self.logger = logging.getLogger(f"scraper.{country_code}")
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    @abstractmethod
    def get_data_url(self) -> str:
        """Return the URL where short-selling data can be found"""
        pass
    
    @abstractmethod
    def download_data(self) -> Any:
        """Download the data from the source"""
        pass
    
    @abstractmethod
    def parse_data(self, data: Any) -> pd.DataFrame:
        """Parse the downloaded data into a pandas DataFrame (or dict of DataFrames)"""
        pass
    
    @abstractmethod
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract position data from DataFrame into standardized format"""
        pass
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method - orchestrates the entire scraping process"""
        try:
            self.logger.info(f"Starting scrape for {self.country_name}")
            
            # Step 1: Download data
            data = self.download_data()
            
            # Step 2: Parse data
            df = self.parse_data(data)
            
            # Step 3: Extract positions
            positions = self.extract_positions(df)
            
            self.logger.info(f"Successfully scraped {len(positions)} positions for {self.country_name}")
            return positions
            
        except Exception as e:
            self.logger.error(f"Error scraping {self.country_name}: {str(e)}")
            raise
    
    def download_with_retry(self, url: str, max_retries: int = 3) -> requests.Response:
        """Download content with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(random.uniform(1, 3))  # Random delay between retries
    
    def validate_position(self, position: Dict[str, Any]) -> bool:
        """
        Validate a single position.

        Key fixes:
        - Allow position_size == 0.0 (zero is valid).
        - Still require manager_name, company_name, date.
        - position_size must be numeric and 0 <= size <= 100.
        """
        # Manager and company must be non-empty strings
        if not position.get('manager_name'):
            return False
        if not position.get('company_name'):
            return False

        # Date must exist and not be in the future
        date_val = position.get('date')
        if not date_val:
            return False
        try:
            date_obj = pd.to_datetime(date_val)
            if date_obj > datetime.now():
                return False
        except Exception:
            return False

        # position_size must be present and numeric; zero is allowed
        if 'position_size' not in position:
            return False
        try:
            size = float(position['position_size'])
        except (TypeError, ValueError):
            return False
        if not (0.0 <= size <= 100.0):
            return False

        return True
    
    def standardize_position(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize position data format with proper normalization"""
        # Import here to avoid circular imports
        from ..services.daily_scraping_service import normalize_company_name, normalize_manager_name
        
        return {
            'manager_name': normalize_manager_name(str(position.get('manager_name', '')).strip()),
            'company_name': normalize_company_name(str(position.get('company_name', '')).strip()),
            'isin': str(position.get('isin', '')).strip() if position.get('isin') else None,
            'position_size': float(position.get('position_size', 0)),
            'date': position.get('date'),
            'is_active': position.get('is_active', True),  # Default to active
            'country_code': self.country_code
        }

