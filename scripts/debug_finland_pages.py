#!/usr/bin/env python3
"""
Debug Finland Pages
"""
import sys
import os
sys.path.append(r'C:\shortselling.eu')

import requests
from bs4 import BeautifulSoup

def debug_finland_pages():
    """Debug the Finland pages to see what data is available"""
    print("🔍 Debugging Finland Pages")
    print("=" * 50)
    
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
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check page title
        title = soup.find('title')
        print(f"Page title: {title.get_text() if title else 'No title'}")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Look for any data containers
        data_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['data', 'table', 'position', 'short']))
        print(f"Found {len(data_containers)} potential data containers")
        
        # Look for links to data files
        links = soup.find_all('a', href=True)
        data_links = [link for link in links if any(keyword in link.get('href', '').lower() for keyword in ['.csv', '.xlsx', '.xls', 'download', 'export'])]
        print(f"Found {len(data_links)} potential data links:")
        for link in data_links[:5]:  # Show first 5
            print(f"  - {link.get('href')} (text: {link.get_text(strip=True)})")
        
        # Look for any text mentioning short positions
        text_content = soup.get_text()
        if 'short position' in text_content.lower():
            print("✅ Found 'short position' text in page")
        else:
            print("❌ No 'short position' text found")
        
        # Check if page has any meaningful content
        if len(text_content) > 1000:
            print(f"✅ Page has substantial content ({len(text_content)} characters)")
        else:
            print(f"❌ Page has minimal content ({len(text_content)} characters)")
            
    except Exception as e:
        print(f"❌ Error accessing current page: {e}")
    
    # Test historic positions page
    print(f"\n📄 Historic Positions Page:")
    print(f"URL: {historic_url}")
    
    try:
        response = requests.get(historic_url, headers=headers, timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check page title
        title = soup.find('title')
        print(f"Page title: {title.get_text() if title else 'No title'}")
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Look for any data containers
        data_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['data', 'table', 'position', 'short']))
        print(f"Found {len(data_containers)} potential data containers")
        
        # Look for links to data files
        links = soup.find_all('a', href=True)
        data_links = [link for link in links if any(keyword in link.get('href', '').lower() for keyword in ['.csv', '.xlsx', '.xls', 'download', 'export'])]
        print(f"Found {len(data_links)} potential data links:")
        for link in data_links[:5]:  # Show first 5
            print(f"  - {link.get('href')} (text: {link.get_text(strip=True)})")
        
        # Look for any text mentioning short positions
        text_content = soup.get_text()
        if 'short position' in text_content.lower():
            print("✅ Found 'short position' text in page")
        else:
            print("❌ No 'short position' text found")
        
        # Check if page has any meaningful content
        if len(text_content) > 1000:
            print(f"✅ Page has substantial content ({len(text_content)} characters)")
        else:
            print(f"❌ Page has minimal content ({len(text_content)} characters)")
            
    except Exception as e:
        print(f"❌ Error accessing historic page: {e}")

if __name__ == "__main__":
    debug_finland_pages()

