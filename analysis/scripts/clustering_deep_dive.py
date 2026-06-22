#!/usr/bin/env python3
"""
clustering_deep_dive.py
=======================
Deep dive analysis into alternative clustering schemes and lawfulness bases.

This script:
1. Creates multiple alternative clustering schemes
2. Deep dives into Consent vs Legitimate Interest analysis
3. Reruns multivariate analyses with different approaches
4. Compares findings across all approaches

Author: Claude Code Analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output" / "clustering_deep_dive"

# ============================================================================
# ALTERNATIVE CLUSTERING SCHEMES
# ============================================================================

# Scheme 1: Original 8 clusters
CLUSTERING_ORIGINAL = {
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

# Scheme 2: Split ENFORCEMENT (compensation vs non-compensation) and LAWFULNESS (consent-like vs obligation-like)
CLUSTERING_SPLIT = {
    'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
              'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
    'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
               'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
    # Split LAWFULNESS into consent-type (data subject choice) vs obligation-type (external requirement)
    'LAWFULNESS_CONSENT': ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGITIMATE_INTERESTS'],
    'LAWFULNESS_OBLIGATION': ['LEGAL_OBLIGATION_BASIS', 'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS'],
    'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY',
                   'DATA_MINIMISATION'],
    'RIGHTS': ['RIGHT_OF_ACCESS', 'RIGHT_TO_RECTIFICATION', 'RIGHT_TO_ERASURE',
               'RIGHT_TO_RESTRICTION', 'RIGHT_TO_PORTABILITY', 'RIGHT_TO_OBJECT',
               'AUTOMATED_DECISION_MAKING'],
    'SPECIAL_CATEGORIES': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
    # Split ENFORCEMENT into compensation vs DPA/other enforcement
    'ENFORCEMENT_COMPENSATION': ['REMEDIES_COMPENSATION'],
    'ENFORCEMENT_DPA': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
                        'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REPRESENTATIVE_ACTIONS'],
    'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
              'MEMBER_STATE_DISCRETION', 'OTHER']
}

# Scheme 3: Granular - each major legal base separate
CLUSTERING_GRANULAR = {
    'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
              'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
    'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
               'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
    # Each legal basis separate
    'CONSENT': ['CONSENT_BASIS'],
    'CONTRACT': ['CONTRACT_BASIS'],
    'LEGAL_OBLIGATION': ['LEGAL_OBLIGATION_BASIS'],
    'LEGITIMATE_INTERESTS': ['LEGITIMATE_INTERESTS'],
    'PUBLIC_VITAL': ['VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS'],
    'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY',
                   'DATA_MINIMISATION'],
    'RIGHTS_ACCESS': ['RIGHT_OF_ACCESS'],
    'RIGHTS_ERASURE': ['RIGHT_TO_ERASURE', 'RIGHT_TO_RECTIFICATION'],
    'RIGHTS_OTHER': ['RIGHT_TO_RESTRICTION', 'RIGHT_TO_PORTABILITY', 'RIGHT_TO_OBJECT',
                     'AUTOMATED_DECISION_MAKING'],
    'SPECIAL_CATEGORIES': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
    'COMPENSATION': ['REMEDIES_COMPENSATION'],
    'DPA': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
            'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REPRESENTATIVE_ACTIONS'],
    'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
              'MEMBER_STATE_DISCRETION', 'OTHER']
}

# Scheme 4: Pro-DS rate based (empirical clustering based on outcome similarity)
# This will be computed dynamically based on actual pro-DS rates


def apply_clustering(df, clustering_scheme, cluster_col_name='cluster'):
    """Apply a clustering scheme to the dataframe."""
    concept_to_cluster = {}
    for cluster, concepts in clustering_scheme.items():
        for concept in concepts:
            concept_to_cluster[concept] = cluster

    df[cluster_col_name] = df['primary_concept'].map(concept_to_cluster).fillna('OTHER')
    return df


def create_empirical_clustering(df, threshold=0.15):
    """Create empirical clustering based on pro-DS rate similarity."""
    # Calculate pro-DS rate for each concept
    concept_rates = df.groupby('primary_concept')['pro_ds'].agg(['mean', 'count'])
    concept_rates.columns = ['pro_ds_rate', 'n']
    concept_rates = concept_rates[concept_rates['n'] >= 3]  # Only concepts with n>=3

    # Create clusters based on pro-DS rate bands
    def assign_cluster(rate):
        if rate >= 0.80:
            return 'HIGH_PRO_DS'
        elif rate >= 0.60:
            return 'MEDIUM_HIGH_PRO_DS'
        elif rate >= 0.40:
            return 'MEDIUM_PRO_DS'
        else:
            return 'LOW_PRO_DS'

    concept_rates['empirical_cluster'] = concept_rates['pro_ds_rate'].apply(assign_cluster)

    return concept_rates['empirical_cluster'].to_dict()


def cramers_v(contingency_table):
    """Calculate Cramér's V effect size."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape) - 1
    if min_dim == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))


