from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Subscription
import json

router = APIRouter()


class SubscriptionCreate(BaseModel):
    first_name: str
    email: str
    frequency: str = "daily"  # daily, weekly, monthly
    countries: List[str] = []  # List of country codes


class SubscriptionResponse(BaseModel):
    id: int
    first_name: str
    email: str
    frequency: str
    countries: List[str]
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new email subscription"""
    # Check if email already exists
    existing = db.query(Subscription).filter(
        Subscription.email == subscription.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    
    # Create new subscription
    db_subscription = Subscription(
        first_name=subscription.first_name,
        email=subscription.email,
        frequency=subscription.frequency,
        countries=json.dumps(subscription.countries),
        is_active=True
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    return SubscriptionResponse(
        id=db_subscription.id,
        first_name=db_subscription.first_name,
        email=db_subscription.email,
        frequency=db_subscription.frequency,
        countries=json.loads(db_subscription.countries),
        is_active=db_subscription.is_active
    )


@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions(db: Session = Depends(get_db)):
    """Get all active subscriptions"""
    subscriptions = db.query(Subscription).filter(Subscription.is_active == True).all()
    
    return [
        SubscriptionResponse(
            id=sub.id,
            first_name=sub.first_name,
            email=sub.email,
            frequency=sub.frequency,
            countries=json.loads(sub.countries),
            is_active=sub.is_active
        )
        for sub in subscriptions
    ]


@router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Delete a subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = False
    db.commit()
    
    return {"message": "Subscription deleted successfully"}
