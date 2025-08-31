#!/usr/bin/env python3
"""
Analyze data quality errors in Excel/CSV files without importing to database
Shows all potential issues that could cause positions to be skipped
"""

import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQualityAnalyzer:
    """Analyze data quality in Excel/CSV files"""
    
    def __init__(self):
        self.base_path = Path("C:/shortselling.eu/excel_files")
        self.total_rows_analyzed = 0
        self.total_rows_with_errors = 0
        self.error_details = []
    
    def analyze_all_countries(self):
        """Analyze data quality for all available countries"""
        print("🔍 Analyzing data quality in Excel/CSV files...")
        print("=" * 80)
        
        # Analyze each country
        self.analyze_uk_data()
        self.analyze_italy_data()
        self.analyze_netherlands_data()
        self.analyze_france_data()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DATA QUALITY ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"📈 Total rows analyzed: {self.total_rows_analyzed:,}")
        print(f"❌ Rows with errors: {self.total_rows_with_errors:,}")
        print(f"✅ Rows without errors: {self.total_rows_analyzed - self.total_rows_with_errors:,}")
        print(f"📊 Error rate: {self.total_rows_with_errors/self.total_rows_analyzed*100:.2f}%")
        
        if self.error_details:
            print(f"\n🔍 ERROR DETAILS (showing first 20):")
            for i, error in enumerate(self.error_details[:20]):
                print(f"   {i+1}. {error}")
            if len(self.error_details) > 20:
                print(f"   ... and {len(self.error_details) - 20} more errors")
    
    def analyze_uk_data(self):
        """Analyze UK data quality"""
        print("\n🇬🇧 Analyzing UK data quality...")
        
        filepath = self.base_path / "United Kingdom" / "short-positions-daily-update.xlsx"
        if not filepath.exists():
            print("❌ UK file not found")
            return
        
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(filepath)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Found {len(sheet_names)} tabs: {', '.join(sheet_names)}")
            
            for sheet_name in sheet_names:
                print(f"📄 Analyzing tab: {sheet_name}")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    self.analyze_dataframe(df, f"UK {sheet_name}")
                    
                except Exception as e:
                    print(f"❌ Error reading tab {sheet_name}: {e}")
                    self.error_details.append(f"UK {sheet_name} read error: {e}")
        
        except Exception as e:
            print(f"❌ Error analyzing UK data: {e}")
            self.error_details.append(f"UK analysis error: {e}")
    
    def analyze_italy_data(self):
        """Analyze Italy data quality"""
        print("\n🇮🇹 Analyzing Italy data quality...")
        
        filepath = self.base_path / "Italy" / "PncPubbl.xlsx"
        if not filepath.exists():
            print("❌ Italy file not found")
            return
        
        try:
            # Read all sheet names
            excel_file = pd.ExcelFile(filepath)
            sheet_names = excel_file.sheet_names
            
            print(f"📋 Found {len(sheet_names)} tabs: {', '.join(sheet_names)}")
            
            for sheet_name in sheet_names:
                # Skip the publication date tab
                if "Pubb" in sheet_name:
                    print(f"⏭️  Skipping tab: {sheet_name} (publication info)")
                    continue
                
                print(f"📄 Analyzing tab: {sheet_name}")
                
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    print(f"📊 Found {len(df)} rows in tab '{sheet_name}'")
                    
                    self.analyze_dataframe(df, f"Italy {sheet_name}")
                    
                except Exception as e:
                    print(f"❌ Error reading tab {sheet_name}: {e}")
                    self.error_details.append(f"Italy {sheet_name} read error: {e}")
        
        except Exception as e:
            print(f"❌ Error analyzing Italy data: {e}")
            self.error_details.append(f"Italy analysis error: {e}")
    
    def analyze_netherlands_data(self):
        """Analyze Netherlands data quality"""
        print("\n🇳🇱 Analyzing Netherlands data quality...")
        
        current_file = self.base_path / "Netherlands" / "nettoshortpositiesactueel.csv"
        history_file = self.base_path / "Netherlands" / "nettoshortpositieshistorie.csv"
        
        if not current_file.exists() or not history_file.exists():
            print("❌ Netherlands files not found")
            return
        
        try:
            # Analyze current positions
            print(f"📄 Analyzing current positions...")
            df_current = pd.read_csv(current_file, sep=';', encoding='utf-8')
            print(f"📊 Found {len(df_current)} rows in current file")
            self.analyze_dataframe(df_current, "Netherlands Current")
            
            # Analyze historical positions
            print(f"📄 Analyzing historical positions...")
            try:
                # Try different encodings for the history file
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        df_history = pd.read_csv(history_file, sep=';', encoding=encoding)
                        print(f"✅ Successfully read history file with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print("❌ Could not read history file with any encoding")
                    return
                
                print(f"📊 Found {len(df_history)} rows in history file")
                self.analyze_dataframe(df_history, "Netherlands History")
                
            except Exception as e:
                print(f"❌ Error reading history file: {e}")
                self.error_details.append(f"Netherlands history read error: {e}")
        
        except Exception as e:
            print(f"❌ Error analyzing Netherlands data: {e}")
            self.error_details.append(f"Netherlands analysis error: {e}")
    
    def analyze_france_data(self):
        """Analyze France data quality"""
        print("\n🇫🇷 Analyzing France data quality...")
        
        filepath = self.base_path / "France" / "export_od_vad_20250812111500_20250812123000.csv"
        if not filepath.exists():
            print("❌ France file not found")
            return
        
        try:
            df = pd.read_csv(filepath, sep=';', encoding='utf-8')
            print(f"📊 Found {len(df)} rows in France file")
            
            self.analyze_dataframe(df, "France")
            
        except Exception as e:
            print(f"❌ Error analyzing France data: {e}")
            self.error_details.append(f"France analysis error: {e}")
    
    def analyze_dataframe(self, df, source_name):
        """Analyze a dataframe for data quality issues"""
        print(f"🔍 Analyzing {len(df)} rows from {source_name}...")
        
        # Define expected columns for each source
        expected_columns = {
            "UK": ['Position Holder', 'Name of Share Issuer', 'ISIN', 'Net Short Position (%)', 'Position Date'],
            "Italy": ['Detentore', 'Emittente', 'ISIN', 'Perc. posizione netta corta', 'Data della posizione'],
            "Netherlands": ['Position holder', 'Name of the issuer', 'ISIN', 'Net short position', 'Position date'],
            "France": ['Detenteur de la position courte nette', 'Emetteur / issuer', 'code ISIN', 'Ratio', 'Date de debut de publication position']
        }
        
        # Determine which column set to use
        if "UK" in source_name:
            columns = expected_columns["UK"]
        elif "Italy" in source_name:
            columns = expected_columns["Italy"]
        elif "Netherlands" in source_name:
            columns = expected_columns["Netherlands"]
        elif "France" in source_name:
            columns = expected_columns["France"]
        else:
            print(f"⚠️  Unknown source: {source_name}")
            return
        
        # Check if all expected columns exist
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Missing columns in {source_name}: {missing_columns}")
            self.error_details.append(f"{source_name} missing columns: {missing_columns}")
            return
        
        # Analyze each row
        for idx, row in df.iterrows():
            self.total_rows_analyzed += 1
            
            try:
                # Extract data
                manager_name = str(row[columns[0]]).strip()
                company_name = str(row[columns[1]]).strip()
                isin = str(row[columns[2]]).strip()
                position_size = row[columns[3]]
                position_date = row[columns[4]]
                
                # Check for various error conditions
                errors = []
                
                # Check for header rows
                if (manager_name == columns[0] or company_name == columns[1] or 
                    manager_name == 'Position Holder' or company_name == 'Name of Share Issuer' or
                    manager_name == 'Detentore' or company_name == 'Emittente' or
                    manager_name == 'Position holder' or company_name == 'Name of the issuer' or
                    manager_name == 'Detenteur de la position courte nette' or company_name == 'Emetteur / issuer'):
                    errors.append("Header row")
                
                # Check for empty values
                if pd.isna(manager_name) or manager_name == '' or manager_name == 'nan':
                    errors.append("Empty manager name")
                
                if pd.isna(company_name) or company_name == '' or company_name == 'nan':
                    errors.append("Empty company name")
                
                if pd.isna(isin) or isin == '' or isin == 'nan':
                    errors.append("Empty ISIN")
                
                # Check for invalid position size
                if pd.isna(position_size):
                    errors.append("NaN position size")
                else:
                    try:
                        size_float = float(position_size)
                        if size_float < 0:
                            errors.append("Negative position size")
                        if size_float > 100:
                            errors.append("Position size > 100%")
                    except (ValueError, TypeError):
                        errors.append("Invalid position size format")
                
                # Check for invalid date
                if pd.isna(position_date):
                    errors.append("NaN date")
                else:
                    try:
                        pd.to_datetime(position_date)
                    except (ValueError, TypeError):
                        errors.append("Invalid date format")
                
                # If there are errors, record them
                if errors:
                    self.total_rows_with_errors += 1
                    error_msg = f"{source_name} row {idx+1}: {', '.join(errors)}"
                    if len(self.error_details) < 100:  # Limit to first 100 errors
                        self.error_details.append(error_msg)
                
            except Exception as e:
                self.total_rows_with_errors += 1
                error_msg = f"{source_name} row {idx+1}: Processing error - {e}"
                if len(self.error_details) < 100:
                    self.error_details.append(error_msg)
        
        print(f"✅ Analyzed {len(df)} rows from {source_name}")

def main():
    """Main function"""
    print("📊 ShortSelling.eu - Data Quality Analysis Tool")
    print("=" * 80)
    print("🔍 This tool analyzes Excel/CSV files for data quality issues")
    print("🔍 It does NOT import data to the database")
    print("🔍 It shows what would be skipped during import")
    print("=" * 80)
    
    # Create analyzer and run analysis
    analyzer = DataQualityAnalyzer()
    analyzer.analyze_all_countries()
    
    print(f"\n🎉 Data quality analysis completed!")
    print(f"📈 Check the summary above for any important positions that might be skipped")

if __name__ == "__main__":
    main()