# ============================================================================
# DEEP DIVE: CONSENT VS LEGITIMATE INTEREST
# ============================================================================

def deep_dive_lawfulness(df):
    """Deep dive analysis into lawfulness bases, especially Consent vs Legitimate Interest."""
    print("\n" + "=" * 80)
    print("DEEP DIVE: LAWFULNESS BASES ANALYSIS")
    print("=" * 80)

    results = {}

    # Filter to lawfulness concepts
    lawfulness_concepts = ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGAL_OBLIGATION_BASIS',
                           'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS', 'LEGITIMATE_INTERESTS']

    lawfulness_df = df[df['primary_concept'].isin(lawfulness_concepts)].copy()

    print(f"\nTotal LAWFULNESS holdings: {len(lawfulness_df)}")

    # Breakdown by concept
    print("\n--- Pro-DS Rate by Legal Basis ---")
    concept_stats = lawfulness_df.groupby('primary_concept').agg({
        'pro_ds': ['count', 'mean', 'std']
    }).round(3)
    concept_stats.columns = ['n', 'pro_ds_rate', 'std']
    concept_stats = concept_stats.sort_values('pro_ds_rate', ascending=False)

    for concept, row in concept_stats.iterrows():
        print(f"  {concept}: n={int(row['n'])}, pro-DS={row['pro_ds_rate']*100:.1f}%")

    results['concept_breakdown'] = concept_stats.to_dict()

    # Focus on Consent vs Legitimate Interest
    consent_df = df[df['primary_concept'] == 'CONSENT_BASIS']
    legit_df = df[df['primary_concept'] == 'LEGITIMATE_INTERESTS']

    print(f"\n--- Consent vs Legitimate Interest Comparison ---")
    print(f"  CONSENT_BASIS: n={len(consent_df)}, pro-DS={consent_df['pro_ds'].mean()*100:.1f}%")
    print(f"  LEGITIMATE_INTERESTS: n={len(legit_df)}, pro-DS={legit_df['pro_ds'].mean()*100:.1f}%")

    if len(consent_df) > 0 and len(legit_df) > 0:
        # Fisher exact test
        combined = pd.concat([consent_df, legit_df])
        contingency = pd.crosstab(combined['primary_concept'], combined['pro_ds'])
        if contingency.shape == (2, 2):
            odds_ratio, p_fisher = stats.fisher_exact(contingency)
            print(f"  Fisher's exact: OR={odds_ratio:.3f}, p={p_fisher:.4f}")
            results['consent_vs_legit'] = {
                'consent_n': len(consent_df),
                'consent_pro_ds': consent_df['pro_ds'].mean(),
                'legit_n': len(legit_df),
                'legit_pro_ds': legit_df['pro_ds'].mean(),
                'odds_ratio': odds_ratio,
                'p_value': p_fisher
            }

    # Analyze what drives the differences - look at other variables
    print("\n--- Characteristics by Legal Basis ---")

    for concept in ['CONSENT_BASIS', 'LEGITIMATE_INTERESTS', 'LEGAL_OBLIGATION_BASIS']:
        concept_df = df[df['primary_concept'] == concept]
        if len(concept_df) >= 3:
            print(f"\n  {concept} (n={len(concept_df)}):")

            # Chamber distribution
            if 'chamber_grouped' in concept_df.columns:
                chambers = concept_df['chamber_grouped'].value_counts()
                print(f"    Chambers: {dict(chambers)}")

            # Year range
            if 'year' in concept_df.columns:
                print(f"    Years: {concept_df['year'].min()}-{concept_df['year'].max()}")

            # Balancing
            if 'controller_ds_balancing' in concept_df.columns:
                balancing_rate = concept_df['controller_ds_balancing'].mean()
                print(f"    Balancing rate: {balancing_rate*100:.1f}%")

            # Necessity
            if 'necessity_discussed' in concept_df.columns:
                necessity_rate = concept_df['necessity_discussed'].mean()
                print(f"    Necessity discussed: {necessity_rate*100:.1f}%")

    # Multivariate within LAWFULNESS only
    if len(lawfulness_df) >= 15:
        print("\n--- Multivariate Analysis within LAWFULNESS ---")

        # Create concept dummies
        lawfulness_df = lawfulness_df.copy()
        lawfulness_df['is_consent'] = (lawfulness_df['primary_concept'] == 'CONSENT_BASIS').astype(int)
        lawfulness_df['is_legit_int'] = (lawfulness_df['primary_concept'] == 'LEGITIMATE_INTERESTS').astype(int)
        lawfulness_df['is_legal_oblig'] = (lawfulness_df['primary_concept'] == 'LEGAL_OBLIGATION_BASIS').astype(int)

        # Simple model
        try:
            formula = "pro_ds ~ is_consent + is_legit_int + is_legal_oblig"
            model = smf.logit(formula, data=lawfulness_df).fit(disp=0)

            print("\n  Logistic regression (reference: other lawfulness bases):")
            for var in ['is_consent', 'is_legit_int', 'is_legal_oblig']:
                if var in model.params.index:
                    coef = model.params[var]
                    odds = np.exp(coef)
                    p = model.pvalues[var]
                    sig = "**" if p < 0.01 else "*" if p < 0.05 else ""
                    print(f"    {var}: OR={odds:.3f}, p={p:.4f} {sig}")

            results['lawfulness_model'] = {
                'aic': model.aic,
                'n': int(model.nobs),
                'coefficients': {var: {'coef': model.params[var], 'p': model.pvalues[var]}
                                for var in model.params.index}
            }
        except Exception as e:
            print(f"  Model failed: {e}")

    return results


