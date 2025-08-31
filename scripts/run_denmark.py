#!/usr/bin/env python3
import sys
import os
import asyncio

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.daily_scraping_service import DailyScrapingService

async def main():
    svc = DailyScrapingService()
    result = await svc.run_for_country_codes(['DK'])
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

