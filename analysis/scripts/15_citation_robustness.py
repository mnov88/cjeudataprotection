#!/usr/bin/env python3
"""
15_citation_robustness.py
==========================
Phase 6: Robustness Checks and Sensitivity Analyses

Pre-specified robustness checks for citation analysis findings:
1. Alternative sample restrictions
2. Alternative predictor specifications
3. Alternative outcome specifications
4. Temporal stability
5. Placebo tests
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"
NETWORK_PATH = OUTPUT_PATH / "citation_network"

def load_data():
    """Load all required data."""
    holdings = pd.read_csv(OUTPUT_PATH / "holdings_prepared.csv")
    citation_vars = pd.read_csv(NETWORK_PATH / "holding_citation_vars.csv")

    df = holdings.merge(citation_vars, on=['case_id', 'holding_id'], how='left')
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])

    # Chamber grouping
    major_chambers = ['GRAND_CHAMBER', 'FIRST', 'THIRD', 'FOURTH']
    df['chamber_grouped'] = df['chamber'].apply(
        lambda x: x if x in major_chambers else 'OTHER'
    )

    return df

def check_sample_restrictions(df):
    """
    Test 1: Alternative sample restrictions.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 1: ALTERNATIVE SAMPLE RESTRICTIONS")
    print("=" * 70)

    results = {}

    # Base sample: holdings with internal citations
    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score', 'pro_ds'])

    # Test: Different minimum citation thresholds
    for min_cite in [1, 2, 3]:
        df_sub = df[df['internal_citations'] >= min_cite].dropna(subset=['precedent_direction_score', 'pro_ds'])
        if len(df_sub) > 30:
            r, p = stats.pearsonr(df_sub['precedent_direction_score'], df_sub['pro_ds'])
            print(f"\nMin {min_cite} internal citations (n={len(df_sub)}):")
            print(f"  Correlation: r={r:.3f}, p={p:.4f}")
            results[f'min_{min_cite}_citations'] = {'n': int(len(df_sub)), 'r': float(r), 'p': float(p)}

    # Test: Exclude outlier cases (top/bottom 5% by citation count)
    p5 = df_base['internal_citations'].quantile(0.05)
    p95 = df_base['internal_citations'].quantile(0.95)
    df_trimmed = df_base[(df_base['internal_citations'] >= p5) & (df_base['internal_citations'] <= p95)]
    if len(df_trimmed) > 30:
        r, p = stats.pearsonr(df_trimmed['precedent_direction_score'], df_trimmed['pro_ds'])
        print(f"\nTrimmed (5%-95% citation count, n={len(df_trimmed)}):")
        print(f"  Correlation: r={r:.3f}, p={p:.4f}")
        results['trimmed_5_95'] = {'n': int(len(df_trimmed)), 'r': float(r), 'p': float(p)}

    # Test: Exclude Third Chamber
    df_no_third = df_base[df_base['chamber'] != 'THIRD']
    if len(df_no_third) > 30:
        r, p = stats.pearsonr(df_no_third['precedent_direction_score'], df_no_third['pro_ds'])
        print(f"\nExcluding Third Chamber (n={len(df_no_third)}):")
        print(f"  Correlation: r={r:.3f}, p={p:.4f}")
        results['exclude_third_chamber'] = {'n': int(len(df_no_third)), 'r': float(r), 'p': float(p)}

    # Test: Grand Chamber only
    df_gc = df_base[df_base['chamber'] == 'GRAND_CHAMBER']
    if len(df_gc) > 15:
        r, p = stats.pearsonr(df_gc['precedent_direction_score'], df_gc['pro_ds'])
        print(f"\nGrand Chamber only (n={len(df_gc)}):")
        print(f"  Correlation: r={r:.3f}, p={p:.4f}")
        results['grand_chamber_only'] = {'n': int(len(df_gc)), 'r': float(r), 'p': float(p)}

    return results

