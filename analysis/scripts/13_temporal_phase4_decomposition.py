#!/usr/bin/env python3
"""
Phase 4: Decomposition Analysis
CJEU GDPR Temporal Effects Study

This script:
4.1 Kitagawa-Blinder-Oaxaca decomposition
4.2 Direct standardization
4.3 Shift-share analysis
4.4 Counterfactual analysis
4.5 Detailed composition accounting
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
# Fixed: Updated path from "parsed-coded" to "data/parsed"
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "parsed" / "holdings.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "temporal"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA LOADING
# ============================================================================
def load_and_prepare_data():
    """Load holdings data and create all needed variables."""
    df = pd.read_csv(DATA_PATH)

    df['judgment_date'] = pd.to_datetime(df['judgment_date'])
    df['year'] = df['judgment_date'].dt.year
    df['period'] = np.where(df['year'] < 2023, 'early', 'late')
    df['period_binary'] = np.where(df['year'] < 2023, 0, 1)

    df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)

    # Concept clusters
    concept_clusters = {
        'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
                  'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
        'ENFORCEMENT': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
                        'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REMEDIES_COMPENSATION',
                        'REPRESENTATIVE_ACTIONS'],
        'RIGHTS': ['RIGHT_OF_ACCESS', 'RIGHT_TO_RECTIFICATION', 'RIGHT_TO_ERASURE',
                   'RIGHT_TO_RESTRICTION', 'RIGHT_TO_PORTABILITY', 'RIGHT_TO_OBJECT',
                   'AUTOMATED_DECISION_MAKING'],
        'LAWFULNESS': ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGAL_OBLIGATION_BASIS',
                       'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS', 'LEGITIMATE_INTERESTS'],
        'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY'],
        'SPECIAL': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
        'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
                   'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
        'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
                  'MEMBER_STATE_DISCRETION', 'OTHER']
    }

    def get_cluster(concept):
        for cluster, concepts in concept_clusters.items():
            if concept in concepts:
                return cluster
        return 'OTHER'

    df['concept_cluster'] = df['primary_concept'].apply(get_cluster)

    df['pro_ds_purpose'] = df['teleological_purposes'].fillna('').apply(
        lambda x: 'HIGH_LEVEL_OF_PROTECTION' in x or 'FUNDAMENTAL_RIGHTS' in x
    ).astype(int)

    df['is_compensation'] = (df['primary_concept'] == 'REMEDIES_COMPENSATION').astype(int)
    df['is_third_chamber'] = (df['chamber'] == 'THIRD').astype(int)
    df['is_grand_chamber'] = (df['chamber'] == 'GRAND_CHAMBER').astype(int)

    bool_cols = ['level_shifting', 'teleological_present', 'systematic_present']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map({'True': 1, 'False': 0, True: 1, False: 0}).fillna(0).astype(int)

    return df

# ============================================================================
# 4.1 BLINDER-OAXACA STYLE DECOMPOSITION
# ============================================================================
def blinder_oaxaca_decomposition(df):
    """
    Perform Blinder-Oaxaca style decomposition of the pro-DS rate gap.

    Decomposition formula:
    Δ = (Y_late - Y_early) = Composition Effect + Coefficient Effect + Interaction

    Where:
    - Composition Effect = (X_late - X_early) × β_early
    - Coefficient Effect = X_early × (β_late - β_early)
    - Interaction = (X_late - X_early) × (β_late - β_early)
    """

    results = {}

    print("=" * 80)
    print("4.1 BLINDER-OAXACA DECOMPOSITION")
    print("=" * 80)

    df_early = df[df['period'] == 'early'].copy()
    df_late = df[df['period'] == 'late'].copy()

    # Raw outcome difference
    y_early = df_early['pro_ds'].mean()
    y_late = df_late['pro_ds'].mean()
    total_diff = y_late - y_early

    print(f"\nRaw Pro-DS Rates:")
    print(f"  Early (2019-2022): {y_early*100:.1f}% (N={len(df_early)})")
    print(f"  Late (2023-2025):  {y_late*100:.1f}% (N={len(df_late)})")
    print(f"  Difference: {total_diff*100:+.1f} percentage points")

    results['raw_rates'] = {
        'early': round(y_early * 100, 2),
        'late': round(y_late * 100, 2),
        'difference_pp': round(total_diff * 100, 2)
    }

    # Fit models for each period
    # Use simpler features for early period due to small N and separation
    features_full = ['is_compensation', 'pro_ds_purpose', 'is_third_chamber']
    features_simple = ['pro_ds_purpose', 'is_third_chamber']  # Exclude compensation (too few in early)

    print(f"\n--- Fitting Period-Specific Models ---")
    print("Note: Using simplified model for early period due to small sample and separation")

    # Early period model (simplified - compensation has near-zero variance)
    X_early = sm.add_constant(df_early[features_simple])
    try:
        model_early = sm.Logit(df_early['pro_ds'], X_early).fit(disp=0, method='bfgs', maxiter=1000)
        print(f"\nEarly period model (simplified):")
        for feat in features_simple:
            print(f"  {feat}: OR = {np.exp(model_early.params[feat]):.3f}")
    except:
        # Fallback to LPM
        model_early = sm.OLS(df_early['pro_ds'], X_early).fit()
        print(f"\nEarly period model (LPM fallback):")
        for feat in features_simple:
            print(f"  {feat}: coef = {model_early.params[feat]:.3f}")

    # Late period model (full features)
    X_late = sm.add_constant(df_late[features_full])
    try:
        model_late = sm.Logit(df_late['pro_ds'], X_late).fit(disp=0)
        print(f"\nLate period model:")
        for feat in features_full:
            print(f"  {feat}: OR = {np.exp(model_late.params[feat]):.3f}")
    except:
        model_late = sm.OLS(df_late['pro_ds'], X_late).fit()
        print(f"\nLate period model (LPM fallback):")
        for feat in features_full:
            print(f"  {feat}: coef = {model_late.params[feat]:.3f}")

    # Calculate mean characteristics (using full feature set)
    features = features_full
    X_mean_early = df_early[features].mean()
    X_mean_late = df_late[features].mean()

    print(f"\n--- Mean Characteristics by Period ---")
    print(f"{'Variable':<25} {'Early':>10} {'Late':>10} {'Diff':>10}")
    print("-" * 55)
    for feat in features:
        print(f"{feat:<25} {X_mean_early[feat]*100:>10.1f}% {X_mean_late[feat]*100:>10.1f}% {(X_mean_late[feat]-X_mean_early[feat])*100:>+10.1f}")

    results['mean_characteristics'] = {
        'early': X_mean_early.to_dict(),
        'late': X_mean_late.to_dict()
    }

    # Linear decomposition (simpler, more interpretable)
    print(f"\n--- Linear Approximation Decomposition ---")

    # Using pooled coefficients as reference
    X_pooled = sm.add_constant(df[features])
    model_pooled = sm.Logit(df['pro_ds'], X_pooled).fit(disp=0)

    # Composition effect: difference in means × pooled coefficient
    composition_effect = 0
    composition_detail = {}
    for feat in features:
        contrib = (X_mean_late[feat] - X_mean_early[feat]) * model_pooled.params[feat]
        composition_effect += contrib
        composition_detail[feat] = {
            'mean_diff': round((X_mean_late[feat] - X_mean_early[feat]) * 100, 2),
            'pooled_coef': round(model_pooled.params[feat], 4),
            'contribution': round(contrib * 100, 2)  # Convert to pp
        }

    # For binary outcome, convert from log-odds scale
    # Simple linear probability approximation
    lpm_early = sm.OLS(df_early['pro_ds'], sm.add_constant(df_early[features])).fit()
    lpm_late = sm.OLS(df_late['pro_ds'], sm.add_constant(df_late[features])).fit()
    lpm_pooled = sm.OLS(df['pro_ds'], sm.add_constant(df[features])).fit()

    # Recalculate with LPM for interpretability
    composition_lpm = 0
    coefficient_lpm = 0
    for feat in features:
        # Composition: change in X × pooled β
        comp = (X_mean_late[feat] - X_mean_early[feat]) * lpm_pooled.params[feat]
        composition_lpm += comp

        # Coefficient: early X × change in β
        coef = X_mean_early[feat] * (lpm_late.params[feat] - lpm_early.params[feat])
        coefficient_lpm += coef

        composition_detail[feat]['lpm_composition_pp'] = round(comp * 100, 2)
        composition_detail[feat]['lpm_coefficient_pp'] = round(coef * 100, 2)

    interaction_lpm = total_diff - composition_lpm - coefficient_lpm

    results['decomposition_lpm'] = {
        'total_difference_pp': round(total_diff * 100, 2),
        'composition_effect_pp': round(composition_lpm * 100, 2),
        'coefficient_effect_pp': round(coefficient_lpm * 100, 2),
        'interaction_pp': round(interaction_lpm * 100, 2),
        'composition_pct': round(composition_lpm / total_diff * 100, 1) if total_diff != 0 else 0,
        'coefficient_pct': round(coefficient_lpm / total_diff * 100, 1) if total_diff != 0 else 0
    }

    print(f"\nDecomposition Results (Linear Probability Model):")
    print(f"  Total difference: {total_diff*100:+.2f} pp")
    print(f"  Composition effect: {composition_lpm*100:+.2f} pp ({abs(composition_lpm/total_diff)*100:.1f}% of total)")
    print(f"  Coefficient effect: {coefficient_lpm*100:+.2f} pp ({abs(coefficient_lpm/total_diff)*100:.1f}% of total)")
    print(f"  Interaction: {interaction_lpm*100:+.2f} pp")

    print(f"\n--- Detailed Composition Effects ---")
    print(f"{'Variable':<25} {'Mean Δ':>10} {'Contrib (pp)':>15}")
    print("-" * 55)
    for feat, detail in composition_detail.items():
        print(f"{feat:<25} {detail['mean_diff']:>+10.1f}% {detail['lpm_composition_pp']:>+15.2f}")

    results['composition_detail'] = composition_detail

    return results

# ============================================================================
# 4.2 DIRECT STANDARDIZATION
# ============================================================================
def direct_standardization(df):
    """
    Calculate standardized pro-DS rates holding composition constant.
    """

    results = {}

    print("\n" + "=" * 80)
    print("4.2 DIRECT STANDARDIZATION")
    print("=" * 80)

    # Standardize by concept cluster
    print("\n--- Standardization by Concept Cluster ---")

    # Calculate within-cluster pro-DS rates by period
    cluster_rates = df.groupby(['period', 'concept_cluster'])['pro_ds'].agg(['mean', 'count'])
    cluster_rates = cluster_rates.unstack(level=0)

    # Standard population: overall marginal distribution
    standard_weights = df['concept_cluster'].value_counts(normalize=True)

    print(f"\nWithin-Cluster Pro-DS Rates:")
    print(f"{'Cluster':<15} {'Weight':>10} {'Early':>10} {'Late':>10} {'Diff':>10}")
    print("-" * 55)

    standardized_early = 0
    standardized_late = 0
    cluster_detail = {}

    for cluster in standard_weights.index:
        weight = standard_weights[cluster]
        early_rate = cluster_rates.loc[cluster, ('mean', 'early')] if ('mean', 'early') in cluster_rates.columns and cluster in cluster_rates.index else np.nan
        late_rate = cluster_rates.loc[cluster, ('mean', 'late')] if ('mean', 'late') in cluster_rates.columns and cluster in cluster_rates.index else np.nan

        if not np.isnan(early_rate) and not np.isnan(late_rate):
            standardized_early += weight * early_rate
            standardized_late += weight * late_rate
            diff = late_rate - early_rate
            print(f"{cluster:<15} {weight*100:>10.1f}% {early_rate*100:>10.1f}% {late_rate*100:>10.1f}% {diff*100:>+10.1f}")

            cluster_detail[cluster] = {
                'weight': round(weight * 100, 2),
                'early_rate': round(early_rate * 100, 2),
                'late_rate': round(late_rate * 100, 2),
                'within_change': round(diff * 100, 2)
            }

    # Raw rates for comparison
    raw_early = df[df['period'] == 'early']['pro_ds'].mean()
    raw_late = df[df['period'] == 'late']['pro_ds'].mean()

    print(f"\nComparison:")
    print(f"  Raw Early Rate:          {raw_early*100:.1f}%")
    print(f"  Raw Late Rate:           {raw_late*100:.1f}%")
    print(f"  Raw Difference:          {(raw_late-raw_early)*100:+.1f} pp")
    print(f"  Standardized Early Rate: {standardized_early*100:.1f}%")
    print(f"  Standardized Late Rate:  {standardized_late*100:.1f}%")
    print(f"  Standardized Difference: {(standardized_late-standardized_early)*100:+.1f} pp")

    # Composition-adjusted decline
    raw_diff = (raw_late - raw_early) * 100
    std_diff = (standardized_late - standardized_early) * 100
    composition_explained = raw_diff - std_diff

    print(f"\n  Composition-Explained:   {composition_explained:+.1f} pp ({abs(composition_explained/raw_diff)*100:.1f}% of raw decline)")
    print(f"  Residual (Coefficient):  {std_diff:+.1f} pp ({abs(std_diff/raw_diff)*100:.1f}% of raw decline)")

    results['concept_cluster_standardization'] = {
        'raw_early': round(raw_early * 100, 2),
        'raw_late': round(raw_late * 100, 2),
        'raw_diff_pp': round(raw_diff, 2),
        'standardized_early': round(standardized_early * 100, 2),
        'standardized_late': round(standardized_late * 100, 2),
        'standardized_diff_pp': round(std_diff, 2),
        'composition_explained_pp': round(composition_explained, 2),
        'composition_explained_pct': round(abs(composition_explained/raw_diff) * 100, 1) if raw_diff != 0 else 0,
        'cluster_detail': cluster_detail
    }

    # Standardize by compensation status
    print("\n--- Standardization by Compensation Status ---")

    comp_rates = df.groupby(['period', 'is_compensation'])['pro_ds'].mean().unstack(level=0)
    comp_weights = df['is_compensation'].value_counts(normalize=True)

    std_early_comp = sum(comp_weights[c] * comp_rates.loc[c, 'early'] for c in [0, 1] if c in comp_rates.index)
    std_late_comp = sum(comp_weights[c] * comp_rates.loc[c, 'late'] for c in [0, 1] if c in comp_rates.index)

    print(f"  Raw Difference:          {(raw_late-raw_early)*100:+.1f} pp")
    print(f"  Standardized Difference: {(std_late_comp-std_early_comp)*100:+.1f} pp")
    print(f"  Composition-Explained:   {((raw_late-raw_early)-(std_late_comp-std_early_comp))*100:+.1f} pp")

    results['compensation_standardization'] = {
        'standardized_diff_pp': round((std_late_comp-std_early_comp) * 100, 2),
        'composition_explained_pp': round(((raw_late-raw_early)-(std_late_comp-std_early_comp)) * 100, 2)
    }

    return results

# ============================================================================
# 4.3 SHIFT-SHARE ANALYSIS
# ============================================================================
def shift_share_analysis(df):
    """
    Decompose change into within-cluster and between-cluster effects.
    """

    results = {}

    print("\n" + "=" * 80)
    print("4.3 SHIFT-SHARE ANALYSIS")
    print("=" * 80)

    # Calculate cluster-level statistics by period
    early = df[df['period'] == 'early']
    late = df[df['period'] == 'late']

    clusters = df['concept_cluster'].unique()

    print(f"\n{'Cluster':<15} {'w_E':>8} {'w_L':>8} {'Δw':>8} {'p_E':>8} {'p_L':>8} {'Δp':>8}")
    print("-" * 65)

    within_effect = 0
    between_effect = 0
    interaction_effect = 0

    detail = {}
    for cluster in clusters:
        # Weights (proportions)
        w_early = (early['concept_cluster'] == cluster).mean()
        w_late = (late['concept_cluster'] == cluster).mean()
        w_avg = (df['concept_cluster'] == cluster).mean()

        # Pro-DS rates within cluster
        p_early = early[early['concept_cluster'] == cluster]['pro_ds'].mean() if w_early > 0 else 0
        p_late = late[late['concept_cluster'] == cluster]['pro_ds'].mean() if w_late > 0 else 0
        p_avg = df[df['concept_cluster'] == cluster]['pro_ds'].mean()

        delta_w = w_late - w_early
        delta_p = p_late - p_early

        # Contributions
        within = w_avg * delta_p  # Within effect: holding composition constant
        between = p_avg * delta_w  # Between effect: changing composition
        interact = delta_w * delta_p  # Interaction

        within_effect += within
        between_effect += between
        interaction_effect += interact

        print(f"{cluster:<15} {w_early*100:>8.1f} {w_late*100:>8.1f} {delta_w*100:>+8.1f} {p_early*100:>8.1f} {p_late*100:>8.1f} {delta_p*100:>+8.1f}")

        detail[cluster] = {
            'weight_early': round(w_early * 100, 2),
            'weight_late': round(w_late * 100, 2),
            'weight_change': round(delta_w * 100, 2),
            'rate_early': round(p_early * 100, 2) if p_early > 0 else None,
            'rate_late': round(p_late * 100, 2) if p_late > 0 else None,
            'rate_change': round(delta_p * 100, 2) if p_early > 0 and p_late > 0 else None,
            'within_contrib_pp': round(within * 100, 2),
            'between_contrib_pp': round(between * 100, 2)
        }

    total = within_effect + between_effect + interaction_effect

    print(f"\n--- Shift-Share Decomposition ---")
    print(f"  Total change: {total*100:+.2f} pp")
    print(f"  Within effect (rate changes): {within_effect*100:+.2f} pp ({abs(within_effect/total)*100:.1f}%)")
    print(f"  Between effect (composition): {between_effect*100:+.2f} pp ({abs(between_effect/total)*100:.1f}%)")
    print(f"  Interaction: {interaction_effect*100:+.2f} pp ({abs(interaction_effect/total)*100:.1f}%)")

    results['shift_share'] = {
        'total_change_pp': round(total * 100, 2),
        'within_effect_pp': round(within_effect * 100, 2),
        'between_effect_pp': round(between_effect * 100, 2),
        'interaction_pp': round(interaction_effect * 100, 2),
        'within_pct': round(abs(within_effect/total) * 100, 1) if total != 0 else 0,
        'between_pct': round(abs(between_effect/total) * 100, 1) if total != 0 else 0,
        'cluster_detail': detail
    }

    return results

# ============================================================================
# 4.4 COUNTERFACTUAL ANALYSIS
# ============================================================================
def counterfactual_analysis(df):
    """
    Estimate counterfactual pro-DS rates under different scenarios.
    """

    results = {}

    print("\n" + "=" * 80)
    print("4.4 COUNTERFACTUAL ANALYSIS")
    print("=" * 80)

    early = df[df['period'] == 'early']
    late = df[df['period'] == 'late']

    actual_early = early['pro_ds'].mean()
    actual_late = late['pro_ds'].mean()

    print(f"\nActual Pro-DS Rates:")
    print(f"  Early: {actual_early*100:.1f}%")
    print(f"  Late:  {actual_late*100:.1f}%")

    # Counterfactual 1: What if late period had early period's compensation rate?
    print(f"\n--- Counterfactual 1: No Compensation Surge ---")
    print("What if the late period had the same compensation case proportion as early?")

    comp_rate_early = early['is_compensation'].mean()
    comp_rate_late = late['is_compensation'].mean()

    # Pro-DS rates by compensation status in late period
    late_comp_pro_ds = late[late['is_compensation'] == 1]['pro_ds'].mean()
    late_noncomp_pro_ds = late[late['is_compensation'] == 0]['pro_ds'].mean()

    # Counterfactual late rate with early compensation proportion
    cf1_late = comp_rate_early * late_comp_pro_ds + (1 - comp_rate_early) * late_noncomp_pro_ds

    print(f"  Early compensation rate: {comp_rate_early*100:.1f}%")
    print(f"  Late compensation rate:  {comp_rate_late*100:.1f}%")
    print(f"  Actual late pro-DS:      {actual_late*100:.1f}%")
    print(f"  Counterfactual late:     {cf1_late*100:.1f}%")
    print(f"  Compensation effect:     {(actual_late - cf1_late)*100:+.1f} pp")

    results['no_compensation_surge'] = {
        'actual_late': round(actual_late * 100, 2),
        'counterfactual_late': round(cf1_late * 100, 2),
        'compensation_effect_pp': round((actual_late - cf1_late) * 100, 2)
    }

    # Counterfactual 2: What if late period had early period's concept cluster distribution?
    print(f"\n--- Counterfactual 2: No Concept Shift ---")
    print("What if the late period had the same concept cluster distribution as early?")

    early_cluster_dist = early['concept_cluster'].value_counts(normalize=True)
    late_cluster_rates = late.groupby('concept_cluster')['pro_ds'].mean()

    cf2_late = sum(early_cluster_dist.get(c, 0) * late_cluster_rates.get(c, 0)
                   for c in df['concept_cluster'].unique())

    print(f"  Actual late pro-DS:      {actual_late*100:.1f}%")
    print(f"  Counterfactual late:     {cf2_late*100:.1f}%")
    print(f"  Concept shift effect:    {(actual_late - cf2_late)*100:+.1f} pp")

    results['no_concept_shift'] = {
        'actual_late': round(actual_late * 100, 2),
        'counterfactual_late': round(cf2_late * 100, 2),
        'concept_shift_effect_pp': round((actual_late - cf2_late) * 100, 2)
    }

    # Counterfactual 3: What if late period had early period's full characteristic distribution?
    print(f"\n--- Counterfactual 3: Full Composition Adjustment ---")

    # Fit model on late period
    features = ['is_compensation', 'is_third_chamber', 'pro_ds_purpose']
    X_late = sm.add_constant(late[features])
    model_late = sm.Logit(late['pro_ds'], X_late).fit(disp=0)

    # Predict with early period characteristics
    X_early_for_pred = sm.add_constant(early[features])
    cf3_predictions = model_late.predict(X_early_for_pred)
    cf3_late = cf3_predictions.mean()

    print(f"  Actual late pro-DS:      {actual_late*100:.1f}%")
    print(f"  Counterfactual late:     {cf3_late*100:.1f}%")
    print(f"  Full composition effect: {(actual_late - cf3_late)*100:+.1f} pp")

    results['full_composition_adjustment'] = {
        'actual_late': round(actual_late * 100, 2),
        'counterfactual_late': round(cf3_late * 100, 2),
        'full_composition_effect_pp': round((actual_late - cf3_late) * 100, 2)
    }

    return results

# ============================================================================
# 4.5 SUMMARY DECOMPOSITION
# ============================================================================
def summary_decomposition(df):
    """
    Provide final summary of decomposition findings.
    """

    results = {}

    print("\n" + "=" * 80)
    print("4.5 SUMMARY DECOMPOSITION")
    print("=" * 80)

    early = df[df['period'] == 'early']
    late = df[df['period'] == 'late']

    raw_early = early['pro_ds'].mean() * 100
    raw_late = late['pro_ds'].mean() * 100
    raw_diff = raw_late - raw_early

    # Method 1: Simple compensation accounting
    comp_rate_early = early['is_compensation'].mean()
    comp_rate_late = late['is_compensation'].mean()
    late_comp_pro_ds = late[late['is_compensation'] == 1]['pro_ds'].mean()
    late_noncomp_pro_ds = late[late['is_compensation'] == 0]['pro_ds'].mean()
    cf_late = comp_rate_early * late_comp_pro_ds + (1 - comp_rate_early) * late_noncomp_pro_ds
    compensation_effect = (raw_late/100 - cf_late) * 100

    # Method 2: Standardization
    clusters = df['concept_cluster'].unique()
    std_weights = df['concept_cluster'].value_counts(normalize=True)
    early_cluster_rates = early.groupby('concept_cluster')['pro_ds'].mean()
    late_cluster_rates = late.groupby('concept_cluster')['pro_ds'].mean()

    std_early = sum(std_weights.get(c, 0) * early_cluster_rates.get(c, 0) for c in clusters) * 100
    std_late = sum(std_weights.get(c, 0) * late_cluster_rates.get(c, 0) for c in clusters) * 100
    std_diff = std_late - std_early

    composition_explained = raw_diff - std_diff

    print(f"\n╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                    DECOMPOSITION SUMMARY                          ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  Raw Pro-DS Rate (Early):        {raw_early:>6.1f}%                         ║")
    print(f"║  Raw Pro-DS Rate (Late):         {raw_late:>6.1f}%                         ║")
    print(f"║  Raw Difference:                {raw_diff:>+7.1f} pp                        ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  DECOMPOSITION (Standardization Method):                         ║")
    print(f"║    Composition Effect:          {composition_explained:>+7.1f} pp  ({abs(composition_explained/raw_diff)*100:>5.1f}%)          ║")
    print(f"║    Coefficient Effect:          {std_diff:>+7.1f} pp  ({abs(std_diff/raw_diff)*100:>5.1f}%)          ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  INTERPRETATION:                                                 ║")
    if abs(composition_explained/raw_diff) > 0.7:
        print(f"║    The decline is PRIMARILY COMPOSITIONAL                        ║")
        print(f"║    ({abs(composition_explained/raw_diff)*100:.0f}% explained by changing case mix)                       ║")
    else:
        print(f"║    The decline reflects BOTH composition and coefficient changes ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")

    results['summary'] = {
        'raw_early_pct': round(raw_early, 2),
        'raw_late_pct': round(raw_late, 2),
        'raw_difference_pp': round(raw_diff, 2),
        'composition_effect_pp': round(composition_explained, 2),
        'coefficient_effect_pp': round(std_diff, 2),
        'composition_pct_of_total': round(abs(composition_explained/raw_diff) * 100, 1) if raw_diff != 0 else 0,
        'coefficient_pct_of_total': round(abs(std_diff/raw_diff) * 100, 1) if raw_diff != 0 else 0,
        'interpretation': 'Primarily compositional' if abs(composition_explained/raw_diff) > 0.7 else 'Mixed'
    }

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Execute Phase 4 analysis."""

    print("=" * 80)
    print("PHASE 4: DECOMPOSITION ANALYSIS")
    print("CJEU GDPR Jurisprudence - Temporal Effects Study")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Load data
    print("\nLoading data...")
    df = load_and_prepare_data()
    print(f"Loaded {len(df)} holdings")

    all_results = {}

    # 4.1 Blinder-Oaxaca decomposition
    all_results['blinder_oaxaca'] = blinder_oaxaca_decomposition(df)

    # 4.2 Direct standardization
    all_results['standardization'] = direct_standardization(df)

    # 4.3 Shift-share analysis
    all_results['shift_share'] = shift_share_analysis(df)

    # 4.4 Counterfactual analysis
    all_results['counterfactual'] = counterfactual_analysis(df)

    # 4.5 Summary
    all_results['summary'] = summary_decomposition(df)

    # Metadata
    all_results['metadata'] = {
        'analysis_date': datetime.now().isoformat(),
        'n_holdings': len(df),
        'n_early': len(df[df['period'] == 'early']),
        'n_late': len(df[df['period'] == 'late'])
    }

    # Key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS - PHASE 4")
    print("=" * 80)

    print("""
    1. RAW DECLINE
       - Early period: {:.1f}% pro-DS
       - Late period:  {:.1f}% pro-DS
       - Difference:   {:.1f} pp

    2. DECOMPOSITION RESULTS
       - Composition effect: {:.1f} pp ({:.0f}% of decline)
       - Coefficient effect: {:.1f} pp ({:.0f}% of decline)

    3. COUNTERFACTUAL: NO COMPENSATION SURGE
       - If late period had early's compensation rate: {:.1f}% pro-DS
       - Compensation surge explains: {:.1f} pp of decline

    4. INTERPRETATION
       {}

    5. CONCLUSION
       The observed decline in pro-DS rulings is {} explained by
       compositional changes (particularly the Article 82 compensation surge),
       not by changes in how the Court decides cases.
    """.format(
        all_results['summary']['summary']['raw_early_pct'],
        all_results['summary']['summary']['raw_late_pct'],
        all_results['summary']['summary']['raw_difference_pp'],
        all_results['summary']['summary']['composition_effect_pp'],
        all_results['summary']['summary']['composition_pct_of_total'],
        all_results['summary']['summary']['coefficient_effect_pp'],
        all_results['summary']['summary']['coefficient_pct_of_total'],
        all_results['counterfactual']['no_compensation_surge']['counterfactual_late'],
        all_results['counterfactual']['no_compensation_surge']['compensation_effect_pp'],
        all_results['summary']['summary']['interpretation'],
        'primarily' if all_results['summary']['summary']['composition_pct_of_total'] > 70 else 'partially'
    ))

    # Save results
    output_file = OUTPUT_DIR / "phase4_decomposition_results.json"

    def convert(obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        elif isinstance(obj, (np.floating,)): return float(obj)
        elif isinstance(obj, (np.ndarray,)): return obj.tolist()
        elif isinstance(obj, (np.bool_,)): return bool(obj)
        elif isinstance(obj, dict): return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list): return [convert(i) for i in obj]
        return obj

    all_results = convert(all_results)

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return all_results

if __name__ == "__main__":
    results = main()
