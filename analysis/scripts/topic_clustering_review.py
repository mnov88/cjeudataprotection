#!/usr/bin/env python3
"""
topic_clustering_review.py
==========================
Review and comparative analysis of topic clustering approach.

This script:
1. Analyzes the current clustering methodology
2. Runs analyses with and without clustering
3. Documents findings and potential issues
4. Outputs a comprehensive review report

REVISION HISTORY:
- v1.0: Initial clustering review implementation
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

import statsmodels.formula.api as smf

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "parsed" / "holdings.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output" / "clustering_review"

# Current cluster definitions (from 01_data_preparation.py)
CONCEPT_CLUSTERS = {
    'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
              'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
    'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
               'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
    'LAWFULNESS': ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGAL_OBLIGATION_BASIS',
                   'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS', 'LEGITIMATE_INTERESTS'],
    'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY',
                   'DATA_MINIMISATION'],
    'RIGHTS': ['RIGHT_OF_ACCESS', 'RIGHT_TO_RECTIFICATION', 'RIGHT_TO_ERASURE',
               'RIGHT_TO_RESTRICTION', 'RIGHT_TO_PORTABILITY', 'RIGHT_TO_OBJECT',
               'AUTOMATED_DECISION_MAKING'],
    'SPECIAL_CATEGORIES': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
    'ENFORCEMENT': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
                    'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REMEDIES_COMPENSATION',
                    'REPRESENTATIVE_ACTIONS'],
    'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
              'MEMBER_STATE_DISCRETION', 'OTHER']
}


def cramers_v(contingency_table):
    """Calculate Cramér's V effect size."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    if min_dim == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))


def analyze_cluster_composition(df):
    """Analyze the composition and internal homogeneity of each cluster."""
    print("\n" + "=" * 80)
    print("CLUSTER COMPOSITION AND INTERNAL HOMOGENEITY ANALYSIS")
    print("=" * 80)

    results = {}

    for cluster_name, concepts in CONCEPT_CLUSTERS.items():
        cluster_df = df[df['concept_cluster'] == cluster_name]
        n_holdings = len(cluster_df)

        if n_holdings == 0:
            continue

        # Get concept-level breakdown
        concept_breakdown = cluster_df.groupby('primary_concept').agg({
            'pro_ds': ['count', 'mean']
        }).round(3)
        concept_breakdown.columns = ['n', 'pro_ds_rate']
        concept_breakdown = concept_breakdown.sort_values('n', ascending=False)

        # Calculate within-cluster variance in pro-DS rate
        pro_ds_rates = concept_breakdown['pro_ds_rate'].values
        within_cluster_var = np.var(pro_ds_rates) if len(pro_ds_rates) > 1 else 0
        within_cluster_range = (pro_ds_rates.max() - pro_ds_rates.min()) if len(pro_ds_rates) > 1 else 0

        cluster_pro_ds_rate = cluster_df['pro_ds'].mean()

        print(f"\n{cluster_name} (n={n_holdings}, cluster pro-DS rate: {cluster_pro_ds_rate*100:.1f}%)")
        print("-" * 60)

        for concept, row in concept_breakdown.iterrows():
            deviation = (row['pro_ds_rate'] - cluster_pro_ds_rate) * 100
            dev_str = f"+{deviation:.1f}" if deviation >= 0 else f"{deviation:.1f}"
            print(f"  {concept}: n={int(row['n'])}, pro-DS={row['pro_ds_rate']*100:.1f}% (dev: {dev_str}pp)")

        print(f"\n  Within-cluster variance: {within_cluster_var:.4f}")
        print(f"  Within-cluster range: {within_cluster_range*100:.1f}pp")

        # Flag potential issues
        if within_cluster_range > 0.30:
            print(f"  ⚠️ WARNING: High internal heterogeneity (range > 30pp)")

        results[cluster_name] = {
            'n': n_holdings,
            'cluster_pro_ds_rate': cluster_pro_ds_rate,
            'n_concepts': len(concept_breakdown),
            'within_cluster_variance': within_cluster_var,
            'within_cluster_range': within_cluster_range,
            'concept_breakdown': concept_breakdown.to_dict(),
            'heterogeneity_flag': within_cluster_range > 0.30
        }

    return results


