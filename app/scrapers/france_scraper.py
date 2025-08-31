#!/usr/bin/env python3
"""
France Short-Selling Scraper
Fetches data from data.gouv.fr - AMF (Autorité des marchés financiers)
"""

import requests
import pandas as pd
import io
import logging
import unicodedata  # NEW: for Unicode normalization (acentos + Arabic)
from datetime import datetime
from typing import Dict, Any, List
from .base_scraper import BaseScraper


# NEW: encoding detector used by parse_data
def _detect_encoding(data: bytes) -> str:
    """
    Detect a reasonable encoding for CSV bytes without dropping characters.
    Preference order:
      - UTF-8 with BOM (utf-8-sig)
      - UTF-8
      - charset-normalizer best guess (if installed)
      - latin-1 fallback
    """
    # UTF-8 with BOM?
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    # Try strict UTF-8
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    # Try charset-normalizer if available
    try:
        from charset_normalizer import from_bytes  # type: ignore
        best = from_bytes(data).best()
        if best and best.encoding:
            return best.encoding
    except Exception:
        pass
    # Safe fallback
    return "latin-1"


class FranceScraper(BaseScraper):
    """Scraper for French short-selling data from data.gouv.fr"""
    
    def __init__(self, country_code: str = "FR", country_name: str = "France"):
        super().__init__(country_code, country_name)
        
    def get_data_url(self) -> str:
        """Get the main data source URL"""
        return "https://www.data.gouv.fr/datasets/historique-des-positions-courtes-nettes-sur-actions-rendues-publiques-depuis-le-1er-novembre-2012/"
    
    def get_api_url(self) -> str:
        """Get the direct API URL for CSV download"""
        return "https://www.data.gouv.fr/api/1/datasets/r/c2539d1c-8531-4937-9cba-3bd8e9786cc5"
    
    def _parse_position_size(self, value) -> float:
        """Parse position size from French format"""
        try:
            if pd.isna(value):
                return 0.0
            
            # Convert to string and clean
            value_str = str(value).strip()
            
            # Remove any percentage signs and convert to float
            value_str = value_str.replace('%', '').replace(',', '.')
            
            # Convert to float and ensure it's a percentage (0-100 range)
            position_size = float(value_str)
            
            # Validate range
            if position_size < 0 or position_size > 100:
                self.logger.warning(f"Invalid position size: {position_size}%, setting to 0")
                return 0.0
            
            return position_size
            
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Could not parse position size '{value}': {e}")
            return 0.0
    
    def download_data(self) -> Dict[str, Any]:
        """Download French short-selling data from data.gouv.fr"""
        self.logger.info("Starting scrape for France")
        self.logger.info("Downloading France AMF data from data.gouv.fr")
        
        try:
            # Direct API call to get CSV data
            api_url = self.get_api_url()
            self.logger.info(f"Fetching data from API: {api_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/csv,application/csv,*/*',
                'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            }
            
            response = requests.get(api_url, headers=headers, timeout=60)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data from API: {response.status_code}")
            
            self.logger.info(f"Successfully downloaded {len(response.content)} bytes")
            
            return {
                'csv_data': response.content,
                'source_url': self.get_data_url(),
                'api_url': api_url,
                'download_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download France data: {e}")
            raise Exception(f"France download failed: {e}")
    
    def parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse the downloaded CSV data"""
        self.logger.info("Parsing France CSV data")
        
        try:
            # Read CSV data
            csv_content = data['csv_data']

            # NEW: detect encoding to preserve Arabic + acentos
            enc = _detect_encoding(csv_content)
            self.logger.info(f"Detected CSV encoding: {enc}")
            
            # Parse CSV with detected encoding and semicolon separator
            df = pd.read_csv(
                io.BytesIO(csv_content),
                encoding=enc,
                sep=';',
                quotechar='"',
                thousands=',',
                decimal='.',
                parse_dates=['Date de debut position',
                             'Date de debut de publication position',
                             'Date de fin de publication position']
            )
            
            # NEW: normalize all text columns to NFC (preserve diacritics/Arabic)
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].map(
                    lambda x: unicodedata.normalize('NFC', x) if isinstance(x, str) else x
                )

            self.logger.info(f"Parsed {len(df)} rows from France CSV")
            self.logger.info(f"France CSV columns: {list(df.columns)}")
            
            # Log sample ISIN data to verify
            if 'code ISIN' in df.columns:
                sample_isins = df['code ISIN'].dropna().head(5).tolist()
                self.logger.info(f"Sample ISIN values: {sample_isins}")
            else:
                self.logger.warning("'code ISIN' column not found in France data!")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to parse France data: {e}")
            raise Exception(f"France data parsing failed: {e}")
    
    def extract_positions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract short positions from parsed data"""
        self.logger.info("Extracting positions from France data")
        
        positions = []
        
        try:
            # Map French column names to our standard format
            column_mapping = {
                'Detenteur de la position courte nette': 'manager_name',
                'Legal Entity Identifier detenteur': 'lei',
                'Emetteur / issuer': 'company_name',
                'Ratio': 'position_size',
                'code ISIN': 'isin',
                'Date de debut position': 'position_start_date',
                'Date de debut de publication position': 'publication_start_date',
                'Date de fin de publication position': 'publication_end_date'
            }
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Extract all raw data first (no normalization beyond parse_data)
            for _, row in df.iterrows():
                try:
                    # Parse position size (convert percentage to decimal)
                    position_size = self._parse_position_size(row.get('position_size', 0))
                    
                    # Use position start date as the main date (Date de debut position)
                    position_date = row.get('position_start_date')
                    if pd.isna(position_date):
                        # Fallback to publication start date if position start date is missing
                        position_date = row.get('publication_start_date')
                    
                    if pd.isna(position_date):
                        continue
                    
                    # Get raw data (already NFC-normalized in parse_data)
                    company_name = str(row.get('company_name', ''))
                    if not company_name or company_name == 'nan':
                        continue
                    
                    manager_name = str(row.get('manager_name', ''))
                    if not manager_name or manager_name == 'nan':
                        continue
                    
                    isin = str(row.get('isin', ''))
                    if not isin or isin == 'nan':
                        continue
                    
                    position_data = {
                        'manager_name': manager_name,
                        'company_name': company_name,
                        'isin': isin,
                        'position_size': position_size,
                        'date': position_date,
                        'country_code': self.country_code,
                        'lei': row.get('lei', ''),
                        'position_start_date': row.get('position_start_date'),
                        'publication_start_date': row.get('publication_start_date'),
                        'publication_end_date': row.get('publication_end_date')
                    }
                    
                    positions.append(position_data)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing row: {e}")
                    continue
            
            # Apply France-specific is_active logic based on most recent position per (manager, company/ISIN)
            positions = self._apply_france_active_logic(positions)
            
            self.logger.info(f"Extracted {len(positions)} positions from France data")
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to extract France positions: {e}")
            raise Exception(f"France position extraction failed: {e}")
    
    def _apply_france_active_logic(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        France logic:
          - One 'is_active=True' row per (manager, ISIN/company) — the most recent disclosure.
          - 'is_active' applies ONLY to the current row: position_size >= 0.5.
          - Historical rows: is_active=False; keep 'was_active_at_row_time' for analysis.
          - 'transition' set on the current row by comparing current vs. previous.
        """
        self.logger.info("Applying France-specific active logic...")

        if not positions:
            return positions

        df = pd.DataFrame(positions).copy()

        # Choose the timeline anchor:
        # Use position_start_date as primary with publication_start_date as fallback
        # This matches the company page logic for consistent results
        df['sort_date'] = pd.to_datetime(
            df['position_start_date'].fillna(df['publication_start_date'])
        )

        # Robust fallback if both are NaT
        df['sort_date'] = pd.to_datetime(df['sort_date'])

        # Normalize identifiers ONCE (much faster than row by row)
        df['isin'] = df['isin'].fillna('').str.strip().str.upper()
        df['company_name'] = df['company_name'].fillna('').str.strip()
        df['manager_name'] = df['manager_name'].fillna('').str.strip()

        # NOTE (requested): removed lossy encode/decode that dropped non-ASCII characters

        # Create manager_company_key efficiently
        df['manager_company_key'] = df['manager_name'] + '_' + df['isin'].fillna(df['company_name'])

        # Sort newest first within each key; tie-break by publication_end_date presence and size
        df = df.sort_values(
            by=['manager_company_key', 'sort_date', 'publication_end_date', 'position_size'],
            ascending=[True, False, True, False]
        )

        # Rank per key (1 = most recent)
        df['recency_rank'] = df.groupby('manager_company_key')['sort_date'].rank(
            method='first', ascending=False
        )

        # Exactly one active row per key
        df['is_active'] = df['recency_rank'] == 1

        # Historical truth at the time of each row (useful but optional)
        df['was_active_at_row_time'] = df['position_size'] >= 0.5

        # CORRECT LOGIC (as in your original script): keep your subsequent rules unchanged
        from datetime import datetime as _dt, timedelta as _td
        date_barrier = _dt.now() - _td(days=730)  # 2 years ago

        df['is_active'] = False
        current_mask = df['recency_rank'] == 1  # Use recency rank instead of is_active
        size_mask = df['position_size'] >= 0.5
        null_end_date_mask = pd.isna(df['publication_end_date'])
        recent_mask = df['sort_date'] >= date_barrier

        df.loc[current_mask & size_mask & null_end_date_mask & recent_mask, 'is_active'] = True

        # Transition classification on current row only
        cur = df[df['recency_rank'] == 1][['manager_company_key', 'position_size']].rename(
            columns={'position_size': 'curr_size'}
        )
        prev = df[df['recency_rank'] == 2][['manager_company_key', 'position_size']].rename(
            columns={'position_size': 'prev_size'}
        )
        trans = cur.merge(prev, on='manager_company_key', how='left')

        def classify_transition(row):
            curr = row['curr_size']
            prev = row['prev_size']
            curr_active = curr >= 0.5
            prev_active = (prev >= 0.5) if pd.notna(prev) else None
            if pd.isna(prev):
                return 'entered' if curr_active else 'inactive_first'
            if (not prev_active) and curr_active:
                return 'entered'
            if prev_active and (not curr_active):
                return 'exited'
            if prev_active and curr_active:
                return 'active_size_change' if curr != prev else 'active_unchanged'
            return 'inactive_unchanged'

        trans['transition'] = trans.apply(classify_transition, axis=1)

        # Initialize transition column and map onto current rows
        df['transition'] = None
        df.loc[df['recency_rank'] == 1, 'transition'] = df.loc[df['recency_rank'] == 1, 'manager_company_key'] \
            .map(dict(zip(trans['manager_company_key'], trans['transition'])))

        # Optional: expose a clean 'timeline_date' used for ordering / charts
        df['timeline_date'] = df['sort_date']

        # Convert back to list[dict]
        out = df.drop(columns=['sort_date']).to_dict(orient='records')

        # Stats
        active_count = sum(1 for p in out if p.get('is_active'))
        total_keys = df['manager_company_key'].nunique()

        self.logger.info(f"France logic applied: {active_count}/{total_keys} current positions active (≥0.5%).")

        return out
