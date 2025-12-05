# Quick Comparison Cell - Add this to scorer.ipynb after loading DATASET_REW
# This checks which columns are identical between original and rewrites

import numpy as np

def quick_compare(original_df, rewrite_df, rewrite_id):
    """Quick comparison showing identical vs different columns."""
    common_cols = set(original_df.columns) & set(rewrite_df.columns)
    
    # Exclude text columns from comparison
    skip_cols = {'text', 'rewritten_text', 'content_preserved', 'full_text', 'text_tokens'}
    compare_cols = common_cols - skip_cols
    
    # Find identical columns
    identical = []
    different = []
    
    for col in compare_cols:
        try:
            orig = original_df[col].values
            rew = rewrite_df[col].values
            
            if original_df[col].dtype in ['float64', 'float32']:
                is_same = np.allclose(orig, rew, rtol=1e-6, atol=1e-6, equal_nan=True)
            else:
                is_same = np.array_equal(orig, rew)
            
            if is_same:
                identical.append(col)
            else:
                different.append(col)
        except:
            pass
    
    # Categorize
    style_identical = [c for c in identical if c.startswith(('taaled_', 'taaco_', 'taassc_'))]
    metadata_identical = [c for c in identical if any(c.startswith(x) for x in 
                          ['gender_', 'grade_', 'race_', 'economically_', 'prompt', 'holistic', 'cv_fold', 'paper_id'])]
    other_identical = [c for c in identical if c not in style_identical and c not in metadata_identical]
    
    print(f"\n{'='*70}")
    print(f"Rewrite {rewrite_id} vs Original")
    print(f"{'='*70}")
    print(f"Total columns compared: {len(compare_cols)}")
    print(f"  ├─ Identical: {len(identical)} ({len(identical)/len(compare_cols)*100:.1f}%)")
    print(f"  └─ Different: {len(different)} ({len(different)/len(compare_cols)*100:.1f}%)")
    
    print(f"\n📊 BREAKDOWN:")
    print(f"  Metadata (expected same): {len(metadata_identical)}")
    print(f"  Style features (SHOULD be different): {len(style_identical)} {'❌' if style_identical else '✅'}")
    print(f"  Other identical: {len(other_identical)}")
    
    if style_identical:
        print(f"\n❌ PROBLEM - These style features are IDENTICAL:")
        for col in sorted(style_identical)[:15]:
            print(f"     {col}")
        if len(style_identical) > 15:
            print(f"     ... and {len(style_identical)-15} more")
        print(f"\n   This is DATA LEAKAGE - style features should change with rewrites!")
    
    return {
        'identical': len(identical),
        'different': len(different),
        'style_identical': len(style_identical),
        'problematic': style_identical
    }

# Run comparison for all rewrites
print("\n" + "="*70)
print("COMPARING ORIGINAL vs REWRITES")
print("="*70)

results = {}
for i in range(1, 7):
    if i in DATASET_REW:
        results[i] = quick_compare(DATASET_REW['original'], DATASET_REW[i], i)

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"{'Rewrite':<10} {'Same Cols':<12} {'Diff Cols':<12} {'Style Same':<15}")
print("-"*70)
for i in range(1, 7):
    if i in results:
        r = results[i]
        status = "❌ LEAK" if r['style_identical'] > 0 else "✅ OK"
        print(f"{i:<10} {r['identical']:<12} {r['different']:<12} {r['style_identical']:<15} {status}")
