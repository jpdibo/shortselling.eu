#!/usr/bin/env python3
"""
Spain Short-selling Data Scraper

IMPORTANT: This scraper downloads ALL available data from CNMV, but the DailyScrapingService
will only add the most recent data that is not already in our database.

Logic:
1. Download current and historical data from CNMV
2. DailyScrapingService checks the most recent date in our database for Spain
3. Only positions from that date onwards (inclusive) are added to avoid duplicates
4. This ensures we get any updates to existing dates plus new dates
"""

import pandas as pd
import tempfile
import os
from io import BytesIO
from typing import List, Dict, Any
from .base_scraper import BaseScraper

class SpainScraper(BaseScraper):
    """Scraper for Spain short-selling data from CNMV"""
    
    def get_data_url(self) -> str:
        # CNMV direct Excel download URL
        return "https://www.cnmv.es/DocPortal/Posiciones-Cortas/NetShortPositions.xls"
    
    def download_data(self) -> Dict[str, Any]:
        """Download Spain CNMV data directly"""
        self.logger.info("Downloading Spain CNMV data directly")
        
        # Download the Excel file directly
        excel_response = self.download_with_retry(self.get_data_url())
        
        return {
            'excel_content': excel_response.content,
            'source_url': self.get_data_url()
        }
    
    def parse_data(self, data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Parse Excel data into DataFrames for multiple sheets"""
        excel_content = data['excel_content']
        
        # Read Excel file with multiple sheets
        excel_file = pd.ExcelFile(BytesIO(excel_content))
        dataframes = {}
        
        for sheet_name in excel_file.sheet_names:
            self.logger.info(f"Processing sheet: {sheet_name}")
            
            # Read the sheet without header first to get the structure
            df_raw = pd.read_excel(BytesIO(excel_content), sheet_name=sheet_name, header=None)
            
            # FIXED: Better header detection - search for LEI and ISIN anywhere in first 8 rows
            header_row_idx = None
            for i in range(min(8, len(df_raw))):  # Check first 8 rows
                row = df_raw.iloc[i]
                row_str = ' '.join(str(cell) for cell in row if pd.notna(cell))
                if 'LEI' in row_str and 'ISIN' in row_str:
                    header_row_idx = i
                    break
            
            if header_row_idx is not None:
                # Set the column names from the header row
                df_raw.columns = df_raw.iloc[header_row_idx]
                # Remove rows up to and including the header row
                df = df_raw.iloc[header_row_idx + 1:].reset_index(drop=True)
            else:
                df = df_raw
            
            # Determine sheet type and is_active status based on sheet name
            sheet_lower = sheet_name.lower()
            if 'última' in sheet_lower or 'current' in sheet_lower:
                sheet_type = 'current'
                is_active = True
            elif 'serie' in sheet_lower or 'series' in sheet_lower:
                sheet_type = 'series'
                is_active = False  # Will be filtered later to exclude current positions
            elif 'anteriores' in sheet_lower or 'previous' in sheet_lower:
                sheet_type = 'previous'
                is_active = False
            else:
                sheet_type = 'unknown'
                is_active = False
            
            # Add metadata
            df['sheet_name'] = sheet_name
            df['sheet_type'] = sheet_type
            df['is_active'] = is_active
            
            dataframes[sheet_name] = df
        
        return dataframes
    
    def extract_positions(self, dataframes: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Extract position data from all DataFrames"""
        all_positions = []
        
        # Map columns for Spain CNMV data
        column_mapping = {
            'manager': 'Tenedor de la Posición / Position holder',
            'company': 'Emisor / Issuer',
            'isin': 'ISIN',
            'position_size': 'Posición corta (%) / Net short position (%)',
            'date': 'Fecha posición / Position date'
        }
        
        # First, extract current positions to use as reference for filtering series tab
        current_positions = set()
        
        # Process current tab first to get reference positions
        for sheet_name, df in dataframes.items():
            # Check if DataFrame is not empty before accessing iloc[0]
            if not df.empty and len(df) > 0 and df['sheet_type'].iloc[0] == 'current':
                self.logger.info(f"Processing current tab: {sheet_name}")
                current_positions_data = self._extract_sheet_positions(df, sheet_name, column_mapping, is_active=True)
                all_positions.extend(current_positions_data)
                
                # FIXED: Better duplicate key including position size
                for pos in current_positions_data:
                    pos_key = (pos['date'], pos['position_size'], pos['company_name'], pos['manager_name'], pos['isin'])
                    current_positions.add(pos_key)
        
        # Now process series and previous tabs
        for sheet_name, df in dataframes.items():
            # Check if DataFrame is not empty before accessing iloc[0]
            if df.empty or len(df) == 0:
                self.logger.warning(f"Skipping empty sheet: {sheet_name}")
                continue
                
            sheet_type = df['sheet_type'].iloc[0]
            self.logger.info(f"Extracting positions from {sheet_name} ({sheet_type}) ({len(df)} rows)")
            
            if sheet_type == 'series':
                # Series tab - exclude positions that match current tab, rest are inactive
                positions = self._extract_sheet_positions(df, sheet_name, column_mapping, is_active=False)
                
                # FIXED: Better duplicate detection including position size
                filtered_positions = []
                for pos in positions:
                    # Create a unique key for comparison (same as current positions)
                    pos_key = (pos['date'], pos['position_size'], pos['company_name'], pos['manager_name'], pos['isin'])
                    if pos_key not in current_positions:
                        filtered_positions.append(pos)
                    else:
                        self.logger.debug(f"Filtering out duplicate position from series: {pos['manager_name']} - {pos['company_name']} ({pos['position_size']}%)")
                
                all_positions.extend(filtered_positions)
                self.logger.info(f"Series tab: kept {len(filtered_positions)} out of {len(positions)} positions after filtering")
                
            elif sheet_type == 'previous':
                # Previous tab - all positions are inactive
                positions = self._extract_sheet_positions(df, sheet_name, column_mapping, is_active=False)
                all_positions.extend(positions)
                
            elif sheet_type == 'current':
                # Current tab already processed above
                continue
                
            else:
                # Unknown tab - skip
                self.logger.warning(f"Skipping unknown sheet type: {sheet_name}")
        
        self.logger.info(f"Extracted {len(all_positions)} total positions from Spain data")
        return all_positions
    
    def _extract_sheet_positions(self, df: pd.DataFrame, sheet_name: str, column_mapping: Dict[str, str], is_active: bool) -> List[Dict[str, Any]]:
        """Extract positions from a single sheet"""
        positions = []
        
        # Check if DataFrame is empty
        if df.empty or len(df) == 0:
            self.logger.warning(f"Empty DataFrame for sheet: {sheet_name}")
            return positions
        
        # FIXED: Don't slice twice - use the data as is
        working_df = df.copy()
        
        if not working_df.empty:
            try:
                # Basic cleaning only - let DailyScrapingService handle normalization
                def clean_text_vectorized(series):
                    return series.fillna('').astype(str).str.strip().str.replace('\x9c', 'o').str.replace('\x9d', 'o').str.replace('\x9e', 'o')
                
                working_df['manager_name'] = clean_text_vectorized(working_df[column_mapping['manager']])
                working_df['company_name'] = clean_text_vectorized(working_df[column_mapping['company']])
                working_df['isin'] = clean_text_vectorized(working_df[column_mapping['isin']]).str.upper()  # ISIN should always be uppercase
                working_df['isin'] = working_df['isin'].replace('', None)
                
                # FIXED: Better position size parsing
                def parse_position_size(series):
                    # Convert to string, strip %, replace comma with dot, remove spaces
                    cleaned = series.astype(str).str.strip().str.replace('%', '').str.replace(',', '.').str.replace(' ', '')
                    # Convert to numeric, coerce errors to NaN
                    return pd.to_numeric(cleaned, errors='coerce')
                
                working_df['position_size'] = parse_position_size(working_df[column_mapping['position_size']])
                
                # Vectorized date parsing
                working_df['date'] = pd.to_datetime(working_df[column_mapping['date']])
                
                # Set is_active based on parameter
                working_df['is_active'] = is_active
                
                # Convert to list of dictionaries
                sheet_positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'is_active']].to_dict('records')
                
                # FIXED: Better validation - check for NaN position sizes
                valid_positions = []
                for pos in sheet_positions:
                    if (pos['manager_name'] and pos['company_name'] and 
                        pd.notna(pos['position_size']) and pos['position_size'] >= 0 and pos['position_size'] <= 100 and
                        pd.notna(pos['date'])):
                        valid_positions.append(pos)
                
                return valid_positions
                
            except Exception as e:
                self.logger.error(f"Error processing sheet {sheet_name}: {str(e)}")
                return positions
        else:
            self.logger.warning(f"Working DataFrame is empty for sheet: {sheet_name}")
        
        return positions
    
    def _is_header_row(self, row) -> bool:
        """Check if row is a header row"""
        # Check if the first column contains the exact header text
        first_col = str(row.iloc[0]).strip()
        
        # Look for exact header matches (case insensitive)
        header_indicators = [
            'LEI',
            'ISIN',
            'Emisor / Issuer',
            'Tenedor de la Posición / Position holder',
            'Fecha posición / Position date',
            'Posición corta (%) / Net short position (%)'
        ]
        
        # Check if the first column exactly matches any header indicator
        for indicator in header_indicators:
            if first_col.lower() == indicator.lower():
                return True
        
        # Additional check: if first column is empty or contains only whitespace
        if not first_col:
            return True
            
        return False
