#!/usr/bin/env python3
"""
Debug Finland Visible Button (Non-headless)
"""
import sys
import os
sys.path.append(r'C:\shortselling.eu')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def debug_finland_visible_button():
    """Debug the Finland pages to find the button without headless mode"""
    print("🔍 Debugging Finland Visible Button (Non-headless)")
    print("=" * 50)
    
    # Setup driver without headless mode
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Commented out to see the page
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    try:
        # Test current positions page
        current_url = "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions/Current-net-short-positions/"
        print(f"\n📄 Current Positions Page:")
        print(f"URL: {current_url}")
        
        driver.get(current_url)
        time.sleep(10)  # Wait longer for page to load
        
        # Wait for table to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✅ Current positions table loaded")
        except TimeoutException:
            print("❌ Timeout waiting for current positions table")
        
        # Scroll down to see if there are more elements
        print("\n📜 Scrolling down to find more elements...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        
        # Look for all elements with any text containing 'excel' or 'csv' or 'save'
        print("\n🔍 Searching for elements with 'excel', 'csv', or 'save' text:")
        
        # Find all elements with text containing 'excel' or 'csv' or 'save'
        excel_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'excel') or contains(text(), 'csv') or contains(text(), 'Excel') or contains(text(), 'CSV') or contains(text(), 'save') or contains(text(), 'Save')]")
        print(f"Found {len(excel_elements)} elements with excel/csv/save text:")
        
        for i, elem in enumerate(excel_elements[:20]):  # Show first 20
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                classes = elem.get_attribute("class")
                if text:  # Only show elements with text
                    print(f"  Element {i+1}: <{tag}> '{text}' (class: {classes})")
            except:
                print(f"  Element {i+1}: [error reading element]")
        
        # Look for all buttons and links with any text
        print(f"\n🔍 Searching for all buttons and links:")
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:")
        for i, button in enumerate(buttons[:30]):  # Show first 30
            try:
                text = button.text.strip()
                if text:  # Only show buttons with text
                    classes = button.get_attribute("class")
                    print(f"  Button {i+1}: '{text}' (class: {classes})")
            except:
                pass
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nFound {len(links)} links:")
        for i, link in enumerate(links[:30]):  # Show first 30
            try:
                text = link.text.strip()
                if text:  # Only show links with text
                    href = link.get_attribute("href")
                    classes = link.get_attribute("class")
                    print(f"  Link {i+1}: '{text}' -> {href} (class: {classes})")
            except:
                pass
        
        # Look for elements with download-related classes
        print(f"\n🔍 Searching for download-related elements:")
        download_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'download') or contains(@class, 'export') or contains(@class, 'save') or contains(@class, 'button') or contains(@class, 'btn')]")
        print(f"Found {len(download_elements)} download-related elements:")
        for i, elem in enumerate(download_elements[:20]):
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                classes = elem.get_attribute("class")
                if text:  # Only show elements with text
                    print(f"  Element {i+1}: <{tag}> '{text}' (class: {classes})")
            except:
                pass
        
        print("\n⏸️  Pausing for 10 seconds to let you see the page...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_finland_visible_button()