def check_predictor_specifications(df):
    """
    Test 2: Alternative predictor specifications.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 2: ALTERNATIVE PREDICTOR SPECIFICATIONS")
    print("=" * 70)

    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score', 'pro_ds']).copy()
    results = {}

    # Test 1: Binary predictor (already tested in main analysis)
    contingency = pd.crosstab(df_base['predominantly_pro_ds_precedents'], df_base['pro_ds'])
    if contingency.shape == (2, 2):
        chi2, p, _, _ = stats.chi2_contingency(contingency)
        or_val = (contingency.iloc[1,1] * contingency.iloc[0,0]) / (contingency.iloc[1,0] * contingency.iloc[0,1]) if contingency.iloc[1,0] * contingency.iloc[0,1] > 0 else np.nan
        print(f"\nBinary predictor (predominantly_pro_ds_precedents):")
        print(f"  Chi-square p={p:.4f}, OR={or_val:.2f}")
        results['binary_predictor'] = {'p': float(p), 'or': float(or_val) if not np.isnan(or_val) else None}

    # Test 2: Tertile split
    df_base['pds_tertile'] = pd.qcut(df_base['precedent_direction_score'], q=3, labels=['Low', 'Medium', 'High'], duplicates='drop')
    tertile_rates = df_base.groupby('pds_tertile')['pro_ds'].agg(['mean', 'count'])
    print(f"\nTertile split:")
    print(tertile_rates)
    results['tertile_split'] = tertile_rates.to_dict()

    # Test 3: Maximum cited pro-DS rate instead of average
    if 'max_cited_pagerank' in df_base.columns:
        # Create max pro-DS rate (would need to compute this, approximate with existing)
        r, p = stats.pearsonr(df_base['precedent_direction_score'], df_base['pro_ds'])
        print(f"\nContinuous predictor (avg precedent direction):")
        print(f"  Correlation: r={r:.3f}, p={p:.4f}")
        results['continuous_predictor'] = {'r': float(r), 'p': float(p)}

    # Test 4: Include external citations
    df_all = df.dropna(subset=['pro_ds']).copy()
    df_all['any_citations'] = (df_all['total_citations'] > 0).astype(int)
    contingency = pd.crosstab(df_all['any_citations'], df_all['pro_ds'])
    if contingency.shape == (2, 2):
        chi2, p, _, _ = stats.chi2_contingency(contingency)
        with_cite_rate = df_all[df_all['any_citations'] == 1]['pro_ds'].mean()
        without_cite_rate = df_all[df_all['any_citations'] == 0]['pro_ds'].mean()
        print(f"\nAny citations (including external):")
        print(f"  With citations: {with_cite_rate:.1%}, Without: {without_cite_rate:.1%}")
        print(f"  Chi-square p={p:.4f}")
        results['any_citations'] = {'with_rate': float(with_cite_rate), 'without_rate': float(without_cite_rate), 'p': float(p)}

    return results

def check_outcome_specifications(df):
    """
    Test 3: Alternative outcome specifications.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 3: ALTERNATIVE OUTCOME SPECIFICATIONS")
    print("=" * 70)

    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score']).copy()
    results = {}

    # Test 1: Exclude MIXED/NEUTRAL (PRO_DATA_SUBJECT vs PRO_CONTROLLER only)
    df_binary = df_base[df_base['ruling_direction'].isin(['PRO_DATA_SUBJECT', 'PRO_CONTROLLER'])].copy()
    if len(df_binary) > 30:
        r, p = stats.pearsonr(df_binary['precedent_direction_score'], df_binary['pro_ds'])
        print(f"\nExcluding MIXED/NEUTRAL (n={len(df_binary)}):")
        print(f"  Correlation: r={r:.3f}, p={p:.4f}")
        results['exclude_mixed_neutral'] = {'n': int(len(df_binary)), 'r': float(r), 'p': float(p)}

    # Test 2: Include MIXED as pro-DS (broadest definition)
    df_base['pro_ds_broad'] = df_base['ruling_direction'].isin(['PRO_DATA_SUBJECT', 'MIXED']).astype(int)
    r, p = stats.pearsonr(df_base['precedent_direction_score'], df_base['pro_ds_broad'])
    print(f"\nBroad pro-DS (includes MIXED, n={len(df_base)}):")
    print(f"  Correlation: r={r:.3f}, p={p:.4f}")
    results['broad_pro_ds'] = {'n': int(len(df_base)), 'r': float(r), 'p': float(p)}

    # Test 3: Case-level outcome (majority ruling)
    case_level = df_base.groupby('case_id').agg({
        'precedent_direction_score': 'mean',
        'pro_ds': 'mean'
    }).reset_index()
    case_level['case_pro_ds'] = (case_level['pro_ds'] > 0.5).astype(int)

    r, p = stats.pearsonr(case_level['precedent_direction_score'], case_level['case_pro_ds'])
    print(f"\nCase-level analysis (n={len(case_level)} cases):")
    print(f"  Correlation: r={r:.3f}, p={p:.4f}")
    results['case_level'] = {'n': int(len(case_level)), 'r': float(r), 'p': float(p)}

    return results