def run_bivariate_with_clustering(df):
    """Run bivariate analysis using clusters."""
    contingency = pd.crosstab(df['concept_cluster'], df['pro_ds'])
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    effect = cramers_v(contingency)

    cluster_stats = df.groupby('concept_cluster').agg({
        'pro_ds': ['count', 'mean']
    }).round(3)
    cluster_stats.columns = ['n', 'pro_ds_rate']
    cluster_stats = cluster_stats.sort_values('pro_ds_rate', ascending=False)

    return {
        'chi2': chi2,
        'p_value': p,
        'dof': dof,
        'effect_size': effect,
        'cluster_stats': cluster_stats.to_dict(),
        'n_categories': len(df['concept_cluster'].unique())
    }


def run_bivariate_without_clustering(df):
    """Run bivariate analysis using raw primary_concept."""
    # Filter to concepts with n >= 5 for valid chi-square
    concept_counts = df['primary_concept'].value_counts()
    valid_concepts = concept_counts[concept_counts >= 5].index
    df_filtered = df[df['primary_concept'].isin(valid_concepts)]

    contingency = pd.crosstab(df_filtered['primary_concept'], df_filtered['pro_ds'])
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    effect = cramers_v(contingency)

    concept_stats = df.groupby('primary_concept').agg({
        'pro_ds': ['count', 'mean']
    }).round(3)
    concept_stats.columns = ['n', 'pro_ds_rate']
    concept_stats = concept_stats.sort_values('pro_ds_rate', ascending=False)

    return {
        'chi2': chi2,
        'p_value': p,
        'dof': dof,
        'effect_size': effect,
        'concept_stats': concept_stats.to_dict(),
        'n_categories': len(valid_concepts),
        'n_excluded': len(df) - len(df_filtered),
        'excluded_concepts': list(concept_counts[concept_counts < 5].index)
    }


def run_multivariate_with_clustering(df):
    """Run multivariate logistic regression with cluster as control."""
    formula = """pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
                 C(concept_cluster, Treatment(reference='OTHER')) +
                 C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose +
                 level_shifting + any_balancing"""

    try:
        model = smf.logit(formula, data=df).fit(disp=0)
        return {
            'converged': model.mle_retvals['converged'],
            'n': int(model.nobs),
            'aic': model.aic,
            'bic': model.bic,
            'pseudo_r2': model.prsquared,
            'n_params': len(model.params),
            'cluster_coefficients': {
                var: {
                    'coef': model.params[var],
                    'odds_ratio': np.exp(model.params[var]),
                    'p': model.pvalues[var]
                }
                for var in model.params.index if 'concept_cluster' in var
            }
        }
    except Exception as e:
        return {'error': str(e)}


def run_multivariate_without_clustering(df):
    """Run multivariate logistic regression without cluster control."""
    formula = """pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
                 C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose +
                 level_shifting + any_balancing"""

    try:
        model = smf.logit(formula, data=df).fit(disp=0)
        return {
            'converged': model.mle_retvals['converged'],
            'n': int(model.nobs),
            'aic': model.aic,
            'bic': model.bic,
            'pseudo_r2': model.prsquared,
            'n_params': len(model.params),
        }
    except Exception as e:
        return {'error': str(e)}


def run_multivariate_with_compensation_control(df):
    """Run multivariate with is_compensation as targeted control instead of full cluster."""
    formula = """pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
                 is_compensation +
                 C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose +
                 level_shifting + any_balancing"""

    try:
        model = smf.logit(formula, data=df).fit(disp=0)
        return {
            'converged': model.mle_retvals['converged'],
            'n': int(model.nobs),
            'aic': model.aic,
            'bic': model.bic,
            'pseudo_r2': model.prsquared,
            'n_params': len(model.params),
            'compensation_effect': {
                'coef': model.params.get('is_compensation', np.nan),
                'odds_ratio': np.exp(model.params.get('is_compensation', np.nan)),
                'p': model.pvalues.get('is_compensation', np.nan)
            }
        }
    except Exception as e:
        return {'error': str(e)}


