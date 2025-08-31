#!/usr/bin/env python3
"""
Analyze the structure of newly added country spreadsheets
Belgium, Spain, Germany, Ireland
"""

import pandas as pd
import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewCountryAnalyzer:
    """Analyze new country spreadsheet structures"""
    
    def __init__(self):
        self.base_path = Path("C:/shortselling.eu/excel_files")
        self.countries = {
            "Belgium": "🇧🇪",
            "Spain": "🇪🇸", 
            "Germany": "🇩🇪",
            "Ireland": "🇮🇪"
        }
    
    def analyze_all_new_countries(self):
        """Analyze all new countries"""
        print("🔍 Analyzing new country spreadsheets...")
        print("=" * 80)
        print("📋 Countries: Belgium, Spain, Germany, Ireland")
        print("=" * 80)
        
        for country_name, flag in self.countries.items():
            print(f"\n{flag} Analyzing {country_name}...")
            self.analyze_country(country_name)
    
    def analyze_country(self, country_name):
        """Analyze a specific country's files"""
        country_path = self.base_path / country_name
        
        if not country_path.exists():
            print(f"❌ No folder found for {country_name}")
            return
        
        print(f"📁 Found folder: {country_path}")
        
        # List all files in the country folder
        files = list(country_path.glob("*"))
        print(f"📄 Found {len(files)} files:")
        
        for file_path in files:
            print(f"   📄 {file_path.name}")
            
            if file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.analyze_excel_file(file_path, country_name)
            elif file_path.suffix.lower() == '.csv':
                self.analyze_csv_file(file_path, country_name)
            else:
                print(f"   ⚠️  Unknown file type: {file_path.suffix}")
    
    def analyze_excel_file(self, file_path, country_name):
        """Analyze Excel file structure"""
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            print(f"   📊 Excel file with {len(sheet_names)} tabs:")
            
            for i, sheet_name in enumerate(sheet_names, 1):
                print(f"      {i}. {sheet_name}")
                
                try:
                    # Read the sheet
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    print(f"         📈 Rows: {len(df):,} | Columns: {len(df.columns)}")
                    
                    # Show column names
                    print(f"         📋 Columns: {list(df.columns)}")
                    
                    # Show first few rows
                    print(f"         🔍 Sample data (first 3 rows):")
                    for idx, row in df.head(3).iterrows():
                        print(f"            Row {idx+1}: {dict(row)}")
                    
                    # Check for data patterns
                    self.analyze_data_patterns(df, f"{country_name} - {sheet_name}")
                    
                except Exception as e:
                    print(f"         ❌ Error reading tab {sheet_name}: {e}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing Excel file: {e}")
    
    def analyze_csv_file(self, file_path, country_name):
        """Analyze CSV file structure"""
        try:
            print(f"   📊 CSV file:")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    print(f"         ✅ Successfully read with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print(f"         ❌ Could not read CSV with any encoding")
                return
            
            print(f"         📈 Rows: {len(df):,} | Columns: {len(df.columns)}")
            print(f"         📋 Columns: {list(df.columns)}")
            
            # Show first few rows
            print(f"         🔍 Sample data (first 3 rows):")
            for idx, row in df.head(3).iterrows():
                print(f"            Row {idx+1}: {dict(row)}")
            
            # Check for data patterns
            self.analyze_data_patterns(df, f"{country_name} - CSV")
            
        except Exception as e:
            print(f"   ❌ Error analyzing CSV file: {e}")
    
    def analyze_data_patterns(self, df, source_name):
        """Analyze data patterns in the dataframe"""
        print(f"         🔍 Data analysis for {source_name}:")
        
        # Check for common short position column patterns
        position_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['position', 'short', 'net', 'perc', 'ratio', '%']):
                position_columns.append(col)
        
        if position_columns:
            print(f"            📊 Potential position columns: {position_columns}")
        
        # Check for date columns
        date_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['date', 'data', 'fecha']):
                date_columns.append(col)
        
        if date_columns:
            print(f"            📅 Potential date columns: {date_columns}")
        
        # Check for company/issuer columns
        company_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['company', 'issuer', 'emittent', 'emittente', 'empresa']):
                company_columns.append(col)
        
        if company_columns:
            print(f"            🏢 Potential company columns: {company_columns}")
        
        # Check for manager/holder columns
        manager_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['manager', 'holder', 'detentor', 'detentore', 'gestor']):
                manager_columns.append(col)
        
        if manager_columns:
            print(f"            👤 Potential manager columns: {manager_columns}")
        
        # Check for ISIN columns
        isin_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if 'isin' in col_lower:
                isin_columns.append(col)
        
        if isin_columns:
            print(f"            🆔 Potential ISIN columns: {isin_columns}")
        
        # Check for non-empty rows
        non_empty_rows = df.dropna(how='all').shape[0]
        print(f"            📊 Non-empty rows: {non_empty_rows:,}")
        
        # Check for header rows (rows that might be headers)
        potential_headers = 0
        for idx, row in df.iterrows():
            row_str = ' '.join(str(val).lower() for val in row.values if pd.notna(val))
            if any(header_word in row_str for header_word in ['position', 'holder', 'company', 'date', 'isin', 'short']):
                potential_headers += 1
        
        if potential_headers > 0:
            print(f"            📋 Potential header rows: {potential_headers}")

def main():
    """Main function"""
    print("📊 ShortSelling.eu - New Country Spreadsheet Analysis")
    print("=" * 80)
    print("🔍 Analyzing Belgium, Spain, Germany, Ireland spreadsheets")
    print("🔍 Understanding file structures, tabs, and column formats")
    print("=" * 80)
    
    analyzer = NewCountryAnalyzer()
    analyzer.analyze_all_new_countries()
    
    print(f"\n🎉 Analysis completed!")
    print(f"📈 Check the output above for file structures and column mappings")

if __name__ == "__main__":
    main()
