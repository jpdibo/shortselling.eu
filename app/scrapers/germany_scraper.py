#!/usr/bin/env python3
"""Germany Short-selling Data Scraper"""

import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_scraper import BaseScraper
from urllib.parse import urljoin, urlparse, parse_qs
import re

class GermanyScraper(BaseScraper):
    """Scraper for Germany short-selling data from Bundesanzeiger"""
    
    def get_data_url(self) -> str:
        return "https://www.bundesanzeiger.de/pub/en/nlp?4"
    
    def download_data(self) -> Dict[str, Any]:
        """Download Germany short-selling data from Bundesanzeiger"""
        self.logger.info("Starting scrape for Germany")
        self.logger.info("Downloading Germany Bundesanzeiger data")
        
        try:
            # Use a session to maintain state between requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            })
            
            # First, get the main page to understand the structure
            main_url = self.get_data_url()
            self.logger.info(f"Accessing main page: {main_url}")
            
            response = session.get(main_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Failed to access main page: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the CSV download link
            csv_download_url = self._find_csv_download_url(soup, main_url)
            if not csv_download_url:
                raise Exception("Could not find CSV download URL")
            
            self.logger.info(f"Found CSV download URL: {csv_download_url}")
            
            # Download current data using session
            current_data = self._download_csv_data_with_session(session, csv_download_url, "current")
            
            # Try to get historical data using session
            historical_data = self._download_historical_data_with_session(session, soup, main_url)
            
            return {
                'current_data': current_data,
                'historical_data': historical_data,
                'source_url': main_url,
                'csv_url': csv_download_url
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download Bundesanzeiger data: {e}")
            raise Exception(f"Bundesanzeiger download failed: {e}")
    
    def _find_csv_download_url(self, soup: BeautifulSoup, base_url: str) -> str:
        """Find the CSV download URL from the page"""
        self.logger.info("Looking for CSV download link...")
        
        # Look for "Download as CSV" link
        csv_links = soup.find_all('a', href=True, string=re.compile(r'Download as CSV', re.I))
        if csv_links:
            href = csv_links[0].get('href')
            if href:
                if href.startswith('http'):
                    return href
                else:
                    return urljoin(base_url, href)
        
        # Look for any link containing 'csv' in href
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'csv' in href.lower():
                if href.startswith('http'):
                    return href
                else:
                    return urljoin(base_url, href)
        
        # Try the known CSV URL pattern
        known_csv_url = "https://www.bundesanzeiger.de/pub/en/nlp?0--top~csv~form~panel-form-csv~resource~link"
        self.logger.info(f"Trying known CSV URL: {known_csv_url}")
        
        test_response = requests.get(known_csv_url, timeout=10)
        if test_response.status_code == 200:
            return known_csv_url
        
        return None
    
    def _download_csv_data(self, csv_url: str, data_type: str) -> pd.DataFrame:
        """Download CSV data from the given URL"""
        self.logger.info(f"Downloading {data_type} CSV data from: {csv_url}")
        
        try:
            response = self.download_with_retry(csv_url)
            
            if response.status_code == 200:
                # Try to parse as CSV
                try:
                    from io import BytesIO
                    # Handle BOM character and clean column names with proper encoding
                    df = pd.read_csv(BytesIO(response.content), encoding='utf-8')
                    
                    # Clean column names (remove BOM and quotes)
                    df.columns = df.columns.str.replace('ï»¿', '').str.replace('"', '').str.strip()
                    
                    self.logger.info(f"✅ Successfully downloaded {data_type} data: {len(df)} rows")
                    return df
                except Exception as e:
                    self.logger.warning(f"Failed to parse as CSV: {e}")
                    
                    # Try to parse as HTML table
                    soup = BeautifulSoup(response.content, 'html.parser')
                    tables = soup.find_all('table')
                    if tables:
                        df = pd.read_html(str(tables[0]))[0]
                        self.logger.info(f"✅ Successfully parsed {data_type} data as HTML table: {len(df)} rows")
                        return df
                    else:
                        # The response might be HTML but not contain tables
                        # Let's try to extract data from the HTML content
                        self.logger.info("Trying to extract data from HTML content...")
                        return self._extract_data_from_html(soup, data_type)
            else:
                raise Exception(f"CSV download failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to download {data_type} CSV data: {e}")
            return pd.DataFrame()
    
    def _download_historical_data(self, soup: BeautifulSoup, base_url: str) -> pd.DataFrame:
        """Try to download historical data by enabling the historical data option"""
        self.logger.info("Attempting to download historical data...")
        
        try:
            # Step 1: Find the filter form (this is the "More search options" form)
            filter_form = soup.find('form', attrs={'action': re.compile(r'filter', re.I)})
            
            if not filter_form:
                # Try to find any form that might be the search/filter form
                forms = soup.find_all('form')
                for form in forms:
                    action = form.get('action', '')
                    if 'filter' in action.lower() or 'nlp' in action.lower():
                        filter_form = form
                        break
            
            if not filter_form:
                self.logger.warning("Could not find filter form")
                return pd.DataFrame()
            
            self.logger.info(f"Found filter form: {filter_form.get('action', 'Unknown')}")
            
            # Step 2: Build form data with historical checkbox enabled
            form_data = self._build_historical_form_data(soup, filter_form)
            
            if not form_data:
                self.logger.warning("Could not build form data")
                return pd.DataFrame()
            
            self.logger.info(f"Form data prepared: {list(form_data.keys())}")
            
            # Step 3: Submit the form (this simulates clicking "More search options" and enabling historical data)
            form_action = filter_form.get('action', '')
            if not form_action.startswith('http'):
                form_action = urljoin(base_url, form_action)
            
            self.logger.info(f"Submitting form to: {form_action}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
                'Referer': base_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            historical_response = requests.post(form_action, data=form_data, headers=headers, timeout=30)
            
            if historical_response.status_code != 200:
                self.logger.error(f"Form submission failed: {historical_response.status_code}")
                return pd.DataFrame()
            
            self.logger.info("✅ Form submitted successfully")
            
            # Step 4: Parse the response and find the CSV download link
            historical_soup = BeautifulSoup(historical_response.content, 'html.parser')
            
            # Look for CSV download link in the response
            historical_csv_url = self._find_csv_download_url(historical_soup, form_action)
            
            if historical_csv_url:
                self.logger.info(f"Found historical CSV URL: {historical_csv_url}")
                
                # Check if this URL is different from the current one
                current_csv_url = "https://www.bundesanzeiger.de/pub/en/nlp?0--top~csv~form~panel-form-csv~resource~link"
                if historical_csv_url != current_csv_url:
                    self.logger.info("✅ Historical CSV URL is different from current URL")
                    return self._download_csv_data(historical_csv_url, "historical")
                else:
                    self.logger.warning("⚠️ Historical CSV URL is the same as current URL - may not contain historical data")
                    # Try to download anyway to see if the content is different
                    return self._download_csv_data(historical_csv_url, "historical")
            else:
                self.logger.warning("No CSV download link found in historical response")
                return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Failed to download historical data: {e}")
            return pd.DataFrame()
    
    def _build_historical_form_data(self, soup: BeautifulSoup, form) -> Dict[str, str]:
        """Build form data for historical data request"""
        form_data = {}
        
        # Get all form inputs
        for input_tag in form.find_all('input'):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            input_type = input_tag.get('type', 'text')
            
            if input_type == 'checkbox':
                # Check the historical data checkbox
                if 'historic' in str(name).lower() or 'history' in str(name).lower():
                    form_data[name] = 'on'
                    self.logger.info(f"Enabled historical checkbox: {name}")
                else:
                    # Keep other checkboxes as they were
                    if input_tag.get('checked'):
                        form_data[name] = 'on'
            else:
                if name:
                    form_data[name] = value
        
        # Get all select elements
        for select_tag in form.find_all('select'):
            name = select_tag.get('name')
            if name:
                selected_option = select_tag.find('option', selected=True)
                if selected_option:
                    form_data[name] = selected_option.get('value', '')
        
        # Look for the historical checkbox specifically
        historical_checkbox = soup.find('input', attrs={'name': 'isHistorical'})
        if historical_checkbox:
            form_data['isHistorical'] = 'on'
            self.logger.info("Added isHistorical checkbox to form data")
        
        self.logger.info(f"Built form data with {len(form_data)} fields")
        return form_data
    
    def _download_csv_data_with_session(self, session: requests.Session, csv_url: str, data_type: str) -> pd.DataFrame:
        """Download CSV data using a session to maintain state"""
        self.logger.info(f"Downloading {data_type} CSV data from: {csv_url}")
        
        try:
            response = session.get(csv_url, timeout=30)
            
            if response.status_code == 200:
                # Try to parse as CSV
                try:
                    from io import BytesIO
                    # Handle BOM character and clean column names with proper encoding
                    df = pd.read_csv(BytesIO(response.content), encoding='utf-8')
                    
                    # Clean column names (remove BOM and quotes)
                    df.columns = df.columns.str.replace('ï»¿', '').str.replace('"', '').str.strip()
                    
                    self.logger.info(f"✅ Successfully downloaded {data_type} data: {len(df)} rows")
                    return df
                except Exception as e:
                    self.logger.warning(f"Failed to parse as CSV: {e}")
                    
                    # Try to parse as HTML table
                    soup = BeautifulSoup(response.content, 'html.parser')
                    tables = soup.find_all('table')
                    if tables:
                        df = pd.read_html(str(tables[0]))[0]
                        self.logger.info(f"✅ Successfully parsed {data_type} data as HTML table: {len(df)} rows")
                        return df
                    else:
                        # The response might be HTML but not contain tables
                        # Let's try to extract data from the HTML content
                        self.logger.info("Trying to extract data from HTML content...")
                        return self._extract_data_from_html(soup, data_type)
            else:
                raise Exception(f"CSV download failed with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to download {data_type} CSV data: {e}")
            return pd.DataFrame()
    
    def _download_historical_data_with_session(self, session: requests.Session, soup: BeautifulSoup, base_url: str) -> pd.DataFrame:
        """Try to download historical data using a session to maintain state"""
        self.logger.info("Attempting to download historical data with session...")
        
        try:
            # Step 1: Find the filter form (this is the "More search options" form)
            filter_form = soup.find('form', attrs={'action': re.compile(r'filter', re.I)})
            
            if not filter_form:
                # Try to find any form that might be the search/filter form
                forms = soup.find_all('form')
                for form in forms:
                    action = form.get('action', '')
                    if 'filter' in action.lower() or 'nlp' in action.lower():
                        filter_form = form
                        break
            
            if not filter_form:
                self.logger.warning("Could not find filter form")
                return pd.DataFrame()
            
            self.logger.info(f"Found filter form: {filter_form.get('action', 'Unknown')}")
            
            # Step 2: Build form data with historical checkbox enabled
            form_data = self._build_historical_form_data(soup, filter_form)
            
            if not form_data:
                self.logger.warning("Could not build form data")
                return pd.DataFrame()
            
            self.logger.info(f"Form data prepared: {list(form_data.keys())}")
            
            # Step 3: Submit the form (this simulates clicking "More search options" and enabling historical data)
            form_action = filter_form.get('action', '')
            if not form_action.startswith('http'):
                form_action = urljoin(base_url, form_action)
            
            self.logger.info(f"Submitting form to: {form_action}")
            
            submit_headers = {
                'Referer': base_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            historical_response = session.post(form_action, data=form_data, headers=submit_headers, timeout=30)
            
            if historical_response.status_code != 200:
                self.logger.error(f"Form submission failed: {historical_response.status_code}")
                return pd.DataFrame()
            
            self.logger.info("✅ Form submitted successfully")
            
            # Step 4: Parse the response and find the CSV download link
            historical_soup = BeautifulSoup(historical_response.content, 'html.parser')
            
            # Look for CSV download link in the response
            historical_csv_url = self._find_csv_download_url(historical_soup, form_action)
            
            if historical_csv_url:
                self.logger.info(f"Found historical CSV URL: {historical_csv_url}")
                
                # Check if this URL is different from the current one
                current_csv_url = "https://www.bundesanzeiger.de/pub/en/nlp?0--top~csv~form~panel-form-csv~resource~link"
                if historical_csv_url != current_csv_url:
                    self.logger.info("✅ Historical CSV URL is different from current URL")
                    return self._download_csv_data_with_session(session, historical_csv_url, "historical")
                else:
                    self.logger.info("⚠️ Historical CSV URL is the same as current URL - trying anyway")
                    # Try to download anyway to see if the content is different
                    return self._download_csv_data_with_session(session, historical_csv_url, "historical")
            else:
                self.logger.warning("No CSV download link found in historical response")
                return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Failed to download historical data: {e}")
            return pd.DataFrame()
    
    def _extract_data_from_html(self, soup: BeautifulSoup, data_type: str) -> pd.DataFrame:
        """Extract data from HTML content when no tables are found"""
        self.logger.info(f"Extracting data from HTML content for {data_type} data")
        
        # Look for data in the HTML content
        # Based on the analysis, the data might be in a different format
        
        # Try to find any structured data
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
        self.logger.info("Parsing Germany Bundesanzeiger data")
        
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
        positions = []
        
        for sheet_name, df in dataframes.items():
            self.logger.info(f"Extracting positions from {sheet_name} ({len(df)} rows)")
            
            # Determine if this is current or historical based on sheet name
            is_active = sheet_name.lower() == 'current'
            
            # Map columns for Germany Bundesanzeiger data
            # Based on the actual data, the columns are:
            # Positionsinhaber, Emittent, ISIN, Position, Datum
            possible_columns = {
                'manager': ['Positionsinhaber', 'Position owner', 'Position Owner', 'Owner', 'Manager', 'Holder'],
                'company': ['Emittent', 'Issuer', 'Company', 'Name of Share Issuer'],
                'isin': ['ISIN', 'Isin'],
                'position_size': ['Position', 'Position Size', 'Net short position', 'Short Position'],
                'date': ['Datum', 'Date', 'Position Date', 'Publication Date']
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
                    
                    # Add is_active column
                    working_df['is_active'] = is_active
                    
                    # Convert to list of dictionaries
                    sheet_positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'is_active']].to_dict('records')
                    
                    # Filter valid positions
                    valid_positions = [pos for pos in sheet_positions if self.validate_position(pos)]
                    positions.extend(valid_positions)
                    
                    self.logger.info(f"Extracted {len(valid_positions)} valid positions from {sheet_name}")
        
        self.logger.info(f"Extracted {len(positions)} total positions from Germany data")
        return positions
    
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
            
            # Handle German date format (YYYY-MM-DD)
            return pd.to_datetime(value)
        except:
            return None
    
    def _is_header_row(self, row) -> bool:
        """Check if row is a header row"""
        if len(row) == 0:
            return True
        
        first_value = str(row.iloc[0]).lower()
        header_keywords = ['position owner', 'issuer', 'isin', 'position', 'date', 'owner', 'manager']
        return any(keyword in first_value for keyword in header_keywords)
    
    def _is_empty_row(self, row) -> bool:
        """Check if row is empty"""
        return row.isna().all() or (row == '').all()
