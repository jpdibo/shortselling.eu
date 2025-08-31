#!/usr/bin/env python3
"""Italy Short-selling Data Scraper"""

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_scraper import BaseScraper

class ItalyScraper(BaseScraper):
    """Scraper for Italy short-selling data from CONSOB"""
    
    def get_data_url(self) -> str:
        return "https://www.consob.it/web/consob-and-its-activities/short-selling"
    
    def download_data(self) -> Dict[str, Any]:
        """Download Italy short-selling data from CONSOB"""
        self.logger.info("Starting scrape for Italy")
        self.logger.info("Downloading Italy CONSOB data")
        
        # Use the actual working URL found in JavaScript
        import time
        import random
        
        base_url = "https://www.consob.it/documents/11973/395154/PncPubl.xlsx/fbefe0a2-795b-bad3-9369-beccbeb14f27"
        
        # Add a random timestamp as the JavaScript does
        rand = int(time.time() * 1000) + random.randint(1000, 9999)
        download_url = f"{base_url}?t={rand}"
        
        self.logger.info(f"Downloading from actual CONSOB URL: {download_url}")
        
        try:
            response = self.download_with_retry(download_url)
            
            # Check if we got a valid Excel file
            if b'PK' in response.content[:100]:  # Excel file signature
                self.logger.info(f"✅ Successfully downloaded CONSOB file ({len(response.content):,} bytes)")
                return {
                    'excel_content': response.content,
                    'source_url': download_url
                }
            else:
                raise Exception("Downloaded file is not a valid Excel file")
                
        except Exception as e:
            self.logger.error(f"Failed to download CONSOB file: {e}")
            raise Exception(f"CONSOB download failed: {e}")
    
    def _find_actual_download_url(self, soup: BeautifulSoup) -> str:
        """Try to find the actual download URL from the page"""
        # Look for script tags that might contain the download URL
        for script in soup.find_all('script'):
            if script.string:
                # Look for URLs in JavaScript code
                urls = re.findall(r'https?://[^\s"\']+\.(?:xlsx?|csv)', script.string)
                if urls:
                    return urls[0]
        
        # Look for data attributes that might contain the URL
        for element in soup.find_all(attrs={'data-url': True}):
            url = element.get('data-url')
            if url and ('xlsx' in url or 'csv' in url):
                return url
        
        # Look for any link with xlsx or csv extension
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.endswith(('.xlsx', '.xls', '.csv')):
                if not href.startswith('http'):
                    href = "https://www.consob.it" + href
                return href
        
        return None
    
    def parse_data(self, data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Parse Excel data into DataFrames"""
        excel_content = data['excel_content']
        
        try:
            # Try to read as Excel file using BytesIO to avoid deprecation warning
            from io import BytesIO
            excel_file = pd.ExcelFile(BytesIO(excel_content))
            self.logger.info(f"Processing {len(excel_file.sheet_names)} sheets: {excel_file.sheet_names}")
            
            all_dataframes = {}
            for sheet_name in excel_file.sheet_names:
                # Skip publication date sheet - it doesn't contain position data
                if 'Pubb. Data' in sheet_name or 'Pubb. Date' in sheet_name:
                    self.logger.info(f"Skipping publication date sheet: {sheet_name}")
                    continue
                    
                self.logger.info(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(BytesIO(excel_content), sheet_name=sheet_name)
                all_dataframes[sheet_name] = df
                
        except Exception as e:
            self.logger.warning(f"Failed to read as Excel: {e}")
            # Try to read as CSV
            try:
                df = pd.read_csv(BytesIO(excel_content))
                all_dataframes = {'data': df}
            except Exception as e2:
                self.logger.error(f"Failed to read as CSV: {e2}")
                raise Exception(f"Could not parse file as Excel or CSV: {e}")
        
        return all_dataframes
    
    def extract_positions(self, dataframes: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Extract position data from DataFrames"""
        positions = []
        
        for sheet_name, df in dataframes.items():
            self.logger.info(f"Extracting positions from {sheet_name} ({len(df)} rows)")
            
            # Determine if this is current or historical based on sheet name
            is_active = any(keyword in sheet_name.lower() for keyword in ['correnti', 'current', 'attuali'])
            
            # Map columns for Italy CONSOB data - using actual column names found
            possible_columns = {
                'manager': ['Detentore', 'Position holder', 'Titolare della posizione', 'Holder', 'Manager'],
                'company': ['Emittente', 'Issuer', 'Company', 'Name of Share Issuer'],
                'isin': ['ISIN', 'Isin'],
                'position_size': ['Perc. posizione netta corta', 'Net short position', 'Posizione netta corta', 'Position size', 'Net short position (%)'],
                'date': ['Data della posizione', 'Position date', 'Data posizione', 'Date', 'Position Date']
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
        
        self.logger.info(f"Extracted {len(positions)} total positions from Italy data")
        return positions
    
    def _infer_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer column mapping from DataFrame content"""
        column_mapping = {}
        
        # Look for columns that contain typical data patterns
        for col in df.columns:
            col_str = str(col).lower()
            
            # Check for manager/position holder columns
            if any(keyword in col_str for keyword in ['holder', 'titolare', 'manager', 'position']):
                if 'position' in col_str or 'holder' in col_str:
                    column_mapping['manager'] = col
            
            # Check for company/issuer columns
            elif any(keyword in col_str for keyword in ['issuer', 'emittente', 'company', 'name']):
                column_mapping['company'] = col
            
            # Check for ISIN columns
            elif 'isin' in col_str:
                column_mapping['isin'] = col
            
            # Check for position size columns
            elif any(keyword in col_str for keyword in ['position', 'size', 'corta', 'netta']):
                if 'size' in col_str or 'position' in col_str:
                    column_mapping['position_size'] = col
            
            # Check for date columns
            elif any(keyword in col_str for keyword in ['date', 'data']):
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
            
            # Handle Italian date format (dd/mm/yyyy)
            return pd.to_datetime(value, dayfirst=True)
        except:
            return None
    
    def _is_header_row(self, row) -> bool:
        """Check if row is a header row"""
        if len(row) == 0:
            return True
        
        first_value = str(row.iloc[0]).lower()
        header_keywords = ['position holder', 'issuer', 'isin', 'position', 'date', 'holder', 'emittente', 'titolare']
        return any(keyword in first_value for keyword in header_keywords)
    
    def _is_empty_row(self, row) -> bool:
        """Check if row is empty"""
        return row.isna().all() or (row == '').all()
