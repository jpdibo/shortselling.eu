#!/usr/bin/env python3
"""
Debug Germany Historical Data
Debug script to understand how the historical data form submission works
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def debug_historical_workflow():
    """Debug the historical data workflow step by step"""
    print("🔍 Debugging Germany Historical Data Workflow")
    print("=" * 60)
    
    # Main URL
    main_url = "https://www.bundesanzeiger.de/pub/en/nlp?4"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
    }
    
    try:
        # Step 1: Get the main page
        print("📄 Step 1: Getting main page...")
        response = requests.get(main_url, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Failed to get main page")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Step 2: Find the filter form
        print("\n🔍 Step 2: Finding filter form...")
        forms = soup.find_all('form')
        print(f"   Found {len(forms)} forms")
        
        filter_form = None
        for i, form in enumerate(forms):
            action = form.get('action', '')
            method = form.get('method', 'GET')
            print(f"   Form {i+1}: Method={method}, Action={action}")
            
            if 'filter' in action.lower():
                filter_form = form
                print(f"   ✅ Found filter form: {action}")
                break
        
        if not filter_form:
            print("❌ Could not find filter form")
            return
        
        # Step 3: Analyze the form inputs
        print("\n📋 Step 3: Analyzing form inputs...")
        inputs = filter_form.find_all('input')
        print(f"   Found {len(inputs)} inputs")
        
        form_data = {}
        for i, input_tag in enumerate(inputs):
            input_type = input_tag.get('type', 'text')
            input_name = input_tag.get('name', '')
            input_value = input_tag.get('value', '')
            input_checked = input_tag.get('checked')
            
            print(f"   Input {i+1}: Type={input_type}, Name='{input_name}', Value='{input_value}', Checked={input_checked}")
            
            if input_name:
                if input_type == 'checkbox':
                    if 'historic' in input_name.lower() or 'history' in input_name.lower():
                        form_data[input_name] = 'on'
                        print(f"     ✅ Added historical checkbox: {input_name}")
                    elif input_checked:
                        form_data[input_name] = 'on'
                else:
                    form_data[input_name] = input_value
        
        # Step 4: Look for the specific isHistorical checkbox
        print("\n🔍 Step 4: Looking for isHistorical checkbox...")
        historical_checkbox = soup.find('input', attrs={'name': 'isHistorical'})
        if historical_checkbox:
            print(f"   ✅ Found isHistorical checkbox")
            print(f"   Value: {historical_checkbox.get('value', '')}")
            print(f"   Checked: {historical_checkbox.get('checked')}")
            form_data['isHistorical'] = 'on'
        else:
            print("   ❌ isHistorical checkbox not found")
        
        # Step 5: Submit the form
        print(f"\n📤 Step 5: Submitting form...")
        form_action = filter_form.get('action', '')
        if not form_action.startswith('http'):
            form_action = urljoin(main_url, form_action)
        
        print(f"   Form action: {form_action}")
        print(f"   Form data: {form_data}")
        
        submit_headers = headers.copy()
        submit_headers.update({
            'Referer': main_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        
        historical_response = requests.post(form_action, data=form_data, headers=submit_headers, timeout=30)
        print(f"   Response status: {historical_response.status_code}")
        
        if historical_response.status_code == 200:
            print("   ✅ Form submitted successfully")
            
            # Step 6: Analyze the response
            print("\n📄 Step 6: Analyzing response...")
            historical_soup = BeautifulSoup(historical_response.content, 'html.parser')
            
            # Look for CSV download links in the response
            csv_links = historical_soup.find_all('a', href=True, string=re.compile(r'Download as CSV', re.I))
            print(f"   Found {len(csv_links)} CSV download links")
            
            for i, link in enumerate(csv_links):
                href = link.get('href')
                text = link.get_text(strip=True)
                print(f"   CSV Link {i+1}: '{text}' -> {href}")
            
            # Look for any links containing 'csv'
            csv_links_all = historical_soup.find_all('a', href=True)
            csv_links_filtered = [link for link in csv_links_all if 'csv' in link.get('href', '').lower()]
            print(f"   Found {len(csv_links_filtered)} total links containing 'csv'")
            
            # Step 7: Try to download the CSV
            if csv_links_filtered:
                csv_url = csv_links_filtered[0].get('href')
                if not csv_url.startswith('http'):
                    csv_url = urljoin(form_action, csv_url)
                
                print(f"\n📥 Step 7: Downloading CSV from: {csv_url}")
                
                csv_response = requests.get(csv_url, headers=headers, timeout=30)
                print(f"   CSV response status: {csv_response.status_code}")
                
                if csv_response.status_code == 200:
                    print(f"   ✅ CSV downloaded successfully")
                    print(f"   Content length: {len(csv_response.content):,} bytes")
                    
                    # Try to parse as CSV
                    try:
                        import pandas as pd
                        from io import StringIO
                        
                        # Clean column names
                        df = pd.read_csv(StringIO(csv_response.text))
                        df.columns = df.columns.str.replace('ï»¿', '').str.replace('"', '').str.strip()
                        
                        print(f"   ✅ Parsed CSV: {len(df)} rows, {len(df.columns)} columns")
                        print(f"   Columns: {list(df.columns)}")
                        
                        if len(df) > 0:
                            print(f"   Sample data:")
                            print(df.head(3).to_string())
                            
                            # Check if this looks like historical data
                            if 'Datum' in df.columns:
                                dates = pd.to_datetime(df['Datum'])
                                print(f"   Date range: {dates.min()} to {dates.max()}")
                                
                                # Count unique dates
                                unique_dates = dates.dt.date.value_counts()
                                print(f"   Number of unique dates: {len(unique_dates)}")
                                print(f"   Date distribution (top 5):")
                                for date, count in unique_dates.head().items():
                                    print(f"     {date}: {count} positions")
                        
                    except Exception as e:
                        print(f"   ❌ Failed to parse CSV: {e}")
                else:
                    print(f"   ❌ Failed to download CSV")
            else:
                print("   ❌ No CSV links found in response")
        else:
            print(f"   ❌ Form submission failed")
            
    except Exception as e:
        print(f"❌ Error in debug workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_historical_workflow()
