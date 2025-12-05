"""
Diagnostic script to compare DATASET_REW dataframes and identify
identical columns between original and rewritten texts.

This helps identify potential data leakage if style features are unchanged.
"""

import numpy as np
import pandas as pd

def compare_dataframes(original_df, rewrite_df, rewrite_name, tolerance=1e-6):
    """
    Compare two dataframes and return columns that are identical.
    
    Parameters:
    -----------
    original_df : pd.DataFrame
        The original dataset
    rewrite_df : pd.DataFrame
        The rewritten dataset
    rewrite_name : str
        Name/ID of the rewrite (for display)
    tolerance : float
        Tolerance for numerical comparison
    
    Returns:
    --------
    dict : Dictionary with comparison results
    """
    # Get common columns
    common_cols = set(original_df.columns) & set(rewrite_df.columns)
    
    # Columns to exclude from comparison (expected to be identical)
    expected_identical = {
        'paper_id', 'cv_fold', 'prompt_name', 'holistic_essay_score',
        'gender_F', 'gender_M', 'race_ethnicity_White', 
        'economically_disadvantaged_1', 'economically_disadvantaged_0'
    }
    # Add grade level columns
    expected_identical.update([col for col in common_cols if col.startswith('grade_level_')])
    
    # Columns that should be different (the key ones to check)
    style_features = [col for col in common_cols if (
        col.startswith('taaled_') or 
        col.startswith('taaco_') or 
        col.startswith('taassc_')
    )]
    
    # Compare each column
    identical_cols = []
    different_cols = []
    problematic_cols = []  # Style features that are identical (bad!)
    
    for col in common_cols:
        if col in ['text', 'rewritten_text', 'content_preserved', 'full_text', 'text_tokens']:
            continue  # Skip text columns
        
        try:
            # Get values
            orig_vals = original_df[col].values
            rew_vals = rewrite_df[col].values
            
            # Check if identical
            if original_df[col].dtype in ['float64', 'float32']:
                is_identical = np.allclose(orig_vals, rew_vals, rtol=tolerance, atol=tolerance, equal_nan=True)
            else:
                is_identical = np.array_equal(orig_vals, rew_vals)
            
            if is_identical:
                identical_cols.append(col)
                # Check if this is a style feature (problematic!)
                if col in style_features:
                    problematic_cols.append(col)
            else:
                different_cols.append(col)
                
        except Exception as e:
            print(f"Error comparing column {col}: {e}")
    
    # Categorize identical columns
    expected_and_identical = [col for col in identical_cols if col in expected_identical]
    unexpected_identical = [col for col in identical_cols if col not in expected_identical]
    
    return {
        'rewrite_name': rewrite_name,
        'total_common_cols': len(common_cols),
        'identical_cols': identical_cols,
        'different_cols': different_cols,
        'expected_identical': expected_and_identical,
        'unexpected_identical': unexpected_identical,
        'problematic_style_cols': problematic_cols,
        'style_features_total': len(style_features),
        'style_features_identical': len(problematic_cols),
        'style_features_different': len([col for col in style_features if col in different_cols])
    }


def print_comparison_report(comparison):
    """Print a formatted comparison report."""
    print(f"\n{'='*80}")
    print(f"COMPARISON: Original vs {comparison['rewrite_name']}")
    print(f"{'='*80}")
    
    print(f"\nTotal common columns: {comparison['total_common_cols']}")
    print(f"  ├─ Identical: {len(comparison['identical_cols'])} ({len(comparison['identical_cols'])/comparison['total_common_cols']*100:.1f}%)")
    print(f"  └─ Different: {len(comparison['different_cols'])} ({len(comparison['different_cols'])/comparison['total_common_cols']*100:.1f}%)")
    
    print(f"\n📊 STYLE FEATURES (TAALED/TAACO/TAASSC):")
    print(f"  ├─ Total: {comparison['style_features_total']}")
    print(f"  ├─ Identical: {comparison['style_features_identical']} ⚠️")
    print(f"  └─ Different: {comparison['style_features_different']} ✓")
    
    if comparison['problematic_style_cols']:
        print(f"\n❌ PROBLEM: These style features are IDENTICAL (should be different!):")
        for col in sorted(comparison['problematic_style_cols'])[:20]:  # Show first 20
            print(f"     - {col}")
        if len(comparison['problematic_style_cols']) > 20:
            print(f"     ... and {len(comparison['problematic_style_cols']) - 20} more")
    else:
        print(f"\n✅ GOOD: All style features are different!")
    
    if comparison['unexpected_identical']:
        print(f"\n⚠️  UNEXPECTED: These non-metadata columns are identical:")
        for col in sorted(comparison['unexpected_identical'])[:10]:
            print(f"     - {col}")
        if len(comparison['unexpected_identical']) > 10:
            print(f"     ... and {len(comparison['unexpected_identical']) - 10} more")
    
    print(f"\n✓ Expected identical (metadata): {len(comparison['expected_identical'])} columns")
    

# ============================================================================
# MAIN COMPARISON RUNNER
# ============================================================================

def run_full_comparison(DATASET_REW):
    """Run comparison for all rewrites against original."""
    
    original = DATASET_REW['original']
    
    print("\n" + "="*80)
    print("DATASET_REW COMPARISON ANALYSIS")
    print("Checking which variables are identical between original and rewrites")
    print("="*80)
    
    all_comparisons = []
    
    for key in [1, 2, 3, 4, 5, 6]:
        if key not in DATASET_REW:
            print(f"\n⚠️  Rewrite {key} not found in DATASET_REW")
            continue
        
        comparison = compare_dataframes(original, DATASET_REW[key], f"Rewrite {key}")
        all_comparisons.append(comparison)
        print_comparison_report(comparison)
    
    # Summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print(f"{'Rewrite':<10} {'Total Cols':<12} {'Identical':<12} {'Different':<12} {'Style Same':<12} {'Style Diff':<12}")
    print("-"*80)
    
    for comp in all_comparisons:
        print(f"{comp['rewrite_name']:<10} "
              f"{comp['total_common_cols']:<12} "
              f"{len(comp['identical_cols']):<12} "
              f"{len(comp['different_cols']):<12} "
              f"{comp['style_features_identical']:<12} "
              f"{comp['style_features_different']:<12}")
    
    # Overall assessment
    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)
    
    total_problematic = sum(comp['style_features_identical'] for comp in all_comparisons)
    
    if total_problematic > 0:
        print("❌ DATA LEAKAGE DETECTED!")
        print(f"   Found {total_problematic} total instances of identical style features.")
        print(f"   This explains the overfitting - models see the same features for")
        print(f"   'different' texts, making it easy to memorize patterns.")
        print(f"\n   CAUSE: The text rewrites may not have been re-analyzed for style features.")
        print(f"   FIX: Re-compute TAALED/TAACO/TAASSC features for all rewritten texts.")
    else:
        print("✅ No obvious data leakage from identical style features.")
        print("   The overfitting issue may be due to:")
        print("   - cv_fold not properly assigned (check our previous fix)")
        print("   - Embeddings being too similar between original and rewrites")
        print("   - Other shared features not caught by this analysis")
    
    return all_comparisons


if __name__ == "__main__":
    print("This script is meant to be imported in scorer.ipynb")
    print("Usage:")
    print("  from compare_original_vs_rewrites import run_full_comparison")
    print("  comparisons = run_full_comparison(DATASET_REW)")
