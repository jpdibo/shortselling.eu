#!/usr/bin/env python3
"""Ireland Short-selling Data Scraper"""

import pandas as pd
import tempfile
import os
import requests
from typing import List, Dict, Any
from .base_scraper import BaseScraper

class IrelandScraper(BaseScraper):
    """Scraper for Ireland short-selling data from Central Bank"""
    
    def __init__(self, country_code: str = "IE", country_name: str = "Ireland"):
        super().__init__(country_code, country_name)
    
    def get_data_url(self) -> str:
        """Get the main data source URL"""
        return "https://www.centralbank.ie/regulation/industry-market-sectors/securities-markets/short-selling-regulation/public-net-short-positions"
    
    def get_excel_url(self) -> str:
        """Get the Excel file download URL"""
        return "https://www.centralbank.ie/docs/default-source/regulation/industry-market-sectors/securities-markets/short-selling-regulation/public-net-short-positions/table-of-significant-net-short-positions-in-shares.xlsx?sfvrsn=49c7d61d_945"
    
    def download_data(self) -> Dict[str, Any]:
        """Download Ireland Central Bank data"""
        self.logger.info("Starting scrape for Ireland")
        self.logger.info("Downloading Ireland Central Bank data from centralbank.ie")
        
        try:
            # Download Excel file
            excel_url = self.get_excel_url()
            self.logger.info(f"Fetching data from: {excel_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(excel_url, headers=headers, timeout=60)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}")
            
            self.logger.info(f"Successfully downloaded {len(response.content)} bytes")
            
            return {
                'excel_content': response.content,
                'source_url': self.get_data_url(),
                'excel_url': excel_url
            }
        except Exception as e:
            self.logger.error(f"Failed to download Ireland data: {e}")
            raise Exception(f"Ireland download failed: {e}")
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse Excel data into a single DataFrame combining all sheets"""
        self.logger.info("Parsing Ireland Excel data")
        
        if not data['excel_content']:
            return pd.DataFrame()
        
        excel_content = data['excel_content']
        
        # Read all sheets from the Excel file
        import io
        excel_file = pd.ExcelFile(io.BytesIO(excel_content))
        all_dataframes = []
        
        self.logger.info(f"Found {len(excel_file.sheet_names)} sheets: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            self.logger.info(f"Processing sheet: {sheet_name}")
            
            try:
                # Read the sheet
                df = pd.read_excel(io.BytesIO(excel_content), sheet_name=sheet_name)
                
                # Determine if this is current or historical based on sheet name
                is_active = 'current' in sheet_name.lower()
                
                # Add metadata
                df['sheet_name'] = sheet_name
                df['is_active'] = is_active
                
                all_dataframes.append(df)
                self.logger.info(f"Parsed {len(df)} rows from sheet: {sheet_name}")
                
            except Exception as e:
                self.logger.warning(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        # Combine all dataframes
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            self.logger.info(f"Combined {len(combined_df)} total rows from all sheets")
            return combined_df
        else:
            return pd.DataFrame()
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract position data from DataFrame"""
        self.logger.info("Extracting positions from Ireland data")
        positions = []
        
        if df.empty:
            self.logger.warning("No data to extract positions from")
            return positions
        
        self.logger.info(f"Extracting positions from {len(df)} rows")
        
        # Map columns for Ireland Central Bank data
        # The Excel file has different column names, so we need to be flexible
        possible_column_mappings = [
            {
                'manager': 'Position Holder:',
                'company': 'Name of the Issuer:',
                'isin': 'ISIN:',
                'position_size': 'Net short position %:',
                'date': 'Position Date:'
            },
            {
                'manager': 'Position Holder',
                'company': 'Name of the Issuer',
                'isin': 'ISIN',
                'position_size': 'Net short position %',
                'date': 'Position Date'
            },
            {
                'manager': 'Position Holder',
                'company': 'Issuer',
                'isin': 'ISIN',
                'position_size': 'Net short position',
                'date': 'Date'
            }
        ]
        
        # Find the correct column mapping
        column_mapping = None
        for mapping in possible_column_mappings:
            if all(col in df.columns for col in mapping.values()):
                column_mapping = mapping
                break
        
        if not column_mapping:
            self.logger.warning(f"Could not find expected columns. Available columns: {list(df.columns)}")
            return positions
        
        self.logger.info(f"Using column mapping: {column_mapping}")
        
        # Vectorized processing - much faster than row by row
        # Remove header rows
        working_df = df[~df.apply(self._is_header_row, axis=1)].copy()
        
        if working_df.empty:
            return []
        
        # Basic cleaning only - let DailyScrapingService handle normalization
        working_df['manager_name'] = working_df[column_mapping['manager']].fillna('').astype(str).str.strip()
        working_df['company_name'] = working_df[column_mapping['company']].fillna('').astype(str).str.strip()
        working_df['isin'] = working_df[column_mapping['isin']].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
        working_df['isin'] = working_df['isin'].replace('', None)
        
        # Filter out rows with missing essential data
        working_df = working_df[
            (working_df['manager_name'] != '') & 
            (working_df['manager_name'] != 'nan') & 
            (working_df['company_name'] != '') & 
            (working_df['company_name'] != 'nan')
        ]
        
        if working_df.empty:
            return []
        
        # Vectorized position size parsing
        working_df['position_size'] = working_df[column_mapping['position_size']].astype(str).str.replace('%', '').str.replace(',', '.').astype(float) * 100
        
        # Vectorized date parsing
        working_df['date'] = pd.to_datetime(working_df[column_mapping['date']])
        
        # Add country code and is_active
        working_df['country_code'] = self.country_code
        working_df['is_active'] = working_df['is_active']
        
        # Convert to list of dictionaries
        positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'country_code', 'is_active']].to_dict('records')
        
        # Filter valid positions
        valid_positions = [pos for pos in positions if self.validate_position(pos)]
        
        self.logger.info(f"Extracted {len(valid_positions)} total positions from Ireland data")
        return valid_positions
    
    def _is_header_row(self, row) -> bool:
        """Check if row is a header row"""
        value = str(row.iloc[0]).lower()
        return 'position holder' in value or 'name of the issuer' in value or 'isin' in value
