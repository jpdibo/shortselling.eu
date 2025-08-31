#!/usr/bin/env python3
"""
Selenium CONSOB Download
Uses Selenium to execute JavaScript and download the CONSOB file
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests

def setup_chrome_driver():
    """Setup Chrome driver with appropriate options"""
    print("🔧 Setting up Chrome driver...")
    
    chrome_options = Options()
    
    # Add options to make it more stealthy
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Disable images and CSS to speed up
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        # Try to create driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome driver setup successful")
        return driver
        
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        print("Make sure Chrome is installed and chromedriver is in PATH")
        return None

def download_consob_file():
    """Download CONSOB file using Selenium"""
    print("🚀 Starting Selenium CONSOB download...")
    
    driver = setup_chrome_driver()
    if not driver:
        return None
    
    try:
        # Navigate to CONSOB page
        url = "https://www.consob.it/web/consob-and-its-activities/short-selling"
        print(f"🌐 Navigating to: {url}")
        
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        print(f"📄 Page title: {driver.title}")
        
        # Check if we got the actual page or captcha
        if "captcha" in driver.title.lower() or "radware" in driver.title.lower():
            print("❌ Got captcha page, trying to wait...")
            time.sleep(10)  # Wait longer for captcha to resolve
            
            # Check again
            if "captcha" in driver.title.lower():
                print("❌ Still on captcha page")
                return None
        
        # Look for the download link
        print("🔍 Looking for download link...")
        
        try:
            # Wait for download link to be present
            download_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'javascript:downloadShortselling()')]"))
            )
            
            print("✅ Found download link!")
            print(f"   Text: {download_link.text}")
            
            # Click the download link
            print("🖱️  Clicking download link...")
            download_link.click()
            
            # Wait for download to start
            time.sleep(3)
            
            # Check if download started
            print("📥 Checking for download...")
            
            # Look for any new network requests or downloads
            # We'll check the browser's download directory
            downloads_dir = os.path.expanduser("~/Downloads")
            print(f"📁 Checking downloads directory: {downloads_dir}")
            
            # Wait a bit more for download to complete
            time.sleep(5)
            
            # Look for Excel files in downloads
            excel_files = []
            for file in os.listdir(downloads_dir):
                if file.endswith(('.xlsx', '.xls')) and 'consob' in file.lower():
                    excel_files.append(file)
            
            if excel_files:
                print(f"✅ Found downloaded files: {excel_files}")
                return os.path.join(downloads_dir, excel_files[0])
            else:
                print("⚠️  No Excel files found in downloads")
                
                # Try to find any recent Excel files
                import glob
                excel_files = glob.glob(os.path.join(downloads_dir, "*.xlsx"))
                excel_files.extend(glob.glob(os.path.join(downloads_dir, "*.xls")))
                
                if excel_files:
                    # Get the most recent file
                    latest_file = max(excel_files, key=os.path.getctime)
                    print(f"📄 Found recent Excel file: {latest_file}")
                    return latest_file
                
        except Exception as e:
            print(f"❌ Error finding/clicking download link: {e}")
            
            # Try alternative approach - execute JavaScript directly
            print("🔄 Trying direct JavaScript execution...")
            try:
                driver.execute_script("downloadShortselling();")
                time.sleep(5)
                
                # Check downloads again
                downloads_dir = os.path.expanduser("~/Downloads")
                excel_files = []
                for file in os.listdir(downloads_dir):
                    if file.endswith(('.xlsx', '.xls')):
                        excel_files.append(file)
                
                if excel_files:
                    # Get the most recent file
                    import glob
                    excel_files = glob.glob(os.path.join(downloads_dir, "*.xlsx"))
                    excel_files.extend(glob.glob(os.path.join(downloads_dir, "*.xls")))
                    
                    if excel_files:
                        latest_file = max(excel_files, key=os.path.getctime)
                        print(f"✅ Found downloaded file: {latest_file}")
                        return latest_file
                        
            except Exception as js_error:
                print(f"❌ JavaScript execution failed: {js_error}")
        
        return None
        
    except Exception as e:
        print(f"❌ Selenium download failed: {e}")
        return None
        
    finally:
        print("🔒 Closing browser...")
        driver.quit()

def try_network_interception():
    """Try to intercept network requests to find the actual download URL"""
    print("🌐 Trying network interception approach...")
    
    driver = setup_chrome_driver()
    if not driver:
        return None
    
    try:
        # Enable network logging
        driver.execute_cdp_cmd('Network.enable', {})
        
        # Navigate to page
        url = "https://www.consob.it/web/consob-and-its-activities/short-selling"
        driver.get(url)
        time.sleep(5)
        
        # Look for download link and click it
        try:
            download_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'javascript:downloadShortselling()')]"))
            )
            download_link.click()
            time.sleep(3)
            
            # Get network logs
            logs = driver.get_log('performance')
            
            # Look for network requests
            for log in logs:
                if 'Network.responseReceived' in log['message']:
                    print(f"📡 Network request: {log['message']}")
                    
        except Exception as e:
            print(f"❌ Network interception failed: {e}")
        
        return None
        
    finally:
        driver.quit()

def main():
    """Main function"""
    print("🤖 Selenium CONSOB Download")
    print("=" * 50)
    print("Using Selenium to execute JavaScript and download CONSOB file...")
    print("=" * 50)
    
    # Try the main approach
    downloaded_file = download_consob_file()
    
    if downloaded_file:
        print(f"\n🎉 SUCCESS! Downloaded file: {downloaded_file}")
        
        # Verify it's a valid Excel file
        try:
            with open(downloaded_file, 'rb') as f:
                content = f.read(100)
                if b'PK' in content:
                    print("✅ Confirmed: Valid Excel file")
                    
                    # Copy to project directory
                    import shutil
                    project_file = f"consob_data_{int(time.time())}.xlsx"
                    shutil.copy2(downloaded_file, project_file)
                    print(f"💾 Copied to project as: {project_file}")
                    return project_file
                else:
                    print("❌ Not a valid Excel file")
                    
        except Exception as e:
            print(f"❌ Error verifying file: {e}")
    
    print(f"\n❌ Selenium approach failed!")
    print("CONSOB's JavaScript download function is heavily protected.")
    print("Next steps:")
    print("1. Try with different browser profiles")
    print("2. Use proxy/VPN")
    print("3. Implement captcha solving")
    print("4. Contact CONSOB for API access")
    
    return None

if __name__ == "__main__":
    main()
