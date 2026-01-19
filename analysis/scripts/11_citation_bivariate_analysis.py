#!/usr/bin/env python3
"""
11_citation_bivariate_analysis.py
==================================
Phase 2: Bivariate Analysis of Citation Effects

Tests pre-registered hypotheses about citation-outcome associations:
  H1.1: Holdings citing pro-DS precedents are more likely to rule pro-DS
  H1.2: Purpose invocation propagates through citations
  H1.3: Grand Chamber citation is associated with different outcomes

Applies Benjamini-Hochberg FDR correction for multiple testing.
"""

import pandas as pd
import numpy as np
from scipy import stats
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
    """Load prepared holdings data with citation variables."""
    # Load prepared holdings
    holdings = pd.read_csv(OUTPUT_PATH / "holdings_prepared.csv")

    # Load citation-derived variables
    citation_vars = pd.read_csv(NETWORK_PATH / "holding_citation_vars.csv")

    # Merge
    df = holdings.merge(citation_vars, on=['case_id', 'holding_id'], how='left')

    print(f"Loaded {len(df)} holdings with citation variables")
    print(f"Holdings with internal citations: {(df['internal_citations'] > 0).sum()}")

    return df

def chi_square_test(df, predictor, outcome='pro_ds', min_cell=5):
    """
    Perform chi-square test (or Fisher's exact if cells too small).

    Returns dict with test results and effect size.
    """
    # Create contingency table
    contingency = pd.crosstab(df[predictor], df[outcome])

    if contingency.shape != (2, 2):
        return {
            'predictor': predictor,
            'test': 'SKIPPED',
            'reason': f'Not 2x2 table: {contingency.shape}',
            'p_value': np.nan,
            'effect_size': np.nan
        }

    # Check minimum cell counts
    min_expected = contingency.sum().min() * contingency.sum(axis=1).min() / contingency.sum().sum()

    if min_expected < min_cell:
        # Use Fisher's exact test
        odds_ratio, p_value = stats.fisher_exact(contingency)
        test_name = 'Fisher exact'
    else:
        # Use chi-square
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        odds_ratio = (contingency.iloc[1, 1] * contingency.iloc[0, 0]) / \
                    (contingency.iloc[1, 0] * contingency.iloc[0, 1]) if contingency.iloc[1, 0] * contingency.iloc[0, 1] > 0 else np.inf
        test_name = 'Chi-square'

    # Phi coefficient (effect size for 2x2)
    n = contingency.sum().sum()
    phi = np.sqrt(stats.chi2_contingency(contingency)[0] / n) if n > 0 else 0

    # Rates
    rate_1 = df[df[predictor] == 1][outcome].mean()
    rate_0 = df[df[predictor] == 0][outcome].mean()
    n_1 = (df[predictor] == 1).sum()
    n_0 = (df[predictor] == 0).sum()

    return {
        'predictor': predictor,
        'test': test_name,
        'p_value': p_value,
        'odds_ratio': odds_ratio,
        'phi': phi,
        'rate_predictor_1': rate_1,
        'rate_predictor_0': rate_0,
        'n_predictor_1': int(n_1),
        'n_predictor_0': int(n_0),
        'rate_difference': rate_1 - rate_0
    }

def benjamini_hochberg(p_values, alpha=0.05):
    """
    Apply Benjamini-Hochberg FDR correction.

    Returns array of adjusted p-values and significance indicators.
    """
    n = len(p_values)
    sorted_idx = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_idx]

    # BH critical values
    critical = np.arange(1, n + 1) * alpha / n

    # Adjusted p-values
    adjusted = np.zeros(n)
    for i in range(n):
        adjusted[sorted_idx[i]] = min(1.0, sorted_p[i] * n / (sorted_idx[i] + 1))

    # Step-up adjustment (ensure monotonicity)
    adjusted_monotonic = np.zeros(n)
    ranks = np.argsort(sorted_idx)
    cummin = np.minimum.accumulate(adjusted[np.argsort(p_values)][::-1])[::-1]
    adjusted_monotonic = cummin[ranks]

    significant = adjusted_monotonic < alpha

    return adjusted_monotonic, significant

