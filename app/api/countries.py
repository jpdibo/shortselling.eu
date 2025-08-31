from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Country
from app.schemas.country import CountryResponse, CountryCreate
from app.services.analytics import get_country_analytics

router = APIRouter()


@router.get("/", response_model=List[CountryResponse])
async def get_countries(db: Session = Depends(get_db)):
    """Get all countries"""
    countries = db.query(Country).filter(Country.is_active == True).all()
    return countries


@router.get("/{country_code}", response_model=CountryResponse)
async def get_country(country_code: str, db: Session = Depends(get_db)):
    """Get country by code"""
    country = db.query(Country).filter(
        Country.code == country_code.upper(),
        Country.is_active == True
    ).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return country


@router.get("/{country_code}/analytics")
async def get_country_analytics_data(country_code: str, db: Session = Depends(get_db)):
    """Get analytics data for a specific country"""
    country = db.query(Country).filter(
        Country.code == country_code.upper(),
        Country.is_active == True
    ).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return await get_country_analytics(db, country.id)


@router.get("/{country_code}/most-shorted")
async def get_most_shorted_companies(country_code: str, db: Session = Depends(get_db)):
    """Get most shorted companies for a country"""
    country = db.query(Country).filter(
        Country.code == country_code.upper(),
        Country.is_active == True
    ).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # This will be implemented in the analytics service
    from app.services.analytics import get_most_shorted_companies
    return await get_most_shorted_companies(db, country.id)


@router.get("/{country_code}/top-managers")
async def get_top_managers(country_code: str, db: Session = Depends(get_db)):
    """Get top managers with most active positions for a country"""
    country = db.query(Country).filter(
        Country.code == country_code.upper(),
        Country.is_active == True
    ).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # This will be implemented in the analytics service
    from app.services.analytics import get_top_managers
    return await get_top_managers(db, country.id)
