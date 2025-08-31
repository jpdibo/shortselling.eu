# app/services/analytics.py
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from app.db.models import Country, Company, Manager, ShortPosition, AnalyticsCache

ACTIVE_THRESHOLD = 0.5  # percent points


# -------------------------------
# Helpers
# -------------------------------

def reconstruct_active_positions_timeline(all_positions, cutoff_date: datetime, days_range: int, country_code: str = None):
    """
    Reconstruct the active positions timeline for a company with continuous business days.
    
    Logic:
    - A manager is active if their most recent position ≥ 0.5%
    - A manager remains active from disclosure date until they drop below 0.5%
    - Show continuous timeline for all business days (Mon-Fri, excluding holidays)
    - Carry forward positions on days without changes
    """
    from collections import defaultdict
    import holidays
    
    # Group positions by manager
    manager_positions = defaultdict(list)
    for pos in all_positions:
        manager_positions[pos.manager_name].append({
            'date': pos.date,
            'position_size': float(pos.position_size or 0.0)
        })
    
    # Sort each manager's positions by date
    for manager in manager_positions:
        manager_positions[manager].sort(key=lambda x: x['date'])
    
    # Define date range
    end_date = datetime.now().date()
    start_date = max(cutoff_date.date(), end_date - timedelta(days=days_range))
    
    # Get holiday calendar based on company's country
    country_holidays = set()
    if country_code:
        try:
            # Map country codes to holiday country names
            country_mapping = {
                'FR': 'France',
                'DE': 'Germany', 
                'GB': 'UnitedKingdom',
                'IT': 'Italy',
                'ES': 'Spain',
                'NL': 'Netherlands',
                'BE': 'Belgium',
                'AT': 'Austria',
                'IE': 'Ireland',
                'PT': 'Portugal',
                'SE': 'Sweden',
                'DK': 'Denmark',
                'NO': 'Norway',
                'FI': 'Finland'
            }
            
            if country_code in country_mapping:
                country_holidays = holidays.country_holidays(country_mapping[country_code])
            else:
                # Default to no holidays for unknown countries
                country_holidays = set()
        except:
            # Fallback to no holidays if library fails
            country_holidays = set()
    
    # Generate all business days in the range
    business_days = []
    current = start_date
    while current <= end_date:
        # Monday = 0, Sunday = 6
        if current.weekday() < 5 and current not in country_holidays:  # Monday to Friday, not a holiday
            business_days.append(current)
        current += timedelta(days=1)
    
    timeline = []
    
    for current_date in business_days:
        daily_positions = []
        total_position = 0.0
        
        for manager_name, positions in manager_positions.items():
            # Find the most recent position as of current_date
            active_position = None
            for pos in positions:
                if pos['date'].date() <= current_date:
                    active_position = pos
                else:
                    break
            
            # Include manager if their most recent position is ≥ 0.5%
            if active_position and active_position['position_size'] >= ACTIVE_THRESHOLD:
                daily_positions.append({
                    "manager_name": manager_name,
                    "position_size": active_position['position_size']
                })
                total_position += active_position['position_size']
        
        # Add entry for every business day, even if no positions (will show 0)
        timeline.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "total_position": total_position,
            "manager_positions": daily_positions
        })
    
    return timeline


def _get_country_code(db: Session, country_id: int) -> Optional[str]:
    row = db.query(Country.code).filter(Country.id == country_id).first()
    return row.code if row else None


