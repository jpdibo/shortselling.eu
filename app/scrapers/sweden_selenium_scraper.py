#!/usr/bin/env python3
"""
Sweden Short-Selling Scraper (Selenium Version)
Fetches data from Finansinspektionen (FI)
Uses Selenium to handle JavaScript-based download links
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, List
from .base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import io
import os

class SwedenSeleniumScraper(BaseScraper):
    """Selenium-based scraper for Swedish short-selling data from Finansinspektionen"""
    
    def __init__(self, country_code: str = "SE", country_name: str = "Sweden"):
        super().__init__(country_code, country_name)
        
    def get_data_url(self) -> str:
        """Get the main data source URL"""
        return "https://www.fi.se/en/our-registers/net-short-positions"
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        import tempfile
        
        # Create temporary download directory
        download_dir = tempfile.mkdtemp()
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Set download directory
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        return driver, download_dir
    
    def download_data(self) -> Dict[str, Any]:
        """Download Swedish short-selling data from Finansinspektionen using Selenium"""
        self.logger.info("Starting Selenium scrape for Sweden")
        self.logger.info("Downloading Sweden Finansinspektionen data with Selenium")
        
        driver = None
        download_dir = None
        try:
            driver, download_dir = self._setup_driver()
            
            # Navigate to the main page
            main_url = self.get_data_url()
            self.logger.info(f"Navigating to: {main_url}")
            
            driver.get(main_url)
            time.sleep(5)  # Wait for page to load
            
            # Handle cookie consent banner if present
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'ACCEPT ALL') or contains(text(), 'Accept All') or contains(text(), 'Accept') or contains(text(), 'Godkänn')]")
                if cookie_buttons:
                    self.logger.info("Found cookie consent banner, accepting cookies...")
                    cookie_buttons[0].click()
                    time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Error handling cookie banner: {e}")
            
            # Download current positions
            current_file_content = self._download_current_positions(driver, download_dir)
            
            # Download historic positions
            historic_file_content = self._download_historic_positions(driver, download_dir)
            
            # Get page source for potential fallback
            page_source = driver.page_source
            
            return {
                'current_file': current_file_content,
                'historic_file': historic_file_content,
                'page_source': page_source.encode('utf-8'),
                'source_url': main_url,
                'download_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download Sweden data with Selenium: {e}")
            raise Exception(f"Sweden Selenium download failed: {e}")
        finally:
            if driver:
                driver.quit()
            if download_dir and os.path.exists(download_dir):
                import shutil
                shutil.rmtree(download_dir)  # Clean up temp directory
    
    def _download_current_positions(self, driver, download_dir) -> bytes:
        """Download current positions Excel file"""
        self.logger.info("Downloading current positions...")
        
        try:
            # Try to extract the actual download URL from JavaScript
            current_url = self._extract_download_url(driver, "Current positions")
            if current_url:
                self.logger.info(f"Extracted current positions URL: {current_url}")
                
                # Download using requests
                import requests
                response = requests.get(current_url, timeout=60)
                if response.status_code == 200:
                    self.logger.info(f"Successfully downloaded current positions file ({len(response.content)} bytes)")
                    return response.content
                else:
                    self.logger.warning(f"Failed to download current positions: {response.status_code}")
            
            # Fallback: Try clicking the link
            try:
                current_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Current positions')]")
                self.logger.info("Found current positions link, trying click...")
                
                # Click the link to trigger JavaScript download
                current_link.click()
                self.logger.info("Clicked current positions link")
                
                # Wait for download to complete
                time.sleep(10)
                
                # Check for downloaded files
                downloaded_files = []
                for filename in os.listdir(download_dir):
                    if filename.endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(download_dir, filename)
                        downloaded_files.append(file_path)
                        self.logger.info(f"Found current positions downloaded file: {filename}")
                
                if downloaded_files:
                    # Read the downloaded file
                    latest_file = max(downloaded_files, key=os.path.getctime)
                    with open(latest_file, 'rb') as f:
                        file_content = f.read()
                    self.logger.info(f"Successfully read current positions file: {os.path.basename(latest_file)} ({len(file_content)} bytes)")
                    return file_content
            except Exception as click_error:
                self.logger.warning(f"Error clicking current positions link: {click_error}")
            
            self.logger.warning("No current positions downloaded files found")
            return b''
                
        except Exception as e:
            self.logger.warning(f"Error downloading current positions: {e}")
            return b''
    
    def _download_historic_positions(self, driver, download_dir) -> bytes:
        """Download historic positions Excel file"""
        self.logger.info("Downloading historic positions...")
        
        try:
            # Try to extract the actual download URL from JavaScript
            historic_url = self._extract_download_url(driver, "Historic positions")
            if historic_url:
                self.logger.info(f"Extracted historic positions URL: {historic_url}")
                
                # Download using requests
                import requests
                response = requests.get(historic_url, timeout=60)
                if response.status_code == 200:
                    self.logger.info(f"Successfully downloaded historic positions file ({len(response.content)} bytes)")
                    return response.content
                else:
                    self.logger.warning(f"Failed to download historic positions: {response.status_code}")
            
            # Fallback: Try clicking the link
            try:
                historic_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Historic positions')]")
                self.logger.info("Found historic positions link, trying click...")
                
                # Click the link to trigger JavaScript download
                historic_link.click()
                self.logger.info("Clicked historic positions link")
                
                # Wait for download to complete
                time.sleep(10)
                
                # Check for downloaded files
                downloaded_files = []
                for filename in os.listdir(download_dir):
                    if filename.endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(download_dir, filename)
                        downloaded_files.append(file_path)
                        self.logger.info(f"Found historic positions downloaded file: {filename}")
                
                if downloaded_files:
                    # Read the downloaded file
                    latest_file = max(downloaded_files, key=os.path.getctime)
                    with open(latest_file, 'rb') as f:
                        file_content = f.read()
                    self.logger.info(f"Successfully read historic positions file: {os.path.basename(latest_file)} ({len(file_content)} bytes)")
                    return file_content
            except Exception as click_error:
                self.logger.warning(f"Error clicking historic positions link: {click_error}")
            
            self.logger.warning("No historic positions downloaded files found")
            return b''
                
        except Exception as e:
            self.logger.warning(f"Error downloading historic positions: {e}")
            return b''
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse the downloaded Excel files"""
        self.logger.info("Parsing Sweden data from Excel downloads")
        
        try:
            all_dataframes = []
            
            # Parse current positions from downloaded file
            if data.get('current_file') and len(data['current_file']) > 0:
                try:
                    current_df = self._parse_excel_file(data['current_file'], "current")
                    if current_df is not None and len(current_df) > 0:
                        current_df['data_type'] = 'current'
                        all_dataframes.append(current_df)
                        self.logger.info(f"Parsed {len(current_df)} current positions from Excel file")
                except Exception as e:
                    self.logger.warning(f"Error parsing current file: {e}")
            
            # Parse historic positions from downloaded file
            if data.get('historic_file') and len(data['historic_file']) > 0:
                try:
                    historic_df = self._parse_excel_file(data['historic_file'], "historic")
                    if historic_df is not None and len(historic_df) > 0:
                        historic_df['data_type'] = 'historic'
                        all_dataframes.append(historic_df)
                        self.logger.info(f"Parsed {len(historic_df)} historic positions from Excel file")
                except Exception as e:
                    self.logger.warning(f"Error parsing historic file: {e}")
            
            if not all_dataframes:
                self.logger.warning("No data found in downloaded Excel files")
                return pd.DataFrame()
            
            # Combine all dataframes
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            self.logger.info(f"Combined {len(combined_df)} total positions from Sweden data")
            
            return combined_df
            
        except Exception as e:
            self.logger.error(f"Failed to parse Sweden data: {e}")
            raise Exception(f"Sweden data parsing failed: {e}")
    
    def _parse_excel_file(self, file_content: bytes, data_type: str) -> pd.DataFrame:
        """Parse Excel file content"""
        try:
            import io
            
            # Try to parse as Excel file first
            try:
                excel_file = io.BytesIO(file_content)
                df = pd.read_excel(excel_file, engine='openpyxl')
                self.logger.info(f"Successfully parsed {data_type} Excel file with {len(df)} rows")
                return df
            except Exception as excel_error:
                self.logger.info(f"Not an Excel file, trying ODS: {excel_error}")
                
                # Try to parse as ODS file (OpenDocument Spreadsheet)
                try:
                    ods_file = io.BytesIO(file_content)
                    df = pd.read_excel(ods_file, engine='odf')
                    self.logger.info(f"Successfully parsed {data_type} ODS file with {len(df)} rows")
                    return df
                except Exception as ods_error:
                    self.logger.info(f"Not an ODS file, trying CSV: {ods_error}")
                
                # Try to parse as CSV file with different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                delimiters = [',', ';', '\t']
                
                for encoding in encodings:
                    try:
                        csv_content = file_content.decode(encoding, errors='ignore')
                        # Clean NULL bytes
                        csv_content = csv_content.replace('\x00', '')
                        
                        # Try different delimiters
                        for delimiter in delimiters:
                            try:
                                df = pd.read_csv(io.StringIO(csv_content), delimiter=delimiter, engine='c')
                                self.logger.info(f"Successfully parsed {data_type} CSV file with encoding '{encoding}', delimiter '{delimiter}' and {len(df)} rows")
                                return df
                            except:
                                continue
                        
                        # If all delimiters fail, try with engine='python' which can auto-detect
                        try:
                            df = pd.read_csv(io.StringIO(csv_content), engine='python')
                            self.logger.info(f"Successfully parsed {data_type} CSV file with encoding '{encoding}' and python engine and {len(df)} rows")
                            return df
                        except:
                            continue
                            
                    except Exception as encoding_error:
                        self.logger.warning(f"Failed to parse {data_type} file with encoding '{encoding}': {encoding_error}")
                        continue
                
                self.logger.error(f"Failed to parse {data_type} file with all encodings and delimiters")
                return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"Error parsing {data_type} file: {e}")
            return pd.DataFrame()
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract short positions from parsed data"""
        self.logger.info("Extracting positions from Sweden data")
        
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
            # Remove header and metadata rows first
            def is_header_or_metadata_row(row):
                first_col = str(row.iloc[0]) if len(row) > 0 else ''
                return any(skip_text in first_col for skip_text in [
                    'Aktuella positioner', 'Historiska positioner', 'Betydande korta nettopositioner',
                    'Position holder', 'Innehavare', 'fi.se/blankning', 'rapportering@fi.se',
                    'Namn på emittent', 'Name of the issuer', 'ISIN', 'Position i procent',
                    'Position in per cent', 'Datum för positionen', 'Position date'
                ])
            
            # Filter out header/metadata rows
            working_df = df[~df.apply(is_header_or_metadata_row, axis=1)].copy()
            
            if not working_df.empty:
                # Basic cleaning only - let DailyScrapingService handle normalization
                working_df['manager_name'] = working_df[column_mapping.get('manager', '')].fillna('').astype(str).str.strip()
                working_df['company_name'] = working_df[column_mapping.get('company', '')].fillna('').astype(str).str.strip()
                working_df['isin'] = working_df[column_mapping.get('isin', '')].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
                working_df['isin'] = working_df['isin'].replace('nan', '')
                
                # Vectorized position size parsing (Swedish format: comma to dot)
                position_col = working_df[column_mapping.get('position_size', '')]
                working_df['position_size'] = position_col.astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
                working_df['position_size'] = pd.to_numeric(working_df['position_size'], errors='coerce').fillna(0.0)
                
                # Vectorized date parsing
                date_col = working_df[column_mapping.get('date', '')]
                working_df['date'] = pd.to_datetime(date_col, errors='coerce')
                working_df['date'] = working_df['date'].fillna(pd.Timestamp.now()).dt.date
                
                # Set is_active based on data_type
                working_df['is_active'] = working_df.get('data_type', '') == 'current'
                
                # Filter out rows with missing essential data
                working_df = working_df[
                    (working_df['manager_name'] != '') & 
                    (working_df['company_name'] != '') & 
                    (working_df['manager_name'] != 'nan') & 
                    (working_df['company_name'] != 'nan')
                ]
                
                # Convert to list of dictionaries
                positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'is_active']].to_dict('records')
            
            self.logger.info(f"Extracted {len(positions)} positions from Sweden data")
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to extract Sweden positions: {e}")
            raise Exception(f"Sweden position extraction failed: {e}")
    
    def _identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify column mapping based on column names"""
        column_mapping = {}
        
        # First, try to find the header row
        header_row = None
        for idx, row in df.iterrows():
            # Look for Swedish/English headers
            first_col = str(row.iloc[0]) if len(row) > 0 else ''
            if 'Position holder' in first_col or 'Innehavare' in first_col:
                header_row = idx
                break
        
        if header_row is not None:
            # Use the header row to map columns
            headers = df.iloc[header_row]
            
            for col_idx, header in enumerate(headers):
                if pd.isna(header):
                    continue
                    
                header_str = str(header).lower()
                
                # Manager/Position holder (Swedish: Innehavare av positionen)
                if 'position holder' in header_str or 'innehavare' in header_str:
                    column_mapping['manager'] = df.columns[col_idx]
                
                # Company/Issuer (Swedish: Namn på emittent)
                elif 'name of the issuer' in header_str or 'emittent' in header_str:
                    column_mapping['company'] = df.columns[col_idx]
                
                # ISIN
                elif 'isin' in header_str:
                    column_mapping['isin'] = df.columns[col_idx]
                
                # Position size (Swedish: Position i procent)
                elif 'position in per cent' in header_str or 'procent' in header_str:
                    column_mapping['position_size'] = df.columns[col_idx]
                
                # Date (Swedish: Datum för positionen)
                elif 'position date' in header_str or 'datum' in header_str:
                    column_mapping['date'] = df.columns[col_idx]
        
        # If no header row found, try column-based mapping
        if not column_mapping:
            for col in df.columns:
                col_lower = col.lower()
                
                # Manager/Position holder
                if any(keyword in col_lower for keyword in ['manager', 'holder', 'investor', 'participant', 'position holder']):
                    column_mapping['manager'] = col
                
                # Company/Issuer
                elif any(keyword in col_lower for keyword in ['company', 'issuer', 'emitter', 'name', 'issuer name']):
                    column_mapping['company'] = col
                
                # ISIN
                elif 'isin' in col_lower:
                    column_mapping['isin'] = col
                
                # Position size
                elif any(keyword in col_lower for keyword in ['position', 'percentage', 'size', 'amount', 'sum short']):
                    column_mapping['position_size'] = col
                
                # Date
                elif any(keyword in col_lower for keyword in ['date', 'time', 'when', 'latest position date']):
                    column_mapping['date'] = col
        
        return column_mapping
    
    def _extract_download_url(self, driver, link_text: str) -> str:
        """Extract the actual download URL from JavaScript links"""
        try:
            # Find the link element
            link_element = driver.find_element(By.XPATH, f"//a[contains(text(), '{link_text}')]")
            
            # Get the href attribute
            href = link_element.get_attribute('href')
            if href and href.startswith('javascript:'):
                # Extract the JavaScript function call
                js_call = href.replace('javascript:', '').strip()
                
                # Parse the JavaScript to extract the URL
                if 'CurrentPositions' in js_call:
                    # Current positions URL pattern
                    base_url = "https://www.fi.se/en/our-registers/net-short-positions/GetAktuellFile/"
                    return base_url
                elif 'HistoricPositions' in js_call:
                    # Historic positions URL pattern
                    base_url = "https://www.fi.se/en/our-registers/net-short-positions/GetHistFile/"
                    return base_url
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting download URL for {link_text}: {e}")
            return None
