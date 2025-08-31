#!/usr/bin/env python3
"""
UK Short-selling Data Scraper

Zero-safe parsing:
- Accepts 0 / 0.0 / "0" / "0.00" / "0%" / "0,00%" / "0 %"
- Leaves weird tokens like "<0.5" unparsed (None) rather than guessing.
"""

import pandas as pd
from io import BytesIO
from typing import List, Dict, Any, Union
from .base_scraper import BaseScraper

class UKScraper(BaseScraper):
    """Scraper for UK short-selling data from FCA"""
    
    def get_data_url(self) -> str:
        return "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    def download_data(self) -> Dict[str, Any]:
        """Download UK short-selling data directly"""
        self.logger.info("Downloading UK FCA data directly")
        excel_response = self.download_with_retry(self.get_data_url())
        return {
            'excel_content': excel_response.content,
            'source_url': self.get_data_url()
        }
    
    # ---------- helpers ----------
    @staticmethod
    def _parse_percent(value) -> Union[float, None]:
        """
        Robust % parser:
          - numeric: passthrough
          - strings: strip %, spaces; normalize comma to dot; parse float
          - returns None if not parseable
        """
        if value is None:
            return None
        if isinstance(value, (int, float)):
            # already numeric (zero included)
            return float(value)
        s = str(value).strip()
        if s == "":
            return None
        # strip %
        if "%" in s:
            s = s.replace("%", "")
        # normalize comma
        s = s.replace(",", ".")
        # remove spaces
        s = s.replace(" ", "")
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def _parse_date(value):
        if value is None:
            return None
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return None
        # ensure naive
        if getattr(dt, "tzinfo", None) is not None:
            try:
                dt = dt.tz_convert(None)
            except Exception:
                dt = dt.tz_localize(None)
        return dt

    def parse_data(self, data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Parse Excel data into DataFrames for both sheets"""
        excel_content = data['excel_content']
        xls = pd.ExcelFile(BytesIO(excel_content))
        dataframes: Dict[str, pd.DataFrame] = {}
        
        for sheet_name in xls.sheet_names:
            self.logger.info(f"Processing sheet: {sheet_name}")
            df = pd.read_excel(BytesIO(excel_content), sheet_name=sheet_name)
            is_active = 'current' in sheet_name.lower()
            df['sheet_name'] = sheet_name
            df['is_active'] = is_active
            dataframes[sheet_name] = df
        
        return dataframes
    
    def extract_positions(self, dataframes: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Extract position data from all DataFrames"""
        all_positions: List[Dict[str, Any]] = []
        
        col = {
            'manager': 'Position Holder',
            'company': 'Name of Share Issuer',
            'isin': 'ISIN',
            'position_size': 'Net Short Position (%)',
            'date': 'Position Date'
        }
        
        for sheet_name, df in dataframes.items():
            self.logger.info(f"Extracting positions from {sheet_name} ({len(df)} rows)")
            
            # quick column sanity
            missing = [v for v in col.values() if v not in df.columns]
            if missing:
                self.logger.warning(f"Skipping sheet '{sheet_name}' — missing columns: {missing}")
                continue

            # Vectorized processing - much faster than row by row
            if not df.empty:
                # Create working copy
                working_df = df.copy()
                
                # Basic cleaning only - let DailyScrapingService handle normalization
                working_df['manager_name'] = working_df[col['manager']].fillna('').astype(str).str.strip()
                working_df['company_name'] = working_df[col['company']].fillna('').astype(str).str.strip()
                working_df['isin'] = working_df[col['isin']].fillna('').astype(str).str.strip().str.upper()  # ISIN should always be uppercase
                working_df['isin'] = working_df['isin'].replace('', None)
                
                # Vectorized position size parsing
                working_df['position_size'] = working_df[col['position_size']].apply(self._parse_percent)
                
                # Vectorized date parsing
                working_df['date'] = working_df[col['date']].apply(self._parse_date)
                working_df['date'] = working_df['date'].apply(lambda x: x.to_pydatetime() if x is not None else None)
                
                # Add is_active column
                working_df['is_active'] = bool(df['is_active'].iloc[0])
                
                # Convert to list of dictionaries
                sheet_positions = working_df[['manager_name', 'company_name', 'isin', 'position_size', 'date', 'is_active']].to_dict('records')
                
                # Filter valid positions
                valid_positions = [pos for pos in sheet_positions if self.validate_position(pos)]
                all_positions.extend(valid_positions)
                
                self.logger.info(f"Extracted {len(valid_positions)} valid positions from {sheet_name}")
        
        # Log zeros seen
        zero_count = sum(1 for p in all_positions if p.get('position_size') == 0.0)
        self.logger.info(f"UK zeros parsed: {zero_count}")
        self.logger.info(f"Extracted {len(all_positions)} total positions from UK data")
        return all_positions
