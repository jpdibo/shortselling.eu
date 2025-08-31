#!/usr/bin/env python3
"""
Advanced CONSOB Download Attempts
Tries multiple sophisticated approaches to bypass bot protection
"""
import requests
import time
import random
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import cloudscraper

def try_cloudscraper():
    """Try using cloudscraper to bypass protection"""
    print("🌩️  Trying CloudScraper approach...")
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Set realistic headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        url = "https://www.consob.it/web/consob-and-its-activities/short-selling"
        
        # First, get the main page
        response = scraper.get(url, headers=headers, timeout=30)
        print(f"✅ CloudScraper got page: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for any download links or forms
            download_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                if 'download' in text or 'file' in text or 'scarica' in text:
                    download_links.append({
                        'text': link.get_text(strip=True),
                        'href': href
                    })
            
            print(f"📥 Found {len(download_links)} download links")
            for link in download_links:
                print(f"   - {link['text']} -> {link['href']}")
            
            # Try to find JavaScript functions
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'downloadShortselling' in script.string:
                    print("🔍 Found downloadShortselling function!")
                    # Extract the function content
                    lines = script.string.split('\n')
                    for i, line in enumerate(lines):
                        if 'downloadShortselling' in line:
                            print(f"   Line {i+1}: {line.strip()}")
                            # Look for URLs in the function
                            urls = re.findall(r'https?://[^\s"\']+\.(?:xlsx?|csv)', line)
                            if urls:
                                print(f"   Found URLs: {urls}")
                                return try_download_url(scraper, urls[0], headers)
            
            # Try common CONSOB patterns with cloudscraper
            common_urls = [
                "https://www.consob.it/documents/46180/46181/posizioni_corte_nette.xlsx",
                "https://www.consob.it/web/site-pubbl/pnc/posizioni_corte_nette.xlsx",
                "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_attuali.xlsx",
                "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_storiche.xlsx"
            ]
            
            for url in common_urls:
                print(f"🔍 Trying: {url}")
                try:
                    file_response = scraper.get(url, headers=headers, timeout=15)
                    if file_response.status_code == 200 and b'PK' in file_response.content[:100]:
                        print(f"✅ Successfully downloaded from: {url}")
                        return file_response.content
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
                    continue
        
        return None
        
    except Exception as e:
        print(f"❌ CloudScraper failed: {e}")
        return None

def try_session_approach():
    """Try maintaining a session with cookies"""
    print("🍪 Trying session-based approach...")
    
    try:
        session = requests.Session()
        
        # Set realistic headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session.headers.update(headers)
        
        # First visit the main site to get cookies
        main_url = "https://www.consob.it"
        print(f"🏠 Visiting main site: {main_url}")
        response = session.get(main_url, timeout=15)
        print(f"   Status: {response.status_code}")
        
        # Wait a bit
        time.sleep(random.uniform(2, 4))
        
        # Now visit the short-selling page
        short_selling_url = "https://www.consob.it/web/consob-and-its-activities/short-selling"
        print(f"📄 Visiting short-selling page: {short_selling_url}")
        response = session.get(short_selling_url, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for any forms that might trigger downloads
            forms = soup.find_all('form')
            print(f"📋 Found {len(forms)} forms")
            
            for form in forms:
                action = form.get('action', '')
                method = form.get('method', 'get').upper()
                print(f"   Form: {method} {action}")
                
                # If there's a form, try submitting it
                if action and method == 'POST':
                    try:
                        # Get form data
                        form_data = {}
                        for input_tag in form.find_all('input'):
                            name = input_tag.get('name')
                            value = input_tag.get('value', '')
                            if name:
                                form_data[name] = value
                        
                        print(f"   Submitting form with data: {form_data}")
                        form_response = session.post(urljoin(short_selling_url, action), data=form_data, timeout=15)
                        print(f"   Form response: {form_response.status_code}")
                        
                        if form_response.status_code == 200 and b'PK' in form_response.content[:100]:
                            print("✅ Got Excel file from form submission!")
                            return form_response.content
                            
                    except Exception as e:
                        print(f"   ❌ Form submission failed: {e}")
                        continue
        
        return None
        
    except Exception as e:
        print(f"❌ Session approach failed: {e}")
        return None

def try_api_endpoints():
    """Try various API endpoints that might exist"""
    print("🔌 Trying API endpoints...")
    
    api_endpoints = [
        "https://www.consob.it/api/short-positions",
        "https://www.consob.it/api/posizioni-corte",
        "https://www.consob.it/web/api/short-positions",
        "https://www.consob.it/web/api/posizioni-corte",
        "https://www.consob.it/api/download/short-positions",
        "https://www.consob.it/api/download/posizioni-corte",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'Content-Type': 'application/json'
    }
    
    for endpoint in api_endpoints:
        try:
            print(f"🔍 Trying API: {endpoint}")
            
            # Try GET request
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   GET: {response.status_code}")
            
            if response.status_code == 200:
                if b'PK' in response.content[:100]:
                    print(f"✅ Got Excel file from API: {endpoint}")
                    return response.content
                elif response.headers.get('content-type', '').startswith('application/json'):
                    print(f"   Got JSON response, checking for download URLs...")
                    try:
                        data = response.json()
                        # Look for download URLs in JSON
                        json_str = json.dumps(data)
                        urls = re.findall(r'https?://[^\s"\']+\.(?:xlsx?|csv)', json_str)
                        if urls:
                            print(f"   Found URLs in JSON: {urls}")
                            return try_download_url(requests, urls[0], headers)
                    except:
                        pass
            
            # Try POST request
            response = requests.post(endpoint, headers=headers, json={}, timeout=10)
            print(f"   POST: {response.status_code}")
            
            if response.status_code == 200 and b'PK' in response.content[:100]:
                print(f"✅ Got Excel file from POST to API: {endpoint}")
                return response.content
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    return None

def try_download_url(session, url, headers):
    """Try to download from a specific URL"""
    try:
        print(f"📥 Attempting download from: {url}")
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            if b'PK' in response.content[:100]:
                print(f"✅ Successfully downloaded Excel file!")
                return response.content
            else:
                print(f"   ⚠️  Got response but not Excel file")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
    
    return None

def try_alternative_domains():
    """Try alternative CONSOB domains or subdomains"""
    print("🌐 Trying alternative domains...")
    
    alternative_urls = [
        "https://consob.it/web/consob-and-its-activities/short-selling",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette.xlsx",
        "https://consob.it/documents/46180/46181/posizioni_corte_nette.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/posizioni_corte_nette.xlsx",
        "https://consob.it/web/site-pubbl/pnc/posizioni_corte_nette.xlsx",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
    }
    
    for url in alternative_urls:
        try:
            print(f"🔍 Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                if b'PK' in response.content[:100]:
                    print(f"✅ Successfully downloaded from: {url}")
                    return response.content
                elif 'captcha' not in response.text.lower():
                    print(f"   ⚠️  Got page but not captcha, might be accessible")
                    # Parse the page for download links
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        if href.endswith(('.xlsx', '.xls', '.csv')):
                            full_url = urljoin(url, href)
                            print(f"   Found file link: {full_url}")
                            file_response = requests.get(full_url, headers=headers, timeout=10)
                            if file_response.status_code == 200 and b'PK' in file_response.content[:100]:
                                print(f"✅ Downloaded file from link: {full_url}")
                                return file_response.content
                                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    return None

def main():
    """Main function - try all approaches"""
    print("🚀 Advanced CONSOB Download Attempts")
    print("=" * 50)
    print("Trying multiple sophisticated approaches to bypass bot protection...")
    print("=" * 50)
    
    approaches = [
        ("CloudScraper", try_cloudscraper),
        ("Session-based", try_session_approach),
        ("API Endpoints", try_api_endpoints),
        ("Alternative Domains", try_alternative_domains),
    ]
    
    for name, approach in approaches:
        print(f"\n🔄 Trying {name} approach...")
        print("-" * 30)
        
        try:
            result = approach()
            if result:
                print(f"\n🎉 SUCCESS with {name} approach!")
                print(f"📊 Downloaded {len(result):,} bytes")
                
                # Save the file
                filename = f"consob_data_{int(time.time())}.xlsx"
                with open(filename, 'wb') as f:
                    f.write(result)
                print(f"💾 Saved as: {filename}")
                return filename
                
        except Exception as e:
            print(f"❌ {name} approach failed: {e}")
            continue
        
        # Wait between approaches
        time.sleep(random.uniform(1, 3))
    
    print(f"\n❌ All approaches failed!")
    print("CONSOB has very strong bot protection.")
    print("Next steps could include:")
    print("1. Browser automation with Selenium")
    print("2. Proxy rotation")
    print("3. Captcha solving services")
    print("4. Contacting CONSOB for API access")
    
    return None

if __name__ == "__main__":
    main()
