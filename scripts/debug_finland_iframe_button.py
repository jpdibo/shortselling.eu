#!/usr/bin/env python3
"""
Debug Finland Iframe and Dynamic Button
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

def debug_finland_iframe_button():
    """Debug the Finland pages to find the button in iframes or dynamic content"""
    print("🔍 Debugging Finland Iframe and Dynamic Button")
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
        time.sleep(15)  # Wait longer for page to load
        
        # Wait for table to load
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("✅ Current positions table loaded")
        except TimeoutException:
            print("❌ Timeout waiting for current positions table")
        
        # Check for iframes
        print(f"\n🔍 Looking for iframes:")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute("src")
                print(f"  Iframe {i+1}: {src}")
                
                # Switch to iframe and look for button
                driver.switch_to.frame(iframe)
                time.sleep(2)
                
                # Look for button in iframe
                iframe_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'excel') or contains(text(), 'csv') or contains(text(), 'save')]")
                if iframe_buttons:
                    print(f"    Found {len(iframe_buttons)} potential buttons in iframe {i+1}")
                    for j, btn in enumerate(iframe_buttons[:5]):
                        try:
                            text = btn.text.strip()
                            tag = btn.tag_name
                            print(f"      Button {j+1}: <{tag}> '{text}'")
                        except:
                            pass
                
                # Switch back to main content
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"  Error with iframe {i+1}: {e}")
                driver.switch_to.default_content()
        
        # Wait for dynamic content and scroll
        print(f"\n⏳ Waiting for dynamic content...")
        time.sleep(10)
        
        # Scroll down multiple times to trigger any lazy loading
        for i in range(3):
            print(f"  Scroll {i+1}/3")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
        
        # Look for all elements with any text containing 'excel' or 'csv' or 'save'
        print("\n🔍 Final search for elements with 'excel', 'csv', or 'save' text:")
        
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
        print(f"\n🔍 Final search for all buttons and links:")
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:")
        for i, button in enumerate(buttons[:50]):  # Show first 50
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
        for i, link in enumerate(links[:50]):  # Show first 50
            try:
                text = link.text.strip()
                if text:  # Only show links with text
                    href = link.get_attribute("href")
                    classes = link.get_attribute("class")
                    print(f"  Link {i+1}: '{text}' -> {href} (class: {classes})")
            except:
                pass
        
        print("\n⏸️  Pausing for 15 seconds to let you see the page...")
        time.sleep(15)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_finland_iframe_button()