# COMMENTED OUT - See ANALYTICS_REFACTORING.md for details
# This function was causing incorrect company ordering by not using is_active=True filter
# Replaced with unified active_positions_subq for all countries
"""
def latest_snapshot_subq(
    db: Session,
    as_of: Optional[datetime] = None,
    country_id: Optional[int] = None,
    threshold: float = ACTIVE_THRESHOLD,
):
    NON-GB snapshot:
    One row per (manager, company, country): the LATEST disclosure up to 'as_of' (inclusive),
    kept only if that latest disclosure is >= threshold.
    sp = ShortPosition

    rn = func.row_number().over(
        partition_by=(sp.manager_id, sp.company_id, sp.country_id),
        order_by=(sp.date.desc(), sp.id.desc()),
    )

    q = db.query(
        sp.id.label("sp_id"),
        sp.company_id.label("company_id"),
        sp.manager_id.label("manager_id"),
        sp.country_id.label("country_id"),
        sp.position_size.label("position_size"),
        sp.date.label("date"),
        rn.label("rn"),
    )

    if as_of is not None:
        q = q.filter(sp.date <= as_of)
    if country_id is not None:
        q = q.filter(sp.country_id == country_id)

    ranked = q.subquery("sp_ranked")

    snap = db.query(
        ranked.c.sp_id,
        ranked.c.company_id,
        ranked.c.manager_id,
        ranked.c.country_id,
        ranked.c.position_size,
        ranked.c.date,
    ).filter(
        and_(
            ranked.c.rn == 1,
            ranked.c.position_size >= threshold,
        )
    ).subquery("active_latest_snapshot")

    return snap
"""


def active_positions_subq(
    db: Session,
    as_of: Optional[datetime] = None,
    country_id: Optional[int] = None,
):
    """
    Get active positions for ALL countries:
    Use rows flagged in DB with is_active = True.
    This is now used for all countries (GB and non-GB) for consistent logic.
    Optionally limit by country_id/as_of.
    """
    sp = ShortPosition
    q = db.query(
        sp.id.label("sp_id"),
        sp.company_id.label("company_id"),
        sp.manager_id.label("manager_id"),
        sp.country_id.label("country_id"),
        sp.position_size.label("position_size"),
        sp.date.label("date"),
    ).filter(sp.is_active == True)

    if country_id is not None:
        q = q.filter(sp.country_id == country_id)
    if as_of is not None:
        q = q.filter(sp.date <= as_of)

    return q.subquery("active_positions")


# -------------------------------
# Country analytics
# -------------------------------
async def get_country_analytics(db: Session, country_id: int) -> Dict[str, Any]:
    """Get comprehensive analytics for a country using unified is_active=True logic for all countries."""
    latest_date = db.query(func.max(ShortPosition.date)).filter(
        ShortPosition.country_id == country_id
    ).scalar()

    if not latest_date:
        return {"error": "No data available for this country"}

    most_shorted = await get_most_shorted_companies(db, country_id, latest_date)
    top_managers = await get_top_managers(db, country_id, latest_date)

    # Use unified logic for all countries - just count active positions
    total_active = db.query(func.count("*")).select_from(
        active_positions_subq(db, country_id=country_id)
    ).scalar()

    return {
        "latest_date": latest_date,
        "most_shorted_companies": most_shorted,
        "top_managers": top_managers,
        "total_active_positions": total_active,
    }


