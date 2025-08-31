from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Manager
from app.schemas.manager import ManagerResponse

router = APIRouter()


@router.get("/", response_model=List[ManagerResponse])
async def get_managers(db: Session = Depends(get_db)):
    """Get all managers"""
    managers = db.query(Manager).all()
    return managers


@router.get("/{manager_id}", response_model=ManagerResponse)
async def get_manager(manager_id: int, db: Session = Depends(get_db)):
    """Get manager by ID"""
    manager = db.query(Manager).filter(Manager.id == manager_id).first()
    
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    return manager


@router.get("/slug/{manager_slug}", response_model=ManagerResponse)
async def get_manager_by_slug(manager_slug: str, db: Session = Depends(get_db)):
    """Get manager by slug"""
    manager = db.query(Manager).filter(Manager.slug == manager_slug).first()
    
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    return manager
