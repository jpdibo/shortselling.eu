#!/usr/bin/env python3
"""
Debug Finland Download Buttons
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

def debug_finland_buttons():
    """Debug the Finland pages to find download buttons"""
    print("🔍 Debugging Finland Download Buttons")
    print("=" * 50)
    
    # Setup driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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
        time.sleep(5)
        
        # Wait for table to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✅ Current positions table loaded")
        except TimeoutException:
            print("❌ Timeout waiting for current positions table")
        
        # Look for all buttons and links
        print("\n🔍 Searching for download buttons on current page:")
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:")
        for i, button in enumerate(buttons[:10]):  # Show first 10
            try:
                text = button.text.strip()
                classes = button.get_attribute("class")
                print(f"  Button {i+1}: '{text}' (class: {classes})")
            except:
                print(f"  Button {i+1}: [error reading button]")
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nFound {len(links)} links:")
        for i, link in enumerate(links[:10]):  # Show first 10
            try:
                text = link.text.strip()
                href = link.get_attribute("href")
                classes = link.get_attribute("class")
                if text and any(keyword in text.lower() for keyword in ['download', 'export', 'save', 'excel', 'csv']):
                    print(f"  Link {i+1}: '{text}' -> {href} (class: {classes})")
            except:
                pass
        
        # Look for elements with download-related classes
        print(f"\n🔍 Searching for download-related elements:")
        download_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'download') or contains(@class, 'export') or contains(@class, 'save')]")
        print(f"Found {len(download_elements)} download-related elements:")
        for i, elem in enumerate(download_elements[:10]):
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                classes = elem.get_attribute("class")
                print(f"  Element {i+1}: <{tag}> '{text}' (class: {classes})")
            except:
                pass
        
        # Test historic positions page
        historic_url = "https://www.finanssivalvonta.fi/en/financial-market-participants/capital-markets/issuers-and-investors/short-positions/Historic-net-short-positions/"
        print(f"\n📄 Historic Positions Page:")
        print(f"URL: {historic_url}")
        
        driver.get(historic_url)
        time.sleep(5)
        
        # Wait for table to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✅ Historic positions table loaded")
        except TimeoutException:
            print("❌ Timeout waiting for historic positions table")
        
        # Look for all buttons and links
        print("\n🔍 Searching for download buttons on historic page:")
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:")
        for i, button in enumerate(buttons[:10]):  # Show first 10
            try:
                text = button.text.strip()
                classes = button.get_attribute("class")
                print(f"  Button {i+1}: '{text}' (class: {classes})")
            except:
                print(f"  Button {i+1}: [error reading button]")
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nFound {len(links)} links:")
        for i, link in enumerate(links[:10]):  # Show first 10
            try:
                text = link.text.strip()
                href = link.get_attribute("href")
                classes = link.get_attribute("class")
                if text and any(keyword in text.lower() for keyword in ['download', 'export', 'save', 'excel', 'csv']):
                    print(f"  Link {i+1}: '{text}' -> {href} (class: {classes})")
            except:
                pass
        
        # Look for elements with download-related classes
        print(f"\n🔍 Searching for download-related elements:")
        download_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'download') or contains(@class, 'export') or contains(@class, 'save')]")
        print(f"Found {len(download_elements)} download-related elements:")
        for i, elem in enumerate(download_elements[:10]):
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                classes = elem.get_attribute("class")
                print(f"  Element {i+1}: <{tag}> '{text}' (class: {classes})")
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_finland_buttons()

