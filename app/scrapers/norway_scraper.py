#!/usr/bin/env python3
"""
Norway Short-Selling Scraper for Complete Historical Data Collection

Fetches comprehensive historical data from Finanstilsynet (Financial Supervisory Authority of Norway)
using Selenium web scraping to get the full historical dataset.

NOTE: API functionality has been moved to norway_api_updater.py
REASON: The API only provides ~1 year of historical data, insufficient for complete analysis.
        This scraper focuses on comprehensive historical scraping via Selenium.
        
USAGE: Use this scraper for initial historical data collection.
       Use norway_api_updater.py later for daily/weekly maintenance updates.
"""

import sys
import os
sys.path.append('..')

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_scraper import BaseScraper

class NorwayScraper(BaseScraper):
    """Scraper for Norwegian short-selling data from Finanstilsynet"""
    
    def __init__(self, country_code: str = "NO", country_name: str = "Norway"):
        super().__init__(country_code, country_name)
        
    def get_data_url(self) -> str:
        """Get the main data source URL"""
        return "https://ssr.finanstilsynet.no/"
    
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        return driver
    
    def download_data(self) -> Dict[str, Any]:
        """Download comprehensive historical data from Norway using Selenium web scraping"""
        self.logger.info("Starting comprehensive Norway historical data collection")
        self.logger.info("Using Selenium web scraping for complete dataset (not limited API)")
        
        driver = None
        try:
            # Setup Selenium driver
            driver = self._setup_driver()
            
            # Get the main page to find current positions
            main_url = self.get_data_url()
            self.logger.info(f"Navigating to: {main_url}")
            
            driver.get(main_url)
            time.sleep(5)  # Wait for page to load
            
            # Wait for the table to load with data
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                self.logger.info("Main table loaded successfully")
            except TimeoutException:
                self.logger.warning("Timeout waiting for main table to load")
            
            # Get the page source after JavaScript has loaded
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract current positions from the main table
            current_positions = self._extract_current_positions(soup)
            
            # Get comprehensive historical data for each stock (this is the key part!)
            detailed_data = self._get_detailed_historical_data(current_positions, driver)
            
            return {
                'current_positions': current_positions,
                'detailed_data': detailed_data,
                'source_url': main_url,
                'method': 'Comprehensive Selenium Scraping',
                'download_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive scraping: {e}")
            raise
        finally:
            if driver:
                driver.quit()
    
    def _extract_current_positions(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract current positions from the main page table"""
        self.logger.info("Extracting current positions from main page")
        
        positions = []
        
        try:
            # Find the main table with current positions
            table = soup.find('table')
            if not table:
                self.logger.warning("No table found on main page")
                return positions
            
            # Find all rows in the table
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 5:
                    try:
                        # Extract data from cells
                        isin = cells[0].get_text(strip=True)
                        name = cells[1].get_text(strip=True)
                        sum_short_num = cells[2].get_text(strip=True)
                        sum_short_percent = cells[3].get_text(strip=True)
                        latest_position = cells[4].get_text(strip=True)
                        
                        # Skip if no meaningful data
                        if not isin or isin == '-':
                            continue
                        
                        # Get the detail page URL
                        detail_link = row.find('a')
                        detail_url = None
                        if detail_link and detail_link.get('href'):
                            detail_url = detail_link.get('href')
                            if not detail_url.startswith('http'):
                                detail_url = f"https://ssr.finanstilsynet.no{detail_url}"
                        
                        positions.append({
                            'isin': isin,
                            'company_name': name,
                            'sum_short_num': sum_short_num,
                            'sum_short_percent': sum_short_percent,
                            'latest_position': latest_position,
                            'detail_url': detail_url
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Error parsing row: {e}")
                        continue
            
            self.logger.info(f"Extracted {len(positions)} current positions")
            return positions
            
        except Exception as e:
            self.logger.error(f"Error extracting current positions: {e}")
            return []
    
    
    def _get_detailed_historical_data(self, current_positions: List[Dict[str, Any]], driver) -> List[Dict[str, Any]]:
        """Get detailed historical data for each stock"""
        self.logger.info("Getting detailed historical data...")
        
        detailed_data = []
        
        for i, position in enumerate(current_positions):
            try:
                detail_url = position.get('detail_url')
                if not detail_url:
                    continue
                
                self.logger.info(f"Processing {i+1}/{len(current_positions)}: {position.get('company_name', 'Unknown')}")
                
                # Navigate to detail page
                driver.get(detail_url)
                time.sleep(3)
                
                # Wait for detail table
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                except TimeoutException:
                    self.logger.warning(f"Timeout waiting for detail table: {position.get('company_name')}")
                    continue
                
                # Parse detail page
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract positions from detail table
                detail_positions = self._extract_detail_positions(soup, position)
                detailed_data.extend(detail_positions)
                
                # Small delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing {position.get('company_name')}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(detailed_data)} detailed positions")
        return detailed_data
    
    def _extract_detail_positions(self, soup: BeautifulSoup, position: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract positions from detail page - handles Active and Historical sections separately"""
        positions = []
        
        try:
            # Look for "Active positions" section
            active_positions = self._extract_positions_by_section(soup, "active", position)
            positions.extend(active_positions)
            
            # Look for "Historical positions" section  
            historical_positions = self._extract_positions_by_section(soup, "historical", position)
            positions.extend(historical_positions)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error extracting detail positions: {e}")
            return []
    
    def _extract_positions_by_section(self, soup: BeautifulSoup, section_type: str, position: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract positions from a specific section (active or historical) - ROBUST VERSION"""
        positions = []
        is_active = (section_type == "active")  # Active table = is_active=True, Historical table = is_active=False
        
        try:
            # ROBUST APPROACH: Find tables by checking their previous siblings for section names
            # Based on HTML structure analysis: each table has a previous sibling div containing the section name
            
            section_keywords = {
                "active": ["active positions", "current positions", "active"],
                "historical": ["historical positions", "historic positions", "historical", "historic"]
            }
            
            keywords = section_keywords[section_type]
            tables = soup.find_all('table')
            section_found = False
            
            for table in tables:
                # Check previous siblings for section indicators
                current_element = table.find_previous_sibling()
                
                # Look through a few previous siblings
                for _ in range(5):  # Check up to 5 previous siblings
                    if current_element:
                        sibling_text = current_element.get_text(strip=True).lower()
                        
                        # Check if this sibling contains our section keywords
                        if any(keyword in sibling_text for keyword in keywords):
                            section_found = True
                            self.logger.info(f"Found {section_type} table via previous sibling: '{current_element.get_text(strip=True)}'")
                            
                            # Parse this table
                            section_positions = self._parse_table_positions(table, position, is_active)
                            positions.extend(section_positions)
                            self.logger.info(f"Extracted {len(section_positions)} {section_type} positions")
                            break
                        
                        current_element = current_element.find_previous_sibling()
                    else:
                        break
                
                if section_found:
                    break
            
            if not section_found:
                if section_type == "active":
                    self.logger.info("No active positions table found - this is normal for some companies")
                else:
                    self.logger.info("No historical positions table found - this is normal for some companies")
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error extracting {section_type} positions: {e}")
            return []
    
    def _find_table_after_element(self, element):
        """Find the first table that appears after the given element"""
        try:
            # Look for table as next sibling or descendant
            current = element
            while current:
                # Check if current element is or contains a table
                if current.name == 'table':
                    return current
                
                table = current.find('table')
                if table:
                    return table
                
                # Move to next sibling
                current = current.find_next_sibling()
                if current and current.name == 'table':
                    return current
                elif current:
                    table = current.find('table')
                    if table:
                        return table
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding table after element: {e}")
            return None
    
    def _parse_table_positions(self, table, position: Dict[str, Any], is_active: bool) -> List[Dict[str, Any]]:
        """Parse positions from a table"""
        positions = []
        
        try:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip headers
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    try:
                        # Extract position data - CORRECT COLUMN ORDER
                        manager_name = cells[0].get_text(strip=True)        # 1. Manager name
                        short_position = cells[1].get_text(strip=True)      # 2. Short position (irrelevant)  
                        position_size = cells[2].get_text(strip=True)       # 3. Short percent (VERY RELEVANT)
                        date_str = cells[3].get_text(strip=True)            # 4. Date (position_start_date)
                        
                        # Parse date - try multiple formats
                        date = None
                        for date_format in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                            try:
                                date = datetime.strptime(date_str, date_format).date()
                                break
                            except ValueError:
                                continue
                        
                        if date is None:
                            self.logger.warning(f"Invalid date format, skipping row: '{date_str}'")
                            continue
                        
                        # Parse position size - handle special values
                        try:
                            # Handle special cases like "< 0,5%" or "-"
                            if position_size.strip() == '-' or '< ' in position_size:
                                size = 0.0  # Treat as zero position
                            else:
                                size = float(position_size.replace('%', '').replace(',', '.').replace('<', '').strip())
                        except ValueError:
                            self.logger.debug(f"Could not parse position size '{position_size}', setting to 0.0")
                            size = 0.0
                        
                        # VALIDATION: Skip invalid/meaningless rows
                        
                        # 1. Skip if no meaningful manager name (empty, company names, etc.)
                        if not manager_name or manager_name.strip() == '':
                            continue
                        
                        # 2. Skip "SUM" rows in active tables (always last row in active section)
                        if manager_name.upper().strip() in ['SUM', 'TOTAL', 'SUMMARY']:
                            self.logger.info(f"Skipping SUM/TOTAL row: {manager_name}")
                            continue
                        
                        # 3. Skip if position size is negative (invalid)
                        if size < 0.0:
                            self.logger.debug(f"Skipping negative position: {manager_name} - {size}%")
                            continue
                        
                        # 4. Skip if date parsing failed (already handled above with continue)
                        
                        positions.append({
                            'date': date,
                            'company_name': position.get('company_name', ''),
                            'isin': position.get('isin', ''),
                            'manager_name': manager_name,
                            'position_size': size,
                            'short_position': short_position,  # Column 2 data
                            'is_active': is_active  # ← NOW PROPERLY SET: True for active table, False for historical table
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Error parsing table row: {e}")
                        continue
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error parsing table positions: {e}")
            return []
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse downloaded data into DataFrame"""
        self.logger.info("Parsing Norway data...")
        
        all_positions = []
        
        # Parse API positions
        api_positions = data.get('api_positions', [])
        for pos in api_positions:
            pos['data_type'] = 'api'
            all_positions.append(pos)
        
        # Parse manual positions
        detailed_data = data.get('detailed_data', [])
        for pos in detailed_data:
            pos['data_type'] = 'manual'
            all_positions.append(pos)
        
        if not all_positions:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_positions)
        
        # Add metadata
        df['country_code'] = self.country_code
        df['country_name'] = self.country_name
        df['source_url'] = data.get('source_url', '')
        df['download_date'] = data.get('download_date', '')
        
        self.logger.info(f"Parsed {len(df)} positions")
        return df
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract positions from DataFrame"""
        if df.empty:
            return []
        
        positions = []
        
        for _, row in df.iterrows():
            try:
                position = {
                    'date': row['date'],
                    'company_name': row['company_name'],
                    'isin': row['isin'],
                    'manager_name': row['manager_name'],
                    'position_size': row['position_size'],
                    'is_active': row.get('is_active', True),  # Use is_active instead of is_current
                    'country_code': self.country_code
                }
                positions.append(position)
            except Exception as e:
                self.logger.warning(f"Error extracting position: {e}")
                continue
        
        return positions
    
    # Database operations removed - handled by DailyScrapingService

# Main execution removed - use DailyScrapingService instead
