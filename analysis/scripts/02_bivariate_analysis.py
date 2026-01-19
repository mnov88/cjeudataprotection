#!/usr/bin/env python3
"""
02_bivariate_analysis.py
========================
Bivariate analysis of factors associated with pro-data subject rulings.

Tests pre-specified hypotheses using chi-square tests with FDR correction.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def cramers_v(contingency_table):
    """Calculate Cramér's V effect size for chi-square test."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    if min_dim == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))

def phi_coefficient(contingency_table):
    """Calculate Phi coefficient for 2x2 tables."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    return np.sqrt(chi2 / n)

def chi_square_test(df, iv_col, dv_col='pro_ds'):
    """Perform chi-square test and return results dict."""
    contingency = pd.crosstab(df[iv_col], df[dv_col])

    # Use Fisher's exact for 2x2 tables with small expected counts
    if contingency.shape == (2, 2):
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        min_expected = expected.min()

        if min_expected < 5:
            # Fisher's exact test
            odds_ratio, p_fisher = stats.fisher_exact(contingency)
            effect = phi_coefficient(contingency)
            test_used = "Fisher's exact"
            p = p_fisher
        else:
            effect = phi_coefficient(contingency)
            test_used = "Chi-square"
    else:
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        min_expected = expected.min()
        effect = cramers_v(contingency)
        test_used = "Chi-square"

    # Calculate proportions for interpretation
    prop_table = contingency.div(contingency.sum(axis=1), axis=0)

    return {
        'variable': iv_col,
        'test': test_used,
        'chi2': chi2 if test_used == "Chi-square" else np.nan,
        'p_value': p,
        'effect_size': effect,
        'effect_type': 'Phi' if contingency.shape == (2, 2) else "Cramér's V",
        'n': len(df),
        'contingency': contingency.to_dict(),
        'proportions': prop_table.to_dict(),
        'min_expected': min_expected if 'min_expected' in dir() else np.nan
    }

def mann_whitney_test(df, iv_col, dv_col='pro_ds'):
    """Perform Mann-Whitney U test for continuous/count variables."""
    group0 = df[df[dv_col] == 0][iv_col].dropna()
    group1 = df[df[dv_col] == 1][iv_col].dropna()

    stat, p = stats.mannwhitneyu(group0, group1, alternative='two-sided')

    # Calculate rank-biserial correlation as effect size
    n1, n2 = len(group0), len(group1)
    r = 1 - (2 * stat) / (n1 * n2)

    return {
        'variable': iv_col,
        'test': 'Mann-Whitney U',
        'statistic': stat,
        'p_value': p,
        'effect_size': abs(r),
        'effect_type': 'rank-biserial r',
        'mean_pro_ds': group1.mean(),
        'mean_other': group0.mean(),
        'n': len(group0) + len(group1)
    }

def fdr_correction(p_values, alpha=0.05):
    """Benjamini-Hochberg FDR correction."""
    p_values = np.array(p_values)
    n = len(p_values)
    ranked = np.argsort(p_values)
    q_values = np.zeros(n)

    for i, idx in enumerate(ranked):
        q_values[idx] = p_values[idx] * n / (i + 1)

    # Ensure monotonicity
    q_values = np.minimum.accumulate(q_values[np.argsort(ranked)[::-1]])[::-1]
    q_values = np.minimum(q_values, 1.0)

    return q_values

def run_bivariate_analysis(df):
    """Run all bivariate hypothesis tests."""

    print("=" * 70)
    print("BIVARIATE ANALYSIS: PRO-DATA SUBJECT RULING PREDICTORS")
    print("=" * 70)

    results = []
    hypotheses = []

    # =========================================================================
    # HYPOTHESIS GROUP 1: INTERPRETIVE SOURCES
    # =========================================================================
    print("\n" + "-" * 70)
    print("H1-H2: INTERPRETIVE SOURCES")
    print("-" * 70)

    # H1: Teleological interpretation → pro-DS (+)
    h1 = chi_square_test(df, 'teleological_present')
    h1['hypothesis'] = 'H1'
    h1['description'] = 'Teleological interpretation predicts pro-DS'
    h1['expected'] = '+'
    results.append(h1)

    prop_tele = df.groupby('teleological_present')['pro_ds'].mean()
    print(f"\nH1: Teleological Interpretation → Pro-DS")
    print(f"    Teleological present:  {prop_tele.get(1, 0)*100:.1f}% pro-DS (n={df['teleological_present'].sum()})")
    print(f"    Teleological absent:   {prop_tele.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['teleological_present'].sum()})")
    print(f"    Φ = {h1['effect_size']:.3f}, p = {h1['p_value']:.4f}")

    # H2: Dominant semantic → pro-controller (-)
    h2 = chi_square_test(df, 'dominant_source')
    h2['hypothesis'] = 'H2'
    h2['description'] = 'Dominant interpretive source affects ruling direction'
    h2['expected'] = 'Semantic = fewer pro-DS'
    results.append(h2)

    prop_dom = df.groupby('dominant_source')['pro_ds'].mean()
    print(f"\nH2: Dominant Source → Ruling Direction")
    for source in ['TELEOLOGICAL', 'SYSTEMATIC', 'SEMANTIC', 'UNCLEAR']:
        if source in prop_dom.index:
            n = (df['dominant_source'] == source).sum()
            print(f"    {source}: {prop_dom[source]*100:.1f}% pro-DS (n={n})")
    print(f"    Cramér's V = {h2['effect_size']:.3f}, p = {h2['p_value']:.4f}")

    # Additional: Pro-DS teleological purposes
    h2b = chi_square_test(df, 'pro_ds_purpose')
    h2b['hypothesis'] = 'H2b'
    h2b['description'] = 'HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS purpose invoked'
    h2b['expected'] = '+'
    results.append(h2b)

    prop_purpose = df.groupby('pro_ds_purpose')['pro_ds'].mean()
    print(f"\nH2b: Pro-DS Purpose (HIGH_PROTECTION/FUNDAMENTAL_RIGHTS) → Pro-DS")
    print(f"    Purpose invoked:     {prop_purpose.get(1, 0)*100:.1f}% pro-DS (n={df['pro_ds_purpose'].sum()})")
    print(f"    Purpose not invoked: {prop_purpose.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['pro_ds_purpose'].sum()})")
    print(f"    Φ = {h2b['effect_size']:.3f}, p = {h2b['p_value']:.4f}")

    # =========================================================================
    # HYPOTHESIS GROUP 2: REASONING STRUCTURE
    # =========================================================================
    print("\n" + "-" * 70)
    print("H3-H4: REASONING STRUCTURE")
    print("-" * 70)

    # H3: Principle-based reasoning → pro-DS (+)
    h3 = chi_square_test(df, 'principle_based_present')
    h3['hypothesis'] = 'H3'
    h3['description'] = 'Principle-based reasoning predicts pro-DS'
    h3['expected'] = '+'
    results.append(h3)

    prop_princ = df.groupby('principle_based_present')['pro_ds'].mean()
    print(f"\nH3: Principle-Based Reasoning → Pro-DS")
    print(f"    Principle present:  {prop_princ.get(1, 0)*100:.1f}% pro-DS (n={df['principle_based_present'].sum()})")
    print(f"    Principle absent:   {prop_princ.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['principle_based_present'].sum()})")
    print(f"    Φ = {h3['effect_size']:.3f}, p = {h3['p_value']:.4f}")

    # H4: Level shifting → pro-DS (+)
    h4 = chi_square_test(df, 'level_shifting')
    h4['hypothesis'] = 'H4'
    h4['description'] = 'Level-shifting predicts pro-DS'
    h4['expected'] = '+'
    results.append(h4)

    prop_shift = df.groupby('level_shifting')['pro_ds'].mean()
    print(f"\nH4: Level-Shifting → Pro-DS")
    print(f"    Level-shifting:    {prop_shift.get(1, 0)*100:.1f}% pro-DS (n={df['level_shifting'].sum()})")
    print(f"    No level-shifting: {prop_shift.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['level_shifting'].sum()})")
    print(f"    Φ = {h4['effect_size']:.3f}, p = {h4['p_value']:.4f}")

    # Dominant reasoning structure
    h4b = chi_square_test(df, 'dominant_structure')
    h4b['hypothesis'] = 'H4b'
    h4b['description'] = 'Dominant reasoning structure affects ruling direction'
    h4b['expected'] = 'PRINCIPLE_BASED = more pro-DS'
    results.append(h4b)

    prop_struct = df.groupby('dominant_structure')['pro_ds'].mean()
    print(f"\nH4b: Dominant Structure → Ruling Direction")
    for struct in ['PRINCIPLE_BASED', 'CASE_LAW_BASED', 'RULE_BASED', 'MIXED']:
        if struct in prop_struct.index:
            n = (df['dominant_structure'] == struct).sum()
            print(f"    {struct}: {prop_struct[struct]*100:.1f}% pro-DS (n={n})")
    print(f"    Cramér's V = {h4b['effect_size']:.3f}, p = {h4b['p_value']:.4f}")

    # =========================================================================
    # HYPOTHESIS GROUP 3: INSTITUTIONAL & CONCEPTUAL
    # =========================================================================
    print("\n" + "-" * 70)
    print("H5-H6: INSTITUTIONAL & CONCEPTUAL FACTORS")
    print("-" * 70)

    # H5: Grand Chamber → pro-DS (+)
    df['is_grand_chamber'] = (df['chamber'] == 'GRAND_CHAMBER').astype(int)
    h5 = chi_square_test(df, 'is_grand_chamber')
    h5['hypothesis'] = 'H5'
    h5['description'] = 'Grand Chamber predicts pro-DS'
    h5['expected'] = '+'
    results.append(h5)

    prop_gc = df.groupby('is_grand_chamber')['pro_ds'].mean()
    print(f"\nH5: Grand Chamber → Pro-DS")
    print(f"    Grand Chamber:     {prop_gc.get(1, 0)*100:.1f}% pro-DS (n={df['is_grand_chamber'].sum()})")
    print(f"    Other chambers:    {prop_gc.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['is_grand_chamber'].sum()})")
    print(f"    Φ = {h5['effect_size']:.3f}, p = {h5['p_value']:.4f}")

    # Chamber detailed
    h5b = chi_square_test(df, 'chamber_grouped')
    h5b['hypothesis'] = 'H5b'
    h5b['description'] = 'Chamber composition affects ruling direction'
    h5b['expected'] = 'Varies by chamber'
    results.append(h5b)

    prop_chamber = df.groupby('chamber_grouped')['pro_ds'].mean().sort_values(ascending=False)
    print(f"\nH5b: Chamber (grouped) → Ruling Direction")
    for chamber in prop_chamber.index:
        n = (df['chamber_grouped'] == chamber).sum()
        print(f"    {chamber}: {prop_chamber[chamber]*100:.1f}% pro-DS (n={n})")
    print(f"    Cramér's V = {h5b['effect_size']:.3f}, p = {h5b['p_value']:.4f}")

    # H6: Concept cluster
    h6 = chi_square_test(df, 'concept_cluster')
    h6['hypothesis'] = 'H6'
    h6['description'] = 'Primary concept cluster affects ruling direction'
    h6['expected'] = 'RIGHTS cluster = more pro-DS'
    results.append(h6)

    prop_concept = df.groupby('concept_cluster')['pro_ds'].mean().sort_values(ascending=False)
    print(f"\nH6: Concept Cluster → Ruling Direction")
    for cluster in prop_concept.index:
        n = (df['concept_cluster'] == cluster).sum()
        print(f"    {cluster}: {prop_concept[cluster]*100:.1f}% pro-DS (n={n})")
    print(f"    Cramér's V = {h6['effect_size']:.3f}, p = {h6['p_value']:.4f}")

    # =========================================================================
    # HYPOTHESIS GROUP 4: BALANCING ANALYSIS
    # =========================================================================
    print("\n" + "-" * 70)
    print("H7-H9: BALANCING ANALYSIS")
    print("-" * 70)

    # H7: Any balancing → pro-controller (-)
    h7 = chi_square_test(df, 'any_balancing')
    h7['hypothesis'] = 'H7'
    h7['description'] = 'Explicit balancing predicts fewer pro-DS outcomes'
    h7['expected'] = '-'
    results.append(h7)

    prop_bal = df.groupby('any_balancing')['pro_ds'].mean()
    print(f"\nH7: Any Balancing → Pro-DS")
    print(f"    Balancing present:  {prop_bal.get(1, 0)*100:.1f}% pro-DS (n={df['any_balancing'].sum()})")
    print(f"    No balancing:       {prop_bal.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['any_balancing'].sum()})")
    print(f"    Φ = {h7['effect_size']:.3f}, p = {h7['p_value']:.4f}")

    # H8: Necessity discussed → pro-controller (-)
    h8 = chi_square_test(df, 'necessity_discussed')
    h8['hypothesis'] = 'H8'
    h8['description'] = 'Necessity analysis predicts fewer pro-DS outcomes'
    h8['expected'] = '-'
    results.append(h8)

    prop_nec = df.groupby('necessity_discussed')['pro_ds'].mean()
    print(f"\nH8: Necessity Discussed → Pro-DS")
    print(f"    Necessity discussed:    {prop_nec.get(1, 0)*100:.1f}% pro-DS (n={df['necessity_discussed'].sum()})")
    print(f"    Necessity not discussed:{prop_nec.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['necessity_discussed'].sum()})")
    print(f"    Φ = {h8['effect_size']:.3f}, p = {h8['p_value']:.4f}")

    # H9: Necessity standard
    # Only among cases where necessity is discussed
    df_nec = df[df['necessity_discussed'] == 1].copy()
    if len(df_nec) > 10:
        h9 = chi_square_test(df_nec, 'necessity_standard')
        h9['hypothesis'] = 'H9'
        h9['description'] = 'Strict necessity standard predicts fewer pro-DS'
        h9['expected'] = 'STRICT = fewer pro-DS'
        results.append(h9)

        prop_std = df_nec.groupby('necessity_standard')['pro_ds'].mean()
        print(f"\nH9: Necessity Standard → Pro-DS (among cases where necessity discussed, n={len(df_nec)})")
        for std in ['STRICT', 'REGULAR', 'NONE']:
            if std in prop_std.index:
                n = (df_nec['necessity_standard'] == std).sum()
                print(f"    {std}: {prop_std[std]*100:.1f}% pro-DS (n={n})")
        print(f"    Cramér's V = {h9['effect_size']:.3f}, p = {h9['p_value']:.4f}")

    # =========================================================================
    # ADDITIONAL EXPLORATORY TESTS
    # =========================================================================
    print("\n" + "-" * 70)
    print("EXPLORATORY ANALYSES")
    print("-" * 70)

    # Case law citations
    h10 = chi_square_test(df, 'has_case_citations')
    h10['hypothesis'] = 'E1'
    h10['description'] = 'Case law citation predicts ruling direction'
    h10['expected'] = 'Exploratory'
    results.append(h10)

    prop_cite = df.groupby('has_case_citations')['pro_ds'].mean()
    print(f"\nE1: Case Law Citations → Pro-DS")
    print(f"    Has citations:  {prop_cite.get(1, 0)*100:.1f}% pro-DS (n={df['has_case_citations'].sum()})")
    print(f"    No citations:   {prop_cite.get(0, 0)*100:.1f}% pro-DS (n={len(df) - df['has_case_citations'].sum()})")
    print(f"    Φ = {h10['effect_size']:.3f}, p = {h10['p_value']:.4f}")

    # Interpretation count (complexity)
    h11 = mann_whitney_test(df, 'interpretation_count')
    h11['hypothesis'] = 'E2'
    h11['description'] = 'Interpretive plurality and ruling direction'
    h11['expected'] = 'Exploratory'
    results.append(h11)

    print(f"\nE2: Interpretation Count → Pro-DS")
    print(f"    Mean interpretation count (pro-DS): {h11['mean_pro_ds']:.2f}")
    print(f"    Mean interpretation count (other):  {h11['mean_other']:.2f}")
    print(f"    rank-biserial r = {h11['effect_size']:.3f}, p = {h11['p_value']:.4f}")

    # Year trend
    h12 = mann_whitney_test(df, 'year')
    h12['hypothesis'] = 'E3'
    h12['description'] = 'Temporal trend in ruling direction'
    h12['expected'] = 'Exploratory'
    results.append(h12)

    print(f"\nE3: Year → Pro-DS")
    print(f"    Mean year (pro-DS): {h12['mean_pro_ds']:.1f}")
    print(f"    Mean year (other):  {h12['mean_other']:.1f}")
    print(f"    rank-biserial r = {h12['effect_size']:.3f}, p = {h12['p_value']:.4f}")

    # =========================================================================
    # FDR CORRECTION
    # =========================================================================
    print("\n" + "=" * 70)
    print("FDR-CORRECTED RESULTS SUMMARY")
    print("=" * 70)

    # Extract p-values and apply FDR correction
    p_values = [r['p_value'] for r in results]
    q_values = fdr_correction(p_values)

    # Add q-values to results
    for i, r in enumerate(results):
        r['q_value'] = q_values[i]
        r['significant_fdr'] = q_values[i] < 0.05

    # Create summary table
    summary_data = []
    for r in results:
        summary_data.append({
            'Hypothesis': r['hypothesis'],
            'Variable': r['variable'],
            'Description': r['description'],
            'Effect Size': f"{r['effect_size']:.3f}",
            'p-value': f"{r['p_value']:.4f}",
            'q-value (FDR)': f"{r['q_value']:.4f}",
            'Significant': '***' if r['q_value'] < 0.001 else ('**' if r['q_value'] < 0.01 else ('*' if r['q_value'] < 0.05 else ''))
        })

    summary_df = pd.DataFrame(summary_data)
    print("\n" + summary_df.to_string(index=False))

    # Count significant results
    n_sig = sum(1 for r in results if r['significant_fdr'])
    print(f"\n{n_sig} of {len(results)} tests significant at FDR q < 0.05")

    # Save results
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Save summary table
    summary_df.to_csv(OUTPUT_PATH / "bivariate_summary.csv", index=False)

    # Save detailed results
    results_clean = []
    for r in results:
        r_clean = {k: v for k, v in r.items() if k not in ['contingency', 'proportions']}
        results_clean.append(r_clean)

    with open(OUTPUT_PATH / "bivariate_results.json", 'w') as f:
        json.dump(results_clean, f, indent=2, default=str)

    print(f"\nResults saved to {OUTPUT_PATH}")

    return results, summary_df

if __name__ == "__main__":
    # Load prepared data
    df = pd.read_csv(DATA_PATH)
    results, summary_df = run_bivariate_analysis(df)
    print("\nBivariate analysis complete!")
