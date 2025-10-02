"""
franchise_mapping.py

Master franchise mapping and validation system for MLB relocation analysis.
Provides accurate franchise lineage tracking and data validation.
"""
from __future__ import annotations
import pandas as pd
import sys
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RelocationEvent:
    """Represents a single franchise relocation event."""
    year: int
    from_city: str
    to_city: str
    from_team_name: str
    to_team_name: str
    notes: str = ""


@dataclass
class FranchiseLineage:
    """Represents the complete history of a franchise including relocations."""
    canonical_id: str
    current_name: str
    lahman_ids: List[str]  # All Lahman franchIDs/teamIDs for this lineage
    relocations: List[RelocationEvent]
    founded_year: int
    notes: str = ""


class FranchiseMapper:
    """Master franchise mapping system with validation."""
    
    def __init__(self):
        self.lineages = self._build_franchise_lineages()
        self.lahman_to_canonical = self._build_lahman_mapping()
    
    def _build_franchise_lineages(self) -> Dict[str, FranchiseLineage]:
        """Build comprehensive franchise lineage mappings."""
        
        lineages = {
            # Atlanta Braves: Boston → Milwaukee → Atlanta
            'ATL': FranchiseLineage(
                canonical_id='ATL',
                current_name='Atlanta Braves',
                lahman_ids=['BSN', 'ML1', 'ATL'],
                founded_year=1876,
                relocations=[
                    RelocationEvent(1953, 'Boston', 'Milwaukee', 'Boston Braves', 'Milwaukee Braves'),
                    RelocationEvent(1966, 'Milwaukee', 'Atlanta', 'Milwaukee Braves', 'Atlanta Braves')
                ],
                notes='Franchise moved twice: Boston (1876-1952) → Milwaukee (1953-1965) → Atlanta (1966-present)'
            ),
            
            # Los Angeles Dodgers: Brooklyn → Los Angeles  
            'LAD': FranchiseLineage(
                canonical_id='LAD',
                current_name='Los Angeles Dodgers',
                lahman_ids=['BRO', 'LAD', 'LAN'],
                founded_year=1884,
                relocations=[
                    RelocationEvent(1958, 'Brooklyn', 'Los Angeles', 'Brooklyn Dodgers', 'Los Angeles Dodgers')
                ],
                notes='Brooklyn era uses teamID BRO but franchID LAD in Lahman data'
            ),
            
            # San Francisco Giants: New York → San Francisco
            'SFG': FranchiseLineage(
                canonical_id='SFG',
                current_name='San Francisco Giants',
                lahman_ids=['NY1', 'SFN'],
                founded_year=1883,
                relocations=[
                    RelocationEvent(1958, 'New York', 'San Francisco', 'New York Giants', 'San Francisco Giants')
                ],
                notes='Same year as Dodgers move to LA'
            ),
            
            # Oakland Athletics: Philadelphia → Kansas City → Oakland
            'OAK': FranchiseLineage(
                canonical_id='OAK',
                current_name='Oakland Athletics',
                lahman_ids=['PHA', 'KC1', 'OAK'],
                founded_year=1901,
                relocations=[
                    RelocationEvent(1955, 'Philadelphia', 'Kansas City', 'Philadelphia Athletics', 'Kansas City Athletics'),
                    RelocationEvent(1968, 'Kansas City', 'Oakland', 'Kansas City Athletics', 'Oakland Athletics')
                ],
                notes='Three-city franchise with planned move to Sacramento in 2025'
            ),
            
            # Minnesota Twins: Washington → Minnesota
            'MIN': FranchiseLineage(
                canonical_id='MIN',
                current_name='Minnesota Twins',
                lahman_ids=['WS1', 'MIN'],
                founded_year=1901,
                relocations=[
                    RelocationEvent(1961, 'Washington', 'Minneapolis-St. Paul', 'Washington Senators', 'Minnesota Twins')
                ],
                notes='Original Washington Senators franchise (1901-1960)'
            ),
            
            # Texas Rangers: Washington → Texas
            'TEX': FranchiseLineage(
                canonical_id='TEX',
                current_name='Texas Rangers',
                lahman_ids=['WS2', 'TEX'],
                founded_year=1961,
                relocations=[
                    RelocationEvent(1972, 'Washington', 'Dallas-Fort Worth', 'Washington Senators', 'Texas Rangers')
                ],
                notes='Expansion Washington Senators franchise (1961-1971), different from original Senators'
            ),
            
            # Baltimore Orioles: St. Louis → Baltimore
            'BAL': FranchiseLineage(
                canonical_id='BAL',
                current_name='Baltimore Orioles',
                lahman_ids=['SLA', 'BAL'],
                founded_year=1902,
                relocations=[
                    RelocationEvent(1954, 'St. Louis', 'Baltimore', 'St. Louis Browns', 'Baltimore Orioles')
                ],
                notes='St. Louis Browns became Baltimore Orioles'
            ),
            
            # Milwaukee Brewers: Seattle → Milwaukee
            'MIL': FranchiseLineage(
                canonical_id='MIL',
                current_name='Milwaukee Brewers',
                lahman_ids=['SE1', 'ML4', 'MIL'],
                founded_year=1969,
                relocations=[
                    RelocationEvent(1970, 'Seattle', 'Milwaukee', 'Seattle Pilots', 'Milwaukee Brewers')
                ],
                notes='Seattle Pilots (1969) became Milwaukee Brewers (1970), switched from AL to NL in 1998'
            ),
            
            # Washington Nationals: Montreal → Washington
            'WSN': FranchiseLineage(
                canonical_id='WSN',
                current_name='Washington Nationals',
                lahman_ids=['MON', 'WAS'],
                founded_year=1969,
                relocations=[
                    RelocationEvent(2005, 'Montreal', 'Washington', 'Montreal Expos', 'Washington Nationals')
                ],
                notes='Montreal Expos (1969-2004) became Washington Nationals (2005-present)'
            ),
            
            # New York Yankees: Baltimore → New York (special case)
            'NYY': FranchiseLineage(
                canonical_id='NYY',
                current_name='New York Yankees',
                lahman_ids=['BLA', 'NYA'],
                founded_year=1901,
                relocations=[
                    RelocationEvent(1903, 'Baltimore', 'New York', 'Baltimore Orioles', 'New York Highlanders')
                ],
                notes='Original Baltimore Orioles (1901-1902) became NY Highlanders/Yankees. Different from modern Orioles.'
            ),
            
            # Houston Astros: League change (NL → AL in 2013)
            'HOU': FranchiseLineage(
                canonical_id='HOU',
                current_name='Houston Astros',
                lahman_ids=['HOU'],
                founded_year=1962,
                relocations=[],
                notes='No city relocation, but switched from NL to AL in 2013'
            ),
            
            # Florida/Miami Marlins: Name change only
            'FLA': FranchiseLineage(
                canonical_id='FLA',
                current_name='Miami Marlins',
                lahman_ids=['FLO', 'MIA'],
                founded_year=1993,
                relocations=[],
                notes='Florida Marlins (1993-2011) became Miami Marlins (2012-present), same city'
            )
        }
        
        return lineages
    
    def _build_lahman_mapping(self) -> Dict[str, str]:
        """Build mapping from Lahman IDs to canonical franchise IDs."""
        mapping = {}
        for canonical_id, lineage in self.lineages.items():
            for lahman_id in lineage.lahman_ids:
                if lahman_id in mapping:
                    raise ValueError(f"Duplicate Lahman ID {lahman_id} found in multiple lineages")
                mapping[lahman_id] = canonical_id
        return mapping
    
    def get_canonical_franchise(self, lahman_id: str) -> Optional[str]:
        """Get canonical franchise ID for a given Lahman ID."""
        return self.lahman_to_canonical.get(lahman_id)
    
    def is_relocated_franchise(self, canonical_id: str) -> bool:
        """Check if a franchise has any relocations."""
        lineage = self.lineages.get(canonical_id)
        return lineage is not None and len(lineage.relocations) > 0
    
    def get_relocation_years(self, canonical_id: str) -> List[int]:
        """Get all relocation years for a franchise."""
        lineage = self.lineages.get(canonical_id)
        if lineage is None:
            return []
        return [rel.year for rel in lineage.relocations]
    
    def get_franchise_info(self, canonical_id: str) -> Optional[FranchiseLineage]:
        """Get complete franchise lineage information."""
        return self.lineages.get(canonical_id)
    
    def validate_data_consistency(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate franchise data consistency and return issues found."""
        issues = {
            'missing_franchises': [],
            'unmapped_lahman_ids': [],
            'year_gaps': [],
            'duplicate_seasons': [],
            'invalid_relocations': []
        }
        
        # Check for unmapped Lahman franchise IDs
        unique_franchise_ids = set(df['franchID'].unique())
        for fid in unique_franchise_ids:
            if fid not in self.lahman_to_canonical:
                issues['unmapped_lahman_ids'].append(fid)
        
        # Check for year gaps in franchise histories
        for canonical_id, lineage in self.lineages.items():
            franchise_data = df[df['franchID'].isin(lineage.lahman_ids)].copy()
            if franchise_data.empty:
                issues['missing_franchises'].append(canonical_id)
                continue
                
            years = sorted(franchise_data['yearID'].unique())
            for i in range(1, len(years)):
                if years[i] - years[i-1] > 1:
                    gap = f"{canonical_id}: gap between {years[i-1]} and {years[i]}"
                    issues['year_gaps'].append(gap)
        
        # Check for duplicate seasons (same franchise, same year)
        df_mapped = df.copy()
        df_mapped['canonical_franchise'] = df_mapped['franchID'].map(self.lahman_to_canonical)
        duplicates = df_mapped.groupby(['canonical_franchise', 'yearID']).size()
        duplicates = duplicates[duplicates > 1]
        for (franchise, year), count in duplicates.items():
            issues['duplicate_seasons'].append(f"{franchise} {year}: {count} entries")
        
        # Validate relocation timing
        for canonical_id, lineage in self.lineages.items():
            franchise_data = df[df['franchID'].isin(lineage.lahman_ids)].copy()
            if franchise_data.empty:
                continue
                
            for relocation in lineage.relocations:
                # Check if data exists around relocation year
                pre_reloc = franchise_data[franchise_data['yearID'] == relocation.year - 1]
                post_reloc = franchise_data[franchise_data['yearID'] == relocation.year]
                
                if pre_reloc.empty or post_reloc.empty:
                    issue = f"{canonical_id}: Missing data around {relocation.year} relocation"
                    issues['invalid_relocations'].append(issue)
        
        return issues


def create_annotated_dataset(df: pd.DataFrame, mapper: FranchiseMapper) -> pd.DataFrame:
    """Create dataset with canonical franchise IDs and relocation annotations."""
    
    # Add canonical franchise mapping
    df_annotated = df.copy()
    df_annotated['canonical_franchise'] = df_annotated['franchID'].map(mapper.lahman_to_canonical)
    
    # Add relocation annotations
    df_annotated['is_relocated_franchise'] = False
    df_annotated['relocation_year'] = None
    df_annotated['pre_relocation'] = False
    df_annotated['post_relocation'] = False
    df_annotated['years_since_relocation'] = None
    
    for canonical_id, lineage in mapper.lineages.items():
        if not lineage.relocations:
            continue
            
        franchise_mask = df_annotated['canonical_franchise'] == canonical_id
        df_annotated.loc[franchise_mask, 'is_relocated_franchise'] = True
        
        # For franchises with multiple relocations, use the most recent one
        latest_relocation = max(lineage.relocations, key=lambda x: x.year)
        df_annotated.loc[franchise_mask, 'relocation_year'] = latest_relocation.year
        
        # Mark pre/post relocation periods
        pre_mask = franchise_mask & (df_annotated['yearID'] < latest_relocation.year)
        post_mask = franchise_mask & (df_annotated['yearID'] >= latest_relocation.year)
        
        df_annotated.loc[pre_mask, 'pre_relocation'] = True
        df_annotated.loc[post_mask, 'post_relocation'] = True
        
        # Calculate years since relocation
        post_years = df_annotated.loc[post_mask, 'yearID'] - latest_relocation.year
        df_annotated.loc[post_mask, 'years_since_relocation'] = post_years
    
    return df_annotated


def validate_relocation_data(df: pd.DataFrame, mapper: FranchiseMapper) -> pd.DataFrame:
    """Comprehensive validation report for relocation data."""
    
    validation_results = []
    
    for canonical_id, lineage in mapper.lineages.items():
        franchise_data = df[df['franchID'].isin(lineage.lahman_ids)].copy()
        
        if franchise_data.empty:
            validation_results.append({
                'franchise': canonical_id,
                'issue_type': 'missing_data',
                'description': f'No data found for franchise {canonical_id}',
                'severity': 'high'
            })
            continue
        
        # Check data completeness
        year_range = franchise_data['yearID'].max() - franchise_data['yearID'].min() + 1
        actual_years = len(franchise_data['yearID'].unique())
        
        if actual_years < year_range:
            validation_results.append({
                'franchise': canonical_id,
                'issue_type': 'missing_years',
                'description': f'Missing {year_range - actual_years} years of data',
                'severity': 'medium'
            })
        
        # Validate each relocation
        for i, relocation in enumerate(lineage.relocations):
            # Check for data around relocation year
            pre_data = franchise_data[franchise_data['yearID'] == relocation.year - 1]
            reloc_data = franchise_data[franchise_data['yearID'] == relocation.year]
            
            if pre_data.empty:
                validation_results.append({
                    'franchise': canonical_id,
                    'issue_type': 'missing_pre_relocation',
                    'description': f'No data for year {relocation.year - 1} before {relocation.year} relocation',
                    'severity': 'high'
                })
            
            if reloc_data.empty:
                validation_results.append({
                    'franchise': canonical_id,
                    'issue_type': 'missing_relocation_year',
                    'description': f'No data for relocation year {relocation.year}',
                    'severity': 'high'
                })
            
            # Check team name consistency
            if not reloc_data.empty:
                team_names = reloc_data['name'].unique()
                expected_name_parts = relocation.to_city.split()
                
                name_match = any(
                    any(part.lower() in name.lower() for part in expected_name_parts)
                    for name in team_names
                )
                
                if not name_match:
                    validation_results.append({
                        'franchise': canonical_id,
                        'issue_type': 'name_mismatch',
                        'description': f'Team name in {relocation.year} does not match expected city {relocation.to_city}',
                        'severity': 'medium'
                    })
    
    return pd.DataFrame(validation_results)


def get_franchise_summary(df: pd.DataFrame, mapper: FranchiseMapper) -> pd.DataFrame:
    """Generate summary statistics for each franchise."""
    
    summaries = []
    
    for canonical_id, lineage in mapper.lineages.items():
        franchise_data = df[df['franchID'].isin(lineage.lahman_ids)].copy()
        
        if franchise_data.empty:
            continue
        
        summary = {
            'canonical_franchise': canonical_id,
            'current_name': lineage.current_name,
            'founded_year': lineage.founded_year,
            'total_seasons': len(franchise_data),
            'first_season': franchise_data['yearID'].min(),
            'last_season': franchise_data['yearID'].max(),
            'total_relocations': len(lineage.relocations),
            'relocation_years': ', '.join(str(r.year) for r in lineage.relocations),
            'lahman_ids': ', '.join(lineage.lahman_ids),
            'avg_win_pct': franchise_data['W_pct'].mean(),
            'total_wins': franchise_data['W'].sum(),
            'total_losses': franchise_data['L'].sum()
        }
        
        # Add pre/post relocation stats if applicable
        if lineage.relocations:
            latest_reloc_year = max(r.year for r in lineage.relocations)
            pre_reloc = franchise_data[franchise_data['yearID'] < latest_reloc_year]
            post_reloc = franchise_data[franchise_data['yearID'] >= latest_reloc_year]
            
            summary.update({
                'pre_relocation_seasons': len(pre_reloc),
                'post_relocation_seasons': len(post_reloc),
                'pre_relocation_win_pct': pre_reloc['W_pct'].mean() if not pre_reloc.empty else None,
                'post_relocation_win_pct': post_reloc['W_pct'].mean() if not post_reloc.empty else None
            })
        
        summaries.append(summary)
    
    return pd.DataFrame(summaries)


# Historical franchise IDs that are NOT part of modern relocated franchises
# These represent defunct teams or separate franchise lineages
DEFUNCT_FRANCHISES = {
    'ATH',  # 1876 Philadelphia Athletics (NL) - different from AL Athletics
    'BLO',  # 1882-1899 Baltimore Orioles (AA/NL) - different from modern Orioles  
    'BFL',  # Buffalo (Federal League)
    'BFB',  # Buffalo (Players League)
    'BUF',  # Buffalo (NL)
    'CLV',  # Cleveland Spiders (NL) - folded 1899
    'DTN',  # Detroit Wolverines (NL) - folded 1888
    'HAR',  # Hartford Dark Blues
    'IND',  # Indianapolis Hoosiers
    'KCN',  # Kansas City Cowboys (NL)
    'LOU',  # Louisville Colonels
    'PRO',  # Providence Grays
    'TRT',  # Troy Trojans
    'WOR',  # Worcester Ruby Legs
    # Federal League teams (1914-1915)
    'CHH', 'BLT', 'BTT', 'KCP', 'NEW', 'PBS', 'SLI'
}


if __name__ == "__main__":
    # Example usage and testing
    import os
    
    mapper = FranchiseMapper()
    
    # Load data with correct path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(script_dir), 'team_seasons.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: team_seasons.csv not found at {csv_path}")
        print("Please run gather_mlb_wl.py first to generate the data")
        sys.exit(1)
    
    df = pd.read_csv(csv_path)
    
    # Run validation
    issues = mapper.validate_data_consistency(df)
    print("Data Validation Issues:")
    for issue_type, problems in issues.items():
        if problems:
            print(f"\n{issue_type.upper()}:")
            for problem in problems:
                print(f"  - {problem}")
    
    # Create annotated dataset
    df_annotated = create_annotated_dataset(df, mapper)
    
    # Generate summary
    summary = get_franchise_summary(df, mapper)
    print(f"\nFranchise Summary:")
    print(summary.to_string(index=False))
    
    # Save annotated data
    output_path = os.path.join(os.path.dirname(script_dir), 'team_seasons_annotated.csv')
    df_annotated.to_csv(output_path, index=False)
    print(f"\nSaved annotated dataset to team_seasons_annotated.csv")