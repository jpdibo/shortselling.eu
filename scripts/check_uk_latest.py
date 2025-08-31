#!/usr/bin/env python3
"""
Force download latest UK data and check for 13/08/2025
"""

import sys
import os
import pandas as pd
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def force_download_uk_data():
    """Force download UK data with no caching"""
    url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    try:
        print(f"📥 Force downloading UK data from: {url}")
        
        # Create session with no caching
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # Download the file
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        temp_file = "temp_uk_data_fresh.xlsx"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Read the Excel file
        df = pd.read_excel(temp_file)
        
        print(f"✅ Downloaded successfully!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Clean up temp file
        os.remove(temp_file)
        
        # Check for 13/08/2025 specifically
        date_col = 'Position Date'
        if date_col in df.columns:
            print(f"\n🔍 Looking for 13/08/2025 data...")
            
            # Show raw date values first
            print(f"📅 Raw date values (first 10):")
            for i, date_val in enumerate(df[date_col].head(10)):
                print(f"   {i}: {date_val} (type: {type(date_val)})")
            
            # Try different date parsing approaches
            print(f"\n🔍 Trying different date parsing approaches...")
            
            # Approach 1: Direct pandas parsing
            df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Approach 2: Try with dayfirst=True (European format)
            df['date_parsed_eu'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
            
            # Approach 3: Try with specific format
            df['date_parsed_format'] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')
            
            # Check each approach for 13/08/2025
            target_date = pd.to_datetime('2025-08-13')
            
            # Check approach 1
            matches1 = df[df['date_parsed'] == target_date]
            print(f"   Approach 1 (standard): {len(matches1)} matches for 13/08/2025")
            
            # Check approach 2
            matches2 = df[df['date_parsed_eu'] == target_date]
            print(f"   Approach 2 (dayfirst): {len(matches2)} matches for 13/08/2025")
            
            # Check approach 3
            matches3 = df[df['date_parsed_format'] == target_date]
            print(f"   Approach 3 (format): {len(matches3)} matches for 13/08/2025")
            
            # Show the most recent dates from each approach
            print(f"\n📊 Most recent dates from each approach:")
            
            valid1 = df[df['date_parsed'].notna()]
            if len(valid1) > 0:
                max1 = valid1['date_parsed'].max()
                print(f"   Approach 1 max: {max1}")
            
            valid2 = df[df['date_parsed_eu'].notna()]
            if len(valid2) > 0:
                max2 = valid2['date_parsed_eu'].max()
                print(f"   Approach 2 max: {max2}")
            
            valid3 = df[df['date_parsed_format'].notna()]
            if len(valid3) > 0:
                max3 = valid3['date_parsed_format'].max()
                print(f"   Approach 3 max: {max3}")
            
            # Show all unique dates from the most recent approach
            print(f"\n📅 All unique dates (most recent first):")
            if len(valid1) > 0:
                unique_dates = valid1['date_parsed'].dt.date.unique()
                unique_dates = sorted(unique_dates, reverse=True)
                for date in unique_dates[:10]:
                    count = len(valid1[valid1['date_parsed'].dt.date == date])
                    print(f"   {date} - {count} positions")
        
        return df
        
    except Exception as e:
        print(f"❌ Error downloading UK data: {e}")
        return None

def main():
    """Main function"""
    print("🔄 Force Download UK FCA Data")
    print("=" * 50)
    
    df = force_download_uk_data()
    if df is None:
        return
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
