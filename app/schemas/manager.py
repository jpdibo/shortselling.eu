from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ManagerBase(BaseModel):
    name: str
    slug: str


class ManagerCreate(ManagerBase):
    pass


class ManagerResponse(ManagerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ManagerUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