def test_h1_1(df):
    """
    H1.1: Holdings citing pro-DS precedents are more likely to rule pro-DS.

    Compare holdings with predominantly pro-DS precedents vs others.
    """
    print("\n" + "=" * 70)
    print("H1.1: PRECEDENT DIRECTION EFFECT")
    print("=" * 70)

    # Filter to holdings with internal citations
    df_with_citations = df[df['internal_citations'] > 0].copy()
    print(f"Holdings with internal citations: {len(df_with_citations)}")

    # Test 1: Binary - predominantly pro-DS precedents
    result_binary = chi_square_test(df_with_citations, 'predominantly_pro_ds_precedents', 'pro_ds')

    print(f"\nBinary Test (predominantly_pro_ds_precedents):")
    print(f"  With pro-DS precedents: {result_binary['rate_predictor_1']:.1%} pro-DS (n={result_binary['n_predictor_1']})")
    print(f"  Without pro-DS precedents: {result_binary['rate_predictor_0']:.1%} pro-DS (n={result_binary['n_predictor_0']})")
    print(f"  Difference: {result_binary['rate_difference']*100:.1f} percentage points")
    print(f"  Odds Ratio: {result_binary['odds_ratio']:.2f}")
    print(f"  Phi: {result_binary['phi']:.3f}")
    print(f"  p-value ({result_binary['test']}): {result_binary['p_value']:.4f}")

    # Test 2: Continuous - precedent direction score (quartiles)
    df_with_citations['precedent_quartile'] = pd.qcut(
        df_with_citations['precedent_direction_score'],
        q=4, labels=['Q1 (low)', 'Q2', 'Q3', 'Q4 (high)'],
        duplicates='drop'
    )

    quartile_rates = df_with_citations.groupby('precedent_quartile').agg({
        'pro_ds': ['sum', 'count', 'mean']
    })
    quartile_rates.columns = ['pro_ds_count', 'total', 'pro_ds_rate']

    print(f"\nPro-DS Rate by Precedent Direction Quartile:")
    print(quartile_rates.to_string())

    # Trend test (Cochran-Armitage)
    # Approximate with correlation
    df_corr = df_with_citations.dropna(subset=['precedent_direction_score', 'pro_ds'])
    r, p_corr = stats.pearsonr(df_corr['precedent_direction_score'], df_corr['pro_ds'])

    print(f"\nCorrelation Analysis:")
    print(f"  Pearson r: {r:.3f}")
    print(f"  p-value: {p_corr:.4f}")

    result_binary['correlation_r'] = r
    result_binary['correlation_p'] = p_corr
    result_binary['quartile_rates'] = quartile_rates.to_dict()

    return result_binary

def test_h1_2(df):
    """
    H1.2: Purpose invocation propagates through citations.

    Test whether citing precedents that invoked pro-DS purposes is associated
    with the citing holding also invoking pro-DS purposes.
    """
    print("\n" + "=" * 70)
    print("H1.2: PURPOSE PROPAGATION EFFECT")
    print("=" * 70)

    df_with_citations = df[df['internal_citations'] > 0].copy()

    # Create binary indicator: cites precedent with high purpose rate
    df_with_citations['high_precedent_purpose'] = (df_with_citations['precedent_purpose_rate'] > 0.5).astype(int)

    # Test: Association between precedent purpose and citing purpose
    if 'pro_ds_purpose' not in df_with_citations.columns:
        print("  WARNING: pro_ds_purpose variable not available")
        return None

    result = chi_square_test(df_with_citations, 'high_precedent_purpose', 'pro_ds_purpose')

    print(f"\nTest: High precedent purpose rate → Citing holding invokes pro-DS purpose")
    print(f"  High precedent purpose: {result['rate_predictor_1']:.1%} invoke purpose (n={result['n_predictor_1']})")
    print(f"  Low precedent purpose: {result['rate_predictor_0']:.1%} invoke purpose (n={result['n_predictor_0']})")
    print(f"  Difference: {result['rate_difference']*100:.1f} percentage points")
    print(f"  Odds Ratio: {result['odds_ratio']:.2f}")
    print(f"  Phi: {result['phi']:.3f}")
    print(f"  p-value ({result['test']}): {result['p_value']:.4f}")

    # Also test outcome association
    result_outcome = chi_square_test(df_with_citations, 'high_precedent_purpose', 'pro_ds')

    print(f"\nTest: High precedent purpose rate → Pro-DS outcome")
    print(f"  High precedent purpose: {result_outcome['rate_predictor_1']:.1%} pro-DS (n={result_outcome['n_predictor_1']})")
    print(f"  Low precedent purpose: {result_outcome['rate_predictor_0']:.1%} pro-DS (n={result_outcome['n_predictor_0']})")
    print(f"  Difference: {result_outcome['rate_difference']*100:.1f} percentage points")
    print(f"  p-value: {result_outcome['p_value']:.4f}")

    result['outcome_test'] = result_outcome

    return result

