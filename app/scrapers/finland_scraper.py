#!/usr/bin/env python3
"""
Finland Short-Selling Scraper
Fetches data from FIN-FSA (Financial Supervisory Authority of Finland)
"""

import requests
import pandas as pd
import io
import logging
from datetime import datetime
from typing import Dict, Any, List
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class FinlandScraper(BaseScraper):
    """Scraper for Finnish short-selling data from FIN-FSA"""
    
    def __init__(self, country_code: str = "FI", country_name: str = "Finland"):
        super().__init__(country_code, country_name)
        
    def get_data_url(self) -> str:
        """Get the main data source URL"""
        return "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions"
    
    def get_current_positions_url(self) -> str:
        """Get the current net short positions URL"""
        return "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions/Current-net-short-positions/"
    
    def get_historic_positions_url(self) -> str:
        """Get the historic net short positions URL"""
        return "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions/Historic-net-short-positions/"
    
    def download_data(self) -> Dict[str, Any]:
        """Download Finnish short-selling data from FIN-FSA"""
        self.logger.info("Starting scrape for Finland")
        self.logger.info("Downloading Finland FIN-FSA data")
        
        try:
            # Download current positions
            current_url = self.get_current_positions_url()
            self.logger.info(f"Fetching current positions from: {current_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,fi;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Get current positions page
            current_response = requests.get(current_url, headers=headers, timeout=60)
            if current_response.status_code != 200:
                raise Exception(f"Failed to fetch current positions: {current_response.status_code}")
            
            self.logger.info(f"Successfully downloaded current positions page ({len(current_response.content)} bytes)")
            
            # Download historic positions
            historic_url = self.get_historic_positions_url()
            self.logger.info(f"Fetching historic positions from: {historic_url}")
            
            historic_response = requests.get(historic_url, headers=headers, timeout=60)
            if historic_response.status_code != 200:
                raise Exception(f"Failed to fetch historic positions: {historic_response.status_code}")
            
            self.logger.info(f"Successfully downloaded historic positions page ({len(historic_response.content)} bytes)")
            
            return {
                'current_page': current_response.content,
                'historic_page': historic_response.content,
                'current_url': current_url,
                'historic_url': historic_url,
                'source_url': self.get_data_url(),
                'download_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download Finland data: {e}")
            raise Exception(f"Finland download failed: {e}")
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse the downloaded HTML data"""
        self.logger.info("Parsing Finland HTML data")
        
        try:
            all_dataframes = []
            
            # Parse current positions
            current_soup = BeautifulSoup(data['current_page'], 'html.parser')
            current_df = self._parse_html_table(current_soup, "current")
            if current_df is not None and len(current_df) > 0:
                current_df['data_type'] = 'current'
                all_dataframes.append(current_df)
                self.logger.info(f"Parsed {len(current_df)} current positions")
            
            # Parse historic positions
            historic_soup = BeautifulSoup(data['historic_page'], 'html.parser')
            historic_df = self._parse_html_table(historic_soup, "historic")
            if historic_df is not None and len(historic_df) > 0:
                historic_df['data_type'] = 'historic'
                all_dataframes.append(historic_df)
                self.logger.info(f"Parsed {len(historic_df)} historic positions")
            
            if not all_dataframes:
                self.logger.warning("No data found in HTML pages")
                return pd.DataFrame()
            
            # Combine all dataframes
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            self.logger.info(f"Combined {len(combined_df)} total positions from Finland data")
            
            return combined_df
            
        except Exception as e:
            self.logger.error(f"Failed to parse Finland data: {e}")
            raise Exception(f"Finland data parsing failed: {e}")
    
    def _parse_html_table(self, soup: BeautifulSoup, data_type: str) -> pd.DataFrame:
        """Parse HTML table from BeautifulSoup object"""
        try:
            # Look for tables in the HTML
            tables = soup.find_all('table')
            
            if not tables:
                self.logger.warning(f"No tables found in {data_type} page")
                return pd.DataFrame()
            
            # Try to find the main data table
            for table in tables:
                # Look for table with typical short position columns
                headers = []
                header_row = table.find('thead')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                else:
                    # Try first row as headers
                    first_row = table.find('tr')
                    if first_row:
                        headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                
                # Check if this looks like a short positions table
                if any(keyword in ' '.join(headers).lower() for keyword in ['position', 'issuer', 'company', 'isin', 'date', 'percentage']):
                    self.logger.info(f"Found potential short positions table in {data_type} page")
                    
                    # Parse table rows
                    rows = []
                    table_rows = table.find_all('tr')[1:] if header_row else table.find_all('tr')  # Skip header if found
                    
                    for row in table_rows:
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if len(row_data) >= 3:  # At least some meaningful data
                                rows.append(row_data)
                    
                    if rows:
                        # Create DataFrame
                        df = pd.DataFrame(rows, columns=headers[:len(rows[0])] if len(headers) >= len(rows[0]) else [f'col_{i}' for i in range(len(rows[0]))])
                        return df
            
            self.logger.warning(f"No suitable table found in {data_type} page")
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Error parsing {data_type} table: {e}")
            return pd.DataFrame()
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract short positions from parsed data"""
        self.logger.info("Extracting positions from Finland data")
        
        positions = []
        
        try:
            if df.empty:
                self.logger.warning("No data to extract positions from")
                return positions
            
            # Try to identify columns based on common patterns
            column_mapping = self._identify_columns(df)
            
            if not column_mapping:
                self.logger.warning("Could not identify required columns")
                return positions
            
            self.logger.info(f"Using column mapping: {column_mapping}")
            
            # Vectorized processing - much faster than row by row
            if not df.empty:
                # Create working copy
                working_df = df.copy()
                
                # Basic cleaning only - let DailyScrapingService handle normalization
                working_df['manager_name'] = working_df[column_mapping.get('manager', '')].fillna('').astype(str).str.strip()
                working_df['company_name'] = working_df[column_mapping.get('company', '')].fillna('').astype(str).str.strip()
                working_df['isin'] = working_df[column_mapping.get('isin', '')].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
                working_df['isin'] = working_df['isin'].replace('', '').replace('nan', '')
                
                # Filter out rows with missing essential data
                working_df = working_df[
                    (working_df['manager_name'] != '') & 
                    (working_df['manager_name'] != 'nan') & 
                    (working_df['company_name'] != '') & 
                    (working_df['company_name'] != 'nan')
                ]
                
                if not working_df.empty:
                    # Vectorized position size parsing
                    working_df['position_size'] = working_df[column_mapping.get('position_size', '')].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
                    
                    # Vectorized date parsing
                    working_df['date'] = pd.to_datetime(working_df[column_mapping.get('date', '')], errors='coerce')
                    working_df['date'] = working_df['date'].fillna(datetime.now().date())
                    working_df['date'] = working_df['date'].dt.date
                    
                    # Add is_active column
                    working_df['is_active'] = working_df.get('data_type', '') == 'current'
                    
                    # Convert to list of dictionaries
                    positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'is_active']].to_dict('records')
            
            self.logger.info(f"Extracted {len(positions)} positions from Finland data")
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to extract Finland positions: {e}")
            raise Exception(f"Finland position extraction failed: {e}")
    
    def _identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify column mapping based on column names"""
        column_mapping = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Manager/Position holder
            if any(keyword in col_lower for keyword in ['manager', 'holder', 'investor', 'participant']):
                column_mapping['manager'] = col
            
            # Company/Issuer
            elif any(keyword in col_lower for keyword in ['company', 'issuer', 'emitter', 'name']):
                column_mapping['company'] = col
            
            # ISIN
            elif 'isin' in col_lower:
                column_mapping['isin'] = col
            
            # Position size
            elif any(keyword in col_lower for keyword in ['position', 'percentage', 'size', 'amount']):
                column_mapping['position_size'] = col
            
            # Date
            elif any(keyword in col_lower for keyword in ['date', 'time', 'when']):
                column_mapping['date'] = col
        
        return column_mapping
