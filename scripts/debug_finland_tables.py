#!/usr/bin/env python3
"""
Debug Finland Tables - Examine actual table content
"""
import sys
import os
sys.path.append(r'C:\shortselling.eu')

import requests
from bs4 import BeautifulSoup

def debug_finland_tables():
    """Debug the Finland tables to see what's actually in them"""
    print("🔍 Debugging Finland Tables - Detailed Analysis")
    print("=" * 60)
    
    # URLs
    current_url = "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions/Current-net-short-positions/"
    historic_url = "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions/Historic-net-short-positions/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fi;q=0.8',
    }
    
    # Test current positions page
    print(f"\n📄 Current Positions Page:")
    print(f"URL: {current_url}")
    
    try:
        response = requests.get(current_url, headers=headers, timeout=60)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\n📊 Table {i+1}:")
            
            # Get headers
            headers_row = table.find('thead')
            if headers_row:
                headers = [th.get_text(strip=True) for th in headers_row.find_all(['th', 'td'])]
                print(f"  Headers: {headers}")
            else:
                # Try first row as headers
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                    print(f"  Headers (from first row): {headers}")
                else:
                    headers = []
                    print(f"  No headers found")
            
            # Get all rows
            rows = table.find_all('tr')
            print(f"  Total rows: {len(rows)}")
            
            # Show first few rows
            for j, row in enumerate(rows[:5]):  # Show first 5 rows
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"  Row {j+1}: {cell_texts}")
                
                # Look for links in this row
                links = row.find_all('a', href=True)
                if links:
                    print(f"    Links found:")
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        print(f"      - {text} -> {href}")
            
            # Look for any links in the entire table
            all_links = table.find_all('a', href=True)
            if all_links:
                print(f"  All links in table:")
                for link in all_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    print(f"    - {text} -> {href}")
                    
                    # Check if this looks like a data file link
                    if any(keyword in href.lower() for keyword in ['.csv', '.xlsx', '.xls', 'download', 'export', 'data']):
                        print(f"      ⭐ POTENTIAL DATA FILE!")
            
    except Exception as e:
        print(f"❌ Error accessing current page: {e}")
    
    # Test historic positions page
    print(f"\n📄 Historic Positions Page:")
    print(f"URL: {historic_url}")
    
    try:
        response = requests.get(historic_url, headers=headers, timeout=60)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\n📊 Table {i+1}:")
            
            # Get headers
            headers_row = table.find('thead')
            if headers_row:
                headers = [th.get_text(strip=True) for th in headers_row.find_all(['th', 'td'])]
                print(f"  Headers: {headers}")
            else:
                # Try first row as headers
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                    print(f"  Headers (from first row): {headers}")
                else:
                    headers = []
                    print(f"  No headers found")
            
            # Get all rows
            rows = table.find_all('tr')
            print(f"  Total rows: {len(rows)}")
            
            # Show first few rows
            for j, row in enumerate(rows[:5]):  # Show first 5 rows
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"  Row {j+1}: {cell_texts}")
                
                # Look for links in this row
                links = row.find_all('a', href=True)
                if links:
                    print(f"    Links found:")
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        print(f"      - {text} -> {href}")
            
            # Look for any links in the entire table
            all_links = table.find_all('a', href=True)
            if all_links:
                print(f"  All links in table:")
                for link in all_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    print(f"    - {text} -> {href}")
                    
                    # Check if this looks like a data file link
                    if any(keyword in href.lower() for keyword in ['.csv', '.xlsx', '.xls', 'download', 'export', 'data']):
                        print(f"      ⭐ POTENTIAL DATA FILE!")
            
    except Exception as e:
        print(f"❌ Error accessing historic page: {e}")

if __name__ == "__main__":
    debug_finland_tables()