def test_h1_3(df):
    """
    H1.3: Grand Chamber citation is associated with different outcomes.

    Test whether citing Grand Chamber precedents is associated with ruling direction.
    """
    print("\n" + "=" * 70)
    print("H1.3: GRAND CHAMBER CITATION EFFECT")
    print("=" * 70)

    df_with_citations = df[df['internal_citations'] > 0].copy()

    result = chi_square_test(df_with_citations, 'cites_gc_precedent', 'pro_ds')

    print(f"\nTest: Citing Grand Chamber precedent → Pro-DS outcome")
    print(f"  Cites GC: {result['rate_predictor_1']:.1%} pro-DS (n={result['n_predictor_1']})")
    print(f"  No GC: {result['rate_predictor_0']:.1%} pro-DS (n={result['n_predictor_0']})")
    print(f"  Difference: {result['rate_difference']*100:.1f} percentage points")
    print(f"  Odds Ratio: {result['odds_ratio']:.2f}")
    print(f"  Phi: {result['phi']:.3f}")
    print(f"  p-value ({result['test']}): {result['p_value']:.4f}")

    # Stratify by citing case chamber
    print(f"\nStratified by Citing Case Chamber:")
    for chamber in df_with_citations['chamber'].unique():
        df_chamber = df_with_citations[df_with_citations['chamber'] == chamber]
        if len(df_chamber) >= 10 and df_chamber['cites_gc_precedent'].nunique() > 1:
            gc_rate = df_chamber[df_chamber['cites_gc_precedent'] == 1]['pro_ds'].mean()
            no_gc_rate = df_chamber[df_chamber['cites_gc_precedent'] == 0]['pro_ds'].mean()
            n_gc = (df_chamber['cites_gc_precedent'] == 1).sum()
            n_no_gc = (df_chamber['cites_gc_precedent'] == 0).sum()
            print(f"  {chamber}: Cites GC={gc_rate:.1%} (n={n_gc}), No GC={no_gc_rate:.1%} (n={n_no_gc})")

    return result

def test_citation_intensity(df):
    """
    Exploratory: Is citation intensity associated with outcomes?
    """
    print("\n" + "=" * 70)
    print("EXPLORATORY: CITATION INTENSITY EFFECT")
    print("=" * 70)

    # Internal citation count categories
    df['citation_category'] = pd.cut(
        df['internal_citations'],
        bins=[-1, 0, 2, 5, 100],
        labels=['0', '1-2', '3-5', '6+']
    )

    cite_rates = df.groupby('citation_category').agg({
        'pro_ds': ['sum', 'count', 'mean']
    })
    cite_rates.columns = ['pro_ds_count', 'total', 'pro_ds_rate']

    print(f"\nPro-DS Rate by Internal Citation Count:")
    print(cite_rates.to_string())

    # Test trend
    df_nonzero = df[df['internal_citations'] > 0].copy()
    r, p = stats.pearsonr(df_nonzero['internal_citations'], df_nonzero['pro_ds'])

    print(f"\nCorrelation (among holdings with citations):")
    print(f"  Pearson r: {r:.3f}")
    print(f"  p-value: {p:.4f}")

    return {
        'category_rates': cite_rates.to_dict(),
        'correlation_r': r,
        'correlation_p': p
    }