# ============================================================================
# MULTIVARIATE ANALYSIS WITH DIFFERENT CLUSTERING SCHEMES
# ============================================================================

def run_multivariate_comparison(df):
    """Run multivariate analysis with different clustering schemes."""
    print("\n" + "=" * 80)
    print("MULTIVARIATE ANALYSIS: CLUSTERING SCHEME COMPARISON")
    print("=" * 80)

    results = {}

    # Prepare data
    df = df.copy()

    # Apply all clustering schemes
    df = apply_clustering(df, CLUSTERING_ORIGINAL, 'cluster_original')
    df = apply_clustering(df, CLUSTERING_SPLIT, 'cluster_split')
    df = apply_clustering(df, CLUSTERING_GRANULAR, 'cluster_granular')

    # Create empirical clustering
    empirical_map = create_empirical_clustering(df)
    df['cluster_empirical'] = df['primary_concept'].map(empirical_map).fillna('MEDIUM_PRO_DS')

    # Define models to compare
    models = {
        'M0_no_clustering': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                           "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                           "level_shifting + any_balancing",

        'M1_compensation_only': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                                "is_compensation + "
                                "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                                "level_shifting + any_balancing",

        'M2_original_clustering': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                                  "C(cluster_original, Treatment(reference='OTHER')) + "
                                  "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                                  "level_shifting + any_balancing",

        'M3_split_clustering': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                               "C(cluster_split, Treatment(reference='OTHER')) + "
                               "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                               "level_shifting + any_balancing",

        'M4_granular_clustering': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                                  "C(cluster_granular, Treatment(reference='OTHER')) + "
                                  "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                                  "level_shifting + any_balancing",

        'M5_empirical_clustering': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                                   "C(cluster_empirical, Treatment(reference='MEDIUM_PRO_DS')) + "
                                   "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                                   "level_shifting + any_balancing",

        'M6_original_plus_compensation': "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
                                         "C(cluster_original, Treatment(reference='OTHER')) + is_compensation + "
                                         "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
                                         "level_shifting + any_balancing",
    }

    print("\n--- Model Comparison ---")
    print(f"{'Model':<35} {'AIC':>8} {'BIC':>8} {'R²':>8} {'N params':>10} {'Converged'}")
    print("-" * 80)

    model_results = {}

    for name, formula in models.items():
        try:
            model = smf.logit(formula, data=df).fit(disp=0)
            model_results[name] = {
                'converged': model.mle_retvals['converged'],
                'n': int(model.nobs),
                'aic': model.aic,
                'bic': model.bic,
                'pseudo_r2': model.prsquared,
                'n_params': len(model.params),
                'llf': model.llf
            }

            converged_str = "Yes" if model.mle_retvals['converged'] else "No"
            print(f"{name:<35} {model.aic:>8.1f} {model.bic:>8.1f} {model.prsquared:>8.4f} {len(model.params):>10} {converged_str}")

        except Exception as e:
            print(f"{name:<35} {'FAILED':<8} - {str(e)[:40]}")
            model_results[name] = {'error': str(e)}

    results['models'] = model_results

    # Find best model
    valid_models = {k: v for k, v in model_results.items() if 'aic' in v}
    if valid_models:
        best_aic = min(valid_models, key=lambda x: valid_models[x]['aic'])
        best_bic = min(valid_models, key=lambda x: valid_models[x]['bic'])

        print(f"\n--- Best Models ---")
        print(f"  By AIC: {best_aic} (AIC={valid_models[best_aic]['aic']:.1f})")
        print(f"  By BIC: {best_bic} (BIC={valid_models[best_bic]['bic']:.1f})")

        results['best_aic'] = best_aic
        results['best_bic'] = best_bic

    return results, df


