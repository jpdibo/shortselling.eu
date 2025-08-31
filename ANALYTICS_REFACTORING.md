# Analytics Refactoring - Active Positions Fix

**Date**: 2025-08-30  
**Issue**: Companies were not being ordered correctly by active positions in the frontend left-hand table  
**Root Cause**: The `latest_snapshot_subq` function was not properly using the `is_active=True` column from the database  

## Problem Description

The frontend main page and country pages show companies ordered by "sum of active positions" in the left-hand side table. However, the logic was using `latest_snapshot_subq` function which implemented complex snapshot logic instead of simply filtering for positions where `is_active=True` in the database.

## Functions Affected by `latest_snapshot_subq`

The following functions were using `latest_snapshot_subq` for non-GB countries:

### Country-Level Analytics
1. **`get_country_analytics`** (line 206)
   - Used for country analytics pages
   - Affects company ordering in country-specific tables

2. **`get_most_shorted_companies`** (lines 259, 273)
   - Used for "Most Shorted Companies" tables on country pages
   - **This is the main issue** - companies not ordered by actual active positions

3. **`get_top_managers`** (line 314)
   - Used for "Top Managers" rankings on country pages
   - Affects manager rankings by active positions count

### Global Analytics
4. **`get_global_top_companies`** (lines 368, 414)
   - Used for global company rankings
   - Affects homepage "Most Shorted Companies" table

5. **`get_global_top_managers`** (line 463)
   - Used for global manager rankings
   - Affects homepage "Managers with Most Active Positions" table

6. **`get_global_analytics`** (line 825)
   - Used for analytics dashboard
   - Affects global statistics and rankings

## Solution

### Before (Complex Logic)
- **GB**: Used `gb_current_subq` with `is_active=True` filter ✅ Correct
- **Non-GB**: Used `latest_snapshot_subq` with complex snapshot logic ❌ Wrong

### After (Simplified Logic)
- **All Countries**: Use `active_positions_subq` (renamed from `gb_current_subq`) with `is_active=True` filter ✅ Correct

## Changes Made

1. **Commented Out**: `latest_snapshot_subq` function (preserved for reference)
2. **Renamed**: `gb_current_subq` → `active_positions_subq`
3. **Simplified**: Removed all country-specific branching logic
4. **Updated**: All function references to use the unified approach

## Database Column Usage

The `short_positions` table has an `is_active` column:
```sql
is_active = Column(Boolean, default=True)  # True if from current tab/file, False if from historical tab/file
```

This column correctly indicates which positions are currently active, and should be the single source of truth for all countries.

## Functions NOT Affected

The following functions use different logic and were not changed:
- `get_company_analytics` - Uses timeline reconstruction logic
- `get_manager_analytics` - Uses timeline reconstruction logic
- `reconstruct_active_positions_timeline` - Timeline-specific logic

## Expected Impact

After this change:
- Companies will be ordered by **actual active positions** (`is_active=True`)
- Consistent logic across all countries (no more GB vs non-GB distinction)
- Frontend tables will show correct rankings
- Global and country-specific analytics will use the same logic

## Testing Required

- [ ] Verify company ordering in homepage left table
- [ ] Verify company ordering in country-specific pages  
- [ ] Verify manager rankings are correct
- [ ] Verify global analytics show consistent data