def test_centrality_effects(df):
    """
    Exploratory: Are network centrality measures associated with outcomes?
    """
    print("\n" + "=" * 70)
    print("EXPLORATORY: NETWORK CENTRALITY EFFECTS")
    print("=" * 70)

    results = {}

    # Test PageRank of cited cases
    df_with_citations = df[df['internal_citations'] > 0].dropna(subset=['avg_cited_pagerank']).copy()

    if len(df_with_citations) > 20:
        # High vs low cited PageRank
        median_pr = df_with_citations['avg_cited_pagerank'].median()
        df_with_citations['high_cited_pagerank'] = (df_with_citations['avg_cited_pagerank'] > median_pr).astype(int)

        result = chi_square_test(df_with_citations, 'high_cited_pagerank', 'pro_ds')

        print(f"\nTest: High avg cited PageRank → Pro-DS outcome")
        print(f"  High PageRank: {result['rate_predictor_1']:.1%} pro-DS (n={result['n_predictor_1']})")
        print(f"  Low PageRank: {result['rate_predictor_0']:.1%} pro-DS (n={result['n_predictor_0']})")
        print(f"  Difference: {result['rate_difference']*100:.1f} pp")
        print(f"  p-value: {result['p_value']:.4f}")

        results['avg_cited_pagerank'] = result

        # Citing case authority score
        median_auth = df_with_citations['citing_case_authority'].median()
        df_with_citations['high_authority'] = (df_with_citations['citing_case_authority'] > median_auth).astype(int)

        result2 = chi_square_test(df_with_citations, 'high_authority', 'pro_ds')

        print(f"\nTest: High citing case authority → Pro-DS outcome")
        print(f"  High authority: {result2['rate_predictor_1']:.1%} pro-DS (n={result2['n_predictor_1']})")
        print(f"  Low authority: {result2['rate_predictor_0']:.1%} pro-DS (n={result2['n_predictor_0']})")
        print(f"  Difference: {result2['rate_difference']*100:.1f} pp")
        print(f"  p-value: {result2['p_value']:.4f}")

        results['citing_authority'] = result2

    return results

def test_concept_specific_citation_effects(df):
    """
    Test whether citation effects vary by concept cluster.
    """
    print("\n" + "=" * 70)
    print("CONCEPT-SPECIFIC CITATION EFFECTS")
    print("=" * 70)

    df_with_citations = df[df['internal_citations'] > 0].copy()

    results = {}

    for cluster in df_with_citations['concept_cluster'].unique():
        df_cluster = df_with_citations[df_with_citations['concept_cluster'] == cluster]

        if len(df_cluster) >= 15 and df_cluster['predominantly_pro_ds_precedents'].nunique() > 1:
            result = chi_square_test(df_cluster, 'predominantly_pro_ds_precedents', 'pro_ds')

            print(f"\n{cluster} (n={len(df_cluster)}):")
            print(f"  Pro-DS precedents: {result['rate_predictor_1']:.1%} pro-DS (n={result['n_predictor_1']})")
            print(f"  Other precedents: {result['rate_predictor_0']:.1%} pro-DS (n={result['n_predictor_0']})")
            print(f"  Difference: {result['rate_difference']*100:.1f} pp, p={result['p_value']:.3f}")

            results[cluster] = result

    return results

