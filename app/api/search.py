#!/usr/bin/env python3
"""
Search API Router
Provides search functionality for companies and managers
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Dict, Any
from app.db.database import get_db
from app.db.models import Company, Manager, Country

router = APIRouter()

@router.get("/search")
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Search for companies and managers by name
    Returns combined results with type indicators
    """
    query = q.strip()
    
    results = []
    
    # Search companies (case-insensitive)
    companies = db.query(
        Company.id,
        Company.name,
        Company.isin,
        Country.name.label("country_name")
    ).join(
        Country, Company.country_id == Country.id
    ).filter(
        or_(
            func.upper(Company.name).contains(func.upper(query)),
            func.upper(Company.isin).contains(func.upper(query))
        )
    ).limit(limit // 2).all()  # Split results between companies and managers
    
    for company in companies:
        results.append({
            "type": "company",
            "id": company.id,
            "name": company.name,
            "isin": company.isin,
            "country": company.country_name
        })
    
    # Search managers (case-insensitive)
    remaining_slots = limit - len(results)
    if remaining_slots > 0:
        managers = db.query(
            Manager.id,
            Manager.name,
            Manager.slug
        ).filter(
            func.upper(Manager.name).contains(func.upper(query))
        ).limit(remaining_slots).all()
        
        for manager in managers:
            results.append({
                "type": "manager",
                "id": manager.id,
                "name": manager.name,
                "slug": manager.slug
            })
    
    # Sort results by relevance (exact matches first, then partial matches)
    def sort_key(result):
        name_lower = result["name"].lower()
        query_lower = query.lower()
        
        if name_lower == query_lower:
            return (0, result["name"])  # Exact match
        elif name_lower.startswith(query_lower):
            return (1, result["name"])  # Starts with query
        else:
            return (2, result["name"])  # Contains query
    
    results.sort(key=sort_key)
    
    return results[:limit]