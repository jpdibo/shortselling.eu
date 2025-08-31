#!/usr/bin/env python3
"""
Scraping API endpoints for ShortSelling.eu
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
import logging

from app.services.daily_scraping_service import DailyScrapingService

router = APIRouter(prefix="/scraping", tags=["scraping"])
logger = logging.getLogger(__name__)

# Global variable to track if scraping is running
scraping_in_progress = False

@router.post("/run-daily-update")
async def run_daily_update(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Trigger daily scraping update for all countries
    """
    global scraping_in_progress
    
    if scraping_in_progress:
        raise HTTPException(
            status_code=409, 
            detail="Scraping is already in progress. Please wait for it to complete."
        )
    
    scraping_in_progress = True
    
    try:
        # Run scraping in background
        scraping_service = DailyScrapingService()
        result = await scraping_service.run_daily_update()
        
        return {
            "success": True,
            "message": "Daily scraping completed successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Daily scraping failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Daily scraping failed: {str(e)}"
        )
    finally:
        scraping_in_progress = False

@router.get("/status")
async def get_scraping_status() -> Dict[str, Any]:
    """
    Get current scraping status and statistics
    """
    try:
        scraping_service = DailyScrapingService()
        status = scraping_service.get_scraping_status()
        
        return {
            "success": True,
            "status": status,
            "scraping_in_progress": scraping_in_progress
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scraping status: {str(e)}"
        )

@router.get("/countries")
async def get_supported_countries() -> Dict[str, Any]:
    """
    Get list of supported countries for scraping
    """
    try:
        scraping_service = DailyScrapingService()
        countries = scraping_service.scraper_factory.get_available_countries()
        
        country_names = {
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'ES': 'Spain',
            'BE': 'Belgium',
            'IE': 'Ireland'
        }
        
        return {
            "success": True,
            "countries": [
                {
                    "code": code,
                    "name": country_names.get(code, code)
                }
                for code in countries
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported countries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported countries: {str(e)}"
        )

@router.post("/test-country/{country_code}")
async def test_country_scraper(country_code: str) -> Dict[str, Any]:
    """
    Test scraping for a specific country
    """
    try:
        scraping_service = DailyScrapingService()
        
        # Check if country is supported
        if not scraping_service.scraper_factory.is_country_supported(country_code):
            raise HTTPException(
                status_code=400,
                detail=f"Country {country_code} is not supported for scraping"
            )
        
        # Create scraper and test
        scraper = scraping_service.scraper_factory.create_scraper(country_code)
        positions = scraper.scrape()
        
        return {
            "success": True,
            "country_code": country_code,
            "positions_found": len(positions),
            "sample_positions": positions[:5] if positions else []  # Return first 5 positions as sample
        }
        
    except Exception as e:
        logger.error(f"Failed to test country {country_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test country {country_code}: {str(e)}"
        )
