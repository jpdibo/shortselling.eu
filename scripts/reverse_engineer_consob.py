#!/usr/bin/env python3
"""
Reverse Engineer CONSOB JavaScript
Tries to extract the actual download URL from the JavaScript function
"""
import requests
import re
import json
from bs4 import BeautifulSoup
import time

def extract_javascript_function():
    """Extract and analyze the downloadShortselling JavaScript function"""
    print("🔍 Reverse Engineering CONSOB JavaScript...")
    
    url = "https://www.consob.it/web/consob-and-its-activities/short-selling"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script')
        
        for i, script in enumerate(scripts):
            if script.string and 'downloadShortselling' in script.string:
                print(f"📜 Found downloadShortselling function in script {i+1}")
                
                # Extract the function content
                function_content = script.string
                
                # Look for URLs in the function
                urls = re.findall(r'https?://[^\s"\']+\.(?:xlsx?|csv)', function_content)
                if urls:
                    print(f"🔗 Found URLs in function: {urls}")
                    return urls
                
                # Look for relative paths that might be download URLs
                relative_paths = re.findall(r'["\']([^"\']*\.(?:xlsx?|csv))["\']', function_content)
                if relative_paths:
                    print(f"📁 Found relative paths: {relative_paths}")
                    full_urls = [f"https://www.consob.it{path}" for path in relative_paths]
                    return full_urls
                
                # Look for any patterns that might indicate download URLs
                patterns = [
                    r'["\']([^"\']*download[^"\']*\.(?:xlsx?|csv))["\']',
                    r'["\']([^"\']*posizioni[^"\']*\.(?:xlsx?|csv))["\']',
                    r'["\']([^"\']*short[^"\']*\.(?:xlsx?|csv))["\']',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, function_content, re.IGNORECASE)
                    if matches:
                        print(f"🎯 Found pattern matches: {matches}")
                        return matches
                
                # Print the function content for manual analysis
                print("📋 Function content:")
                lines = function_content.split('\n')
                for j, line in enumerate(lines):
                    if 'downloadShortselling' in line or 'http' in line or '.xlsx' in line or '.csv' in line:
                        print(f"   Line {j+1}: {line.strip()}")
                
                # Look for any AJAX calls or fetch requests
                ajax_patterns = [
                    r'\.ajax\([^)]*url["\']([^"\']+)["\']',
                    r'fetch\(["\']([^"\']+)["\']',
                    r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
                    r'window\.open\(["\']([^"\']+)["\']',
                ]
                
                for pattern in ajax_patterns:
                    matches = re.findall(pattern, function_content)
                    if matches:
                        print(f"🌐 Found AJAX/fetch URLs: {matches}")
                        return matches
        
        print("❌ No download URLs found in JavaScript")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting JavaScript: {e}")
        return None

def try_common_consob_patterns():
    """Try common CONSOB URL patterns with different approaches"""
    print("🔍 Trying common CONSOB patterns...")
    
    # Common patterns based on other European regulators
    patterns = [
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/posizioni_corte_nette.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_attuali.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_storiche.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_correnti.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_previous.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/elenco_posizioni_corte_nette.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/elenco_posizioni_corte_nette.csv",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'Referer': 'https://www.consob.it/web/consob-and-its-activities/short-selling',
    }
    
    for url in patterns:
        try:
            print(f"🔍 Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                if b'PK' in response.content[:100]:
                    print(f"✅ SUCCESS! Found working URL: {url}")
                    return url
                else:
                    print(f"   ⚠️  Got response but not Excel file")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    return None

def main():
    """Main function"""
    print("🔬 Reverse Engineering CONSOB Download")
    print("=" * 50)
    
    # Try to extract URLs from JavaScript
    urls = extract_javascript_function()
    
    if urls:
        print(f"\n🎯 Found potential URLs: {urls}")
        
        # Try to download from these URLs
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
            'Referer': 'https://www.consob.it/web/consob-and-its-activities/short-selling',
        }
        
        for url in urls:
            try:
                print(f"📥 Trying to download from: {url}")
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200 and b'PK' in response.content[:100]:
                    print(f"✅ SUCCESS! Downloaded from: {url}")
                    
                    # Save the file
                    filename = f"consob_data_{int(time.time())}.xlsx"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"💾 Saved as: {filename}")
                    return filename
                    
            except Exception as e:
                print(f"❌ Failed to download from {url}: {e}")
                continue
    
    # Try common patterns
    working_url = try_common_consob_patterns()
    
    if working_url:
        print(f"\n🎉 Found working URL: {working_url}")
        return working_url
    
    print(f"\n❌ Could not find working download URL")
    print("CONSOB's JavaScript is heavily obfuscated or protected.")
    
    return None

if __name__ == "__main__":
    main()
