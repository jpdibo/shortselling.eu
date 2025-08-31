#!/usr/bin/env python3
"""
Analyze Bundesanzeiger Website Structure
Analyzes the structure of the Bundesanzeiger short-selling website to understand
how to access current and historical data
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, parse_qs
import time

def analyze_bundesanzeiger_structure():
    """Analyze the structure of the Bundesanzeiger website"""
    print("🔍 Analyzing Bundesanzeiger Website Structure")
    print("=" * 60)
    
    # Main URL
    main_url = "https://www.bundesanzeiger.de/pub/en/nlp?4"
    print(f"📍 Main URL: {main_url}")
    
    try:
        # Get the main page
        print("\n📄 Accessing main page...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
        }
        
        response = requests.get(main_url, headers=headers, timeout=30)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to access main page: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Analyze page structure
        print(f"\n📋 Page Title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for CSV download links
        print("\n🔗 Looking for CSV download links...")
        csv_links = soup.find_all('a', href=True, string=re.compile(r'Download as CSV', re.I))
        print(f"   Found {len(csv_links)} 'Download as CSV' links")
        
        for i, link in enumerate(csv_links):
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"   {i+1}. Text: '{text}' -> {href}")
        
        # Look for any links containing 'csv'
        csv_links_all = soup.find_all('a', href=True)
        csv_links_filtered = [link for link in csv_links_all if 'csv' in link.get('href', '').lower()]
        print(f"\n   Found {len(csv_links_filtered)} links containing 'csv' in href")
        
        for i, link in enumerate(csv_links_filtered[:5]):  # Show first 5
            href = link.get('href')
            text = link.get_text(strip=True)
            print(f"   {i+1}. Text: '{text}' -> {href}")
        
        # Look for "More search options" section
        print("\n🔍 Looking for 'More search options' section...")
        search_options_sections = soup.find_all('div', class_=re.compile(r'search|option|filter', re.I))
        print(f"   Found {len(search_options_sections)} potential search option sections")
        
        # Look for "Also find historicised data" checkbox
        print("\n📋 Looking for historical data checkbox...")
        historical_checkboxes = soup.find_all('input', attrs={'name': re.compile(r'historic|history', re.I)})
        print(f"   Found {len(historical_checkboxes)} historical data checkboxes")
        
        for i, checkbox in enumerate(historical_checkboxes):
            name = checkbox.get('name')
            value = checkbox.get('value')
            checked = checkbox.get('checked')
            print(f"   {i+1}. Name: '{name}', Value: '{value}', Checked: {checked}")
        
        # Look for all checkboxes
        all_checkboxes = soup.find_all('input', type='checkbox')
        print(f"\n   Found {len(all_checkboxes)} total checkboxes")
        
        for i, checkbox in enumerate(all_checkboxes[:10]):  # Show first 10
            name = checkbox.get('name')
            value = checkbox.get('value')
            checked = checkbox.get('checked')
            print(f"   {i+1}. Name: '{name}', Value: '{value}', Checked: {checked}")
        
        # Look for forms
        print("\n📝 Looking for forms...")
        forms = soup.find_all('form')
        print(f"   Found {len(forms)} forms")
        
        for i, form in enumerate(forms):
            action = form.get('action', '')
            method = form.get('method', 'GET')
            print(f"   {i+1}. Method: {method}, Action: {action}")
            
            # Look for form inputs
            inputs = form.find_all('input')
            print(f"      Inputs: {len(inputs)}")
            
            for j, input_tag in enumerate(inputs[:5]):  # Show first 5
                input_type = input_tag.get('type', 'text')
                input_name = input_tag.get('name', '')
                input_value = input_tag.get('value', '')
                print(f"        {j+1}. Type: {input_type}, Name: '{input_name}', Value: '{input_value}'")
        
        # Test the known CSV URL
        print("\n🧪 Testing known CSV URL...")
        known_csv_url = "https://www.bundesanzeiger.de/pub/en/nlp?0--top~csv~form~panel-form-csv~resource~link"
        
        try:
            csv_response = requests.get(known_csv_url, headers=headers, timeout=15)
            print(f"   Status: {csv_response.status_code}")
            
            if csv_response.status_code == 200:
                print(f"   ✅ Successfully accessed CSV URL")
                print(f"   Content length: {len(csv_response.content):,} bytes")
                print(f"   Content type: {csv_response.headers.get('content-type', 'Unknown')}")
                
                # Check if it's CSV content
                if 'csv' in csv_response.headers.get('content-type', '').lower():
                    print("   ✅ Confirmed CSV content")
                elif b'Position owner' in csv_response.content[:1000]:
                    print("   ✅ Contains expected data (Position owner)")
                else:
                    print("   ⚠️  Content doesn't look like CSV")
                    
                    # Try to parse as HTML
                    csv_soup = BeautifulSoup(csv_response.content, 'html.parser')
                    tables = csv_soup.find_all('table')
                    print(f"   Found {len(tables)} tables in response")
                    
                    if tables:
                        print("   ✅ Found HTML table - can be parsed")
            else:
                print(f"   ❌ Failed to access CSV URL")
                
        except Exception as e:
            print(f"   ❌ Error testing CSV URL: {e}")
        
        # Look for pagination and results
        print("\n📊 Looking for results and pagination...")
        pagination = soup.find_all('a', href=True, string=re.compile(r'\d+', re.I))
        print(f"   Found {len(pagination)} potential pagination links")
        
        # Look for result counts
        result_texts = soup.find_all(string=re.compile(r'\d+ matches?', re.I))
        print(f"   Found {len(result_texts)} result count texts")
        for text in result_texts:
            print(f"   - {text.strip()}")
        
        # Look for data tables
        tables = soup.find_all('table')
        print(f"\n📋 Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            cols = table.find_all('th') or table.find_all('td')
            print(f"   Table {i+1}: {len(rows)} rows, {len(cols)} columns")
            
            # Show first few rows
            for j, row in enumerate(rows[:3]):
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"     Row {j+1}: {cell_texts}")
        
        print("\n✅ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Error analyzing website: {e}")
        import traceback
        traceback.print_exc()

def test_csv_download():
    """Test the CSV download functionality"""
    print("\n🧪 Testing CSV Download")
    print("=" * 40)
    
    csv_url = "https://www.bundesanzeiger.de/pub/en/nlp?0--top~csv~form~panel-form-csv~resource~link"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/csv,text/plain,*/*',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
        'Referer': 'https://www.bundesanzeiger.de/pub/en/nlp?4',
    }
    
    try:
        response = requests.get(csv_url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Content length: {len(response.content):,} bytes")
            
            # Try to parse as CSV
            try:
                import pandas as pd
                df = pd.read_csv(pd.StringIO(response.text))
                print(f"✅ Successfully parsed as CSV: {len(df)} rows, {len(df.columns)} columns")
                print(f"Columns: {list(df.columns)}")
                
                if len(df) > 0:
                    print(f"Sample data:")
                    print(df.head(3).to_string())
                    
            except Exception as e:
                print(f"❌ Failed to parse as CSV: {e}")
                
                # Try to parse as HTML table
                try:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    tables = soup.find_all('table')
                    
                    if tables:
                        df = pd.read_html(str(tables[0]))[0]
                        print(f"✅ Successfully parsed as HTML table: {len(df)} rows, {len(df.columns)} columns")
                        print(f"Columns: {list(df.columns)}")
                        
                        if len(df) > 0:
                            print(f"Sample data:")
                            print(df.head(3).to_string())
                    else:
                        print("❌ No tables found in HTML")
                        
                except Exception as e2:
                    print(f"❌ Failed to parse as HTML table: {e2}")
        else:
            print(f"❌ Failed to download CSV")
            
    except Exception as e:
        print(f"❌ Error testing CSV download: {e}")

def main():
    """Main function"""
    analyze_bundesanzeiger_structure()
    test_csv_download()

if __name__ == "__main__":
    main()
