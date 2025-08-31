#!/usr/bin/env python3
"""
Debug UK data dates to find the most recent data
"""

import sys
import os
import pandas as pd
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def download_and_analyze_uk_data():
    """Download UK data and analyze dates carefully"""
    url = "https://www.fca.org.uk/publication/data/short-positions-daily-update.xlsx"
    
    try:
        print(f"📥 Downloading UK data from: {url}")
        
        # Create session with proper headers
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
        temp_file = "temp_uk_data.xlsx"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Read the Excel file
        df = pd.read_excel(temp_file)
        
        print(f"✅ Downloaded successfully!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Clean up temp file
        os.remove(temp_file)
        
        # Analyze the date column carefully
        date_col = 'Position Date'
        if date_col in df.columns:
            print(f"\n📅 Analyzing date column: {date_col}")
            
            # Convert to datetime
            df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Check for any parsing errors
            invalid_dates = df[df['date_parsed'].isna()]
            if len(invalid_dates) > 0:
                print(f"   ⚠️  Found {len(invalid_dates)} rows with invalid dates:")
                print(invalid_dates[date_col].head(10).tolist())
            
            # Get date statistics
            valid_dates = df[df['date_parsed'].notna()]
            print(f"   Valid dates: {len(valid_dates)}")
            print(f"   Date range: {valid_dates['date_parsed'].min()} to {valid_dates['date_parsed'].max()}")
            
            # Show the most recent dates
            print(f"\n📊 Most recent 10 dates:")
            recent_dates = valid_dates.nlargest(10, 'date_parsed')
            for idx, row in recent_dates.iterrows():
                print(f"   {row['date_parsed'].strftime('%Y-%m-%d')} - {row['Position Holder']} - {row['Name of Share Issuer']}")
            
            # Check for 13/08/2025 specifically
            target_date = pd.to_datetime('2025-08-13')
            matches = valid_dates[valid_dates['date_parsed'].dt.date == target_date.date()]
            if len(matches) > 0:
                print(f"\n🎯 Found {len(matches)} positions from 13/08/2025:")
                for idx, row in matches.head(5).iterrows():
                    print(f"   {row['Position Holder']} - {row['Name of Share Issuer']} - {row['Net Short Position (%)']}%")
            else:
                print(f"\n❌ No positions found from 13/08/2025")
            
            # Show unique dates in descending order
            print(f"\n📅 All unique dates (most recent first):")
            unique_dates = valid_dates['date_parsed'].dt.date.unique()
            unique_dates = sorted(unique_dates, reverse=True)
            for date in unique_dates[:10]:  # Show top 10
                count = len(valid_dates[valid_dates['date_parsed'].dt.date == date])
                print(f"   {date} - {count} positions")
        
        return df
        
    except Exception as e:
        print(f"❌ Error downloading UK data: {e}")
        return None

def main():
    """Main function"""
    print("🔍 UK FCA Date Analysis")
    print("=" * 50)
    
    df = download_and_analyze_uk_data()
    if df is None:
        return
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
