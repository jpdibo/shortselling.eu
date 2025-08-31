import pandas as pd
import requests
from datetime import datetime
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import re
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from .base_scraper import BaseScraper


class DenmarkScraper(BaseScraper):
    """Scraper for Danish short-selling data from DFSA"""
    
    def __init__(self, country_code: str, country_name: str):
        super().__init__(country_code, country_name)
        self.data_url = "https://www.dfsa.dk/financial-themes/capital-market/short-selling/published-net-short-positions"
    
    def get_data_url(self) -> str:
        """Get the main data URL"""
        return self.data_url
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        return driver
    
    def download_data(self) -> Dict[str, Any]:
        """Download Danish short-selling data from DFSA"""
        self.logger.info("Starting scrape for Denmark")
        self.logger.info("Downloading Denmark DFSA data")
        
        driver = None
        try:
            # Setup Selenium driver
            driver = self._setup_driver()
            
            # Navigate to the main page
            self.logger.info(f"Navigating to: {self.data_url}")
            driver.get(self.data_url)
            time.sleep(5)  # Wait for page to load
            
            # Find the download link for the Excel file
            download_link = self._find_download_link(driver)
            
            if not download_link:
                raise Exception("Could not find download link on the page")
            
            self.logger.info(f"Found download link: {download_link}")
            
            # Download the Excel file
            excel_content = self._download_excel_file(download_link)
            
            if not excel_content:
                raise Exception("Failed to download Excel file")
            
            self.logger.info(f"Successfully downloaded Excel file ({len(excel_content)} bytes)")
            
            return {
                'excel_content': excel_content,
                'source_url': self.data_url,
                'download_url': download_link,
                'download_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download Denmark data: {e}")
            raise Exception(f"Denmark download failed: {e}")
        finally:
            if driver:
                driver.quit()
    
    def _find_download_link(self, driver) -> str:
        """Find the download link for the Excel file"""
        try:
            # Look for the specific text that contains the download link
            # The text should be something like "Here you will find the sum of net short positions at or above 0.5% of the issued share capital."
            
            # Wait for the page to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for links that contain Excel file patterns
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                href = link.get_attribute('href')
                if href and ('.xlsx' in href or 'SS%20over%200,5%20pct' in href):
                    self.logger.info(f"Found Excel download link: {href}")
                    return href
            
            # If no direct link found, try to find the text and click it
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for the specific text and find the associated link
            target_text = "sum of net short positions at or above 0.5%"
            for link in soup.find_all('a'):
                if target_text.lower() in link.get_text().lower():
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            href = f"https://www.dfsa.dk{href}"
                        self.logger.info(f"Found link via text search: {href}")
                        return href
            
            self.logger.warning("Could not find download link on page")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding download link: {e}")
            return None
    
    def _download_excel_file(self, download_url: str) -> bytes:
        """Download the Excel file from the given URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(download_url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                return response.content
            else:
                self.logger.error(f"Failed to download Excel file: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading Excel file: {e}")
            return None
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse the downloaded data into a pandas DataFrame"""
        self.logger.info("Parsing Denmark data")
        
        try:
            if 'excel_content' not in data:
                self.logger.error("No Excel content found in downloaded data")
                return pd.DataFrame()
            
            # Save Excel content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                temp_file.write(data['excel_content'])
                temp_file_path = temp_file.name
            
            try:
                # Read the Excel file, specifically looking for the 'English' tab
                excel_file = pd.ExcelFile(temp_file_path)
                
                # Look for the 'English' sheet
                english_sheet = None
                for sheet_name in excel_file.sheet_names:
                    if 'english' in sheet_name.lower():
                        english_sheet = sheet_name
                        break
                
                if not english_sheet:
                    # If no English sheet found, use the first sheet
                    english_sheet = excel_file.sheet_names[0]
                    self.logger.warning(f"No 'English' sheet found, using first sheet: {english_sheet}")
                
                self.logger.info(f"Reading sheet: {english_sheet}")
                
                # Read the Excel sheet - explicitly read ALL rows, ignoring any filters
                # Use openpyxl engine to ensure we get all data
                df = pd.read_excel(
                    temp_file_path, 
                    sheet_name=english_sheet,
                    engine='openpyxl',
                    na_filter=False  # Don't filter out any values
                )
                
                self.logger.info(f"Successfully parsed Excel file with {len(df)} rows and {len(df.columns)} columns")
                self.logger.info(f"Columns: {list(df.columns)}")
                
                # Check if there are any filters applied and show breakdown
                if 'Active/Historical' in df.columns:
                    status_counts = df['Active/Historical'].value_counts()
                    self.logger.info(f"Active/Historical breakdown: {dict(status_counts)}")
                
                return df
                
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except PermissionError:
                    # File might be locked by Windows, ignore cleanup error
                    pass
                    
        except Exception as e:
            self.logger.error(f"Failed to parse Denmark data: {e}")
            raise Exception(f"Denmark data parsing failed: {e}")
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract short positions from parsed data"""
        self.logger.info("Extracting positions from Denmark data")
        
        positions = []
        
        try:
            if df.empty:
                self.logger.warning("No data to extract positions from")
                return positions
            
            # Identify columns based on common Danish short-selling data structure
            columns = self._identify_columns(df)
            
            if not columns:
                self.logger.error("Could not identify required columns")
                return positions
            
            # Count total rows and active/historical breakdown
            total_rows = len(df)
            active_count = 0
            historical_count = 0
            
            if 'status' in columns:
                for idx, row in df.iterrows():
                    status = str(row.get(columns['status'], '')).strip()
                    if 'active' in status.lower():
                        active_count += 1
                    elif 'historical' in status.lower():
                        historical_count += 1
            
            self.logger.info(f"Total rows: {total_rows}")
            self.logger.info(f"Active positions: {active_count}")
            self.logger.info(f"Historical positions: {historical_count}")
            
            # Vectorized processing - much faster than row by row
            if not df.empty:
                # Create working copy
                working_df = df.copy()
                
                # Basic cleaning only - let DailyScrapingService handle normalization
                working_df['company_name'] = working_df[columns.get('company_name', '')].fillna('').astype(str).str.strip()
                working_df['isin'] = working_df[columns.get('isin', '')].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
                working_df['isin'] = working_df['isin'].replace('nan', '')
                working_df['manager_name'] = working_df[columns.get('manager_name', '')].fillna('').astype(str).str.strip()
                working_df['manager_name'] = working_df['manager_name'].replace('nan', '')
                
                # Filter out rows with missing company name
                working_df = working_df[working_df['company_name'] != '']
                
                if not working_df.empty:
                    # Vectorized position size parsing - handle Danish decimal format (comma to dot)
                    position_col = working_df[columns.get('position_size', '')]
                    working_df['position_size'] = position_col.astype(str).str.replace(',', '.').str.replace('%', '').str.strip().astype(float)
                    
                    # Vectorized date parsing
                    working_df['date'] = pd.to_datetime(working_df[columns.get('date', '')], format='%d-%m-%Y', errors='coerce')
                    
                    # Vectorized status parsing
                    if 'status' in columns:
                        working_df['is_active'] = working_df[columns['status']].fillna('').astype(str).str.lower().str.contains('active')
                    else:
                        working_df['is_active'] = True
                    
                    # Convert to list of dictionaries
                    positions = working_df[['company_name', 'isin', 'manager_name', 'position_size', 'date', 'is_active']].to_dict('records')
                    
                    # Filter valid positions
                    valid_positions = [pos for pos in positions if pos['company_name'] and pos['position_size'] > 0]
                    positions = valid_positions
                    
                    processed_count = len(valid_positions)
            
            self.logger.info(f"Processed {processed_count} rows successfully")
            self.logger.info(f"Extracted {len(positions)} positions from Denmark data")
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to extract Denmark positions: {e}")
            raise Exception(f"Denmark position extraction failed: {e}")
    
    def _identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify the relevant columns in the DataFrame"""
        columns = {}
        
        try:
            # Get column names
            col_names = [str(col).strip() for col in df.columns]
            self.logger.info(f"Available columns: {col_names}")
            
            # Look for exact column names from Denmark Excel file
            for col in col_names:
                # Company name - exact match
                if col == 'Name of the issuer':
                    columns['company_name'] = col
                
                # ISIN - exact match
                elif col == 'ISIN':
                    columns['isin'] = col
                
                # Manager name - exact match
                elif col == 'Position holder':
                    columns['manager_name'] = col
                
                # Position size - exact match
                elif col == 'Net short position (%)':
                    columns['position_size'] = col
                
                # Date - exact match
                elif col == 'Date, where position was created, changed or ceased to be held (dd-mm-yyyy)':
                    columns['date'] = col
                
                # Active/Historical - exact match
                elif col == 'Active/Historical':
                    columns['status'] = col
            
            # If we found the essential columns, return them
            if 'company_name' in columns and 'position_size' in columns:
                self.logger.info(f"Identified columns: {columns}")
                return columns
            else:
                self.logger.warning("Could not identify all required columns")
                self.logger.warning(f"Found: {list(columns.keys())}")
                self.logger.warning(f"Required: company_name, position_size")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error identifying columns: {e}")
            return {}
    
    def _extract_position(self, row, columns: Dict[str, str]) -> Dict[str, Any]:
        """Extract a single position from a row"""
        try:
            # Get company name
            company_name = str(row.get(columns.get('company_name', ''), '')).strip()
            if not company_name or company_name == 'nan':
                return None
            
            # Get ISIN (optional)
            isin = str(row.get(columns.get('isin', ''), '')).strip()
            if isin == 'nan':
                isin = ''
            
            # Get manager name (optional)
            manager_name = str(row.get(columns.get('manager_name', ''), '')).strip()
            if manager_name == 'nan':
                manager_name = 'Unknown'
            
            # Get position size
            position_size_str = str(row.get(columns.get('position_size', ''), '0')).strip()
            try:
                # Parse percentage value
                position_size = float(re.findall(r'[\d.]+', position_size_str.replace(',', '.'))[0])
            except:
                position_size = 0.0
            
            # Get date
            date_str = str(row.get(columns.get('date', ''), ''))
            try:
                if date_str and date_str != 'nan':
                    # Denmark uses dd-mm-yyyy format, need to specify dayfirst=True
                    date = pd.to_datetime(date_str, dayfirst=True).date()
                else:
                    date = datetime.now().date()
            except:
                date = datetime.now().date()
            
            # Determine if this is current based on Active/Historical column
            is_active = True  # Default to active
            if 'status' in columns:
                status = str(row.get(columns.get('status', ''), '')).strip().lower()
                is_active = 'active' in status
            
            return {
                'manager_name': manager_name,
                'company_name': company_name,
                'isin': isin,
                'position_size': position_size,
                'date': date,
                'is_active': is_active
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting position: {e}")
            return None