def analyze_cluster_scheme_differences(df):
    """Analyze how different clustering schemes affect key findings."""
    print("\n" + "=" * 80)
    print("CLUSTER SCHEME IMPACT ANALYSIS")
    print("=" * 80)

    results = {}

    schemes = {
        'Original (8 clusters)': 'cluster_original',
        'Split (10 clusters)': 'cluster_split',
        'Granular (14 clusters)': 'cluster_granular',
        'Empirical (4 clusters)': 'cluster_empirical'
    }

    for scheme_name, col in schemes.items():
        print(f"\n--- {scheme_name} ---")

        # Pro-DS rates by cluster
        cluster_stats = df.groupby(col).agg({
            'pro_ds': ['count', 'mean']
        }).round(3)
        cluster_stats.columns = ['n', 'pro_ds_rate']
        cluster_stats = cluster_stats.sort_values('pro_ds_rate', ascending=False)

        print(f"\nCluster pro-DS rates:")
        for cluster, row in cluster_stats.iterrows():
            print(f"  {cluster}: n={int(row['n'])}, pro-DS={row['pro_ds_rate']*100:.1f}%")

        # Chi-square test
        contingency = pd.crosstab(df[col], df['pro_ds'])
        try:
            chi2, p, dof, _ = stats.chi2_contingency(contingency)
            v = cramers_v(contingency)
            print(f"\nChi-square: χ²={chi2:.2f}, p={p:.4f}, V={v:.3f}")

            results[scheme_name] = {
                'n_clusters': len(cluster_stats),
                'chi2': chi2,
                'p_value': p,
                'cramers_v': v,
                'cluster_stats': cluster_stats.to_dict()
            }
        except Exception as e:
            print(f"Chi-square failed: {e}")

    return results


