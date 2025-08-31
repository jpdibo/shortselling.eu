#!/usr/bin/env python3
"""
Finland Short-Selling Scraper (Selenium Version)
Fetches data from FIN-FSA (Financial Supervisory Authority of Finland)
Uses Selenium to handle dynamic content loading
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

class FinlandSeleniumScraper(BaseScraper):
    """Selenium-based scraper for Finnish short-selling data from FIN-FSA"""
    
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
        """Download Finnish short-selling data from FIN-FSA using Selenium"""
        self.logger.info("Starting Selenium scrape for Finland")
        self.logger.info("Downloading Finland FIN-FSA data with Selenium")
        
        driver = None
        download_dir = None
        try:
            driver, download_dir = self._setup_driver()
            
            # Download current positions with Excel/CSV download
            current_url = self.get_current_positions_url()
            self.logger.info(f"Fetching current positions from: {current_url}")
            
            driver.get(current_url)
            time.sleep(10)  # Wait longer for page to load
            
            # Wait for table to load
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                self.logger.info("Current positions table loaded")
            except TimeoutException:
                self.logger.warning("Timeout waiting for current positions table")
            
            # Scroll down to trigger any lazy loading and make sure the button is visible
            self.logger.info("Scrolling down to ensure all content is loaded...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)
            
            # Handle cookie consent banner if present
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'ACCEPT ALL') or contains(text(), 'Accept All') or contains(text(), 'Accept')]")
                if cookie_buttons:
                    self.logger.info("Found cookie consent banner, accepting cookies...")
                    cookie_buttons[0].click()
                    time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Error handling cookie banner: {e}")
            
            # Look for and click the "Save as excel (.csv)" button for current positions
            try:
                # Look for the specific "Save as excel (.csv)" button
                button_selectors = [
                    "//span[contains(text(), 'Save as excel (.csv)')]",
                    "//span[contains(text(), 'save as excel (.csv)')]",
                    "//*[contains(text(), 'Save as excel (.csv)')]",
                    "//*[contains(text(), 'save as excel (.csv)')]",
                    "//span[contains(text(), 'Save as excel')]",
                    "//span[contains(text(), 'save as excel')]",
                    "//*[contains(text(), 'Save as excel')]",
                    "//*[contains(text(), 'save as excel')]"
                ]
                
                download_button = None
                for selector in button_selectors:
                    try:
                        # First try to find any element with the text, not necessarily clickable
                        elements = driver.find_elements(By.XPATH, selector)
                        if elements:
                            for element in elements:
                                try:
                                    # Try to make it clickable by scrolling to it
                                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    if element.is_enabled() and element.is_displayed():
                                        download_button = element
                                        self.logger.info(f"Found current positions download button with selector: {selector}")
                                        break
                                except:
                                    continue
                            if download_button:
                                break
                    except Exception as e:
                        self.logger.warning(f"Error with selector {selector}: {e}")
                        continue
                
                if download_button:
                    self.logger.info("Clicking current positions download button...")
                    try:
                        # Try JavaScript click first to bypass element interception
                        driver.execute_script("arguments[0].click();", download_button)
                        self.logger.info("Current positions download button clicked with JavaScript")
                    except Exception as js_error:
                        self.logger.warning(f"JavaScript click failed: {js_error}")
                        try:
                            # Fallback to regular click
                            download_button.click()
                            self.logger.info("Current positions download button clicked with regular click")
                        except Exception as click_error:
                            self.logger.warning(f"Regular click also failed: {click_error}")
                            # Try to click using ActionChains
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(driver)
                            actions.move_to_element(download_button).click().perform()
                            self.logger.info("Current positions download button clicked with ActionChains")
                    
                    time.sleep(10)  # Wait for download to complete
                    self.logger.info("Current positions download button clicked successfully")
                    
                    # Check for downloaded files
                    downloaded_files = []
                    for filename in os.listdir(download_dir):
                        if filename.endswith(('.csv', '.xlsx', '.xls')):
                            file_path = os.path.join(download_dir, filename)
                            downloaded_files.append(file_path)
                            self.logger.info(f"Found current positions downloaded file: {filename}")
                    
                    if downloaded_files:
                        # Read the downloaded file
                        latest_file = max(downloaded_files, key=os.path.getctime)
                        with open(latest_file, 'rb') as f:
                            current_file_content = f.read()
                        self.logger.info(f"Successfully read current positions downloaded file: {os.path.basename(latest_file)} ({len(current_file_content)} bytes)")
                        
                        # Rename the current file to prevent historic download from overwriting it
                        current_renamed_file = os.path.join(download_dir, "current_positions.csv")
                        os.rename(latest_file, current_renamed_file)
                        self.logger.info(f"Renamed current file to: {os.path.basename(current_renamed_file)}")
                    else:
                        self.logger.warning("No current positions downloaded files found")
                        current_file_content = b''
                else:
                    self.logger.warning("Could not find current positions download button")
                    current_file_content = b''
                    
            except Exception as e:
                self.logger.warning(f"Error clicking current positions download button: {e}")
                current_file_content = b''
            
            current_page_source = driver.page_source
            
            # Download historic positions with Excel/CSV download
            historic_url = self.get_historic_positions_url()
            self.logger.info(f"Fetching historic positions from: {historic_url}")
            
            driver.get(historic_url)
            time.sleep(10)  # Wait longer for page to load
            
            # Wait for table to load
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                self.logger.info("Historic positions table loaded")
            except TimeoutException:
                self.logger.warning("Timeout waiting for historic positions table")
            
            # Scroll down to trigger any lazy loading and make sure the button is visible
            self.logger.info("Scrolling down to ensure all content is loaded...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)
            
            # Handle cookie consent banner if present
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'ACCEPT ALL') or contains(text(), 'Accept All') or contains(text(), 'Accept')]")
                if cookie_buttons:
                    self.logger.info("Found cookie consent banner, accepting cookies...")
                    cookie_buttons[0].click()
                    time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Error handling cookie banner: {e}")
            
            # Look for and click the "Save as excel (.csv)" button for historic positions
            try:
                # Look for the specific "Save as excel (.csv)" button
                button_selectors = [
                    "//span[contains(text(), 'Save as excel (.csv)')]",
                    "//span[contains(text(), 'save as excel (.csv)')]",
                    "//*[contains(text(), 'Save as excel (.csv)')]",
                    "//*[contains(text(), 'save as excel (.csv)')]",
                    "//span[contains(text(), 'Save as excel')]",
                    "//span[contains(text(), 'save as excel')]",
                    "//*[contains(text(), 'Save as excel')]",
                    "//*[contains(text(), 'save as excel')]"
                ]
                
                download_button = None
                for selector in button_selectors:
                    try:
                        # First try to find any element with the text, not necessarily clickable
                        elements = driver.find_elements(By.XPATH, selector)
                        if elements:
                            for element in elements:
                                try:
                                    # Try to make it clickable by scrolling to it
                                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    if element.is_enabled() and element.is_displayed():
                                        download_button = element
                                        self.logger.info(f"Found historic positions download button with selector: {selector}")
                                        break
                                except:
                                    continue
                            if download_button:
                                break
                    except Exception as e:
                        self.logger.warning(f"Error with selector {selector}: {e}")
                        continue
                
                if download_button:
                    self.logger.info("Clicking historic positions download button...")
                    try:
                        # Try JavaScript click first to bypass element interception
                        driver.execute_script("arguments[0].click();", download_button)
                        self.logger.info("Historic positions download button clicked with JavaScript")
                    except Exception as js_error:
                        self.logger.warning(f"JavaScript click failed: {js_error}")
                        try:
                            # Fallback to regular click
                            download_button.click()
                            self.logger.info("Historic positions download button clicked with regular click")
                        except Exception as click_error:
                            self.logger.warning(f"Regular click also failed: {click_error}")
                            # Try to click using ActionChains
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(driver)
                            actions.move_to_element(download_button).click().perform()
                            self.logger.info("Historic positions download button clicked with ActionChains")
                    
                    time.sleep(10)  # Wait for download to complete
                    self.logger.info("Historic positions download button clicked successfully")
                    
                    # Check for downloaded files
                    downloaded_files = []
                    for filename in os.listdir(download_dir):
                        if filename.endswith(('.csv', '.xlsx', '.xls')):
                            file_path = os.path.join(download_dir, filename)
                            downloaded_files.append(file_path)
                            self.logger.info(f"Found historic positions downloaded file: {filename}")
                    
                    if downloaded_files:
                        # Filter out the current positions file we renamed earlier
                        historic_files = [f for f in downloaded_files if not f.endswith('current_positions.csv')]
                        if historic_files:
                            # Read the latest historic file
                            latest_file = max(historic_files, key=os.path.getctime)
                            with open(latest_file, 'rb') as f:
                                historic_file_content = f.read()
                            self.logger.info(f"Successfully read historic positions downloaded file: {os.path.basename(latest_file)} ({len(historic_file_content)} bytes)")
                            
                            # Rename for clarity
                            historic_renamed_file = os.path.join(download_dir, "historic_positions.csv")
                            if latest_file != historic_renamed_file:
                                os.rename(latest_file, historic_renamed_file)
                                self.logger.info(f"Renamed historic file to: {os.path.basename(historic_renamed_file)}")
                        else:
                            self.logger.warning("No new historic positions files found (excluding current file)")
                            historic_file_content = b''
                    else:
                        self.logger.warning("No historic positions downloaded files found")
                        historic_file_content = b''
                else:
                    self.logger.warning("Could not find historic positions download button")
                    historic_file_content = b''
                    
            except Exception as e:
                self.logger.warning(f"Error clicking historic positions download button: {e}")
                historic_file_content = b''
            
            historic_page_source = driver.page_source
            
            return {
                'current_page': current_page_source.encode('utf-8'),
                'historic_page': historic_page_source.encode('utf-8'),
                'current_file': current_file_content,
                'historic_file': historic_file_content,
                'current_url': current_url,
                'historic_url': historic_url,
                'source_url': self.get_data_url(),
                'download_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download Finland data with Selenium: {e}")
            raise Exception(f"Finland Selenium download failed: {e}")
        finally:
            if driver:
                driver.quit()
            if download_dir and os.path.exists(download_dir):
                import shutil
                shutil.rmtree(download_dir)  # Clean up temp directory
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse the downloaded data files and HTML data"""
        self.logger.info("Parsing Finland data from Selenium downloads")
        
        try:
            from bs4 import BeautifulSoup
            import io
            
            all_dataframes = []
            
            # Parse current positions from downloaded file
            if data.get('current_file') and len(data['current_file']) > 0:
                try:
                    current_df = self._parse_downloaded_file(data['current_file'], "current")
                    if current_df is not None and len(current_df) > 0:
                        current_df['data_type'] = 'current'
                        all_dataframes.append(current_df)
                        self.logger.info(f"Parsed {len(current_df)} current positions from downloaded file")
                except Exception as e:
                    self.logger.warning(f"Error parsing current file: {e}")
                    # Fallback to HTML parsing
                    current_soup = BeautifulSoup(data['current_page'], 'html.parser')
                    current_df = self._parse_html_table(current_soup, "current")
                    if current_df is not None and len(current_df) > 0:
                        current_df['data_type'] = 'current'
                        all_dataframes.append(current_df)
                        self.logger.info(f"Parsed {len(current_df)} current positions from HTML fallback")
            
            # Parse historic positions from downloaded file
            if data.get('historic_file') and len(data['historic_file']) > 0:
                try:
                    historic_df = self._parse_downloaded_file(data['historic_file'], "historic")
                    if historic_df is not None and len(historic_df) > 0:
                        historic_df['data_type'] = 'historic'
                        all_dataframes.append(historic_df)
                        self.logger.info(f"Parsed {len(historic_df)} historic positions from downloaded file")
                except Exception as e:
                    self.logger.warning(f"Error parsing historic file: {e}")
                    # Fallback to HTML parsing
                    historic_soup = BeautifulSoup(data['historic_page'], 'html.parser')
                    historic_df = self._parse_html_table(historic_soup, "historic")
                    if historic_df is not None and len(historic_df) > 0:
                        historic_df['data_type'] = 'historic'
                        all_dataframes.append(historic_df)
                        self.logger.info(f"Parsed {len(historic_df)} historic positions from HTML fallback")
            
            if not all_dataframes:
                self.logger.warning("No data found in downloaded files or HTML pages")
                return pd.DataFrame()
            
            # Combine all dataframes
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            self.logger.info(f"Combined {len(combined_df)} total positions from Finland data")
            
            # Clean up any malformed columns
            combined_df = self._fix_malformed_columns(combined_df)
            
            return combined_df
            
        except Exception as e:
            self.logger.error(f"Failed to parse Finland data: {e}")
            raise Exception(f"Finland data parsing failed: {e}")
    
    def _parse_html_table(self, soup, data_type: str) -> pd.DataFrame:
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
            
            for idx, row in df.iterrows():
                try:
                    # Extract data using column mapping
                    manager_name = str(row.get(column_mapping.get('manager', ''), '')).strip()
                    company_name = str(row.get(column_mapping.get('company', ''), '')).strip()
                    isin = str(row.get(column_mapping.get('isin', ''), '')).strip()
                    position_size_str = str(row.get(column_mapping.get('position_size', ''), '')).strip()
                    date_str = str(row.get(column_mapping.get('date', ''), '')).strip()
                    
                    # Skip if essential data is missing
                    if not all([manager_name, company_name]) or manager_name == 'nan':
                        continue
                    
                    # Parse position size (remove % and convert to float)
                    try:
                        position_size = float(position_size_str.replace('%', '').replace(',', '.'))
                    except:
                        position_size = 0.0
                    
                    # Parse date
                    try:
                        if pd.isna(pd.to_datetime(date_str)):
                            date = datetime.now().date()
                        else:
                            date = pd.to_datetime(date_str).date()
                    except:
                        date = datetime.now().date()
                    
                    # Determine if this is current or historical
                    is_active = row.get('data_type', '') == 'current'
                    
                    position = {
                        'manager_name': manager_name,
                        'company_name': company_name,
                        'isin': isin if isin and isin != 'nan' else '',
                        'position_size': position_size,
                        'date': date,
                        'is_active': is_active
                    }
                    
                    positions.append(position)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing row {idx}: {e}")
                    continue
            
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
    
    def _fix_malformed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix malformed columns where data got parsed into wrong columns"""
        try:
            # Look for columns that contain semicolon-separated data (malformed parsing)
            malformed_cols = []
            for col in df.columns:
                if ';' in str(col):
                    malformed_cols.append(col)
            
            if not malformed_cols:
                return df
            
            self.logger.info(f"Found malformed columns: {malformed_cols}")
            
            # Process rows that have data in malformed columns
            fixed_rows = []
            for idx, row in df.iterrows():
                # Check if this row has data in a malformed column
                has_malformed_data = False
                for malformed_col in malformed_cols:
                    if pd.notna(row.get(malformed_col)) and str(row.get(malformed_col)).strip():
                        has_malformed_data = True
                        malformed_data = str(row.get(malformed_col)).strip()
                        
                        # Split the semicolon-separated data
                        parts = malformed_data.split(';')
                        if len(parts) >= 5:  # Should have manager, company, isin, position, date
                            # Create a fixed row
                            fixed_row = row.copy()
                            fixed_row['Position holder'] = parts[0].strip()
                            fixed_row['Name of the issuer'] = parts[1].strip()
                            fixed_row['ISIN'] = parts[2].strip()
                            fixed_row['Net short position (%)'] = parts[3].strip()
                            fixed_row['Date'] = parts[4].strip()
                            
                            # Clear the malformed column
                            fixed_row[malformed_col] = pd.NA
                            
                            fixed_rows.append(fixed_row)
                            self.logger.debug(f"Fixed malformed row: {parts[0]} -> {parts[1]}")
                        break
                
                if not has_malformed_data:
                    # Keep the row as-is if no malformed data
                    fixed_rows.append(row)
            
            # Create new DataFrame with fixed rows
            if fixed_rows:
                fixed_df = pd.DataFrame(fixed_rows)
                
                # Drop the malformed columns
                for malformed_col in malformed_cols:
                    if malformed_col in fixed_df.columns:
                        fixed_df = fixed_df.drop(columns=[malformed_col])
                
                self.logger.info(f"Fixed {len([r for r in fixed_rows if any(pd.notna(r.get(col)) and str(r.get(col)).strip() for col in malformed_cols)])} malformed rows")
                return fixed_df
            else:
                return df
                
        except Exception as e:
            self.logger.error(f"Error fixing malformed columns: {e}")
            return df
    
    def _parse_downloaded_file(self, file_content: bytes, data_type: str) -> pd.DataFrame:
        """Parse downloaded Excel/CSV file"""
        try:
            import io
            
            # Try to parse as Excel file first
            try:
                excel_file = io.BytesIO(file_content)
                df = pd.read_excel(excel_file, engine='openpyxl')
                self.logger.info(f"Successfully parsed {data_type} file as Excel")
                return df
            except Exception as excel_error:
                self.logger.info(f"Not an Excel file, trying CSV: {excel_error}")
                
                # Try to parse as CSV file
                try:
                    csv_content = file_content.decode('utf-8')
                    
                    # Try different delimiters and check for proper column separation
                    for delimiter in [';', ',', '\t']:
                        try:
                            df = pd.read_csv(io.StringIO(csv_content), delimiter=delimiter)
                            
                            # Check if we have multiple columns (proper parsing)
                            if len(df.columns) > 3:  # Should have at least manager, company, ISIN, position, date
                                self.logger.info(f"Successfully parsed {data_type} file as CSV with delimiter '{delimiter}' ({len(df.columns)} columns)")
                                return df
                            else:
                                self.logger.debug(f"Delimiter '{delimiter}' resulted in only {len(df.columns)} columns, trying next")
                                
                        except Exception as e:
                            self.logger.debug(f"Failed with delimiter '{delimiter}': {e}")
                            continue
                    
                    # If all specific delimiters fail, try with engine='python' which can auto-detect
                    df = pd.read_csv(io.StringIO(csv_content), engine='python')
                    self.logger.info(f"Successfully parsed {data_type} file as CSV with python engine")
                    return df
                    
                except Exception as csv_error:
                    self.logger.warning(f"Failed to parse {data_type} file as CSV: {csv_error}")
                    
                    # Try with different encoding
                    try:
                        csv_content = file_content.decode('latin-1')
                        
                        # Try different delimiters with latin-1 encoding
                        for delimiter in [';', ',', '\t']:
                            try:
                                df = pd.read_csv(io.StringIO(csv_content), delimiter=delimiter)
                                
                                # Check if we have multiple columns (proper parsing)
                                if len(df.columns) > 3:
                                    self.logger.info(f"Successfully parsed {data_type} file as CSV with latin-1 encoding and delimiter '{delimiter}' ({len(df.columns)} columns)")
                                    return df
                                    
                            except Exception as e:
                                self.logger.debug(f"Failed with latin-1 and delimiter '{delimiter}': {e}")
                                continue
                        
                        # If all delimiters fail, try with engine='python' which can auto-detect
                        df = pd.read_csv(io.StringIO(csv_content), engine='python')
                        self.logger.info(f"Successfully parsed {data_type} file as CSV with latin-1 encoding and python engine")
                        return df
                        
                    except Exception as latin_error:
                        self.logger.error(f"Failed to parse {data_type} file with all methods: {latin_error}")
                        return pd.DataFrame()
                        
        except Exception as e:
            self.logger.error(f"Error parsing {data_type} downloaded file: {e}")
            return pd.DataFrame()
