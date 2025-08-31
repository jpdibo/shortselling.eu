#!/usr/bin/env python3
"""
Test CONSOB URLs
Tests various CONSOB URL patterns to find the actual data download location
"""
import requests
import time

def test_consob_urls():
    """Test various CONSOB URL patterns"""
    print("🔍 Testing CONSOB URL Patterns")
    print("=" * 50)
    
    # Common CONSOB URL patterns
    urls_to_test = [
        # Direct file URLs
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette.xlsx",
        "https://www.consob.it/documents/46180/46181/short_positions.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette.csv",
        "https://www.consob.it/documents/46180/46181/short_positions.csv",
        
        # Alternative paths
        "https://www.consob.it/web/site-pubbl/pnc/posizioni_corte_nette.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/short_positions.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/posizioni_corte_nette.csv",
        "https://www.consob.it/web/site-pubbl/pnc/short_positions.csv",
        
        # Different document paths
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_attuali.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_storiche.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_correnti.xlsx",
        "https://www.consob.it/documents/46180/46181/posizioni_corte_nette_previous.xlsx",
        
        # API-like endpoints
        "https://www.consob.it/api/short-positions/download",
        "https://www.consob.it/api/posizioni-corte/download",
        "https://www.consob.it/web/api/short-positions",
        "https://www.consob.it/web/api/posizioni-corte",
        
        # Alternative page URLs
        "https://www.consob.it/web/site-pubbl/pnc",
        "https://www.consob.it/web/consob-and-its-activities/short-selling/data",
        "https://www.consob.it/web/consob-and-its-activities/short-selling/download",
        
        # Legacy URLs
        "https://www.consob.it/web/site-pubbl/pnc/elenco_posizioni_corte_nette.xlsx",
        "https://www.consob.it/web/site-pubbl/pnc/elenco_posizioni_corte_nette.csv",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    working_urls = []
    
    for url in urls_to_test:
        try:
            print(f"🔍 Testing: {url}")
            
            # Try HEAD request first (faster)
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', 'Unknown')
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📏 Content-Length: {content_length}")
                
                # If it's a file, try to get a small sample
                if 'excel' in content_type or 'csv' in content_type or url.endswith(('.xlsx', '.xls', '.csv')):
                    print(f"   📥 This looks like a data file!")
                    working_urls.append({
                        'url': url,
                        'content_type': content_type,
                        'content_length': content_length
                    })
                    
                    # Try to get first few bytes to verify it's a real file
                    try:
                        sample_response = requests.get(url, headers=headers, timeout=10, stream=True)
                        if sample_response.status_code == 200:
                            # Read first 100 bytes
                            sample_content = sample_response.raw.read(100)
                            sample_response.close()
                            
                            # Check if it looks like Excel or CSV
                            if b'PK' in sample_content:  # Excel file signature
                                print(f"   ✅ Confirmed: Excel file (PK signature found)")
                            elif b',' in sample_content or b';' in sample_content:  # CSV indicators
                                print(f"   ✅ Confirmed: CSV file (comma/semicolon found)")
                            else:
                                print(f"   ⚠️  Unknown file format")
                    except Exception as e:
                        print(f"   ⚠️  Could not verify file content: {e}")
                
            elif response.status_code == 404:
                print(f"   ❌ Status: {response.status_code} (Not Found)")
            elif response.status_code == 403:
                print(f"   🚫 Status: {response.status_code} (Forbidden)")
            elif response.status_code == 302 or response.status_code == 301:
                print(f"   🔄 Status: {response.status_code} (Redirect)")
                print(f"   📍 Redirect to: {response.headers.get('location', 'Unknown')}")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay to be respectful
        time.sleep(0.5)
    
    print(f"\n📊 Summary:")
    print(f"   - Tested {len(urls_to_test)} URLs")
    print(f"   - Found {len(working_urls)} potentially working URLs")
    
    if working_urls:
        print(f"\n✅ Working URLs found:")
        for url_info in working_urls:
            print(f"   - {url_info['url']}")
            print(f"     Content-Type: {url_info['content_type']}")
            print(f"     Content-Length: {url_info['content_length']}")
    else:
        print(f"\n❌ No working URLs found")
        print(f"   This suggests CONSOB may require:")
        print(f"   - Authentication/session")
        print(f"   - Captcha solving")
        print(f"   - JavaScript execution")
        print(f"   - Different access method")

if __name__ == "__main__":
    test_consob_urls()
