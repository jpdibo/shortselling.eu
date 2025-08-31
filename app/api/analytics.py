#!/usr/bin/env python3
"""
Analytics API Router
Exposes endpoints for analytics (global, country, company, manager).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import analytics as analytics_service

router = APIRouter()

# ---------------------------------------------------------------------
# Global endpoints
# ---------------------------------------------------------------------

@router.get("/global/top-companies")
async def get_global_top_companies_endpoint(db: Session = Depends(get_db)):
    return await analytics_service.get_global_top_companies(db)


@router.get("/global/top-managers")
async def get_global_top_managers_endpoint(db: Session = Depends(get_db)):
    return await analytics_service.get_global_top_managers(db)


@router.get("/global")
async def get_global_analytics_endpoint(timeframe: str = "3m", db: Session = Depends(get_db)):
    return await analytics_service.get_global_analytics(db, timeframe)


# ---------------------------------------------------------------------
# Country endpoints
# ---------------------------------------------------------------------

async def get_country_by_identifier(identifier: str, db: Session):
    """Helper to get country by ID or code"""
    from app.db.models import Country
    from fastapi import HTTPException
    
    # Try to parse as integer first
    try:
        country_id = int(identifier)
        country = db.query(Country).filter(Country.id == country_id).first()
    except ValueError:
        # If not an integer, treat as country code
        country = db.query(Country).filter(Country.code == identifier.upper()).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return country

@router.get("/countries/{country_identifier}/most-shorted")
async def get_country_most_shorted_endpoint(country_identifier: str, db: Session = Depends(get_db)):
    country = await get_country_by_identifier(country_identifier, db)
    return await analytics_service.get_most_shorted_companies(db, country.id)


@router.get("/countries/{country_identifier}/top-managers")
async def get_country_top_managers_endpoint(country_identifier: str, db: Session = Depends(get_db)):
    country = await get_country_by_identifier(country_identifier, db)
    return await analytics_service.get_top_managers(db, country.id)


@router.get("/countries/{country_identifier}/analytics")
async def get_country_analytics_endpoint(country_identifier: str, db: Session = Depends(get_db)):
    country = await get_country_by_identifier(country_identifier, db)
    return await analytics_service.get_country_analytics(db, country.id)


# ---------------------------------------------------------------------
# Company endpoints
# ---------------------------------------------------------------------

@router.get("/companies/{company_id}")
async def get_company_analytics_endpoint(company_id: int, timeframe: str = "3m", db: Session = Depends(get_db)):
    return await analytics_service.get_company_analytics(db, company_id, timeframe)


@router.get("/companies/by-name/{company_name}")
async def get_company_analytics_by_name_endpoint(company_name: str, timeframe: str = "3m", db: Session = Depends(get_db)):
    return await analytics_service.get_company_analytics_by_name(db, company_name, timeframe)


# ---------------------------------------------------------------------
# Manager endpoints
# ---------------------------------------------------------------------

@router.get("/managers/{manager_slug}")
async def get_manager_analytics_endpoint(manager_slug: str, timeframe: str = "3m", db: Session = Depends(get_db)):
    return await analytics_service.get_manager_analytics_by_slug(db, manager_slug, timeframe)