def analyze_compensation_effect(df):
    """Deep dive into the REMEDIES_COMPENSATION effect that drives ENFORCEMENT cluster."""
    print("\n" + "=" * 80)
    print("COMPENSATION EFFECT ANALYSIS")
    print("=" * 80)

    # Overall stats
    comp_df = df[df['is_compensation'] == 1]
    non_comp_df = df[df['is_compensation'] == 0]

    comp_pro_ds = comp_df['pro_ds'].mean()
    non_comp_pro_ds = non_comp_df['pro_ds'].mean()
    gap = (non_comp_pro_ds - comp_pro_ds) * 100

    print(f"\nCompensation cases: n={len(comp_df)}, pro-DS rate: {comp_pro_ds*100:.1f}%")
    print(f"Non-compensation cases: n={len(non_comp_df)}, pro-DS rate: {non_comp_pro_ds*100:.1f}%")
    print(f"Gap: {gap:.1f}pp")

    # Compare to overall ENFORCEMENT cluster (excluding compensation)
    enf_non_comp = df[(df['concept_cluster'] == 'ENFORCEMENT') & (df['is_compensation'] == 0)]
    if len(enf_non_comp) > 0:
        enf_non_comp_rate = enf_non_comp['pro_ds'].mean()
        print(f"\nENFORCEMENT (non-compensation): n={len(enf_non_comp)}, pro-DS rate: {enf_non_comp_rate*100:.1f}%")

        # Compare to other non-ENFORCEMENT
        other_clusters = df[df['concept_cluster'] != 'ENFORCEMENT']['pro_ds'].mean()
        print(f"Other clusters: pro-DS rate: {other_clusters*100:.1f}%")

    # Statistical test
    contingency = pd.crosstab(df['is_compensation'], df['pro_ds'])
    try:
        odds_ratio, p_fisher = stats.fisher_exact(contingency)
        print(f"\nFisher's exact test: OR={odds_ratio:.3f}, p={p_fisher:.4f}")
    except:
        pass

    return {
        'n_compensation': len(comp_df),
        'n_non_compensation': len(non_comp_df),
        'compensation_pro_ds_rate': comp_pro_ds,
        'non_compensation_pro_ds_rate': non_comp_pro_ds,
        'gap_pp': gap
    }


