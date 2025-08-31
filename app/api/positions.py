from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.db.models import ShortPosition, Company, Manager, Country
from app.schemas.position import PositionResponse

router = APIRouter()


@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    country_code: Optional[str] = None,
    company_id: Optional[int] = None,
    manager_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get short positions with optional filters"""
    query = db.query(ShortPosition)
    
    if country_code:
        query = query.join(Country).filter(Country.code == country_code.upper())
    
    if company_id:
        query = query.filter(ShortPosition.company_id == company_id)
    
    if manager_id:
        query = query.filter(ShortPosition.manager_id == manager_id)
    
    if is_active is not None:
        query = query.filter(ShortPosition.is_active == is_active)
    
    if date:
        query = query.filter(ShortPosition.date == date)
    
    positions = query.limit(limit).all()
    return positions


@router.get("/latest")
async def get_latest_positions(
    country_code: Optional[str] = None,
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db)
):
    """Get latest short positions from entire database in descending order"""
    # Query with proper joins to get company, manager, and country names
    # Order by date descending to get the newest positions first
    # Exclude 0% positions and get diverse data across countries and dates
    query = db.query(ShortPosition).join(
        Company, ShortPosition.company_id == Company.id
    ).join(
        Manager, ShortPosition.manager_id == Manager.id
    ).join(
        Country, ShortPosition.country_id == Country.id
    ).filter(
        ShortPosition.position_size > 0.0  # Exclude 0% positions
    )
    
    if country_code:
        query = query.filter(Country.code == country_code.upper())
    
    # Order by date descending to get newest positions first
    positions = query.order_by(ShortPosition.date.desc(), ShortPosition.id.desc()).limit(limit).all()
    
    return [
        {
            "id": pos.id,
            "date": pos.date,
            "company": pos.company.name,
            "company_id": pos.company.id,  # Added for frontend routing
            "manager": pos.manager.name,
            "manager_slug": pos.manager.slug,  # Added for frontend routing
            "country": pos.country.name,
            "country_code": pos.country.code,  # Added for flag display
            "position_size": pos.position_size,
            "is_active": pos.is_active
        }
        for pos in positions
    ]