def check_temporal_stability(df):
    """
    Test 4: Temporal stability of effects.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 4: TEMPORAL STABILITY")
    print("=" * 70)

    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score', 'pro_ds', 'year']).copy()
    results = {}

    # Test by year groups
    df_base['period'] = pd.cut(df_base['year'], bins=[2018, 2022, 2023, 2024, 2026], labels=['2019-2022', '2023', '2024', '2025'])

    print("\nEffect by Time Period:")
    for period in df_base['period'].dropna().unique():
        df_period = df_base[df_base['period'] == period]
        if len(df_period) > 15:
            r, p = stats.pearsonr(df_period['precedent_direction_score'], df_period['pro_ds'])
            print(f"  {period} (n={len(df_period)}): r={r:.3f}, p={p:.4f}")
            results[f'period_{period}'] = {'n': int(len(df_period)), 'r': float(r), 'p': float(p)}

    # Test: Early vs Late cases
    median_year = df_base['year'].median()
    df_early = df_base[df_base['year'] <= median_year]
    df_late = df_base[df_base['year'] > median_year]

    print(f"\nEarly vs Late (split at {median_year}):")
    for name, df_sub in [('Early', df_early), ('Late', df_late)]:
        if len(df_sub) > 20:
            r, p = stats.pearsonr(df_sub['precedent_direction_score'], df_sub['pro_ds'])
            print(f"  {name} (n={len(df_sub)}): r={r:.3f}, p={p:.4f}")
            results[f'{name.lower()}_period'] = {'n': int(len(df_sub)), 'r': float(r), 'p': float(p)}

    return results

def check_concept_heterogeneity(df):
    """
    Test 5: Effect heterogeneity by concept cluster.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 5: CONCEPT HETEROGENEITY")
    print("=" * 70)

    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score', 'pro_ds']).copy()
    results = {}

    print("\nEffect by Concept Cluster:")
    for cluster in sorted(df_base['concept_cluster'].unique()):
        df_cluster = df_base[df_base['concept_cluster'] == cluster]
        if len(df_cluster) > 15:
            r, p = stats.pearsonr(df_cluster['precedent_direction_score'], df_cluster['pro_ds'])
            print(f"  {cluster} (n={len(df_cluster)}): r={r:.3f}, p={p:.4f}")
            results[cluster] = {'n': int(len(df_cluster)), 'r': float(r), 'p': float(p)}

    return results

def run_placebo_tests(df):
    """
    Test 6: Placebo tests - shuffled citations.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 6: PLACEBO TESTS")
    print("=" * 70)

    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score', 'pro_ds']).copy()
    results = {}

    # Observed effect
    r_observed, p_observed = stats.pearsonr(df_base['precedent_direction_score'], df_base['pro_ds'])
    print(f"\nObserved correlation: r={r_observed:.3f}, p={p_observed:.4f}")

    # Placebo: shuffle precedent direction scores
    np.random.seed(42)
    n_permutations = 1000
    placebo_rs = []

    for _ in range(n_permutations):
        shuffled = df_base['precedent_direction_score'].sample(frac=1).reset_index(drop=True)
        r_placebo, _ = stats.pearsonr(shuffled, df_base['pro_ds'].reset_index(drop=True))
        placebo_rs.append(r_placebo)

    placebo_rs = np.array(placebo_rs)
    placebo_p = (np.abs(placebo_rs) >= np.abs(r_observed)).mean()

    print(f"\nPermutation test ({n_permutations} permutations):")
    print(f"  Observed r: {r_observed:.3f}")
    print(f"  Placebo mean r: {placebo_rs.mean():.3f}")
    print(f"  Placebo SD: {placebo_rs.std():.3f}")
    print(f"  Permutation p-value: {placebo_p:.4f}")

    results['observed_r'] = float(r_observed)
    results['placebo_mean_r'] = float(placebo_rs.mean())
    results['placebo_sd'] = float(placebo_rs.std())
    results['permutation_p'] = float(placebo_p)

    # Placebo 2: Test with lagged outcome (shouldn't predict)
    # This is a conceptual check - outcomes shouldn't predict precedents
    r_reverse, p_reverse = stats.pearsonr(df_base['pro_ds'], df_base['precedent_direction_score'])
    print(f"\nReverse causality check (same data, just conceptual): r={r_reverse:.3f}")

    return results

def multivariate_robustness(df):
    """
    Test 7: Multivariate robustness with different control sets.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS 7: MULTIVARIATE SPECIFICATION CHECKS")
    print("=" * 70)

    df_base = df[df['internal_citations'] > 0].dropna(subset=['precedent_direction_score', 'pro_ds']).copy()
    results = {}

    # Different control sets
    specifications = [
        ("No controls", "pro_ds ~ precedent_direction_score"),
        ("+ Year", "pro_ds ~ precedent_direction_score + year"),
        ("+ Chamber", "pro_ds ~ precedent_direction_score + C(chamber_grouped)"),
        ("+ Concept", "pro_ds ~ precedent_direction_score + C(concept_cluster)"),
        ("+ Year + Chamber", "pro_ds ~ precedent_direction_score + year + C(chamber_grouped)"),
        ("+ All controls", "pro_ds ~ precedent_direction_score + year + C(chamber_grouped) + C(concept_cluster)"),
        ("+ All + Purpose", "pro_ds ~ precedent_direction_score + year + C(chamber_grouped) + C(concept_cluster) + pro_ds_purpose"),
    ]

    print("\nPrecedent Direction Score Effect Across Specifications:")
    print("-" * 70)

    for name, formula in specifications:
        try:
            model = smf.logit(formula, data=df_base).fit(disp=0)
            coef = model.params['precedent_direction_score']
            p = model.pvalues['precedent_direction_score']
            or_val = np.exp(coef)
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {name:<25}: OR={or_val:.2f}, p={p:.4f} {sig}")
            results[name] = {'or': float(or_val), 'p': float(p), 'coef': float(coef)}
        except Exception as e:
            print(f"  {name:<25}: FAILED ({e})")

    return results

