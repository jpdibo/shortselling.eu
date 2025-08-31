#!/usr/bin/env python3
"""
Download CONSOB Actual URL
Downloads the CONSOB file using the actual URL found in JavaScript
"""
import requests
import time
import random

def download_consob_file():
    """Download CONSOB file using the actual URL from JavaScript"""
    print("🎯 Downloading CONSOB file using actual URL...")
    
    # The actual URL found in the JavaScript function
    base_url = "https://www.consob.it/documents/11973/395154/PncPubl.xlsx/fbefe0a2-795b-bad3-9369-beccbeb14f27"
    
    # Add a random timestamp as the JavaScript does
    rand = int(time.time() * 1000) + random.randint(1000, 9999)
    download_url = f"{base_url}?t={rand}"
    
    print(f"📥 Download URL: {download_url}")
    
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
        'Referer': 'https://www.consob.it/web/consob-and-its-activities/short-selling',
    }
    
    try:
        print("🔄 Attempting download...")
        response = requests.get(download_url, headers=headers, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Content length: {len(response.content):,} bytes")
        print(f"📊 Content type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            # Check if it's an Excel file
            if b'PK' in response.content[:100]:
                print("✅ SUCCESS! Downloaded valid Excel file!")
                
                # Save the file
                timestamp = int(time.time())
                filename = f"consob_data_{timestamp}.xlsx"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"💾 Saved as: {filename}")
                print(f"📊 File size: {len(response.content):,} bytes")
                
                return filename
            else:
                print("❌ Downloaded file is not a valid Excel file")
                print("First 100 bytes:", response.content[:100])
                return None
        else:
            print(f"❌ Download failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

def try_with_session():
    """Try downloading with a session to maintain cookies"""
    print("🍪 Trying with session approach...")
    
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
    }
    
    session.headers.update(headers)
    
    try:
        # First visit the main page to get cookies
        print("🏠 Visiting main page...")
        main_response = session.get("https://www.consob.it", timeout=15)
        print(f"   Status: {main_response.status_code}")
        
        time.sleep(2)
        
        # Visit the short-selling page
        print("📄 Visiting short-selling page...")
        short_selling_response = session.get("https://www.consob.it/web/consob-and-its-activities/short-selling", timeout=15)
        print(f"   Status: {short_selling_response.status_code}")
        
        time.sleep(2)
        
        # Now try to download the file
        base_url = "https://www.consob.it/documents/11973/395154/PncPubl.xlsx/fbefe0a2-795b-bad3-9369-beccbeb14f27"
        rand = int(time.time() * 1000) + random.randint(1000, 9999)
        download_url = f"{base_url}?t={rand}"
        
        print(f"📥 Downloading with session: {download_url}")
        
        file_response = session.get(download_url, timeout=30)
        
        print(f"📊 Response status: {file_response.status_code}")
        print(f"📊 Content length: {len(file_response.content):,} bytes")
        
        if file_response.status_code == 200 and b'PK' in file_response.content[:100]:
            print("✅ SUCCESS with session approach!")
            
            timestamp = int(time.time())
            filename = f"consob_data_session_{timestamp}.xlsx"
            
            with open(filename, 'wb') as f:
                f.write(file_response.content)
            
            print(f"💾 Saved as: {filename}")
            return filename
        else:
            print("❌ Session approach failed")
            return None
            
    except Exception as e:
        print(f"❌ Session approach error: {e}")
        return None

def main():
    """Main function"""
    print("🎯 CONSOB Actual URL Download")
    print("=" * 50)
    print("Using the actual download URL found in JavaScript...")
    print("=" * 50)
    
    # Try direct download
    result = download_consob_file()
    
    if result:
        print(f"\n🎉 SUCCESS! Downloaded CONSOB file: {result}")
        return result
    
    # Try with session
    print(f"\n🔄 Trying session approach...")
    result = try_with_session()
    
    if result:
        print(f"\n🎉 SUCCESS with session! Downloaded CONSOB file: {result}")
        return result
    
    print(f"\n❌ Both approaches failed!")
    print("The URL might require additional authentication or session data.")
    
    return None

if __name__ == "__main__":
    main()
