"""
data_validation.py

Comprehensive data validation and quality checks for MLB relocation analysis.
Validates data accuracy, completeness, and consistency across multiple sources.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import requests
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """Result of a data validation check."""
    check_name: str
    status: str  # 'pass', 'warning', 'fail'
    message: str
    details: Optional[Dict] = None


class DataValidator:
    """Comprehensive data validation system."""
    
    def __init__(self):
        self.validation_results: List[ValidationResult] = []
    
    def validate_basic_data_quality(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Basic data quality checks."""
        results = []
        
        # Check for required columns
        required_cols = ['yearID', 'teamID', 'franchID', 'lgID', 'name', 'W', 'L', 'G', 'W_pct']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            results.append(ValidationResult(
                'required_columns',
                'fail',
                f'Missing required columns: {missing_cols}'
            ))
        else:
            results.append(ValidationResult(
                'required_columns',
                'pass',
                'All required columns present'
            ))
        
        # Check for null values in critical columns
        critical_cols = ['yearID', 'franchID', 'W', 'L']
        null_counts = {}
        for col in critical_cols:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    null_counts[col] = null_count
        
        if null_counts:
            results.append(ValidationResult(
                'null_values',
                'fail',
                f'Null values found in critical columns',
                details=null_counts
            ))
        else:
            results.append(ValidationResult(
                'null_values',
                'pass',
                'No null values in critical columns'
            ))
        
        # Check win percentage calculation accuracy
        if all(col in df.columns for col in ['W', 'L', 'G', 'W_pct']):
            df_check = df.copy()
            df_check['calculated_G'] = df_check['W'] + df_check['L']
            df_check['calculated_W_pct'] = df_check['W'] / df_check['calculated_G']
            
            # Allow small floating point differences
            g_mismatch = abs(df_check['G'] - df_check['calculated_G']) > 1
            pct_mismatch = abs(df_check['W_pct'] - df_check['calculated_W_pct']) > 0.01
            
            g_errors = g_mismatch.sum()
            pct_errors = pct_mismatch.sum()
            
            if g_errors > 0 or pct_errors > 0:
                results.append(ValidationResult(
                    'calculation_accuracy',
                    'warning',
                    f'Calculation mismatches: {g_errors} games, {pct_errors} win percentages'
                ))
            else:
                results.append(ValidationResult(
                    'calculation_accuracy',
                    'pass',
                    'Win percentage calculations are accurate'
                ))
        
        return results
    
    def validate_historical_accuracy(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Validate historical accuracy against known facts."""
        results = []
        
        # Check for reasonable year ranges
        min_year = df['yearID'].min()
        max_year = df['yearID'].max()
        current_year = datetime.now().year
        
        if min_year < 1871:
            results.append(ValidationResult(
                'year_range',
                'warning',
                f'Data includes years before 1871 (first professional season): {min_year}'
            ))
        
        if max_year > current_year:
            results.append(ValidationResult(
                'year_range',
                'fail',
                f'Data includes future years: {max_year}'
            ))
        
        # Check for reasonable game counts
        # Modern era should be close to 162 games, earlier eras varied
        modern_era = df[df['yearID'] >= 1961].copy()  # 162-game era
        if not modern_era.empty:
            # Allow for strike-shortened seasons (1981, 1994, 2020)
            strike_years = {1981, 1994, 2020}
            normal_modern = modern_era[~modern_era['yearID'].isin(strike_years)]
            
            if not normal_modern.empty:
                low_games = normal_modern[normal_modern['G'] < 160]
                high_games = normal_modern[normal_modern['G'] > 164]
                
                if len(low_games) > 0:
                    results.append(ValidationResult(
                        'game_counts',
                        'warning',
                        f'{len(low_games)} modern seasons with unusually low game counts',
                        details={'low_game_seasons': low_games[['yearID', 'teamID', 'G']].to_dict('records')}
                    ))
                
                if len(high_games) > 0:
                    results.append(ValidationResult(
                        'game_counts',
                        'warning',
                        f'{len(high_games)} modern seasons with unusually high game counts',
                        details={'high_game_seasons': high_games[['yearID', 'teamID', 'G']].to_dict('records')}
                    ))
        
        # Check for impossible win percentages
        impossible_pct = df[(df['W_pct'] < 0) | (df['W_pct'] > 1)]
        if not impossible_pct.empty:
            results.append(ValidationResult(
                'win_percentages',
                'fail',
                f'{len(impossible_pct)} seasons with impossible win percentages',
                details={'impossible_records': impossible_pct[['yearID', 'teamID', 'W_pct']].to_dict('records')}
            ))
        
        # Check for extremely unusual records (< 20% or > 80% win rate)
        extreme_records = df[(df['W_pct'] < 0.2) | (df['W_pct'] > 0.8)]
        if not extreme_records.empty:
            results.append(ValidationResult(
                'extreme_records',
                'warning',
                f'{len(extreme_records)} seasons with extreme win percentages (< 20% or > 80%)',
                details={'extreme_seasons': extreme_records[['yearID', 'teamID', 'name', 'W_pct']].to_dict('records')}
            ))
        
        return results
    
    def validate_franchise_continuity(self, df: pd.DataFrame, mapper) -> List[ValidationResult]:
        """Validate franchise continuity across relocations."""
        results = []
        
        for canonical_id, lineage in mapper.lineages.items():
            franchise_data = df[df['franchID'].isin(lineage.lahman_ids)].copy()
            
            if franchise_data.empty:
                continue
            
            # Sort by year
            franchise_data = franchise_data.sort_values('yearID')
            
            # Check for continuity across relocations
            for relocation in lineage.relocations:
                pre_reloc = franchise_data[franchise_data['yearID'] == relocation.year - 1]
                post_reloc = franchise_data[franchise_data['yearID'] == relocation.year]
                
                if not pre_reloc.empty and not post_reloc.empty:
                    # Check if franchID changed appropriately
                    pre_fid = pre_reloc['franchID'].iloc[0]
                    post_fid = post_reloc['franchID'].iloc[0]
                    
                    # For some franchises, franchID stays the same (like LAD)
                    # For others, it should change (like BSN → ML1 → ATL)
                    if canonical_id == 'ATL':
                        if relocation.year == 1953 and pre_fid == post_fid:
                            results.append(ValidationResult(
                                'franchise_id_continuity',
                                'warning',
                                f'{canonical_id}: franchID did not change at {relocation.year} relocation'
                            ))
                    
                    # Check league consistency (should stay the same unless noted)
                    pre_league = pre_reloc['lgID'].iloc[0]
                    post_league = post_reloc['lgID'].iloc[0]
                    
                    if pre_league != post_league and canonical_id != 'HOU':  # HOU changed leagues in 2013
                        results.append(ValidationResult(
                            'league_continuity',
                            'warning',
                            f'{canonical_id}: League changed from {pre_league} to {post_league} at {relocation.year}'
                        ))
        
        return results
    
    def validate_against_external_sources(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Validate against external data sources (when available)."""
        results = []
        
        # Known historical facts to validate against
        known_facts = [
            # (year, teamID, expected_wins, expected_losses, description)
            (1906, 'CHN', 116, 36, 'Cubs record-setting season'),
            (1962, 'NYN', 40, 120, 'Mets worst season'),
            (2001, 'SEA', 116, 46, 'Mariners tied AL record'),
            (1899, 'CL4', 20, 134, 'Cleveland Spiders worst record ever'),
        ]
        
        for year, team_id, exp_w, exp_l, description in known_facts:
            matching_rows = df[(df['yearID'] == year) & (df['teamID'] == team_id)]
            
            if matching_rows.empty:
                results.append(ValidationResult(
                    'historical_facts',
                    'warning',
                    f'Missing data for known historical fact: {description} ({year})'
                ))
            else:
                row = matching_rows.iloc[0]
                if row['W'] != exp_w or row['L'] != exp_l:
                    results.append(ValidationResult(
                        'historical_facts',
                        'fail',
                        f'Historical fact mismatch: {description} - Expected {exp_w}-{exp_l}, got {row["W"]}-{row["L"]}'
                    ))
                else:
                    results.append(ValidationResult(
                        'historical_facts',
                        'pass',
                        f'Confirmed historical fact: {description}'
                    ))
        
        return results
    
    def run_all_validations(self, df: pd.DataFrame, mapper) -> Dict[str, List[ValidationResult]]:
        """Run all validation checks and return organized results."""
        
        all_results = {
            'basic_quality': self.validate_basic_data_quality(df),
            'historical_accuracy': self.validate_historical_accuracy(df),
            'franchise_continuity': self.validate_franchise_continuity(df, mapper),
            'external_validation': self.validate_against_external_sources(df)
        }
        
        return all_results
    
    def generate_validation_report(self, validation_results: Dict[str, List[ValidationResult]]) -> str:
        """Generate a comprehensive validation report."""
        
        report = ["=" * 60]
        report.append("MLB DATA VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_checks = sum(len(results) for results in validation_results.values())
        total_passes = sum(
            len([r for r in results if r.status == 'pass']) 
            for results in validation_results.values()
        )
        total_warnings = sum(
            len([r for r in results if r.status == 'warning']) 
            for results in validation_results.values()
        )
        total_failures = sum(
            len([r for r in results if r.status == 'fail']) 
            for results in validation_results.values()
        )
        
        report.append("SUMMARY:")
        report.append(f"  Total Checks: {total_checks}")
        report.append(f"  Passed: {total_passes}")
        report.append(f"  Warnings: {total_warnings}")
        report.append(f"  Failed: {total_failures}")
        report.append("")
        
        for category, results in validation_results.items():
            report.append(f"{category.upper().replace('_', ' ')}:")
            report.append("-" * 40)
            
            if not results:
                report.append("  No checks performed")
            else:
                for result in results:
                    status_symbol = {
                        'pass': '✓',
                        'warning': '⚠',
                        'fail': '✗'
                    }.get(result.status, '?')
                    
                    report.append(f"  {status_symbol} {result.check_name}: {result.message}")
                    
                    if result.details:
                        for key, value in result.details.items():
                            if isinstance(value, list) and len(value) <= 5:
                                report.append(f"    {key}: {value}")
                            elif isinstance(value, list):
                                report.append(f"    {key}: {len(value)} items (showing first 3)")
                                for item in value[:3]:
                                    report.append(f"      {item}")
                            else:
                                report.append(f"    {key}: {value}")
            
            report.append("")
        
        return "\n".join(report)


def cross_validate_relocations(df: pd.DataFrame, mapper) -> List[ValidationResult]:
    """Cross-validate relocation data against multiple sources."""
    results = []
    
    # Known relocation facts from multiple sources
    relocation_facts = [
        ('LAD', 1958, 'Brooklyn', 'Los Angeles'),
        ('SFG', 1958, 'New York', 'San Francisco'), 
        ('ATL', 1953, 'Boston', 'Milwaukee'),
        ('ATL', 1966, 'Milwaukee', 'Atlanta'),
        ('OAK', 1955, 'Philadelphia', 'Kansas City'),
        ('OAK', 1968, 'Kansas City', 'Oakland'),
        ('MIN', 1961, 'Washington', 'Minneapolis'),
        ('TEX', 1972, 'Washington', 'Dallas-Fort Worth'),
        ('BAL', 1954, 'St. Louis', 'Baltimore'),
        ('MIL', 1970, 'Seattle', 'Milwaukee'),
        ('WSN', 2005, 'Montreal', 'Washington')
    ]
    
    for canonical_id, year, from_city, to_city in relocation_facts:
        lineage = mapper.get_franchise_info(canonical_id)
        if lineage is None:
            results.append(ValidationResult(
                'relocation_mapping',
                'fail',
                f'No lineage found for {canonical_id}'
            ))
            continue
        
        # Check if relocation is properly recorded
        matching_relocations = [
            r for r in lineage.relocations 
            if r.year == year and from_city.lower() in r.from_city.lower()
        ]
        
        if not matching_relocations:
            results.append(ValidationResult(
                'relocation_mapping',
                'fail',
                f'Missing relocation: {canonical_id} {from_city} → {to_city} in {year}'
            ))
        else:
            results.append(ValidationResult(
                'relocation_mapping',
                'pass',
                f'Confirmed relocation: {canonical_id} {from_city} → {to_city} in {year}'
            ))
        
        # Validate data exists around relocation
        franchise_data = df[df['franchID'].isin(lineage.lahman_ids)]
        pre_data = franchise_data[franchise_data['yearID'] == year - 1]
        post_data = franchise_data[franchise_data['yearID'] == year]
        
        if pre_data.empty or post_data.empty:
            results.append(ValidationResult(
                'relocation_data_continuity',
                'fail',
                f'Missing data around {canonical_id} {year} relocation'
            ))
    
    return results


def validate_team_name_consistency(df: pd.DataFrame, mapper) -> List[ValidationResult]:
    """Validate team name consistency within franchise lineages."""
    results = []
    
    for canonical_id, lineage in mapper.lineages.items():
        franchise_data = df[df['franchID'].isin(lineage.lahman_ids)].copy()
        
        if franchise_data.empty:
            continue
        
        # Check name changes align with relocations
        franchise_data = franchise_data.sort_values('yearID')
        unique_names = franchise_data['name'].unique()
        
        # For relocated franchises, expect name changes
        if lineage.relocations and len(unique_names) < 2:
            results.append(ValidationResult(
                'team_name_changes',
                'warning',
                f'{canonical_id}: Expected name changes due to relocations, but only found: {unique_names}'
            ))
        
        # Check for city name consistency in team names
        for relocation in lineage.relocations:
            post_reloc_data = franchise_data[franchise_data['yearID'] >= relocation.year]
            if not post_reloc_data.empty:
                post_names = post_reloc_data['name'].unique()
                
                # Check if new city appears in team names
                city_parts = relocation.to_city.split()
                city_found = any(
                    any(part.lower() in name.lower() for part in city_parts)
                    for name in post_names
                )
                
                if not city_found:
                    results.append(ValidationResult(
                        'city_name_consistency',
                        'warning',
                        f'{canonical_id}: City "{relocation.to_city}" not found in post-{relocation.year} team names: {post_names}'
                    ))
    
    return results


def check_data_completeness(df: pd.DataFrame, mapper) -> List[ValidationResult]:
    """Check data completeness for statistical analysis."""
    results = []
    
    # Check minimum seasons for statistical significance
    MIN_SEASONS_PRE = 10
    MIN_SEASONS_POST = 10
    
    insufficient_data = []
    
    for canonical_id, lineage in mapper.lineages.items():
        if not lineage.relocations:
            continue
            
        franchise_data = df[df['franchID'].isin(lineage.lahman_ids)]
        
        if franchise_data.empty:
            continue
        
        # Use most recent relocation for analysis
        latest_relocation = max(lineage.relocations, key=lambda x: x.year)
        
        pre_reloc = franchise_data[franchise_data['yearID'] < latest_relocation.year]
        post_reloc = franchise_data[franchise_data['yearID'] >= latest_relocation.year]
        
        pre_count = len(pre_reloc)
        post_count = len(post_reloc)
        
        if pre_count < MIN_SEASONS_PRE or post_count < MIN_SEASONS_POST:
            insufficient_data.append({
                'franchise': canonical_id,
                'relocation_year': latest_relocation.year,
                'pre_seasons': pre_count,
                'post_seasons': post_count,
                'sufficient_for_analysis': False
            })
        else:
            insufficient_data.append({
                'franchise': canonical_id,
                'relocation_year': latest_relocation.year,
                'pre_seasons': pre_count,
                'post_seasons': post_count,
                'sufficient_for_analysis': True
            })
    
    insufficient_count = len([d for d in insufficient_data if not d['sufficient_for_analysis']])
    
    if insufficient_count > 0:
        results.append(ValidationResult(
            'statistical_sufficiency',
            'warning',
            f'{insufficient_count} franchises have insufficient data for robust statistical analysis',
            details={'franchise_data_counts': insufficient_data}
        ))
    else:
        results.append(ValidationResult(
            'statistical_sufficiency',
            'pass',
            'All relocated franchises have sufficient data for statistical analysis'
        ))
    
    return results


def run_comprehensive_validation(df_path: str = '../team_seasons.csv') -> str:
    """Run all validation checks and return comprehensive report."""
    
    # Import here to avoid circular imports
    from franchise_mapping import FranchiseMapper
    
    # Load data
    df = pd.read_csv(df_path)
    mapper = FranchiseMapper()
    validator = DataValidator()
    
    # Run all validations
    validation_results = validator.run_all_validations(df, mapper)
    
    # Add custom validations
    validation_results['relocation_cross_validation'] = cross_validate_relocations(df, mapper)
    validation_results['team_name_consistency'] = validate_team_name_consistency(df, mapper)
    validation_results['data_completeness'] = check_data_completeness(df, mapper)
    
    # Generate report
    report = validator.generate_validation_report(validation_results)
    
    return report


if __name__ == "__main__":
    # Run validation and save report
    report = run_comprehensive_validation()
    
    print(report)
    
    # Save report to file
    with open('../validation_report.txt', 'w') as f:
        f.write(report)
    
    print(f"\nValidation report saved to validation_report.txt")