def generate_review_report(results):
    """Generate comprehensive markdown review report."""

    report = """# Topic Clustering Review Report

## Executive Summary

This report reviews the topic clustering methodology used in the CJEU GDPR data protection analysis.
The analysis compares results with and without clustering to assess its impact on findings.

## 1. Current Clustering Methodology

### 1.1 Cluster Definitions

The current implementation groups 41 GDPR concepts into 8 clusters:

| Cluster | N Concepts | Description |
|---------|------------|-------------|
| SCOPE | 5 | Material and territorial scope, personal data definition |
| ACTORS | 4 | Controller, processor, recipient definitions |
| LAWFULNESS | 6 | Legal bases for processing (consent, contract, etc.) |
| PRINCIPLES | 4 | Core data protection principles |
| RIGHTS | 7 | Data subject rights (access, erasure, etc.) |
| SPECIAL_CATEGORIES | 2 | Sensitive data processing |
| ENFORCEMENT | 8 | DPA powers, remedies, compensation |
| OTHER | 5 | Miscellaneous provisions |

### 1.2 Methodology Assessment

**Strengths:**
- Groups legally related concepts together
- Reduces dimensionality for statistical analysis
- Aligns with GDPR chapter structure
- Provides interpretable results

**Potential Issues:**
"""

    # Add heterogeneity findings
    if 'cluster_composition' in results:
        heterogeneous_clusters = [
            name for name, data in results['cluster_composition'].items()
            if data.get('heterogeneity_flag', False)
        ]
        if heterogeneous_clusters:
            report += f"- **Internal heterogeneity** detected in: {', '.join(heterogeneous_clusters)}\n"
        else:
            report += "- No major internal heterogeneity detected\n"

    # Add ENFORCEMENT/compensation issue
    if 'compensation_analysis' in results:
        gap = results['compensation_analysis']['gap_pp']
        report += f"""
- **ENFORCEMENT cluster heterogeneity**: The REMEDIES_COMPENSATION concept (n={results['compensation_analysis']['n_compensation']})
  has a {abs(gap):.1f}pp {'lower' if gap > 0 else 'higher'} pro-DS rate than non-compensation cases, creating
  significant internal variance within the ENFORCEMENT cluster.

"""

    report += """
## 2. Comparative Analysis Results

### 2.1 Bivariate Analysis Comparison

"""

    if 'bivariate_with_cluster' in results and 'bivariate_without_cluster' in results:
        with_cluster = results['bivariate_with_cluster']
        without_cluster = results['bivariate_without_cluster']

        report += f"""| Metric | With Clustering | Without Clustering |
|--------|-----------------|-------------------|
| Chi-square | {with_cluster['chi2']:.2f} | {without_cluster['chi2']:.2f} |
| p-value | {with_cluster['p_value']:.4f} | {without_cluster['p_value']:.4f} |
| Effect size (Cramér's V) | {with_cluster['effect_size']:.3f} | {without_cluster['effect_size']:.3f} |
| N categories | {with_cluster['n_categories']} | {without_cluster['n_categories']} |

"""
        if without_cluster.get('n_excluded', 0) > 0:
            report += f"*Note: Without clustering, {without_cluster['n_excluded']} holdings were excluded due to concepts with n<5*\n\n"

    report += """### 2.2 Multivariate Analysis Comparison

"""

    if all(k in results for k in ['mv_with_cluster', 'mv_without_cluster', 'mv_with_compensation']):
        mv_with = results['mv_with_cluster']
        mv_without = results['mv_without_cluster']
        mv_comp = results['mv_with_compensation']

        if 'error' not in mv_with and 'error' not in mv_without and 'error' not in mv_comp:
            report += f"""| Model | AIC | BIC | Pseudo-R² | N params |
|-------|-----|-----|-----------|----------|
| With full clustering | {mv_with['aic']:.1f} | {mv_with['bic']:.1f} | {mv_with['pseudo_r2']:.4f} | {mv_with['n_params']} |
| Without clustering | {mv_without['aic']:.1f} | {mv_without['bic']:.1f} | {mv_without['pseudo_r2']:.4f} | {mv_without['n_params']} |
| With compensation only | {mv_comp['aic']:.1f} | {mv_comp['bic']:.1f} | {mv_comp['pseudo_r2']:.4f} | {mv_comp['n_params']} |

"""
            # Model comparison interpretation
            best_aic = min(mv_with['aic'], mv_without['aic'], mv_comp['aic'])
            report += "**Model Selection (by AIC):**\n"
            if best_aic == mv_with['aic']:
                report += "- Full clustering model provides best fit\n"
            elif best_aic == mv_comp['aic']:
                report += "- Compensation-only control provides best fit (most parsimonious)\n"
            else:
                report += "- Model without clustering provides best fit\n"

            aic_diff = mv_with['aic'] - mv_comp['aic']
            report += f"- AIC difference (full clustering vs compensation-only): {aic_diff:.1f}\n"

    report += """

## 3. Key Findings

### 3.1 Clustering Impact on Results

"""

    # Interpret findings
    if 'bivariate_with_cluster' in results and 'bivariate_without_cluster' in results:
        with_v = results['bivariate_with_cluster']['effect_size']
        without_v = results['bivariate_without_cluster']['effect_size']

        if without_v > with_v:
            report += f"""- **Information loss from clustering**: The unclustered analysis shows a stronger
  effect (V={without_v:.3f}) than the clustered analysis (V={with_v:.3f}), suggesting
  that clustering masks some concept-level variation.

"""
        else:
            report += f"""- **Clustering captures key variation**: The clustered analysis effect size
  (V={with_v:.3f}) is comparable to unclustered (V={without_v:.3f}).

"""

    if 'compensation_analysis' in results:
        comp = results['compensation_analysis']
        report += f"""### 3.2 The Compensation Paradox

The REMEDIES_COMPENSATION concept creates significant heterogeneity within the ENFORCEMENT cluster:
- **Compensation pro-DS rate**: {comp['compensation_pro_ds_rate']*100:.1f}%
- **Non-compensation pro-DS rate**: {comp['non_compensation_pro_ds_rate']*100:.1f}%
- **Gap**: {comp['gap_pp']:.1f} percentage points

This finding suggests that:
1. The ENFORCEMENT cluster should potentially be split or treated specially
2. Using `is_compensation` as a targeted control may be more appropriate than full clustering
3. The compensation cases represent a distinct legal phenomenon (stricter proof requirements)

"""

    report += """
## 4. Recommendations

### 4.1 For Current Analysis

1. **Continue using clustering** for interpretability and dimensionality reduction
2. **Always include `is_compensation` as additional control** to account for the compensation paradox
3. **Report sensitivity analyses** both with and without clustering

### 4.2 For Future Work

1. Consider **splitting ENFORCEMENT cluster** into compensation vs. non-compensation
2. Explore **alternative clustering schemes** based on empirical (data-driven) methods
3. Consider **hierarchical models** with concepts nested within clusters

### 4.3 Alternative Approaches

If clustering is not used, consider:
1. **Primary concept as random effect** in mixed models (handles sparse categories)
2. **LASSO/Ridge regression** with concept dummies for variable selection
3. **Empirical Bayes shrinkage** for concept-level estimates

## 5. Conclusion

The current topic clustering approach is methodologically sound and provides interpretable results.
However, the significant heterogeneity within the ENFORCEMENT cluster (driven by REMEDIES_COMPENSATION)
warrants special attention. We recommend:

1. Maintaining the current clustering for primary analyses
2. Using `is_compensation` as an additional targeted control
3. Reporting sensitivity analyses without clustering to demonstrate robustness
"""

    return report


