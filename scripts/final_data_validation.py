"""
final_data_validation.py

Final validation and recommendations for MLB relocation analysis pipeline.
Provides actionable insights for improving data accuracy.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
import sys
import os
from typing import Dict
from corrected_franchise_mapping import CorrectedFranchiseMapper


def validate_relocation_analysis_readiness(df_path: str = 'team_seasons_analysis_ready.csv') -> Dict:
    """Validate if data is ready for statistical relocation analysis."""
    
    if not os.path.exists(df_path):
        return {'status': 'error', 'message': 'Analysis-ready dataset not found. Run corrected_franchise_mapping.py first.'}
    
    df = pd.read_csv(df_path)
    mapper = CorrectedFranchiseMapper()
    
    validation = {
        'status': 'success',
        'total_seasons': len(df),
        'relocated_franchises': [],
        'statistical_power': {},
        'data_quality_issues': [],
        'recommendations': []
    }
    
    # Analyze each relocated franchise
    for canonical_id in mapper.get_relocated_franchises():
        franchise_data = df[df['canonical_franchise'] == canonical_id]
        
        if franchise_data.empty:
            continue
        
        lineage = mapper.get_franchise_info(canonical_id)
        latest_relocation = max(lineage.relocations, key=lambda x: x.year)
        
        pre_data = franchise_data[franchise_data['pre_relocation'] == True]
        post_data = franchise_data[franchise_data['post_relocation'] == True]
        
        franchise_analysis = {
            'franchise': canonical_id,
            'name': lineage.current_name,
            'relocation_year': latest_relocation.year,
            'pre_seasons': len(pre_data),
            'post_seasons': len(post_data),
            'pre_avg_wpct': pre_data['W_pct'].mean() if not pre_data.empty else None,
            'post_avg_wpct': post_data['W_pct'].mean() if not post_data.empty else None,
            'pre_std': pre_data['W_pct'].std() if not pre_data.empty else None,
            'post_std': post_data['W_pct'].std() if not post_data.empty else None,
            'sufficient_for_ttest': len(pre_data) >= 10 and len(post_data) >= 10,
            'years_since_relocation': post_data['years_since_relocation'].max() if not post_data.empty else 0
        }
        
        # Calculate effect size (Cohen's d) if both periods have data
        if franchise_analysis['pre_avg_wpct'] is not None and franchise_analysis['post_avg_wpct'] is not None:
            pooled_std = np.sqrt(((len(pre_data) - 1) * pre_data['W_pct'].var() + 
                                 (len(post_data) - 1) * post_data['W_pct'].var()) / 
                                (len(pre_data) + len(post_data) - 2))
            
            if pooled_std > 0:
                cohens_d = (franchise_analysis['post_avg_wpct'] - franchise_analysis['pre_avg_wpct']) / pooled_std
                franchise_analysis['effect_size'] = cohens_d
                franchise_analysis['effect_magnitude'] = (
                    'large' if abs(cohens_d) >= 0.8 else
                    'medium' if abs(cohens_d) >= 0.5 else
                    'small' if abs(cohens_d) >= 0.2 else
                    'negligible'
                )
            else:
                franchise_analysis['effect_size'] = None
                franchise_analysis['effect_magnitude'] = 'unknown'
        
        validation['relocated_franchises'].append(franchise_analysis)
    
    # Overall statistical power assessment
    sufficient_franchises = [f for f in validation['relocated_franchises'] if f['sufficient_for_ttest']]
    
    validation['statistical_power'] = {
        'total_relocated_franchises': len(validation['relocated_franchises']),
        'sufficient_data_franchises': len(sufficient_franchises),
        'insufficient_data_franchises': len(validation['relocated_franchises']) - len(sufficient_franchises),
        'ready_for_meta_analysis': len(sufficient_franchises) >= 5,
        'avg_pre_seasons': np.mean([f['pre_seasons'] for f in sufficient_franchises]) if sufficient_franchises else 0,
        'avg_post_seasons': np.mean([f['post_seasons'] for f in sufficient_franchises]) if sufficient_franchises else 0
    }
    
    # Identify data quality issues
    if validation['statistical_power']['insufficient_data_franchises'] > 0:
        validation['data_quality_issues'].append(
            f"{validation['statistical_power']['insufficient_data_franchises']} franchises have insufficient data for robust t-tests"
        )
    
    # Check for very recent relocations
    recent_relocations = [f for f in validation['relocated_franchises'] if f['years_since_relocation'] < 10]
    if recent_relocations:
        validation['data_quality_issues'].append(
            f"{len(recent_relocations)} franchises have recent relocations with limited post-relocation data"
        )
    
    # Generate recommendations
    if validation['statistical_power']['ready_for_meta_analysis']:
        validation['recommendations'].append("Dataset is ready for meta-analysis of relocation effects")
    else:
        validation['recommendations'].append("Consider including more franchises or historical data for stronger meta-analysis")
    
    if validation['statistical_power']['insufficient_data_franchises'] > 0:
        validation['recommendations'].append("Consider excluding franchises with insufficient data from primary analysis")
    
    validation['recommendations'].extend([
        "Use paired t-tests for individual franchise analysis",
        "Consider time-series analysis to account for temporal trends",
        "Control for era effects (deadball era, expansion era, etc.)",
        "Validate results against known historical context"
    ])
    
    return validation


def print_validation_report(validation: Dict):
    """Print comprehensive validation report."""
    
    print("FINAL DATA VALIDATION REPORT")
    print("=" * 60)
    print(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("DATASET OVERVIEW:")
    print(f"  Total seasons: {validation['total_seasons']:,}")
    print(f"  Relocated franchises: {validation['statistical_power']['total_relocated_franchises']}")
    print(f"  Franchises with sufficient data: {validation['statistical_power']['sufficient_data_franchises']}")
    print()
    
    print("STATISTICAL POWER ANALYSIS:")
    print(f"  Ready for meta-analysis: {validation['statistical_power']['ready_for_meta_analysis']}")
    print(f"  Average pre-relocation seasons: {validation['statistical_power']['avg_pre_seasons']:.1f}")
    print(f"  Average post-relocation seasons: {validation['statistical_power']['avg_post_seasons']:.1f}")
    print()
    
    print("FRANCHISE-LEVEL ANALYSIS:")
    print("-" * 40)
    
    for franchise in validation['relocated_franchises']:
        status = "[SUFFICIENT]" if franchise['sufficient_for_ttest'] else "[INSUFFICIENT]"
        effect = franchise.get('effect_magnitude', 'unknown')
        
        print(f"{status} {franchise['franchise']} ({franchise['name']})")
        print(f"  Relocation: {franchise['relocation_year']} ({franchise['from_city']} → {franchise['to_city']})")
        print(f"  Data: {franchise['pre_seasons']} pre + {franchise['post_seasons']} post seasons")
        
        if franchise['pre_avg_wpct'] is not None and franchise['post_avg_wpct'] is not None:
            change = franchise['post_avg_wpct'] - franchise['pre_avg_wpct']
            direction = "improved" if change > 0 else "declined" if change < 0 else "unchanged"
            print(f"  Performance: {direction} by {abs(change):.3f} ({effect} effect)")
        
        print()
    
    if validation['data_quality_issues']:
        print("DATA QUALITY ISSUES:")
        for issue in validation['data_quality_issues']:
            print(f"  - {issue}")
        print()
    
    print("RECOMMENDATIONS:")
    for i, rec in enumerate(validation['recommendations'], 1):
        print(f"  {i}. {rec}")


def main():
    """Run final validation and generate recommendations."""
    
    # Change to correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    
    # Check if analysis-ready data exists
    if not os.path.exists('team_seasons_analysis_ready.csv'):
        print("Analysis-ready dataset not found. Generating...")
        
        # Import and run the corrected mapping
        import sys
        sys.path.append('scripts')
        from corrected_franchise_mapping import CorrectedFranchiseMapper
        
        if not os.path.exists('team_seasons.csv'):
            print("Error: team_seasons.csv not found. Please run gather_mlb_wl.py first.")
            return 1
        
        df = pd.read_csv('team_seasons.csv')
        mapper = CorrectedFranchiseMapper()
        analysis_data = mapper.get_analysis_ready_data(df)
        analysis_data.to_csv('team_seasons_analysis_ready.csv', index=False)
        print("Generated team_seasons_analysis_ready.csv")
    
    # Run validation
    validation = validate_relocation_analysis_readiness()
    
    # Print report
    print_validation_report(validation)
    
    # Save validation results
    validation_df = pd.DataFrame(validation['relocated_franchises'])
    validation_df.to_csv('franchise_validation_results.csv', index=False)
    
    print(f"\n[SUCCESS] Validation results saved to: franchise_validation_results.csv")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())