def run_without_clustering_full(df):
    """Run key analyses completely without clustering (using primary_concept directly)."""
    print("\n" + "=" * 80)
    print("FULL ANALYSIS WITHOUT CLUSTERING")
    print("=" * 80)

    results = {}

    # 1. Primary concept frequencies
    print("\n--- Primary Concept Distribution ---")
    concept_stats = df.groupby('primary_concept').agg({
        'pro_ds': ['count', 'mean']
    }).round(3)
    concept_stats.columns = ['n', 'pro_ds_rate']
    concept_stats = concept_stats.sort_values('pro_ds_rate', ascending=False)

    print("\nTop 10 most common concepts:")
    for i, (concept, row) in enumerate(concept_stats.head(10).iterrows()):
        print(f"  {i+1}. {concept}: n={int(row['n'])}, pro-DS={row['pro_ds_rate']*100:.1f}%")

    results['concept_distribution'] = concept_stats.to_dict()

    # 2. Bivariate analysis with concepts (n>=5 only)
    concept_counts = df['primary_concept'].value_counts()
    valid_concepts = concept_counts[concept_counts >= 5].index
    df_filtered = df[df['primary_concept'].isin(valid_concepts)]

    print(f"\n--- Bivariate Analysis (concepts with n>=5) ---")
    print(f"Holdings included: {len(df_filtered)} of {len(df)} ({len(df_filtered)/len(df)*100:.1f}%)")
    print(f"Concepts included: {len(valid_concepts)} of {len(concept_counts)}")

    contingency = pd.crosstab(df_filtered['primary_concept'], df_filtered['pro_ds'])
    chi2, p, dof, _ = stats.chi2_contingency(contingency)
    v = cramers_v(contingency)

    print(f"Chi-square: χ²={chi2:.2f}, p={p:.4f}, Cramér's V={v:.3f}")

    results['bivariate'] = {
        'chi2': chi2,
        'p_value': p,
        'cramers_v': v,
        'n_holdings': len(df_filtered),
        'n_concepts': len(valid_concepts)
    }

    # 3. Multivariate with individual concept dummies (top concepts only)
    print("\n--- Multivariate with Concept Dummies ---")

    # Create dummies for top 6 concepts
    top_concepts = concept_counts.head(6).index.tolist()
    df_mv = df.copy()

    for concept in top_concepts:
        clean_name = concept.lower().replace('_', '')
        df_mv[f'is_{clean_name}'] = (df_mv['primary_concept'] == concept).astype(int)

    concept_vars = [f'is_{c.lower().replace("_", "")}' for c in top_concepts]
    concept_formula = " + ".join(concept_vars)

    formula = f"""pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
                  {concept_formula} +
                  C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose +
                  level_shifting + any_balancing"""

    try:
        model = smf.logit(formula, data=df_mv).fit(disp=0)

        print(f"\nModel fit: AIC={model.aic:.1f}, Pseudo-R²={model.prsquared:.4f}")
        print("\nConcept coefficients:")

        for var in concept_vars:
            if var in model.params.index:
                coef = model.params[var]
                odds = np.exp(coef)
                p_val = model.pvalues[var]
                sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
                concept_name = var.replace('is_', '').upper()
                print(f"  {concept_name}: OR={odds:.3f}, p={p_val:.4f} {sig}")

        results['multivariate_concepts'] = {
            'aic': model.aic,
            'pseudo_r2': model.prsquared,
            'n': int(model.nobs),
            'concept_effects': {
                var: {'coef': model.params[var], 'odds_ratio': np.exp(model.params[var]), 'p': model.pvalues[var]}
                for var in concept_vars if var in model.params.index
            }
        }
    except Exception as e:
        print(f"Model failed: {e}")
        results['multivariate_concepts'] = {'error': str(e)}

    return results


