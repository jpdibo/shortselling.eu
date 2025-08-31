#!/usr/bin/env python3
"""
Check UK Excel file structure and look for multiple sheets
"""

import sys
import os
import pandas as pd
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_uk_excel_structure():
    """Check the structure of the UK Excel file"""
    url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    try:
        print(f"📥 Downloading UK data from: {url}")
        
        # Create session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Download the file
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        temp_file = "temp_uk_data_structure.xlsx"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Check Excel file structure
        print(f"\n🔍 Checking Excel file structure...")
        
        # Get all sheet names
        excel_file = pd.ExcelFile(temp_file)
        print(f"   Sheet names: {excel_file.sheet_names}")
        
        # Check each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n📊 Sheet: {sheet_name}")
            
            # Read the sheet
            df = pd.read_excel(temp_file, sheet_name=sheet_name)
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {list(df.columns)}")
            
            # Check for date column
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                print(f"   Date column: {date_col}")
                
                # Convert to datetime
                df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
                valid_dates = df[df['date_parsed'].notna()]
                
                if len(valid_dates) > 0:
                    print(f"   Date range: {valid_dates['date_parsed'].min()} to {valid_dates['date_parsed'].max()}")
                    
                    # Check for 13/08/2025
                    target_date = pd.to_datetime('2025-08-13')
                    matches = valid_dates[valid_dates['date_parsed'] == target_date]
                    if len(matches) > 0:
                        print(f"   🎯 Found {len(matches)} positions from 13/08/2025!")
                        for idx, row in matches.head(3).iterrows():
                            print(f"      {row.get('Position Holder', 'N/A')} - {row.get('Name of Share Issuer', 'N/A')}")
                    else:
                        print(f"   ❌ No positions from 13/08/2025")
                    
                    # Show most recent dates
                    print(f"   Most recent 5 dates:")
                    recent_dates = valid_dates.nlargest(5, 'date_parsed')
                    for idx, row in recent_dates.iterrows():
                        print(f"      {row['date_parsed'].strftime('%Y-%m-%d')} - {row.get('Position Holder', 'N/A')}")
        
        # Clean up temp file
        os.remove(temp_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_alternative_urls():
    """Check if there are alternative URLs for UK data"""
    print(f"\n🔍 Checking for alternative UK data URLs...")
    
    # List of potential alternative URLs
    alternative_urls = [
        "https://www.fca.org.uk/publication/data/short-positions-daily-update-latest.xlsx",
        "https://www.fca.org.uk/publication/data/short-positions.xlsx",
        "https://www.fca.org.uk/publication/data/short-positions-current.xlsx",
        "https://www.fca.org.uk/publication/data/short-positions-recent.xlsx",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    
    for url in alternative_urls:
        try:
            print(f"   Checking: {url}")
            response = session.head(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Found working URL: {url}")
                return url
            else:
                print(f"   ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def main():
    """Main function"""
    print("🔍 UK Excel Structure Analysis")
    print("=" * 50)
    
    # Check Excel structure
    success = check_uk_excel_structure()
    
    if success:
        # Check alternative URLs
        alternative_url = check_alternative_urls()
        if alternative_url:
            print(f"\n🎯 Found alternative URL: {alternative_url}")
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
