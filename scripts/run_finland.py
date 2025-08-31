#!/usr/bin/env python3
import sys
import os
import asyncio
import traceback
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("Starting Finland Scraper...")
print(f"Python path: {sys.path[0]}")

try:
    from app.services.daily_scraping_service import DailyScrapingService
    print("Successfully imported DailyScrapingService")
except Exception as e:
    print(f"Failed to import DailyScrapingService: {e}")
    traceback.print_exc()
    sys.exit(1)

async def main():
    try:
        print("Creating DailyScrapingService instance...")
        svc = DailyScrapingService()
        print("Running scraper for FI...")
        result = await svc.run_for_country_codes(['FI'])
        print(f"Finland Scraper completed!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Finland Scraper failed: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Script failed: {e}")
        traceback.print_exc()