# -------------------------------
# Most shorted companies (by country)
# -------------------------------
async def get_most_shorted_companies(
    db: Session, country_id: int, date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Rank companies by sum of CURRENT active short positions in a country.
    Uses unified is_active=True logic for all countries.
    """
    # Get country code to check if it's Ireland
    country = db.query(Country).filter(Country.id == country_id).first()
    is_ireland = country and country.code == 'IE'
    
    if is_ireland:
        # COMPLETE REWRITE FOR IRELAND: Direct query bypassing active_positions_subq
        print(f"🔍 Using COMPLETE REWRITE for Ireland (country_id: {country_id})")
        
        # Direct query for Ireland - ONLY get companies with is_active=True positions
        companies_now = db.query(
            Company.id.label("company_id"),
            Company.name.label("company_name"),
            func.sum(ShortPosition.position_size).label("total_short_exposure"),
            func.avg(ShortPosition.position_size).label("average_position_size"),
            func.count(ShortPosition.id).label("position_count"),
            func.max(ShortPosition.date).label("most_recent_position_date"),
        ).join(
            ShortPosition, ShortPosition.company_id == Company.id
        ).filter(
            and_(
                ShortPosition.country_id == country_id,
                ShortPosition.is_active == True
            )
        ).group_by(
            Company.id, Company.name
        ).all()
        
        print(f"🔍 Ireland DIRECT query returned {len(companies_now)} companies")
        for comp in companies_now:
            print(f"  - {comp.company_name}: {comp.total_short_exposure}% ({comp.position_count} positions)")
        
        # Previous week active positions for comparison
        one_week_ago = datetime.now() - timedelta(days=7)
        companies_prev = db.query(
            Company.id.label("company_id"),
            func.sum(ShortPosition.position_size).label("previous_total"),
        ).join(
            ShortPosition, ShortPosition.company_id == Company.id
        ).filter(
            and_(
                ShortPosition.country_id == country_id,
                ShortPosition.is_active == True,
                ShortPosition.date <= one_week_ago
            )
        ).group_by(
            Company.id
        ).all()

        prev_map = {row.company_id: float(row.previous_total or 0.0) for row in companies_prev}
    else:
        # Standard logic for other countries
        # Current active positions for this country
        active_now = active_positions_subq(db, country_id=country_id)
        companies_now = db.query(
            Company.id.label("company_id"),
            Company.name.label("company_name"),
            func.sum(active_now.c.position_size).label("total_short_exposure"),
            func.avg(active_now.c.position_size).label("average_position_size"),
            func.count(active_now.c.sp_id).label("position_count"),
            func.max(active_now.c.date).label("most_recent_position_date"),
        ).join(
            active_now, active_now.c.company_id == Company.id
        ).group_by(
            Company.id, Company.name
        ).all()

        # Previous week active positions for comparison
        one_week_ago = datetime.now() - timedelta(days=7)
        active_prev = active_positions_subq(db, as_of=one_week_ago, country_id=country_id)
        companies_prev = db.query(
            Company.id.label("company_id"),
            func.sum(active_prev.c.position_size).label("previous_total"),
        ).join(
            active_prev, active_prev.c.company_id == Company.id
        ).group_by(
            Company.id
        ).all()

        prev_map = {row.company_id: float(row.previous_total or 0.0) for row in companies_prev}

    results: List[Dict[str, Any]] = []
    for row in companies_now:
        current_total = float(row.total_short_exposure or 0.0)
        previous_total = prev_map.get(row.company_id, 0.0)
        results.append({
            "company_name": row.company_name,
            "company_id": row.company_id,
            "total_short_positions": current_total,
            "average_position_size": float(row.average_position_size or 0.0),
            "position_count": int(row.position_count or 0),
            "week_delta": current_total - previous_total,
            "most_recent_position_date": row.most_recent_position_date,
        })

    results.sort(key=lambda x: x["total_short_positions"], reverse=True)
    return results[:10]


# -------------------------------
# Top managers (by country)
# -------------------------------
async def get_top_managers(
    db: Session, country_id: int, date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Top managers by sum of CURRENT active positions using unified logic."""
    # Use unified active positions logic for all countries
    active_snap = active_positions_subq(db, country_id=country_id)

    rows = db.query(
        Manager.name,
        Manager.slug,
        func.sum(active_snap.c.position_size).label("total_exposure"),
        func.count(active_snap.c.sp_id).label("active_positions"),
    ).join(
        active_snap, active_snap.c.manager_id == Manager.id
    ).group_by(
        Manager.id, Manager.name, Manager.slug
    ).order_by(
        desc("total_exposure")
    ).limit(10).all()

    return [
        {
            "name": r.name,
            "slug": r.slug,
            "active_positions": int(r.active_positions or 0),
            "total_exposure": float(r.total_exposure or 0.0),
        }
        for r in rows
    ]


# -------------------------------
# Global top companies
# -------------------------------
async def get_global_top_companies(db: Session) -> List[Dict[str, Any]]:
    """
    Global ranking: Use unified active positions logic for all countries
    """
    # Get all countries to process each separately 
    countries = db.query(Country.id, Country.code).all()
    
    all_companies = {}
    
    for country_id, country_code in countries:
        # Use unified active positions logic for all countries
        active_snap = active_positions_subq(db, country_id=country_id)
        companies = db.query(
            Company.id.label("company_id"),
            Company.name.label("company_name"),
            func.sum(active_snap.c.position_size).label("total_short_exposure"),
            func.count(active_snap.c.sp_id).label("position_count"),
            func.max(active_snap.c.date).label("most_recent_position_date"),
        ).join(
            active_snap, active_snap.c.company_id == Company.id
        ).group_by(
            Company.id, Company.name
        ).all()
        
        # Aggregate results across countries
        for company in companies:
            key = company.company_id
            if key not in all_companies:
                all_companies[key] = {
                    "company_id": company.company_id,
                    "company_name": company.company_name,
                    "total_short_exposure": float(company.total_short_exposure or 0.0),
                    "position_count": int(company.position_count or 0),
                    "most_recent_position_date": company.most_recent_position_date,
                }
            else:
                all_companies[key]["total_short_exposure"] += float(company.total_short_exposure or 0.0)
                all_companies[key]["position_count"] += int(company.position_count or 0)
                # Keep the most recent date across all countries for this company
                if company.most_recent_position_date and (
                    not all_companies[key]["most_recent_position_date"] or 
                    company.most_recent_position_date > all_companies[key]["most_recent_position_date"]
                ):
                    all_companies[key]["most_recent_position_date"] = company.most_recent_position_date
    
    current_companies = list(all_companies.values())

    # Previous week: Same unified logic but as of one week ago
    one_week_ago = datetime.now() - timedelta(days=7)
    all_companies_prev = {}
    
    for country_id, country_code in countries:
        # Use unified active positions logic as of one week ago
        active_snap_prev = active_positions_subq(db, as_of=one_week_ago, country_id=country_id)
        companies_prev = db.query(
            Company.id.label("company_id"),
            func.sum(active_snap_prev.c.position_size).label("total_short_exposure"),
        ).join(
            active_snap_prev, active_snap_prev.c.company_id == Company.id
        ).group_by(
            Company.id
        ).all()
        
        # Aggregate previous week results
        for company in companies_prev:
            key = company.company_id
            if key not in all_companies_prev:
                all_companies_prev[key] = float(company.total_short_exposure or 0.0)
            else:
                all_companies_prev[key] += float(company.total_short_exposure or 0.0)

    # Build previous week map (already aggregated)
    prev_map: Dict[int, float] = all_companies_prev

    # Build results
    results: List[Dict[str, Any]] = []
    for company in current_companies:
        previous_total = prev_map.get(company["company_id"], 0.0)
        results.append({
            "company_name": company["company_name"],
            "company_id": company["company_id"],
            "total_short_positions": company["total_short_exposure"],
            "average_position_size": company["total_short_exposure"] / max(company["position_count"], 1),
            "position_count": company["position_count"],
            "week_delta": company["total_short_exposure"] - previous_total,
            "most_recent_position_date": company["most_recent_position_date"],
        })

    results.sort(key=lambda x: x["total_short_positions"], reverse=True)
    return results[:10]


# -------------------------------
# Global top managers
# -------------------------------
async def get_global_top_managers(db: Session) -> List[Dict[str, Any]]:
    """
    Global managers: Use unified active positions logic for all countries
    """
    # Use unified active positions logic across all countries
    active_snap = active_positions_subq(db, country_id=None)
    rows = db.query(
        Manager.name,
        Manager.slug,
        func.sum(active_snap.c.position_size).label("total_exposure"),
        func.count(active_snap.c.sp_id).label("active_positions"),
    ).join(
        active_snap, active_snap.c.manager_id == Manager.id
    ).group_by(
        Manager.id, Manager.name, Manager.slug
    ).order_by(
        func.count(active_snap.c.sp_id).desc()  # Order by active positions count
    ).limit(10).all()

    return [
        {
            "name": r.name,
            "slug": r.slug,
            "active_positions": int(r.active_positions or 0),
            "total_exposure": float(r.total_exposure or 0.0),
        }
        for r in rows
    ]


# -------------------------------
# Company & Manager analytics (kept simple)
# -------------------------------
async def get_company_analytics(db: Session, company_id: int, timeframe: str = "3m") -> Dict[str, Any]:
    """
    Get company analytics with positions over time for frontend consumption
    """
    # First get company info
    company_row = db.query(
        Company.id,
        Company.name,
        Company.isin,
        Country.code,
        Country.name.label("country_name"),
        Country.flag
    ).join(
        Country, Country.id == Company.country_id
    ).filter(
        Company.id == company_id
    ).first()
    
    if not company_row:
        raise ValueError(f"Company with ID {company_id} not found")
    
    # Parse timeframe to get date range
    timeframe_map = {
        "1w": 7,
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365
    }
    days = timeframe_map.get(timeframe.lower(), 90)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get ALL positions for this company (not just within timeframe) to reconstruct active state
    # Apply data integrity filters to exclude invalid active positions
    query = db.query(
        ShortPosition.date,
        ShortPosition.position_size,
        Manager.name.label("manager_name")
    ).join(
        Manager, Manager.id == ShortPosition.manager_id
    ).filter(
        ShortPosition.company_id == company_id
    )

    # For France, exclude positions older than 2 years (data integrity protection)
    if company_row.code == "FR":
        date_barrier = datetime.now() - timedelta(days=730)  # 2 years ago
        query = query.filter(
            ShortPosition.date >= date_barrier  # Only recent positions
        )
    else:
        # For non-France countries, still apply the 2-year date barrier for data integrity
        date_barrier = datetime.now() - timedelta(days=730)  # 2 years ago
        query = query.filter(ShortPosition.date >= date_barrier)

    all_positions = query.order_by(
        Manager.id, ShortPosition.date
    ).all()
    
    # Reconstruct active positions timeline
    positions_over_time = reconstruct_active_positions_timeline(
        all_positions, cutoff_date, timeframe_map.get(timeframe.lower(), 90), company_row.code
    )
    
    return {
        "company": {
            "id": company_row.id,
            "name": company_row.name,
            "isin_code": company_row.isin,
            "country": {
                "code": company_row.code,
                "name": company_row.country_name,
                "flag": company_row.flag
            }
        },
        "positions_over_time": positions_over_time
    }


async def get_company_analytics_by_name(db: Session, company_name: str, timeframe: str = "3m") -> Dict[str, Any]:
    """
    Get company analytics by company name (case-insensitive)
    """
    # Find company by name (case-insensitive)
    company_row = db.query(Company.id).filter(
        func.upper(Company.name) == func.upper(company_name)
    ).first()
    
    if not company_row:
        raise ValueError(f"Company '{company_name}' not found")
    
    # Use the existing function with the company ID
    return await get_company_analytics(db, company_row.id, timeframe)


async def get_manager_analytics_by_slug(db: Session, manager_slug: str, timeframe: str = "3m") -> Dict[str, Any]:
    """
    Get manager analytics by manager slug
    """
    # Find manager by slug
    manager = db.query(Manager).filter(Manager.slug == manager_slug).first()
    
    if not manager:
        raise ValueError(f"Manager with slug '{manager_slug}' not found")
    
    return await get_manager_analytics(db, manager.id, timeframe)


async def get_manager_analytics(db: Session, manager_id: int, timeframe: str = "3m") -> Dict[str, Any]:
    """
    Get comprehensive manager analytics with active and historical positions by country
    """
    # Get manager info
    manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not manager:
        raise ValueError(f"Manager with ID {manager_id} not found")
    
    # Parse timeframe
    timeframe_map = {
        "1w": 7,
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365
    }
    days = timeframe_map.get(timeframe.lower(), 90)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get all positions for this manager to determine current active and historical
    all_positions = db.query(
        ShortPosition.id,
        ShortPosition.date,
        ShortPosition.position_size,
        Company.name.label("company_name"),
        Company.id.label("company_id"),
        Country.name.label("country_name"),
        Country.flag.label("country_flag"),
        Country.code.label("country_code")
    ).join(
        Company, Company.id == ShortPosition.company_id
    ).join(
        Country, Country.id == Company.country_id
    ).filter(
        ShortPosition.manager_id == manager_id
    ).order_by(
        Company.id, ShortPosition.date.desc()
    ).all()
    
    # Group positions by company to determine current state
    from collections import defaultdict
    positions_by_company = defaultdict(list)
    for pos in all_positions:
        positions_by_company[pos.company_id].append(pos)
    
    current_active_positions = []
    historical_positions = []
    
    for company_id, company_positions in positions_by_company.items():
        # Sort by date descending (most recent first)
        company_positions.sort(key=lambda x: x.date, reverse=True)
        
        # Get the most recent position for this company
        most_recent = company_positions[0]
        
        if most_recent.position_size >= ACTIVE_THRESHOLD:
            # Currently active
            current_active_positions.append({
                "company_name": most_recent.company_name,
                "country_name": most_recent.country_name,
                "country_flag": most_recent.country_flag,
                "country_code": most_recent.country_code,
                "position_size": float(most_recent.position_size),
                "disclosure_date": most_recent.date.strftime("%Y-%m-%d")
            })
        
        # Add historical positions (positions that were active but are now inactive or closed)
        for i, pos in enumerate(company_positions):
            # Skip the current active position
            if i == 0 and pos.position_size >= ACTIVE_THRESHOLD:
                continue
            
            # Add positions that were once active
            if pos.position_size >= ACTIVE_THRESHOLD:
                # Find when this position ended (next position date or now)
                exit_date = company_positions[i-1].date if i > 0 else datetime.now().date()
                
                historical_positions.append({
                    "company_name": pos.company_name,
                    "country_name": pos.country_name,
                    "country_flag": pos.country_flag,
                    "country_code": pos.country_code,
                    "position_size": float(pos.position_size),
                    "disclosure_date": pos.date.strftime("%Y-%m-%d"),
                    "exit_date": exit_date.strftime("%Y-%m-%d")
                })
    
    # Sort historical positions by exit date (most recent first)
    historical_positions.sort(key=lambda x: x["exit_date"], reverse=True)
    
    # Get all unique countries from both active and historical positions
    all_countries = set()
    for pos in current_active_positions:
        all_countries.add(pos["country_name"])
    for pos in historical_positions:
        all_countries.add(pos["country_name"])
    
    countries_list = sorted(list(all_countries))
    
    return {
        "manager": {
            "id": manager.id,
            "name": manager.name,
            "slug": manager.slug
        },
        "current_active_positions": current_active_positions,
        "historical_positions": historical_positions[:50],  # Increased limit
        "countries": countries_list  # List of all countries for filtering
    }


# -------------------------------
# Cache helpers
# -------------------------------
def get_cached_analytics(cache_key: str, db: Session) -> Optional[Dict[str, Any]]:
    cache_entry = db.query(AnalyticsCache).filter(
        AnalyticsCache.cache_key == cache_key
    ).first()
    if cache_entry and cache_entry.expires_at > datetime.now():
        return json.loads(cache_entry.cache_data)
    return None


def set_cached_analytics(cache_key: str, data: Dict[str, Any], db: Session, ttl_hours: int = 24):
    db.query(AnalyticsCache).filter(
        AnalyticsCache.cache_key == cache_key
    ).delete()
    cache_entry = AnalyticsCache(
        cache_key=cache_key,
        cache_data=json.dumps(data),
        expires_at=datetime.now() + timedelta(hours=ttl_hours),
    )
    db.add(cache_entry)
    db.commit()


# -------------------------------
# Global Analytics Dashboard
# -------------------------------
async def get_global_analytics(db: Session, timeframe: str = "3m") -> Dict[str, Any]:
    """
    Get global analytics dashboard data including:
    - Summary statistics
    - Top countries by active positions
    - Top managers by active positions (ranked by position count, not value)
    - Positions trend over time
    """
    # Parse timeframe
    timeframe_map = {
        "1w": 7,
        "1m": 30, 
        "3m": 90,
        "6m": 180,
        "1y": 365
    }
    days = timeframe_map.get(timeframe.lower(), 90)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Summary statistics using active positions only
    total_active_positions = db.query(func.count(ShortPosition.id)).filter(
        and_(
            ShortPosition.date >= cutoff_date,
            ShortPosition.is_active == True
        )
    ).scalar() or 0
    
    total_countries = db.query(func.count(func.distinct(Country.id))).join(
        Company, Company.country_id == Country.id
    ).join(
        ShortPosition, ShortPosition.company_id == Company.id
    ).filter(
        and_(
            ShortPosition.date >= cutoff_date,
            ShortPosition.is_active == True
        )
    ).scalar() or 0
    
    total_companies = db.query(func.count(func.distinct(Company.id))).join(
        ShortPosition, ShortPosition.company_id == Company.id
    ).filter(
        and_(
            ShortPosition.date >= cutoff_date,
            ShortPosition.is_active == True
        )
    ).scalar() or 0
    
    total_managers = db.query(func.count(func.distinct(Manager.id))).join(
        ShortPosition, ShortPosition.manager_id == Manager.id
    ).filter(
        and_(
            ShortPosition.date >= cutoff_date,
            ShortPosition.is_active == True
        )
    ).scalar() or 0
    
    latest_data_date = db.query(func.max(ShortPosition.date)).scalar()
    
    # Get top countries by active positions count
    top_countries = db.query(
        Country.name.label("country_name"),
        Country.flag.label("country_flag"),
        func.count(ShortPosition.id).label("active_positions"),
        func.sum(ShortPosition.position_size).label("total_value")
    ).join(
        Company, Company.country_id == Country.id
    ).join(
        ShortPosition, ShortPosition.company_id == Company.id
    ).filter(
        and_(
            ShortPosition.date >= cutoff_date,
            ShortPosition.is_active == True
        )
    ).group_by(
        Country.id, Country.name, Country.flag
    ).order_by(
        func.count(ShortPosition.id).desc()
    ).limit(10).all()
    
    # Get top managers by active positions count using unified logic
    active_snap = active_positions_subq(db, country_id=None)
    manager_rows = db.query(
        Manager.name,
        Manager.slug,
        func.sum(active_snap.c.position_size).label("total_value"),
        func.count(active_snap.c.sp_id).label("active_positions"),
    ).join(
        active_snap, active_snap.c.manager_id == Manager.id
    ).group_by(
        Manager.id, Manager.name, Manager.slug
    ).order_by(
        func.count(active_snap.c.sp_id).desc()  # Order by active positions count
    ).limit(10).all()

    top_managers = [
        {
            "manager_name": row.name,
            "active_positions": int(row.active_positions or 0),
            "total_value": float(row.total_value or 0.0),
        }
        for row in manager_rows
    ]
    
    # Get positions trend over time using active positions only
    positions_trend = db.query(
        func.date(ShortPosition.date).label("date"),
        func.count(ShortPosition.id).label("active_positions"),
        func.sum(ShortPosition.position_size).label("total_value")
    ).filter(
        and_(
            ShortPosition.date >= cutoff_date,
            ShortPosition.is_active == True
        )
    ).group_by(
        func.date(ShortPosition.date)
    ).order_by(
        func.date(ShortPosition.date)
    ).all()
    
    return {
        "total_active_positions": total_active_positions,
        "total_countries": total_countries,
        "total_companies": total_companies,
        "total_managers": total_managers,
        "latest_data_date": latest_data_date.isoformat() if latest_data_date else None,
        "top_countries": [
            {
                "country_name": row.country_name,
                "country_flag": row.country_flag,
                "active_positions": row.active_positions,
                "total_value": float(row.total_value or 0)
            }
            for row in top_countries
        ],
        "top_managers": top_managers[:10],  # Top 10 managers by position count
        "positions_trend": [
            {
                "date": row.date.strftime("%Y-%m-%d"),
                "active_positions": row.active_positions,
                "total_value": float(row.total_value or 0)
            }
            for row in positions_trend
        ]
    }
