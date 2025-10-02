"""
enhanced_gather_mlb_wl.py

Enhanced version of gather_mlb_wl.py with improved franchise mapping,
validation, and relocation analysis capabilities.
"""
from __future__ import annotations
import argparse
import sys
from typing import Optional
import pandas as pd
from franchise_mapping import FranchiseMapper, create_annotated_dataset
from data_validation import run_comprehensive_validation, DataValidator


def load_and_validate_data(lahman_path: str, mapper: FranchiseMapper) -> pd.DataFrame:
    """Load Lahman data with enhanced validation."""
    
    print(f"Loading Lahman data from: {lahman_path}")
    
    # Use the original loading logic but with enhanced validation
    from gather_mlb_wl import load_lahman_teams
    
    try:
        df = load_lahman_teams(lahman_path)
        print(f"Loaded {len(df)} team seasons from {df['yearID'].min()} to {df['yearID'].max()}")
    except Exception as e:
        print(f"Error loading Lahman data: {e}", file=sys.stderr)
        raise
    
    # Run validation
    validator = DataValidator()
    validation_results = validator.run_all_validations(df, mapper)
    
    # Check for critical failures
    critical_failures = []
    for category, results in validation_results.items():
        for result in results:
            if result.status == 'fail':
                critical_failures.append(f"{category}: {result.message}")
    
    if critical_failures:
        print("CRITICAL DATA VALIDATION FAILURES:")
        for failure in critical_failures:
            print(f"  ✗ {failure}")
        print("\nPlease fix these issues before proceeding with analysis.")
        return None
    
    # Report warnings
    warnings = []
    for category, results in validation_results.items():
        for result in results:
            if result.status == 'warning':
                warnings.append(f"{category}: {result.message}")
    
    if warnings:
        print(f"\nData validation warnings ({len(warnings)} found):")
        for warning in warnings[:5]:  # Show first 5
            print(f"  ⚠ {warning}")
        if len(warnings) > 5:
            print(f"  ... and {len(warnings) - 5} more warnings")
    
    return df


def create_relocation_analysis_dataset(df: pd.DataFrame, mapper: FranchiseMapper, 
                                     output_path: str) -> pd.DataFrame:
    """Create enhanced dataset optimized for relocation analysis."""
    
    print("Creating relocation analysis dataset...")
    
    # Create annotated dataset
    df_annotated = create_annotated_dataset(df, mapper)
    
    # Add additional analysis columns
    df_annotated['era'] = pd.cut(
        df_annotated['yearID'], 
        bins=[0, 1900, 1920, 1940, 1960, 1980, 2000, 2030],
        labels=['Pre-1900', '1900-1919', '1920-1939', '1940-1959', '1960-1979', '1980-1999', '2000+']
    )
    
    # Add franchise age
    df_annotated['franchise_age'] = 0
    for canonical_id, lineage in mapper.lineages.items():
        mask = df_annotated['canonical_franchise'] == canonical_id
        df_annotated.loc[mask, 'franchise_age'] = df_annotated.loc[mask, 'yearID'] - lineage.founded_year
    
    # Add relocation context
    df_annotated['relocation_context'] = 'none'
    
    for canonical_id, lineage in mapper.lineages.items():
        if not lineage.relocations:
            continue
            
        franchise_mask = df_annotated['canonical_franchise'] == canonical_id
        
        for relocation in lineage.relocations:
            # Mark seasons around relocation
            reloc_mask = franchise_mask & (
                (df_annotated['yearID'] >= relocation.year - 2) & 
                (df_annotated['yearID'] <= relocation.year + 2)
            )
            df_annotated.loc[reloc_mask, 'relocation_context'] = f'around_{relocation.year}'
    
    # Save dataset
    df_annotated.to_csv(output_path, index=False)
    print(f"Saved enhanced dataset to {output_path}")
    
    # Generate summary statistics
    print("\nRELOCATION ANALYSIS SUMMARY:")
    print("=" * 50)
    
    relocated_franchises = df_annotated[df_annotated['is_relocated_franchise'] == True]
    
    if not relocated_franchises.empty:
        print(f"Relocated franchises: {relocated_franchises['canonical_franchise'].nunique()}")
        print(f"Total seasons with relocated franchises: {len(relocated_franchises)}")
        print(f"Pre-relocation seasons: {relocated_franchises['pre_relocation'].sum()}")
        print(f"Post-relocation seasons: {relocated_franchises['post_relocation'].sum()}")
        
        # Summary by franchise
        summary = relocated_franchises.groupby('canonical_franchise').agg({
            'yearID': ['min', 'max', 'count'],
            'pre_relocation': 'sum',
            'post_relocation': 'sum',
            'W_pct': 'mean'
        }).round(3)
        
        summary.columns = ['First_Year', 'Last_Year', 'Total_Seasons', 'Pre_Reloc_Seasons', 'Post_Reloc_Seasons', 'Avg_Win_Pct']
        print("\nBy Franchise:")
        print(summary.to_string())
    
    return df_annotated


def main(argv: Optional[list[str]] = None) -> int:
    """Enhanced main function with comprehensive validation and mapping."""
    
    parser = argparse.ArgumentParser(
        description="Enhanced MLB win/loss data gathering with franchise mapping and validation"
    )
    parser.add_argument("--lahman", required=True, help="Path or URL to Lahman Teams.csv")
    parser.add_argument("--output", required=True, help="Output CSV path for enhanced team seasons")
    parser.add_argument("--validation-report", help="Path for validation report (optional)")
    parser.add_argument("--skip-validation", action="store_true", help="Skip validation checks")
    
    args = parser.parse_args(argv)
    
    # Initialize franchise mapper
    mapper = FranchiseMapper()
    
    # Load and validate data
    df = load_and_validate_data(args.lahman, mapper)
    if df is None:
        return 1
    
    # Create enhanced dataset
    df_enhanced = create_relocation_analysis_dataset(df, mapper, args.output)
    
    # Generate and save validation report
    if not args.skip_validation:
        if args.validation_report:
            report = run_comprehensive_validation(df_path=args.lahman)
            with open(args.validation_report, 'w') as f:
                f.write(report)
            print(f"Validation report saved to {args.validation_report}")
        else:
            print("\nRun with --validation-report to save detailed validation report")
    
    print(f"\n✓ Enhanced dataset ready for relocation analysis: {args.output}")
    print("✓ Data validation completed")
    print("✓ Franchise mapping applied")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())