def main():
    print("=" * 70)
    print("PHASE 2: BIVARIATE ANALYSIS OF CITATION EFFECTS")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load data
    print("\n[1/7] Loading data...")
    df = load_data()

    # Run hypothesis tests
    print("\n[2/7] Testing H1.1: Precedent Direction Effect...")
    h1_1 = test_h1_1(df)

    print("\n[3/7] Testing H1.2: Purpose Propagation Effect...")
    h1_2 = test_h1_2(df)

    print("\n[4/7] Testing H1.3: Grand Chamber Citation Effect...")
    h1_3 = test_h1_3(df)

    # Exploratory tests
    print("\n[5/7] Exploratory: Citation Intensity...")
    intensity = test_citation_intensity(df)

    print("\n[6/7] Exploratory: Centrality Effects...")
    centrality = test_centrality_effects(df)

    print("\n[7/7] Concept-Specific Effects...")
    concept_effects = test_concept_specific_citation_effects(df)

    # Collect all p-values for FDR correction
    print("\n" + "=" * 70)
    print("MULTIPLE TESTING CORRECTION (Benjamini-Hochberg)")
    print("=" * 70)

    all_tests = []

    # Primary hypothesis tests
    if h1_1 and not np.isnan(h1_1.get('p_value', np.nan)):
        all_tests.append(('H1.1: Precedent Direction', h1_1['p_value'], h1_1))
    if h1_2 and not np.isnan(h1_2.get('p_value', np.nan)):
        all_tests.append(('H1.2: Purpose Propagation', h1_2['p_value'], h1_2))
    if h1_3 and not np.isnan(h1_3.get('p_value', np.nan)):
        all_tests.append(('H1.3: Grand Chamber Citation', h1_3['p_value'], h1_3))

    # Exploratory
    if intensity and not np.isnan(intensity.get('correlation_p', np.nan)):
        all_tests.append(('Exploratory: Citation Intensity', intensity['correlation_p'], intensity))
    for name, result in centrality.items():
        if result and not np.isnan(result.get('p_value', np.nan)):
            all_tests.append((f'Exploratory: {name}', result['p_value'], result))

    if len(all_tests) > 0:
        test_names = [t[0] for t in all_tests]
        p_values = [t[1] for t in all_tests]

        adjusted_p, significant = benjamini_hochberg(p_values, alpha=0.05)

        print(f"\nTest Results (FDR-corrected at q=0.05):")
        print("-" * 70)

        fdr_results = []
        for i, (name, p_raw, result) in enumerate(all_tests):
            sig_marker = "***" if significant[i] else ""
            effect = result.get('rate_difference', result.get('correlation_r', 0)) or 0
            print(f"  {name}")
            print(f"    Raw p: {p_raw:.4f}, Adjusted p: {adjusted_p[i]:.4f} {sig_marker}")
            print(f"    Effect: {effect*100:.1f}pp" if isinstance(effect, float) else f"    Effect: {effect}")

            fdr_results.append({
                'test': name,
                'p_raw': float(p_raw),
                'p_adjusted': float(adjusted_p[i]),
                'significant_fdr': bool(significant[i]),
                'effect_size': float(effect) if isinstance(effect, float) else None
            })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY OF BIVARIATE FINDINGS")
    print("=" * 70)

    findings = []

    if h1_1:
        interpretation = "SUPPORTED" if h1_1['p_value'] < 0.05 and h1_1['rate_difference'] > 0 else "NOT SUPPORTED"
        findings.append(f"H1.1 Precedent Direction: {interpretation}")
        findings.append(f"  - Pro-DS precedents → {h1_1['rate_predictor_1']:.1%} pro-DS")
        findings.append(f"  - Other precedents → {h1_1['rate_predictor_0']:.1%} pro-DS")
        findings.append(f"  - Gap: {h1_1['rate_difference']*100:.1f}pp (p={h1_1['p_value']:.4f})")

    if h1_2:
        interpretation = "SUPPORTED" if h1_2['p_value'] < 0.05 and h1_2['rate_difference'] > 0 else "NOT SUPPORTED"
        findings.append(f"\nH1.2 Purpose Propagation: {interpretation}")
        findings.append(f"  - High purpose precedents → {h1_2['rate_predictor_1']:.1%} invoke purpose")
        findings.append(f"  - Low purpose precedents → {h1_2['rate_predictor_0']:.1%} invoke purpose")
        findings.append(f"  - Gap: {h1_2['rate_difference']*100:.1f}pp (p={h1_2['p_value']:.4f})")

    if h1_3:
        interpretation = "SUPPORTED" if h1_3['p_value'] < 0.05 else "NOT SUPPORTED"
        findings.append(f"\nH1.3 Grand Chamber Citation: {interpretation}")
        findings.append(f"  - Cites GC → {h1_3['rate_predictor_1']:.1%} pro-DS")
        findings.append(f"  - No GC → {h1_3['rate_predictor_0']:.1%} pro-DS")
        findings.append(f"  - Gap: {h1_3['rate_difference']*100:.1f}pp (p={h1_3['p_value']:.4f})")

    for f in findings:
        print(f)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'n_holdings': int(len(df)),
        'n_holdings_with_citations': int((df['internal_citations'] > 0).sum()),
        'hypotheses': {
            'H1_1_precedent_direction': h1_1,
            'H1_2_purpose_propagation': h1_2,
            'H1_3_grand_chamber': h1_3
        },
        'exploratory': {
            'citation_intensity': intensity,
            'centrality_effects': {k: v for k, v in centrality.items()},
            'concept_specific': {k: v for k, v in concept_effects.items()}
        },
        'fdr_correction': fdr_results if len(all_tests) > 0 else [],
        'summary': findings
    }

    # Convert numpy types for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return obj

    results = convert_numpy(results)

    output_file = NETWORK_PATH / "bivariate_citation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 70)
    print("PHASE 2 COMPLETE: BIVARIATE ANALYSIS")
    print("=" * 70)

    return results

if __name__ == "__main__":
    results = main()
