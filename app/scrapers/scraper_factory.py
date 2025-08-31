#!/usr/bin/env python3
"""
Scraper Factory for creating country-specific scrapers
"""

from typing import Optional
from .uk_scraper import UKScraper
from .germany_scraper import GermanyScraper
from .spain_scraper import SpainScraper
from .belgium_scraper import BelgiumScraper
from .ireland_scraper import IrelandScraper
from .italy_scraper import ItalyScraper
from .netherlands_scraper import NetherlandsScraper
from .france_scraper import FranceScraper
from .finland_selenium_scraper import FinlandSeleniumScraper
from .sweden_selenium_scraper import SwedenSeleniumScraper
from .norway_scraper import NorwayScraper
from .denmark_scraper import DenmarkScraper

class ScraperFactory:
    """Factory for creating country-specific scrapers"""
    
    def __init__(self):
        self.scrapers = {
            'GB': UKScraper,
            'DE': GermanyScraper,
            'ES': SpainScraper,
            'BE': BelgiumScraper,
            'IE': IrelandScraper,
            'IT': ItalyScraper,
            'NL': NetherlandsScraper,
            'FR': FranceScraper,
                                    'FI': FinlandSeleniumScraper,
                        'SE': SwedenSeleniumScraper,
                        'NO': NorwayScraper,
                        'DK': DenmarkScraper
        }
    
    def create_scraper(self, country_code: str):
        """Create a scraper for the given country code"""
        country_code = country_code.upper()
        
        if country_code not in self.scrapers:
            raise ValueError(f"No scraper available for country code: {country_code}")
        
        scraper_class = self.scrapers[country_code]
        
        # Map country codes to names
        country_names = {
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'ES': 'Spain',
            'BE': 'Belgium',
            'IE': 'Ireland',
            'IT': 'Italy',
            'NL': 'Netherlands',
            'FR': 'France',
                                    'FI': 'Finland',
                        'SE': 'Sweden',
                        'NO': 'Norway',
                        'DK': 'Denmark'
        }
        
        return scraper_class(country_code, country_names[country_code])
    
    def get_available_countries(self) -> list:
        """Get list of available country codes"""
        return list(self.scrapers.keys())
    
    def is_country_supported(self, country_code: str) -> bool:
        """Check if a country is supported"""
        return country_code.upper() in self.scrapers
