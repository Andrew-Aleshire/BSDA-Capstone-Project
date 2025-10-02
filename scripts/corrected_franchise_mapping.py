"""
corrected_franchise_mapping.py

Corrected and comprehensive franchise mapping system based on validation results.
Includes all modern franchises and properly handles historical data.
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


class CorrectedFranchiseMapper:
    """Corrected franchise mapping system with comprehensive coverage."""
    
    def __init__(self):
        self.lineages = self._build_franchise_lineages()
        self.lahman_to_canonical = self._build_lahman_mapping()
    
    def _build_franchise_lineages(self) -> Dict[str, FranchiseLineage]:
        """Build comprehensive franchise lineage mappings with corrections."""
        
        lineages = {
            # RELOCATED FRANCHISES (Primary focus for analysis)
            
            # Atlanta Braves: Boston → Milwaukee → Atlanta
            'ATL': FranchiseLineage(
                canonical_id='ATL',
                current_name='Atlanta Braves',
                lahman_ids=['ATL'],  # Lahman uses ATL for entire lineage
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
                lahman_ids=['LAD'],  # Lahman uses LAD for entire lineage
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
                lahman_ids=['SFG'],  # Lahman uses SFG for entire lineage
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
                lahman_ids=['OAK'],  # Lahman uses OAK for entire lineage
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
                lahman_ids=['MIN'],  # Lahman uses MIN for entire lineage
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
                lahman_ids=['TEX'],  # Lahman uses TEX for entire lineage
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
                lahman_ids=['BAL'],  # Lahman uses BAL for entire lineage
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
                lahman_ids=['MIL'],  # Lahman uses MIL for entire lineage
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
                lahman_ids=['WSN'],  # Lahman uses WSN for entire lineage
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
                lahman_ids=['NYY'],  # Lahman uses NYY for entire lineage
                founded_year=1901,
                relocations=[
                    RelocationEvent(1903, 'Baltimore', 'New York', 'Baltimore Orioles', 'New York Highlanders')
                ],
                notes='Original Baltimore Orioles (1901-1902) became NY Highlanders/Yankees. Different from modern Orioles.'
            ),
            
            # Los Angeles Angels: Name/location changes within same metro area
            'ANA': FranchiseLineage(
                canonical_id='ANA',
                current_name='Los Angeles Angels',
                lahman_ids=['ANA'],  # Lahman uses ANA for entire lineage
                founded_year=1961,
                relocations=[],  # Same metro area, just name changes
                notes='Los Angeles Angels (1961-1964) → California Angels (1965-1996) → Anaheim Angels (1997-2004) → Los Angeles Angels of Anaheim (2005-2015) → Los Angeles Angels (2016-present)'
            ),
            
            # Florida/Miami Marlins: Name change only
            'FLA': FranchiseLineage(
                canonical_id='FLA',
                current_name='Miami Marlins',
                lahman_ids=['FLA'],  # Lahman uses FLA for entire lineage
                founded_year=1993,
                relocations=[],
                notes='Florida Marlins (1993-2011) became Miami Marlins (2012-present), same city'
            ),
            
            # STABLE FRANCHISES (No relocations)
            
            'BOS': FranchiseLineage(
                canonical_id='BOS',
                current_name='Boston Red Sox',
                lahman_ids=['BOS'],
                founded_year=1901,
                relocations=[],
                notes='Boston Red Sox, stable franchise'
            ),
            
            'CHC': FranchiseLineage(
                canonical_id='CHC',
                current_name='Chicago Cubs',
                lahman_ids=['CHC'],
                founded_year=1876,
                relocations=[],
                notes='Chicago Cubs, stable franchise'
            ),
            
            'CHW': FranchiseLineage(
                canonical_id='CHW',
                current_name='Chicago White Sox',
                lahman_ids=['CHW'],
                founded_year=1901,
                relocations=[],
                notes='Chicago White Sox, stable franchise'
            ),
            
            'CIN': FranchiseLineage(
                canonical_id='CIN',
                current_name='Cincinnati Reds',
                lahman_ids=['CIN'],
                founded_year=1882,
                relocations=[],
                notes='Cincinnati Reds, stable franchise'
            ),
            
            'CLE': FranchiseLineage(
                canonical_id='CLE',
                current_name='Cleveland Guardians',
                lahman_ids=['CLE'],
                founded_year=1901,
                relocations=[],
                notes='Cleveland franchise, name changed to Guardians in 2022'
            ),
            
            'DET': FranchiseLineage(
                canonical_id='DET',
                current_name='Detroit Tigers',
                lahman_ids=['DET'],
                founded_year=1901,
                relocations=[],
                notes='Detroit Tigers, stable franchise'
            ),
            
            'PHI': FranchiseLineage(
                canonical_id='PHI',
                current_name='Philadelphia Phillies',
                lahman_ids=['PHI'],
                founded_year=1883,
                relocations=[],
                notes='Philadelphia Phillies, stable franchise'
            ),
            
            'PIT': FranchiseLineage(
                canonical_id='PIT',
                current_name='Pittsburgh Pirates',
                lahman_ids=['PIT'],
                founded_year=1882,
                relocations=[],
                notes='Pittsburgh Pirates, stable franchise'
            ),
            
            'STL': FranchiseLineage(
                canonical_id='STL',
                current_name='St. Louis Cardinals',
                lahman_ids=['STL'],
                founded_year=1882,
                relocations=[],
                notes='St. Louis Cardinals, stable franchise'
            ),
            
            # EXPANSION TEAMS (No relocations)
            
            'ARI': FranchiseLineage(
                canonical_id='ARI',
                current_name='Arizona Diamondbacks',
                lahman_ids=['ARI'],
                founded_year=1998,
                relocations=[],
                notes='Arizona Diamondbacks expansion team'
            ),
            
            'COL': FranchiseLineage(
                canonical_id='COL',
                current_name='Colorado Rockies',
                lahman_ids=['COL'],
                founded_year=1993,
                relocations=[],
                notes='Colorado Rockies expansion team'
            ),
            
            'HOU': FranchiseLineage(
                canonical_id='HOU',
                current_name='Houston Astros',
                lahman_ids=['HOU'],
                founded_year=1962,
                relocations=[],
                notes='Houston Astros, switched from NL to AL in 2013'
            ),
            
            'KCR': FranchiseLineage(
                canonical_id='KCR',
                current_name='Kansas City Royals',
                lahman_ids=['KCR'],
                founded_year=1969,
                relocations=[],
                notes='Kansas City Royals expansion team'
            ),
            
            'NYM': FranchiseLineage(
                canonical_id='NYM',
                current_name='New York Mets',
                lahman_ids=['NYM'],
                founded_year=1962,
                relocations=[],
                notes='New York Mets expansion team'
            ),
            
            'SDP': FranchiseLineage(
                canonical_id='SDP',
                current_name='San Diego Padres',
                lahman_ids=['SDP'],
                founded_year=1969,
                relocations=[],
                notes='San Diego Padres expansion team'
            ),
            
            'SEA': FranchiseLineage(
                canonical_id='SEA',
                current_name='Seattle Mariners',
                lahman_ids=['SEA'],
                founded_year=1977,
                relocations=[],
                notes='Seattle Mariners expansion team'
            ),
            
            'TBD': FranchiseLineage(
                canonical_id='TBD',
                current_name='Tampa Bay Rays',
                lahman_ids=['TBD'],
                founded_year=1998,
                relocations=[],
                notes='Tampa Bay Rays expansion team'
            ),
            
            'TOR': FranchiseLineage(
                canonical_id='TOR',
                current_name='Toronto Blue Jays',
                lahman_ids=['TOR'],
                founded_year=1977,
                relocations=[],
                notes='Toronto Blue Jays expansion team'
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
    
    def get_relocated_franchises(self) -> List[str]:
        """Get list of all franchises that have relocated."""
        return [
            canonical_id for canonical_id, lineage in self.lineages.items()
            if lineage.relocations
        ]
    
    def get_analysis_ready_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create analysis-ready dataset with proper franchise mapping."""
        
        # Filter to only include mapped franchises
        mapped_data = df[df['franchID'].isin(self.lahman_to_canonical.keys())].copy()
        
        # Add canonical franchise mapping
        mapped_data['canonical_franchise'] = mapped_data['franchID'].map(self.lahman_to_canonical)
        
        # Add relocation annotations
        mapped_data['is_relocated_franchise'] = False
        mapped_data['relocation_year'] = None
        mapped_data['pre_relocation'] = False
        mapped_data['post_relocation'] = False
        mapped_data['years_since_relocation'] = None
        mapped_data['relocation_era'] = 'none'
        
        for canonical_id, lineage in self.lineages.items():
            if not lineage.relocations:
                continue
                
            franchise_mask = mapped_data['canonical_franchise'] == canonical_id
            mapped_data.loc[franchise_mask, 'is_relocated_franchise'] = True
            
            # For franchises with multiple relocations, use the most recent one for primary analysis
            latest_relocation = max(lineage.relocations, key=lambda x: x.year)
            mapped_data.loc[franchise_mask, 'relocation_year'] = latest_relocation.year
            
            # Mark pre/post relocation periods
            pre_mask = franchise_mask & (mapped_data['yearID'] < latest_relocation.year)
            post_mask = franchise_mask & (mapped_data['yearID'] >= latest_relocation.year)
            
            mapped_data.loc[pre_mask, 'pre_relocation'] = True
            mapped_data.loc[post_mask, 'post_relocation'] = True
            
            # Calculate years since relocation
            post_years = mapped_data.loc[post_mask, 'yearID'] - latest_relocation.year
            mapped_data.loc[post_mask, 'years_since_relocation'] = post_years
            
            # Add relocation era context
            for relocation in lineage.relocations:
                era_mask = franchise_mask & (
                    (mapped_data['yearID'] >= relocation.year - 3) & 
                    (mapped_data['yearID'] <= relocation.year + 3)
                )
                mapped_data.loc[era_mask, 'relocation_era'] = f'around_{relocation.year}'
        
        return mapped_data
    
    def generate_relocation_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate summary statistics for relocated franchises."""
        
        analysis_data = self.get_analysis_ready_data(df)
        relocated_only = analysis_data[analysis_data['is_relocated_franchise'] == True]
        
        summaries = []
        
        for canonical_id in self.get_relocated_franchises():
            franchise_data = relocated_only[relocated_only['canonical_franchise'] == canonical_id]
            
            if franchise_data.empty:
                continue
            
            lineage = self.get_franchise_info(canonical_id)
            latest_relocation = max(lineage.relocations, key=lambda x: x.year)
            
            pre_data = franchise_data[franchise_data['pre_relocation'] == True]
            post_data = franchise_data[franchise_data['post_relocation'] == True]
            
            summary = {
                'franchise': canonical_id,
                'current_name': lineage.current_name,
                'relocation_year': latest_relocation.year,
                'from_city': latest_relocation.from_city,
                'to_city': latest_relocation.to_city,
                'total_seasons': len(franchise_data),
                'pre_relocation_seasons': len(pre_data),
                'post_relocation_seasons': len(post_data),
                'pre_relocation_avg_wpct': pre_data['W_pct'].mean() if not pre_data.empty else None,
                'post_relocation_avg_wpct': post_data['W_pct'].mean() if not post_data.empty else None,
                'wpct_change': None,
                'sufficient_data': len(pre_data) >= 10 and len(post_data) >= 10
            }
            
            if summary['pre_relocation_avg_wpct'] is not None and summary['post_relocation_avg_wpct'] is not None:
                summary['wpct_change'] = summary['post_relocation_avg_wpct'] - summary['pre_relocation_avg_wpct']
            
            summaries.append(summary)
        
        return pd.DataFrame(summaries)


def main():
    """Test the corrected franchise mapping."""
    
    print("TESTING CORRECTED FRANCHISE MAPPING")
    print("=" * 50)
    
    # Load data
    if not os.path.exists('team_seasons.csv'):
        print("Error: team_seasons.csv not found")
        return 1
    
    df = pd.read_csv('team_seasons.csv')
    
    # Test corrected mapper
    mapper = CorrectedFranchiseMapper()
    
    print(f"Loaded {len(df)} team seasons")
    print(f"Mapped franchises: {len(mapper.lineages)}")
    print(f"Relocated franchises: {len(mapper.get_relocated_franchises())}")
    
    # Get analysis-ready data
    analysis_data = mapper.get_analysis_ready_data(df)
    print(f"Analysis-ready seasons: {len(analysis_data)} ({len(analysis_data)/len(df)*100:.1f}% of total)")
    
    # Generate relocation summary
    relocation_summary = mapper.generate_relocation_summary(df)
    
    print("\nRELOCATION ANALYSIS SUMMARY:")
    print("=" * 50)
    
    if not relocation_summary.empty:
        # Format for display
        display_cols = ['franchise', 'current_name', 'relocation_year', 'from_city', 'to_city', 
                       'pre_relocation_seasons', 'post_relocation_seasons', 'sufficient_data']
        
        print(relocation_summary[display_cols].to_string(index=False))
        
        print(f"\nWin Percentage Changes:")
        wpct_changes = relocation_summary[['franchise', 'pre_relocation_avg_wpct', 'post_relocation_avg_wpct', 'wpct_change']].copy()
        wpct_changes = wpct_changes.round(3)
        print(wpct_changes.to_string(index=False))
        
        # Save results
        analysis_data.to_csv('team_seasons_analysis_ready.csv', index=False)
        relocation_summary.to_csv('relocation_summary.csv', index=False)
        
        print(f"\n[SUCCESS] Analysis-ready data saved to: team_seasons_analysis_ready.csv")
        print(f"[SUCCESS] Relocation summary saved to: relocation_summary.csv")
        
        # Statistical readiness
        sufficient_data = relocation_summary['sufficient_data'].sum()
        total_relocated = len(relocation_summary)
        
        print(f"\nSTATISTICAL ANALYSIS READINESS:")
        print(f"  Franchises with sufficient data: {sufficient_data}/{total_relocated}")
        print(f"  Ready for statistical testing: {sufficient_data >= 5}")
    
    return 0


if __name__ == "__main__":
    import os
    
    # Change to parent directory where team_seasons.csv is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    
    sys.exit(main())