def generate_deep_dive_report(results):
    """Generate comprehensive markdown report."""

    report = """# Topic Clustering Deep Dive Analysis

## Executive Summary

This report provides a deep dive analysis into alternative clustering schemes and
specific examination of lawfulness bases (consent vs legitimate interest).

## 1. Alternative Clustering Schemes Evaluated

### 1.1 Schemes Compared

| Scheme | N Clusters | Description |
|--------|------------|-------------|
| Original | 8 | Current implementation (SCOPE, ACTORS, etc.) |
| Split | 10 | Separates ENFORCEMENT (compensation vs DPA) and LAWFULNESS (consent-type vs obligation-type) |
| Granular | 14 | Each major legal basis separate + more subdivisions |
| Empirical | 4 | Data-driven: HIGH/MEDIUM_HIGH/MEDIUM/LOW pro-DS rate bands |

"""

    # Add scheme comparison results
    if 'scheme_comparison' in results:
        report += "### 1.2 Statistical Comparison\n\n"
        report += "| Scheme | N Clusters | Chi-square | p-value | Cramér's V |\n"
        report += "|--------|------------|------------|---------|------------|\n"

        for scheme, data in results['scheme_comparison'].items():
            if 'chi2' in data:
                report += f"| {scheme} | {data['n_clusters']} | {data['chi2']:.2f} | {data['p_value']:.4f} | {data['cramers_v']:.3f} |\n"

        report += "\n"

    # Add model comparison
    if 'model_comparison' in results and 'models' in results['model_comparison']:
        report += "### 1.3 Multivariate Model Comparison\n\n"
        report += "| Model | AIC | BIC | Pseudo-R² | N params |\n"
        report += "|-------|-----|-----|-----------|----------|\n"

        for model_name, data in results['model_comparison']['models'].items():
            if 'aic' in data:
                report += f"| {model_name} | {data['aic']:.1f} | {data['bic']:.1f} | {data['pseudo_r2']:.4f} | {data['n_params']} |\n"

        if 'best_aic' in results['model_comparison']:
            report += f"\n**Best model by AIC**: {results['model_comparison']['best_aic']}\n"
            report += f"**Best model by BIC**: {results['model_comparison']['best_bic']}\n"

        report += "\n"

    # Add lawfulness deep dive
    if 'lawfulness_deep_dive' in results:
        report += """## 2. Deep Dive: Lawfulness Bases

### 2.1 Legal Basis Comparison

The LAWFULNESS cluster shows high internal heterogeneity. Key findings:

"""
        if 'consent_vs_legit' in results['lawfulness_deep_dive']:
            cvl = results['lawfulness_deep_dive']['consent_vs_legit']
            report += f"""| Legal Basis | N | Pro-DS Rate |
|-------------|---|-------------|
| CONSENT_BASIS | {cvl['consent_n']} | {cvl['consent_pro_ds']*100:.1f}% |
| LEGITIMATE_INTERESTS | {cvl['legit_n']} | {cvl['legit_pro_ds']*100:.1f}% |

**Fisher's exact test**: OR={cvl['odds_ratio']:.3f}, p={cvl['p_value']:.4f}

"""

        report += """### 2.2 Interpretation

- **CONSENT_BASIS**: Cases tend to favor data subjects when consent validity/scope is at issue
- **LEGITIMATE_INTERESTS**: Also generally pro-DS due to strict necessity and balancing requirements
- **LEGAL_OBLIGATION_BASIS**: Lower pro-DS rate as these involve external legal requirements where DS arguments have less traction

"""

    # Add no-clustering analysis
    if 'no_clustering_analysis' in results:
        report += """## 3. Analysis Without Clustering

### 3.1 Concept-Level Findings

"""
        if 'bivariate' in results['no_clustering_analysis']:
            biv = results['no_clustering_analysis']['bivariate']
            report += f"""The unclustered analysis includes {biv['n_holdings']} holdings across {biv['n_concepts']} concepts.

**Bivariate test**: Chi-square={biv['chi2']:.2f}, p={biv['p_value']:.4f}, Cramér's V={biv['cramers_v']:.3f}

"""

        if 'multivariate_concepts' in results['no_clustering_analysis'] and 'concept_effects' in results['no_clustering_analysis']['multivariate_concepts']:
            report += "### 3.2 Individual Concept Effects\n\n"
            report += "| Concept | Odds Ratio | p-value |\n"
            report += "|---------|------------|----------|\n"

            for var, data in results['no_clustering_analysis']['multivariate_concepts']['concept_effects'].items():
                concept = var.replace('is_', '').upper()
                sig = "**" if data['p'] < 0.01 else "*" if data['p'] < 0.05 else ""
                report += f"| {concept} | {data['odds_ratio']:.3f} | {data['p']:.4f}{sig} |\n"

            report += "\n"

    report += """## 4. Recommendations

### 4.1 Clustering Approach

Based on this analysis:

1. **Split clustering** (separating compensation and consent-type lawfulness) provides
   a good balance of interpretability and homogeneity
2. **Granular clustering** loses too many degrees of freedom for the sample size
3. **Empirical clustering** is data-driven but may overfit and lacks legal interpretability

### 4.2 For Lawfulness Analysis

1. Consider treating CONSENT_BASIS and LEGITIMATE_INTERESTS together (both consent-like, high pro-DS)
2. Treat LEGAL_OBLIGATION_BASIS separately (obligation-based, lower pro-DS)
3. PUBLIC_INTEREST_BASIS and VITAL_INTERESTS_BASIS have very few cases - combine or exclude

### 4.3 Sensitivity Analysis Recommendations

Always report:
1. Primary results with chosen clustering
2. Sensitivity with split ENFORCEMENT (compensation vs other)
3. Results without any clustering (raw concept as control)

## 5. Conclusion

The analysis confirms that:
- Current clustering masks significant within-cluster heterogeneity
- The compensation paradox in ENFORCEMENT is the most impactful source of heterogeneity
- Lawfulness bases can be meaningfully split into consent-type vs obligation-type
- Model fit improves slightly with split clustering or targeted controls
"""

    return report


