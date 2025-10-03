# Data Pipeline Notes

## What This Does
Explains how I cleaned up the MLB data to properly analyze team performance before and after relocations. Had to deal with a lot of messy franchise history.

## Main Changes

### 1. Fixed Franchise Mapping
**File:** `scripts/corrected_franchise_mapping.py`

**What it does:**
- Maps all the major MLB relocations correctly
- Handles tricky cases (teams that moved multiple times, league switches)
- Removes old defunct teams from the 1800s that would mess up the analysis
- Creates consistent IDs so we can track teams across moves

**Teams that moved:**
- Atlanta Braves: Boston → Milwaukee → Atlanta
- Los Angeles Dodgers: Brooklyn → Los Angeles  
- San Francisco Giants: New York → San Francisco
- Oakland Athletics: Philadelphia → Kansas City → Oakland
- Minnesota Twins: Washington → Minnesota
- Texas Rangers: Washington → Texas
- Baltimore Orioles: St. Louis → Baltimore
- Milwaukee Brewers: Seattle → Milwaukee
- Washington Nationals: Montreal → Washington
- New York Yankees: Baltimore → New York (way back in 1903)

### 2. Data Quality Checks
**Files:** `scripts/data_validation.py`, `scripts/validate_and_fix_data.py`

**What gets checked:**
- Missing data, calculation errors
- Reasonable year ranges and game counts
- Making sure franchise histories make sense
- Cross-checking against known baseball facts

**Problems found and fixed:**
- Started with 120 franchise IDs, narrowed down to 30 that matter
- Figured out how the Lahman database IDs work
- Removed 80 old teams from the 1800s that aren't relevant
- Double-checked all the win percentage math (it's correct)

### 3. Clean Dataset
**Output:** `team_seasons_analysis_ready.csv`

**What's in it:**
- 2,836 seasons (kept 92.2% of the original data)
- 30 franchises total (10 moved, 20 stayed put or are expansion teams)
- Marked which seasons are before/after relocations
- Calculated years since each move
- Consistent franchise IDs throughout

## Ready for Analysis

### Teams with enough data (≥10 seasons before and after moving):
1. **Atlanta Braves** (moved 1966): 90 seasons before + 59 after
2. **Los Angeles Dodgers** (moved 1958): 74 before + 67 after
3. **San Francisco Giants** (moved 1958): 75 before + 67 after
4. **Oakland Athletics** (moved 1968): 67 before + 57 after
5. **Minnesota Twins** (moved 1961): 60 before + 64 after
6. **Baltimore Orioles** (moved 1954): 53 before + 71 after
7. **Texas Rangers** (moved 1972): 11 before + 53 after
8. **Washington Nationals** (moved 2005): 36 before + 20 after

### Teams without enough data:
- **Milwaukee Brewers** (moved 1970): Only 1 season before moving
- **New York Yankees** (moved 1903): Only 2 seasons before moving

## How Teams Did After Moving

| Team | Move | Before | After | Change |
|------|------|--------|-------|--------|
| Yankees | Baltimore → New York (1903) | .436 | .569 | +.133 |
| Brewers | Seattle → Milwaukee (1970) | .395 | .489 | +.094 |
| Orioles | St. Louis → Baltimore (1954) | .433 | .505 | +.073 |
| Rangers | Washington → Texas (1972) | .418 | .487 | +.069 |
| Athletics | Kansas City → Oakland (1968) | .464 | .514 | +.050 |
| Dodgers | Brooklyn → Los Angeles (1958) | .515 | .550 | +.034 |
| Twins | Washington → Minnesota (1961) | .465 | .497 | +.033 |
| Braves | Milwaukee → Atlanta (1966) | .497 | .522 | +.024 |
| Nationals | Montreal → Washington (2005) | .486 | .480 | -.006 |
| Giants | New York → San Francisco (1958) | .554 | .516 | -.038 |

## Before and After

### Started with:
- 3,075 total seasons
- 120 franchise IDs (lots of old/irrelevant teams)
- Messy franchise mapping
- No validation

### Ended up with:
- 2,836 clean seasons (kept 92.2%)
- 30 relevant franchises
- Proper franchise histories mapped out
- Full validation pipeline
- 8 out of 10 relocated teams ready for statistical analysis

## Files Created

1. **`scripts/corrected_franchise_mapping.py`** - Maps franchise histories
2. **`scripts/data_validation.py`** - Checks data quality
3. **`scripts/validate_and_fix_data.py`** - Fixes data problems
4. **`scripts/pipeline_summary.py`** - Shows pipeline status
5. **`team_seasons_analysis_ready.csv`** - Clean data for analysis
6. **`relocation_summary.csv`** - Summary of what happened to each team
7. **`data_quality_report.txt`** - Data quality notes