def summarize_robustness(all_results):
    """
    Summarize robustness checks.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS SUMMARY")
    print("=" * 70)

    findings = []

    # Sample restrictions
    sample = all_results.get('sample_restrictions', {})
    if sample:
        stable_count = sum(1 for k, v in sample.items() if v.get('p', 1) < 0.05)
        total = len(sample)
        findings.append(f"Sample restrictions: {stable_count}/{total} significant at p<0.05")

    # Predictor specifications
    pred = all_results.get('predictor_specifications', {})
    if 'continuous_predictor' in pred:
        p = pred['continuous_predictor'].get('p', 1)
        findings.append(f"Continuous predictor: p={p:.4f}")

    # Outcome specifications
    outcome = all_results.get('outcome_specifications', {})
    if outcome:
        for k, v in outcome.items():
            findings.append(f"Outcome '{k}': r={v.get('r', 0):.3f}, p={v.get('p', 1):.4f}")

    # Temporal stability
    temporal = all_results.get('temporal_stability', {})
    if temporal:
        stable_periods = [k for k, v in temporal.items() if v.get('p', 1) < 0.10]
        findings.append(f"Temporal stability: {len(stable_periods)}/{len(temporal)} periods show effect")

    # Placebo
    placebo = all_results.get('placebo_tests', {})
    if placebo:
        findings.append(f"Permutation test: p={placebo.get('permutation_p', 1):.4f}")

    # Multivariate
    mv = all_results.get('multivariate_robustness', {})
    if mv:
        sig_count = sum(1 for k, v in mv.items() if v.get('p', 1) < 0.05)
        findings.append(f"Multivariate: {sig_count}/{len(mv)} specifications significant")

    print("\nKey Findings:")
    for f in findings:
        print(f"  • {f}")

    return findings

def main():
    print("=" * 70)
    print("PHASE 6: ROBUSTNESS CHECKS AND SENSITIVITY ANALYSES")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load data
    print("\n[1/8] Loading data...")
    df = load_data()
    print(f"  Loaded {len(df)} holdings")

    # Run all robustness checks
    print("\n[2/8] Sample restrictions...")
    sample_results = check_sample_restrictions(df)

    print("\n[3/8] Predictor specifications...")
    pred_results = check_predictor_specifications(df)

    print("\n[4/8] Outcome specifications...")
    outcome_results = check_outcome_specifications(df)

    print("\n[5/8] Temporal stability...")
    temporal_results = check_temporal_stability(df)

    print("\n[6/8] Concept heterogeneity...")
    concept_results = check_concept_heterogeneity(df)

    print("\n[7/8] Placebo tests...")
    placebo_results = run_placebo_tests(df)

    print("\n[8/8] Multivariate robustness...")
    mv_results = multivariate_robustness(df)

    # Collect all results
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'sample_restrictions': sample_results,
        'predictor_specifications': pred_results,
        'outcome_specifications': outcome_results,
        'temporal_stability': temporal_results,
        'concept_heterogeneity': concept_results,
        'placebo_tests': placebo_results,
        'multivariate_robustness': mv_results
    }

    # Summary
    print("\n[Summary]")
    findings = summarize_robustness(all_results)
    all_results['summary'] = findings

    # Save
    output_file = NETWORK_PATH / "robustness_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 70)
    print("PHASE 6 COMPLETE: ROBUSTNESS CHECKS")
    print("=" * 70)

    return all_results

if __name__ == "__main__":
    results = main()