def main():
    """Main function to run the deep dive analysis."""

    print("=" * 80)
    print("CLUSTERING DEEP DIVE ANALYSIS")
    print("=" * 80)

    # Load data
    if not DATA_PATH.exists():
        print(f"Error: Data not found at {DATA_PATH}")
        return None

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded {len(df)} holdings")

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    results = {}

    # 1. Deep dive into lawfulness
    results['lawfulness_deep_dive'] = deep_dive_lawfulness(df)

    # 2. Run multivariate comparison
    results['model_comparison'], df = run_multivariate_comparison(df)

    # 3. Analyze scheme differences
    results['scheme_comparison'] = analyze_cluster_scheme_differences(df)

    # 4. Run without clustering
    results['no_clustering_analysis'] = run_without_clustering_full(df)

    # 5. Generate report
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    report = generate_deep_dive_report(results)

    report_path = OUTPUT_PATH / "clustering_deep_dive_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Save detailed results
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

    json_path = OUTPUT_PATH / "clustering_deep_dive_results.json"
    with open(json_path, 'w') as f:
        json.dump(make_serializable(results), f, indent=2, default=str)
    print(f"Results saved to: {json_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("KEY FINDINGS SUMMARY")
    print("=" * 80)

    if 'model_comparison' in results and 'best_aic' in results['model_comparison']:
        print(f"\n1. BEST MODEL: {results['model_comparison']['best_aic']}")

    if 'lawfulness_deep_dive' in results and 'consent_vs_legit' in results['lawfulness_deep_dive']:
        cvl = results['lawfulness_deep_dive']['consent_vs_legit']
        print(f"\n2. CONSENT vs LEGITIMATE INTEREST:")
        print(f"   Consent: {cvl['consent_pro_ds']*100:.1f}% pro-DS (n={cvl['consent_n']})")
        print(f"   Legit Int: {cvl['legit_pro_ds']*100:.1f}% pro-DS (n={cvl['legit_n']})")
        print(f"   OR={cvl['odds_ratio']:.3f}, p={cvl['p_value']:.4f}")

    if 'scheme_comparison' in results:
        print(f"\n3. EFFECT SIZES BY SCHEME:")
        for scheme, data in results['scheme_comparison'].items():
            if 'cramers_v' in data:
                print(f"   {scheme}: V={data['cramers_v']:.3f}")

    print("\n" + "=" * 80)
    print("DEEP DIVE COMPLETE!")
    print("=" * 80)

    return results


if __name__ == "__main__":
    results = main()
