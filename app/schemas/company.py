from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    isin: Optional[str] = None


class CompanyCreate(CompanyBase):
    country_id: int


class CompanyResponse(CompanyBase):
    id: int
    country_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    isin: Optional[str] = None
