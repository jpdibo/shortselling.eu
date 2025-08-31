#!/usr/bin/env python3
"""Netherlands Short-selling Data Scraper"""

import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_scraper import BaseScraper
from urllib.parse import urljoin, urlparse, parse_qs
import re

class NetherlandsScraper(BaseScraper):
    """Scraper for Netherlands short-selling data from AFM"""
    
    def get_current_data_url(self) -> str:
        return "https://www.afm.nl/en/sector/registers/meldingenregisters/netto-shortposities-actueel"
    
    def get_historical_data_url(self) -> str:
        return "https://www.afm.nl/en/sector/registers/meldingenregisters/netto-shortposities-historie"
    
    def get_data_url(self) -> str:
        """Required by base class - returns current data URL"""
        return self.get_current_data_url()
    
    def _create_session(self) -> requests.Session:
        """Create a session with proper headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8',
        })
        return session
    
    def download_data(self) -> Dict[str, Any]:
        """Download Netherlands short-selling data from AFM"""
        self.logger.info("Starting scrape for Netherlands")
        self.logger.info("Downloading Netherlands AFM data")
        
        try:
            # Use a session to maintain state between requests
            session = self._create_session()
            
            # Download current data from current positions page
            self.logger.info("Downloading current positions data...")
            current_data = self._download_current_data(session)
            
            # Download historical data from historical positions page
            self.logger.info("Downloading historical positions data...")
            historical_data = self._download_historical_data(session)
            
            return {
                'current_data': current_data,
                'historical_data': historical_data,
                'source_url': self.get_current_data_url()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download AFM data: {e}")
            raise Exception(f"AFM download failed: {e}")
    
    def _download_current_data(self, session: requests.Session) -> pd.DataFrame:
        """Download current positions data from the current positions page"""
        current_url = self.get_current_data_url()
        self.logger.info(f"Accessing current positions page: {current_url}")
        
        response = session.get(current_url, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Failed to access current positions page: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the CSV download link
        csv_url = self._find_csv_download_url(soup, current_url)
        if not csv_url:
            raise Exception("Could not find CSV download URL on current positions page")
        
        self.logger.info(f"Found current CSV download URL: {csv_url}")
        
        # Download the CSV data
        return self._download_csv_data_with_session(session, csv_url, "current")
    
    def _download_historical_data(self, session: requests.Session) -> pd.DataFrame:
        """Download historical positions data from the historical positions page"""
        historical_url = self.get_historical_data_url()
        self.logger.info(f"Accessing historical positions page: {historical_url}")
        
        response = session.get(historical_url, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Failed to access historical positions page: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the CSV download link
        csv_url = self._find_csv_download_url(soup, historical_url)
        if not csv_url:
            raise Exception("Could not find CSV download URL on historical positions page")
        
        self.logger.info(f"Found historical CSV download URL: {csv_url}")
        
        # Download the CSV data
        return self._download_csv_data_with_session(session, csv_url, "historical")
    
    def _find_csv_download_url(self, soup: BeautifulSoup, base_url: str) -> str:
        """Find the CSV download URL from the page"""
        self.logger.info("Looking for CSV download link...")
        
        # Look for "Export as CSV" link
        csv_links = soup.find_all('a', href=True, string=re.compile(r'Export as CSV', re.I))
        if csv_links:
            href = csv_links[0].get('href')
            if href:
                if href.startswith('http'):
                    return href
                else:
                    return urljoin(base_url, href)
        
        # Look for any link containing 'export' and 'csv' in href
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'export' in href.lower() and 'csv' in href.lower():
                if href.startswith('http'):
                    return href
                else:
                    return urljoin(base_url, href)
        
        # Look for any link containing 'export.aspx' pattern
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'export.aspx' in href.lower():
                if href.startswith('http'):
                    return href
                else:
                    return urljoin(base_url, href)
        
        return None
    
    def _download_csv_data_with_session(self, session: requests.Session, csv_url: str, data_type: str) -> pd.DataFrame:
        """Download CSV data using a session to maintain state"""
        self.logger.info(f"Downloading {data_type} CSV data from: {csv_url}")
        
        try:
            response = session.get(csv_url, timeout=30)
            
            if response.status_code == 200:
                # Try to parse as CSV
                try:
                    from io import StringIO
                    # Handle BOM character and clean column names
                    df = pd.read_csv(StringIO(response.text), sep=';', encoding='utf-8')
                    
                    # Clean column names (remove BOM and quotes)
                    df.columns = df.columns.str.replace('ï»¿', '').str.replace('"', '').str.strip()
                    
                    self.logger.info(f"✅ Successfully downloaded {data_type} data: {len(df)} rows")
                    return df
                except Exception as e:
                    self.logger.warning(f"Failed to parse as CSV with semicolon separator: {e}")
                    
                    # Try with comma separator
                    try:
                        df = pd.read_csv(StringIO(response.text), sep=',', encoding='utf-8')
                        df.columns = df.columns.str.replace('ï»¿', '').str.replace('"', '').str.strip()
                        self.logger.info(f"✅ Successfully downloaded {data_type} data with comma separator: {len(df)} rows")
                        return df
                    except Exception as e2:
                        self.logger.warning(f"Failed to parse as CSV with comma separator: {e2}")
                        
                        # Try to parse as HTML table
                        soup = BeautifulSoup(response.content, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            df = pd.read_html(str(tables[0]))[0]
                            self.logger.info(f"✅ Successfully parsed {data_type} data as HTML table: {len(df)} rows")
                            return df
                        else:
                            # The response might be HTML but not contain tables
                            self.logger.info("Trying to extract data from HTML content...")
                            return self._extract_data_from_html(soup, data_type)
            else:
                raise Exception(f"CSV download failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to download {data_type} CSV data: {e}")
            return pd.DataFrame()
    

    
    def _extract_data_from_html(self, soup: BeautifulSoup, data_type: str) -> pd.DataFrame:
        """Extract data from HTML content when no tables are found"""
        self.logger.info(f"Extracting data from HTML content for {data_type} data")
        
        # Look for data in the HTML content
        data_rows = []
        
        # Look for div elements that might contain position data
        position_divs = soup.find_all('div', class_=re.compile(r'position|row|item', re.I))
        
        if position_divs:
            self.logger.info(f"Found {len(position_divs)} potential position divs")
            
            for div in position_divs:
                # Extract text content
                text = div.get_text(strip=True)
                if text and len(text) > 10:  # Filter out empty or very short content
                    data_rows.append({'content': text})
        
        # If no structured divs found, try to extract from the main content
        if not data_rows:
            main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main', re.I))
            if main_content:
                # Split content into lines and look for data patterns
                lines = main_content.get_text().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 20:  # Look for substantial lines
                        data_rows.append({'content': line})
        
        if data_rows:
            df = pd.DataFrame(data_rows)
            self.logger.info(f"Extracted {len(df)} rows from HTML content")
            return df
        else:
            self.logger.warning("No data found in HTML content")
            return pd.DataFrame()
    
    def parse_data(self, data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Parse the downloaded data"""
        self.logger.info("Parsing Netherlands AFM data")
        
        dataframes = {}
        
        # Parse current data
        if 'current_data' in data and not data['current_data'].empty:
            dataframes['current'] = data['current_data']
            self.logger.info(f"Parsed current data: {len(data['current_data'])} rows")
        
        # Parse historical data
        if 'historical_data' in data and not data['historical_data'].empty:
            dataframes['historical'] = data['historical_data']
            self.logger.info(f"Parsed historical data: {len(data['historical_data'])} rows")
        
        return dataframes
    
    def extract_positions(self, dataframes: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Extract position data from DataFrames"""
        all_positions = []
        
        for sheet_name, df in dataframes.items():
            self.logger.info(f"Extracting positions from {sheet_name} ({len(df)} rows)")
            
            # IMPORTANT: Don't just set is_active based on sheet name!
            # The "current" sheet contains both active AND historical positions
            # We need to apply proper logic after extraction
            
            # Map columns for Netherlands AFM data
            # Based on the search results, the columns are:
            # Position holder, Name of the issuer, ISIN, Net short position, Position date
            possible_columns = {
                'manager': ['Position holder', 'Positie houder', 'Position Owner', 'Owner', 'Manager', 'Holder'],
                'company': ['Name of the issuer', 'Name of share issuer', 'Naam van de emittent', 'Issuer', 'Company'],
                'isin': ['ISIN', 'Isin'],
                'position_size': ['Net short position', 'Netto Shortpositie', 'Position Size', 'Short Position'],
                'date': ['Position date', 'Positiedatum', 'Date', 'Position Date', 'Publication Date']
            }
            
            # Find the actual column names in this sheet
            column_mapping = {}
            for field, possible_names in possible_columns.items():
                for name in possible_names:
                    if name in df.columns:
                        column_mapping[field] = name
                        break
            
            # If we can't find the expected columns, try to infer from first few rows
            if not column_mapping:
                column_mapping = self._infer_columns(df)
            
            self.logger.info(f"Column mapping for {sheet_name}: {column_mapping}")
            
            # Vectorized processing - much faster than row by row
            if not df.empty and column_mapping:
                # Create a working copy
                working_df = df.copy()
                
                # Remove header and empty rows
                working_df = working_df[~working_df.apply(self._is_header_row, axis=1)]
                working_df = working_df[~working_df.apply(self._is_empty_row, axis=1)]
                
                if not working_df.empty:
                    # Basic cleaning only - let DailyScrapingService handle normalization
                    working_df['manager_name'] = working_df[column_mapping.get('manager', '')].fillna('').astype(str).str.strip()
                    working_df['company_name'] = working_df[column_mapping.get('company', '')].fillna('').astype(str).str.strip()
                    working_df['isin'] = working_df[column_mapping.get('isin', '')].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
                    working_df['isin'] = working_df['isin'].replace('', None)
                    
                    # Vectorized position size parsing
                    working_df['position_size'] = working_df[column_mapping.get('position_size', 0)].apply(self._parse_position_size)
                    
                    # Vectorized date parsing
                    working_df['date'] = working_df[column_mapping.get('date', '')].apply(self._parse_date)
                    
                    # Add sheet source for later processing
                    working_df['source_sheet'] = sheet_name
                    
                    # Convert to list of dictionaries (without is_active for now)
                    sheet_positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'source_sheet']].to_dict('records')
                    
                    # Filter valid positions
                    valid_positions = [pos for pos in sheet_positions if self.validate_position(pos)]
                    all_positions.extend(valid_positions)
                    
                    self.logger.info(f"Extracted {len(valid_positions)} valid positions from {sheet_name}")
        
        # Apply Netherlands-specific active logic
        all_positions = self._apply_netherlands_active_logic(all_positions)
        
        self.logger.info(f"Extracted {len(all_positions)} total positions from Netherlands data")
        return all_positions
    
    def _apply_netherlands_active_logic(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Netherlands logic:
        - Historical sheet: All positions are is_active=False
        - Current sheet: Contains both active and historical positions
          - Only the most recent position per (manager, company/ISIN) is is_active=True
          - All other positions in current sheet are is_active=False
        """
        self.logger.info("Applying Netherlands-specific active logic...")
        
        if not positions:
            return positions
        
        import pandas as pd
        df = pd.DataFrame(positions)
        
        # Basic cleaning only - let DailyScrapingService handle normalization
        df['isin'] = df['isin'].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
        df['company_name'] = df['company_name'].fillna('').astype(str).str.strip()
        df['manager_name'] = df['manager_name'].fillna('').astype(str).str.strip()
        
        # Create unique key for each (manager, company/ISIN) combination
        df['manager_company_key'] = df.apply(
            lambda row: f"{row['manager_name']}_{row['isin'] if row['isin'] else row['company_name']}",
            axis=1
        )
        
        # Convert dates to datetime for proper sorting
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by manager_company_key, then by date (newest first)
        df = df.sort_values(['manager_company_key', 'date'], ascending=[True, False])
        
        # Initialize is_active to False for all positions
        df['is_active'] = False
        
        # Process by source sheet
        for sheet_name in df['source_sheet'].unique():
            sheet_df = df[df['source_sheet'] == sheet_name]
            
            if sheet_name.lower() == 'historical':
                # Historical sheet: All positions remain is_active=False
                self.logger.info(f"Historical sheet: All {len(sheet_df)} positions set to is_active=False")
                
            elif sheet_name.lower() == 'current':
                # Current sheet: Only most recent per (manager, company) is active
                # Get the most recent position for each manager_company_key
                most_recent_indices = sheet_df.groupby('manager_company_key')['date'].idxmax()
                
                # Set is_active=True only for the most recent positions
                df.loc[most_recent_indices, 'is_active'] = True
                
                active_count = len(most_recent_indices)
                total_count = len(sheet_df)
                self.logger.info(f"Current sheet: {active_count}/{total_count} positions set to is_active=True (most recent per manager/company)")
        
        # Convert back to list of dictionaries
        result = df.drop(columns=['manager_company_key', 'source_sheet']).to_dict('records')
        
        total_active = sum(1 for p in result if p['is_active'])
        self.logger.info(f"Netherlands active logic applied: {total_active}/{len(result)} positions marked as active")
        
        return result
    
    def _infer_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer column mapping from DataFrame content"""
        column_mapping = {}
        
        # Look for columns that contain typical data patterns
        for col in df.columns:
            col_str = str(col).lower()
            
            # Check for manager/position owner columns
            if any(keyword in col_str for keyword in ['owner', 'manager', 'holder', 'position']):
                if 'position' in col_str and 'owner' in col_str:
                    column_mapping['manager'] = col
            
            # Check for company/issuer columns
            elif any(keyword in col_str for keyword in ['issuer', 'company', 'name']):
                column_mapping['company'] = col
            
            # Check for ISIN columns
            elif 'isin' in col_str:
                column_mapping['isin'] = col
            
            # Check for position size columns
            elif any(keyword in col_str for keyword in ['position', 'size', 'short']):
                if 'position' in col_str and 'size' not in col_str:
                    column_mapping['position_size'] = col
            
            # Check for date columns
            elif any(keyword in col_str for keyword in ['date', 'publication']):
                column_mapping['date'] = col
        
        return column_mapping
    
    def _parse_position_size(self, value) -> float:
        """Parse position size value, handling different formats"""
        try:
            if pd.isna(value):
                return 0.0
            
            # Convert to string and clean
            value_str = str(value).strip()
            
            # Remove percentage signs and convert comma to dot
            value_str = value_str.replace('%', '').replace(',', '.')
            
            # Convert to float
            return float(value_str)
        except:
            return 0.0
    
    def _parse_date(self, value) -> pd.Timestamp:
        """Parse date value"""
        try:
            if pd.isna(value):
                return None
            
            # Handle Dutch date format (DD MMM YYYY or YYYY-MM-DD)
            return pd.to_datetime(value)
        except:
            return None
    
    def _is_header_row(self, row) -> bool:
        """Check if row is a header row"""
        if len(row) == 0:
            return True
        
        first_value = str(row.iloc[0]).lower()
        header_keywords = ['position holder', 'issuer', 'isin', 'position', 'date', 'owner', 'manager']
        return any(keyword in first_value for keyword in header_keywords)
    
    def _is_empty_row(self, row) -> bool:
        """Check if row is empty"""
        return row.isna().all() or (row == '').all()
