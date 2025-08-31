#!/usr/bin/env python3
"""Belgium Short-selling Data Scraper"""

import pandas as pd
import tempfile
import os
import requests
from typing import List, Dict, Any
from .base_scraper import BaseScraper

class BelgiumScraper(BaseScraper):
    """Scraper for Belgium short-selling data from FSMA"""
    
    def __init__(self, country_code: str = "BE", country_name: str = "Belgium"):
        super().__init__(country_code, country_name)
    
    def get_data_url(self) -> str:
        """Get the main data source URL"""
        return "https://www.fsma.be/en/shortselling"
    
    def get_current_csv_url(self) -> str:
        """Get the current positions CSV download URL"""
        return "https://www.fsma.be/en/de-shortselling?page&_format=csv"
    
    def get_historical_csv_url(self) -> str:
        """Get the historical positions CSV download URL"""
        return "https://www.fsma.be/en/de-shortselling-history?page&_format=csv"
    
    def download_data(self) -> Dict[str, Any]:
        """Download Belgium FSMA data"""
        self.logger.info("Starting scrape for Belgium")
        self.logger.info("Downloading Belgium FSMA data from fsma.be")
        
        try:
            # Download current positions
            current_url = self.get_current_csv_url()
            self.logger.info(f"Fetching current data from: {current_url}")
            current_response = requests.get(current_url, timeout=60)
            
            if current_response.status_code != 200:
                raise Exception(f"Failed to fetch current data: {current_response.status_code}")
            
            # Download historical positions
            historical_url = self.get_historical_csv_url()
            self.logger.info(f"Fetching historical data from: {historical_url}")
            historical_response = requests.get(historical_url, timeout=60)
            
            if historical_response.status_code != 200:
                raise Exception(f"Failed to fetch historical data: {historical_response.status_code}")
            
            self.logger.info(f"Successfully downloaded {len(current_response.content)} bytes (current) and {len(historical_response.content)} bytes (historical)")
            
            return {
                'current_csv': current_response.content,
                'historical_csv': historical_response.content,
                'current_url': current_url,
                'historical_url': historical_url,
                'source_url': self.get_data_url()
            }
        except Exception as e:
            self.logger.error(f"Failed to download Belgium data: {e}")
            raise Exception(f"Belgium download failed: {e}")
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse CSV data into a single DataFrame combining current and historical"""
        self.logger.info("Parsing Belgium CSV data")
        
        all_dataframes = []
        
        # Parse current positions
        if data['current_csv']:
            try:
                import io
                df_current = pd.read_csv(
                    io.BytesIO(data['current_csv']),
                    encoding='utf-8',
                    sep=',',
                    quotechar='"'
                )
                df_current['is_active'] = True
                all_dataframes.append(df_current)
                self.logger.info(f"Parsed {len(df_current)} current positions")
            except Exception as e:
                self.logger.warning(f"Error parsing current data: {e}")
        
        # Parse historical positions
        if data['historical_csv']:
            try:
                import io
                df_historical = pd.read_csv(
                    io.BytesIO(data['historical_csv']),
                    encoding='utf-8',
                    sep=',',
                    quotechar='"'
                )
                df_historical['is_active'] = False
                all_dataframes.append(df_historical)
                self.logger.info(f"Parsed {len(df_historical)} historical positions")
            except Exception as e:
                self.logger.warning(f"Error parsing historical data: {e}")
        
        # Combine all dataframes
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            self.logger.info(f"Combined {len(combined_df)} total rows")
            return combined_df
        else:
            return pd.DataFrame()
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract position data from DataFrame"""
        self.logger.info("Extracting positions from Belgium data")
        
        if df.empty:
            self.logger.warning("No data to extract positions from")
            return []
        
        self.logger.info(f"Extracting positions from {len(df)} rows")
        
        # Map columns for Belgium FSMA data based on the CSV format
        column_mapping = {
            'manager': 'Position holder',
            'company': 'Issuer',
            'isin': 'ISIN',
            'position_size': 'Net short position',
            'date': 'Position date',
            'change_date': 'Change Position Date'
        }
        
        # Vectorized processing - much faster than row by row
        # Remove header rows
        working_df = df[~df.apply(self._is_header_row, axis=1)].copy()
        
        if working_df.empty:
            return []
        
        # Basic cleaning only - let DailyScrapingService handle normalization
        working_df['manager_name'] = working_df[column_mapping['manager']].fillna('').astype(str).str.strip().str.strip('"')
        working_df['company_name'] = working_df[column_mapping['company']].fillna('').astype(str).str.strip().str.strip('"')
        working_df['isin'] = working_df[column_mapping['isin']].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
        working_df['isin'] = working_df['isin'].replace('', None)
        
        # Vectorized position size parsing (handle Belgian comma format)
        working_df['position_size'] = working_df[column_mapping['position_size']].astype(str).str.replace(',', '.').astype(float)
        
        # Vectorized date parsing
        working_df['date'] = pd.to_datetime(working_df[column_mapping['date']], format='%d/%m/%Y')
        
        # Add country code and is_active
        working_df['country_code'] = self.country_code
        working_df['is_active'] = working_df['is_active']
        
        # Handle change date if available
        if column_mapping['change_date'] in working_df.columns:
            working_df['change_date'] = pd.to_datetime(working_df[column_mapping['change_date']], format='%d/%m/%Y', errors='coerce')
        
        # Convert to list of dictionaries
        positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'country_code', 'is_active']].to_dict('records')
        
        # Add change_date to positions that have it
        if column_mapping['change_date'] in working_df.columns:
            for i, pos in enumerate(positions):
                if pd.notna(working_df.iloc[i]['change_date']):
                    pos['change_date'] = working_df.iloc[i]['change_date']
        
        # Standardize and filter valid positions
        standardized_positions = []
        for pos in positions:
            if self.validate_position(pos):
                standardized_pos = self.standardize_position(pos)
                standardized_positions.append(standardized_pos)
        
        self.logger.info(f"Extracted {len(standardized_positions)} total positions from Belgium data")
        return standardized_positions
    
    def _is_header_row(self, row) -> bool:
        """Check if row is a header row"""
        value = str(row.iloc[0]).lower()
        return 'position holder' in value or 'issuer' in value or 'isin' in value
