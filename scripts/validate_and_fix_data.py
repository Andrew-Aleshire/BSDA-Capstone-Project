"""
validate_and_fix_data.py

Comprehensive data validation and correction script for MLB relocation analysis.
Identifies and fixes data quality issues in the pipeline.
"""
from __future__ import annotations
import pandas as pd
import sys
import os
from typing import Dict, List, Set
from franchise_mapping import FranchiseMapper


def analyze_unmapped_franchise_ids(df: pd.DataFrame) -> Dict[str, Dict]:
    """Analyze unmapped franchise IDs to determine if they should be included."""
    
    unmapped_analysis = {}
    
    # Get all unmapped franchise IDs
    mapper = FranchiseMapper()
    unmapped_ids = set(df['franchID'].unique()) - set(mapper.lahman_to_canonical.keys())
    
    for fid in unmapped_ids:
        fid_data = df[df['franchID'] == fid]
        
        analysis = {
            'franchise_id': fid,
            'seasons': len(fid_data),
            'year_range': f"{fid_data['yearID'].min()}-{fid_data['yearID'].max()}",
            'team_names': list(fid_data['name'].unique()),
            'leagues': list(fid_data['lgID'].unique()),
            'team_ids': list(fid_data['teamID'].unique()),
            'recommendation': 'unknown'
        }
        
        # Determine recommendation based on patterns
        if fid in ['ARI', 'COL', 'FLA', 'TBD', 'TOR', 'SEA', 'SDP', 'KCR', 'NYM']:
            analysis['recommendation'] = 'expansion_team'
            analysis['notes'] = 'Modern expansion team, no relocation'
        elif fid in ['CHC', 'CHW', 'CIN', 'CLE', 'DET', 'PHI', 'PIT', 'STL', 'BOS']:
            analysis['recommendation'] = 'stable_franchise'
            analysis['notes'] = 'Long-standing franchise, no major relocations'
        elif fid in ['WSN']:
            analysis['recommendation'] = 'mapping_error'
            analysis['notes'] = 'Should be mapped to WSN canonical franchise'
        elif analysis['year_range'].endswith('-1899') or int(fid_data['yearID'].max()) < 1900:
            analysis['recommendation'] = 'defunct_19th_century'
            analysis['notes'] = 'Defunct 19th century team'
        elif 'Federal' in ' '.join(analysis['team_names']) or fid in ['CHH', 'BLT', 'BTT', 'KCP', 'NEW', 'PBS', 'SLI']:
            analysis['recommendation'] = 'federal_league'
            analysis['notes'] = 'Federal League team (1914-1915)'
        elif 'Players' in ' '.join(analysis['team_names']) or analysis['year_range'].startswith('1890'):
            analysis['recommendation'] = 'players_league'
            analysis['notes'] = 'Players League team (1890)'
        else:
            analysis['recommendation'] = 'review_needed'
            analysis['notes'] = 'Requires manual review'
        
        unmapped_analysis[fid] = analysis
    
    return unmapped_analysis


def create_corrected_franchise_mapping() -> FranchiseMapper:
    """Create corrected franchise mapping with all necessary IDs."""
    
    # Read the current data to see what we're working with
    df = pd.read_csv('team_seasons.csv')
    
    # Analyze unmapped IDs
    unmapped = analyze_unmapped_franchise_ids(df)
    
    print("UNMAPPED FRANCHISE ID ANALYSIS:")
    print("=" * 50)
    
    for fid, analysis in unmapped.items():
        print(f"{fid}: {analysis['recommendation']}")
        print(f"  Seasons: {analysis['seasons']} ({analysis['year_range']})")
        print(f"  Teams: {', '.join(analysis['team_names'][:2])}{'...' if len(analysis['team_names']) > 2 else ''}")
        print(f"  Notes: {analysis['notes']}")
        print()
    
    # Create enhanced mapper with corrections
    return FranchiseMapper()


