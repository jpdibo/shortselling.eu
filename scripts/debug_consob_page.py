#!/usr/bin/env python3
"""
Debug CONSOB Page
Examines the CONSOB short-selling page to understand the download mechanism
"""
import requests
from bs4 import BeautifulSoup
import re

def debug_consob_page():
    """Debug the CONSOB page structure"""
    print("🔍 Debugging CONSOB Page Structure")
    print("=" * 50)
    
    url = "https://www.consob.it/web/consob-and-its-activities/short-selling"
    
    try:
        print(f"📥 Fetching page: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Page fetched successfully (Status: {response.status_code})")
        print(f"📄 Content length: {len(response.content):,} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n🔍 Looking for download links...")
        
        # Find all links
        links = soup.find_all('a', href=True)
        print(f"📊 Found {len(links)} links on the page")
        
        # Look for JavaScript links
        js_links = []
        for link in links:
            href = link.get('href', '')
            if 'javascript:' in href:
                js_links.append({
                    'text': link.get_text(strip=True),
                    'href': href
                })
        
        print(f"\n🔗 JavaScript links found ({len(js_links)}):")
        for link in js_links:
            print(f"   - Text: '{link['text']}' -> {link['href']}")
        
        # Look for any download-related links
        download_links = []
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            if 'download' in text or 'file' in text or 'xlsx' in href or 'xls' in href or 'csv' in href:
                download_links.append({
                    'text': link.get_text(strip=True),
                    'href': href
                })
        
        print(f"\n📥 Download-related links found ({len(download_links)}):")
        for link in download_links:
            print(f"   - Text: '{link['text']}' -> {link['href']}")
        
        # Look for script tags that might contain download URLs
        print(f"\n📜 Examining script tags...")
        scripts = soup.find_all('script')
        print(f"📊 Found {len(scripts)} script tags")
        
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string
                
                # Look for URLs in JavaScript
                urls = re.findall(r'https?://[^\s"\']+\.(?:xlsx?|csv)', script_content)
                if urls:
                    print(f"   Script {i+1}: Found URLs: {urls}")
                
                # Look for downloadShortselling function
                if 'downloadShortselling' in script_content:
                    print(f"   Script {i+1}: Contains downloadShortselling function")
                    # Extract the function content
                    lines = script_content.split('\n')
                    for j, line in enumerate(lines):
                        if 'downloadShortselling' in line:
                            print(f"      Line {j+1}: {line.strip()}")
                            # Look at a few lines around it
                            for k in range(max(0, j-2), min(len(lines), j+3)):
                                if k != j:
                                    print(f"      Line {k+1}: {lines[k].strip()}")
        
        # Look for any form or data attributes
        print(f"\n📋 Looking for forms and data attributes...")
        forms = soup.find_all('form')
        print(f"📊 Found {len(forms)} forms")
        
        for i, form in enumerate(forms):
            print(f"   Form {i+1}: action='{form.get('action', 'None')}' method='{form.get('method', 'None')}'")
        
        # Look for elements with data attributes
        data_elements = soup.find_all(attrs={'data-url': True})
        print(f"📊 Found {len(data_elements)} elements with data-url attribute")
        for elem in data_elements:
            print(f"   - {elem.name}: data-url='{elem.get('data-url')}'")
        
        # Look for any iframe that might contain the download
        iframes = soup.find_all('iframe')
        print(f"📊 Found {len(iframes)} iframes")
        for iframe in iframes:
            print(f"   - src='{iframe.get('src', 'None')}'")
        
        print(f"\n🔍 Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for any text containing "download" or "file"
        text_content = soup.get_text()
        download_mentions = re.findall(r'[^.]*(?:download|file|scarica)[^.]*\.', text_content, re.IGNORECASE)
        print(f"\n📝 Text mentions of download/file ({len(download_mentions)}):")
        for mention in download_mentions[:10]:  # Show first 10
            print(f"   - {mention.strip()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_consob_page()
