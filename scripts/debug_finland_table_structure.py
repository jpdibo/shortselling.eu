#!/usr/bin/env python3
"""
Debug Finland Table Structure
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

def debug_finland_table_structure():
    """Debug the Finland table structure to find export functionality"""
    print("🔍 Debugging Finland Table Structure")
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
        
        # Examine table structure
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"\n📊 Found {len(tables)} tables on current page:")
        
        for i, table in enumerate(tables):
            print(f"\n  Table {i+1}:")
            
            # Get table headers
            headers = table.find_elements(By.TAG_NAME, "th")
            print(f"    Headers ({len(headers)}):")
            for j, header in enumerate(headers[:5]):  # Show first 5
                try:
                    text = header.text.strip()
                    print(f"      Header {j+1}: '{text}'")
                except:
                    print(f"      Header {j+1}: [error reading]")
            
            # Get table rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"    Rows: {len(rows)}")
            
            # Look for any export/download elements within the table
            export_elements = table.find_elements(By.XPATH, ".//*[contains(@class, 'export') or contains(@class, 'download') or contains(@class, 'save') or contains(text(), 'export') or contains(text(), 'download') or contains(text(), 'save')]")
            if export_elements:
                print(f"    Export elements found: {len(export_elements)}")
                for j, elem in enumerate(export_elements[:3]):
                    try:
                        tag = elem.tag_name
                        text = elem.text.strip()
                        classes = elem.get_attribute("class")
                        print(f"      Export element {j+1}: <{tag}> '{text}' (class: {classes})")
                    except:
                        pass
            
            # Look for any buttons within the table
            buttons = table.find_elements(By.TAG_NAME, "button")
            if buttons:
                print(f"    Buttons found: {len(buttons)}")
                for j, button in enumerate(buttons[:3]):
                    try:
                        text = button.text.strip()
                        classes = button.get_attribute("class")
                        print(f"      Button {j+1}: '{text}' (class: {classes})")
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
        
        # Examine table structure
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"\n📊 Found {len(tables)} tables on historic page:")
        
        for i, table in enumerate(tables):
            print(f"\n  Table {i+1}:")
            
            # Get table headers
            headers = table.find_elements(By.TAG_NAME, "th")
            print(f"    Headers ({len(headers)}):")
            for j, header in enumerate(headers[:5]):  # Show first 5
                try:
                    text = header.text.strip()
                    print(f"      Header {j+1}: '{text}'")
                except:
                    print(f"      Header {j+1}: [error reading]")
            
            # Get table rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"    Rows: {len(rows)}")
            
            # Look for any export/download elements within the table
            export_elements = table.find_elements(By.XPATH, ".//*[contains(@class, 'export') or contains(@class, 'download') or contains(@class, 'save') or contains(text(), 'export') or contains(text(), 'download') or contains(text(), 'save')]")
            if export_elements:
                print(f"    Export elements found: {len(export_elements)}")
                for j, elem in enumerate(export_elements[:3]):
                    try:
                        tag = elem.tag_name
                        text = elem.text.strip()
                        classes = elem.get_attribute("class")
                        print(f"      Export element {j+1}: <{tag}> '{text}' (class: {classes})")
                    except:
                        pass
            
            # Look for any buttons within the table
            buttons = table.find_elements(By.TAG_NAME, "button")
            if buttons:
                print(f"    Buttons found: {len(buttons)}")
                for j, button in enumerate(buttons[:3]):
                    try:
                        text = button.text.strip()
                        classes = button.get_attribute("class")
                        print(f"      Button {j+1}: '{text}' (class: {classes})")
                    except:
                        pass
        
        # Look for any iframes that might contain the actual data
        print(f"\n🔍 Looking for iframes:")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute("src")
                print(f"  Iframe {i+1}: {src}")
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_finland_table_structure()