def main():
    """Main function to run the clustering review."""

    print("=" * 80)
    print("TOPIC CLUSTERING REVIEW ANALYSIS")
    print("=" * 80)

    # Load data
    if not DATA_PATH.exists():
        print(f"Error: Prepared data not found at {DATA_PATH}")
        print("Please run 01_data_preparation.py first")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded {len(df)} holdings from {len(df['case_id'].unique())} cases")

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Collect all results
    results = {}

    # 1. Analyze cluster composition
    print("\n" + "=" * 80)
    print("PHASE 1: CLUSTER COMPOSITION ANALYSIS")
    print("=" * 80)
    results['cluster_composition'] = analyze_cluster_composition(df)

    # 2. Run bivariate analyses
    print("\n" + "=" * 80)
    print("PHASE 2: BIVARIATE ANALYSIS COMPARISON")
    print("=" * 80)

    print("\nWith clustering:")
    results['bivariate_with_cluster'] = run_bivariate_with_clustering(df)
    print(f"  Chi-square = {results['bivariate_with_cluster']['chi2']:.2f}, "
          f"p = {results['bivariate_with_cluster']['p_value']:.4f}, "
          f"V = {results['bivariate_with_cluster']['effect_size']:.3f}")

    print("\nWithout clustering (using primary_concept):")
    results['bivariate_without_cluster'] = run_bivariate_without_clustering(df)
    print(f"  Chi-square = {results['bivariate_without_cluster']['chi2']:.2f}, "
          f"p = {results['bivariate_without_cluster']['p_value']:.4f}, "
          f"V = {results['bivariate_without_cluster']['effect_size']:.3f}")
    if results['bivariate_without_cluster']['n_excluded'] > 0:
        print(f"  (Excluded {results['bivariate_without_cluster']['n_excluded']} holdings with n<5 concepts)")

    # 3. Run multivariate analyses
    print("\n" + "=" * 80)
    print("PHASE 3: MULTIVARIATE ANALYSIS COMPARISON")
    print("=" * 80)

    print("\nModel 1: With full concept_cluster control")
    results['mv_with_cluster'] = run_multivariate_with_clustering(df)
    if 'error' not in results['mv_with_cluster']:
        print(f"  AIC = {results['mv_with_cluster']['aic']:.1f}, "
              f"Pseudo-R² = {results['mv_with_cluster']['pseudo_r2']:.4f}")
    else:
        print(f"  Error: {results['mv_with_cluster']['error']}")

    print("\nModel 2: Without concept_cluster control")
    results['mv_without_cluster'] = run_multivariate_without_clustering(df)
    if 'error' not in results['mv_without_cluster']:
        print(f"  AIC = {results['mv_without_cluster']['aic']:.1f}, "
              f"Pseudo-R² = {results['mv_without_cluster']['pseudo_r2']:.4f}")
    else:
        print(f"  Error: {results['mv_without_cluster']['error']}")

    print("\nModel 3: With is_compensation control only (targeted)")
    results['mv_with_compensation'] = run_multivariate_with_compensation_control(df)
    if 'error' not in results['mv_with_compensation']:
        print(f"  AIC = {results['mv_with_compensation']['aic']:.1f}, "
              f"Pseudo-R² = {results['mv_with_compensation']['pseudo_r2']:.4f}")
        if 'compensation_effect' in results['mv_with_compensation']:
            ce = results['mv_with_compensation']['compensation_effect']
            print(f"  Compensation effect: OR = {ce['odds_ratio']:.3f}, p = {ce['p']:.4f}")
    else:
        print(f"  Error: {results['mv_with_compensation']['error']}")

    # 4. Analyze compensation effect
    results['compensation_analysis'] = analyze_compensation_effect(df)

    # 5. Generate and save report
    print("\n" + "=" * 80)
    print("PHASE 4: GENERATING REPORT")
    print("=" * 80)

    report = generate_review_report(results)

    report_path = OUTPUT_PATH / "clustering_review_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Save detailed results as JSON
    # Convert non-serializable types
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj

    results_json = make_serializable(results)
    json_path = OUTPUT_PATH / "clustering_review_results.json"
    with open(json_path, 'w') as f:
        json.dump(results_json, f, indent=2, default=str)
    print(f"Detailed results saved to: {json_path}")

    # 6. Print key summary
    print("\n" + "=" * 80)
    print("KEY FINDINGS SUMMARY")
    print("=" * 80)

    # Model comparison
    if all('error' not in results.get(k, {'error': True}) for k in ['mv_with_cluster', 'mv_without_cluster', 'mv_with_compensation']):
        aics = {
            'Full clustering': results['mv_with_cluster']['aic'],
            'No clustering': results['mv_without_cluster']['aic'],
            'Compensation only': results['mv_with_compensation']['aic']
        }
        best_model = min(aics, key=aics.get)
        print(f"\n1. BEST MODEL (by AIC): {best_model}")
        print(f"   AIC values: {', '.join(f'{k}={v:.1f}' for k, v in sorted(aics.items(), key=lambda x: x[1]))}")

    # Compensation effect
    if 'compensation_analysis' in results:
        gap = results['compensation_analysis']['gap_pp']
        print(f"\n2. COMPENSATION EFFECT: {abs(gap):.1f}pp gap in pro-DS rate")
        print(f"   Compensation cases: {results['compensation_analysis']['compensation_pro_ds_rate']*100:.1f}% pro-DS")
        print(f"   Other cases: {results['compensation_analysis']['non_compensation_pro_ds_rate']*100:.1f}% pro-DS")

    # Effect size comparison
    if 'bivariate_with_cluster' in results and 'bivariate_without_cluster' in results:
        v_diff = results['bivariate_without_cluster']['effect_size'] - results['bivariate_with_cluster']['effect_size']
        print(f"\n3. CLUSTERING EFFECT ON BIVARIATE ASSOCIATION:")
        print(f"   With clustering: V = {results['bivariate_with_cluster']['effect_size']:.3f}")
        print(f"   Without clustering: V = {results['bivariate_without_cluster']['effect_size']:.3f}")
        if abs(v_diff) > 0.05:
            direction = "stronger" if v_diff > 0 else "weaker"
            print(f"   → Unclustered analysis shows {direction} association (Δ = {v_diff:.3f})")
        else:
            print(f"   → Similar effect sizes (Δ = {v_diff:.3f})")

    print("\n" + "=" * 80)
    print("CLUSTERING REVIEW COMPLETE!")
    print("=" * 80)

    return results


if __name__ == "__main__":
    results = main()