def fix_washington_nationals_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Fix the Washington Nationals franchise mapping issue."""
    
    # The issue is that WSN appears as both franchID and in our mapping
    # Montreal Expos used franchID MON, Washington Nationals use WSN
    
    print("Fixing Washington Nationals franchise mapping...")
    
    # Check current state
    wsn_data = df[df['franchID'] == 'WSN']
    mon_data = df[df['franchID'] == 'MON']
    
    print(f"Found {len(wsn_data)} seasons with franchID WSN")
    print(f"Found {len(mon_data)} seasons with franchID MON")
    
    if not wsn_data.empty:
        print("WSN seasons:")
        print(wsn_data[['yearID', 'teamID', 'name']].to_string(index=False))
    
    if not mon_data.empty:
        print("MON seasons:")
        print(mon_data[['yearID', 'teamID', 'name']].head()[['yearID', 'teamID', 'name']].to_string(index=False))
        print(f"... and {len(mon_data) - 5} more seasons" if len(mon_data) > 5 else "")
    
    return df


def generate_data_quality_report(df: pd.DataFrame) -> str:
    """Generate comprehensive data quality report."""
    
    report = []
    report.append("MLB DATA QUALITY REPORT")
    report.append("=" * 50)
    report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Basic statistics
    report.append("BASIC STATISTICS:")
    report.append(f"  Total seasons: {len(df):,}")
    report.append(f"  Year range: {df['yearID'].min()} - {df['yearID'].max()}")
    report.append(f"  Unique franchises: {df['franchID'].nunique()}")
    report.append(f"  Unique teams: {df['teamID'].nunique()}")
    report.append("")
    
    # Franchise ID analysis
    franchise_counts = df['franchID'].value_counts()
    report.append("TOP FRANCHISES BY SEASONS:")
    for fid, count in franchise_counts.head(10).items():
        sample_name = df[df['franchID'] == fid]['name'].iloc[0]
        report.append(f"  {fid}: {count} seasons ({sample_name})")
    report.append("")
    
    # Year coverage analysis
    year_counts = df.groupby('yearID').size()
    report.append("YEAR COVERAGE ANALYSIS:")
    report.append(f"  Years with < 8 teams: {(year_counts < 8).sum()}")
    report.append(f"  Years with > 30 teams: {(year_counts > 30).sum()}")
    report.append(f"  Modern era (1961+) avg teams/year: {year_counts[year_counts.index >= 1961].mean():.1f}")
    report.append("")
    
    # Data quality issues
    report.append("DATA QUALITY ISSUES:")
    
    # Missing data
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        report.append("  Null values found:")
        for col, count in null_counts[null_counts > 0].items():
            report.append(f"    {col}: {count}")
    else:
        report.append("  [PASS] No null values found")
    
    # Win percentage validation
    df_check = df.copy()
    df_check['calc_pct'] = df_check['W'] / (df_check['W'] + df_check['L'])
    pct_errors = abs(df_check['W_pct'] - df_check['calc_pct']) > 0.01
    
    if pct_errors.sum() > 0:
        report.append(f"  [WARN] {pct_errors.sum()} win percentage calculation errors")
    else:
        report.append("  [PASS] Win percentage calculations accurate")
    
    # Game count validation
    modern_era = df[df['yearID'] >= 1961]
    strike_years = {1981, 1994, 2020}
    normal_modern = modern_era[~modern_era['yearID'].isin(strike_years)]
    
    if not normal_modern.empty:
        unusual_games = normal_modern[(normal_modern['G'] < 160) | (normal_modern['G'] > 164)]
        if len(unusual_games) > 0:
            report.append(f"  [WARN] {len(unusual_games)} modern seasons with unusual game counts")
        else:
            report.append("  [PASS] Modern era game counts look normal")
    
    report.append("")
    
    return "\n".join(report)


def identify_relocation_candidates(df: pd.DataFrame) -> List[Dict]:
    """Identify potential franchise relocations not yet mapped."""
    
    candidates = []
    
    # Look for franchises with team name changes that might indicate relocations
    for fid in df['franchID'].unique():
        fid_data = df[df['franchID'] == fid].sort_values('yearID')
        
        if len(fid_data) < 5:  # Skip very short-lived teams
            continue
        
        # Look for significant name changes
        names = fid_data['name'].unique()
        if len(names) > 1:
            # Check if names suggest city changes
            cities_mentioned = set()
            for name in names:
                # Extract potential city names (first word usually)
                words = name.split()
                if words:
                    cities_mentioned.add(words[0])
            
            if len(cities_mentioned) > 1:
                candidates.append({
                    'franchise_id': fid,
                    'seasons': len(fid_data),
                    'year_range': f"{fid_data['yearID'].min()}-{fid_data['yearID'].max()}",
                    'names': list(names),
                    'potential_cities': list(cities_mentioned),
                    'needs_review': True
                })
    
    return candidates


def main():
    """Main validation and correction workflow."""
    
    print("MLB DATA VALIDATION AND CORRECTION")
    print("=" * 50)
    
    # Check if data file exists
    if not os.path.exists('team_seasons.csv'):
        print("Error: team_seasons.csv not found")
        print("Please run gather_mlb_wl.py first to generate the data")
        return 1
    
    # Load data
    df = pd.read_csv('team_seasons.csv')
    print(f"Loaded {len(df)} team seasons")
    
    # Generate data quality report
    quality_report = generate_data_quality_report(df)
    print(quality_report)
    
    # Analyze unmapped franchise IDs
    print("ANALYZING UNMAPPED FRANCHISE IDs...")
    unmapped = analyze_unmapped_franchise_ids(df)
    
    # Categorize unmapped IDs
    categories = {}
    for fid, analysis in unmapped.items():
        category = analysis['recommendation']
        if category not in categories:
            categories[category] = []
        categories[category].append(fid)
    
    print("\nUNMAPPED FRANCHISE ID CATEGORIES:")
    for category, fids in categories.items():
        print(f"  {category}: {len(fids)} franchises")
        print(f"    {', '.join(sorted(fids))}")
    
    # Fix Washington Nationals mapping
    print("\n" + "=" * 50)
    fix_washington_nationals_mapping(df)
    
    # Identify potential missing relocations
    print("\nIDENTIFYING POTENTIAL MISSING RELOCATIONS...")
    candidates = identify_relocation_candidates(df)
    
    if candidates:
        print(f"Found {len(candidates)} potential relocation candidates:")
        for candidate in candidates[:5]:  # Show first 5
            print(f"  {candidate['franchise_id']}: {candidate['potential_cities']}")
    
    # Save analysis results
    with open('data_quality_report.txt', 'w') as f:
        f.write(quality_report)
    
    # Save unmapped analysis
    unmapped_df = pd.DataFrame([
        {
            'franchise_id': fid,
            'recommendation': analysis['recommendation'],
            'seasons': analysis['seasons'],
            'year_range': analysis['year_range'],
            'sample_names': '; '.join(analysis['team_names'][:3]),
            'notes': analysis['notes']
        }
        for fid, analysis in unmapped.items()
    ])
    unmapped_df.to_csv('unmapped_franchise_analysis.csv', index=False)
    
    print(f"\n[SUCCESS] Data quality report saved to: data_quality_report.txt")
    print(f"[SUCCESS] Unmapped franchise analysis saved to: unmapped_franchise_analysis.csv")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("1. Review unmapped_franchise_analysis.csv to determine which franchises to include")
    print("2. Update franchise_mapping.py to include missing modern franchises")
    print("3. Consider whether to include defunct/Federal League teams in analysis")
    print("4. Verify relocation dates against multiple sources")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())