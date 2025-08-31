from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CountryBase(BaseModel):
    code: str
    name: str
    flag: str
    priority: str = "high"
    url: str


class CountryCreate(CountryBase):
    pass


class CountryResponse(CountryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CountryUpdate(BaseModel):
    name: Optional[str] = None
    flag: Optional[str] = None
    priority: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None
