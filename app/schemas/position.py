from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PositionBase(BaseModel):
    date: datetime
    position_size: float
    is_active: bool


class PositionCreate(PositionBase):
    company_id: int
    manager_id: int
    country_id: int
    source_url: Optional[str] = None
    raw_data: Optional[str] = None


class PositionResponse(PositionBase):
    id: int
    company_id: int
    manager_id: int
    country_id: int
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PositionUpdate(BaseModel):
    position_size: Optional[float] = None
    is_active: Optional[bool] = None
    source_url: Optional[str] = None
    raw_data: Optional[str] = None
