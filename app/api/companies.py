from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Company, Country
from app.schemas.company import CompanyResponse

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    country_code: str = None,
    db: Session = Depends(get_db)
):
    """Get companies, optionally filtered by country"""
    query = db.query(Company)
    
    if country_code:
        query = query.join(Country).filter(Country.code == country_code.upper())
    
    companies = query.all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company
