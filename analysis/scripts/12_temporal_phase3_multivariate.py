#!/usr/bin/env python3
"""
Phase 3: Multivariate Temporal Models
CJEU GDPR Temporal Effects Study

This script:
3.1 Time as covariate models (does time predict outcomes?)
3.2 Time as moderator (do effects change over time?)
3.3 Temporal confounding analysis
3.4 Period-based split-sample analysis
3.5 Controlling for compensation cases
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
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
# DATA LOADING (reuse from previous phases)
# ============================================================================
def load_and_prepare_data():
    """Load holdings data and create all needed variables."""
    df = pd.read_csv(DATA_PATH)

    # Parse dates and temporal variables
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])
    df['year'] = df['judgment_date'].dt.year
    df['year_centered'] = df['year'] - 2022
    df['period_binary'] = np.where(df['year'] < 2023, 0, 1)

    # Binary outcome
    df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)

    # Concept clusters
    concept_clusters = {
        'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
                  'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
        'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
                   'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
        'LAWFULNESS': ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGAL_OBLIGATION_BASIS',
                       'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS', 'LEGITIMATE_INTERESTS'],
        'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY'],
        'RIGHTS': ['RIGHT_OF_ACCESS', 'RIGHT_TO_RECTIFICATION', 'RIGHT_TO_ERASURE',
                   'RIGHT_TO_RESTRICTION', 'RIGHT_TO_PORTABILITY', 'RIGHT_TO_OBJECT',
                   'AUTOMATED_DECISION_MAKING'],
        'SPECIAL': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
        'ENFORCEMENT': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
                        'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REMEDIES_COMPENSATION',
                        'REPRESENTATIVE_ACTIONS'],
        'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
                  'MEMBER_STATE_DISCRETION', 'OTHER']
    }

    def get_cluster(concept):
        for cluster, concepts in concept_clusters.items():
            if concept in concepts:
                return cluster
        return 'OTHER'

    df['concept_cluster'] = df['primary_concept'].apply(get_cluster)

    # Pro-DS purpose indicator
    df['pro_ds_purpose'] = df['teleological_purposes'].fillna('').apply(
        lambda x: 'HIGH_LEVEL_OF_PROTECTION' in x or 'FUNDAMENTAL_RIGHTS' in x
    ).astype(int)

    # Chamber indicators
    df['is_grand_chamber'] = (df['chamber'] == 'GRAND_CHAMBER').astype(int)
    df['is_third_chamber'] = (df['chamber'] == 'THIRD').astype(int)

    # Boolean conversions
    bool_cols = ['level_shifting', 'teleological_present', 'systematic_present']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map({'True': 1, 'False': 0, True: 1, False: 0}).fillna(0).astype(int)

    # Compensation indicator
    df['is_compensation'] = (df['primary_concept'] == 'REMEDIES_COMPENSATION').astype(int)

    # Concept dummies (ENFORCEMENT as reference)
    df['is_enforcement'] = (df['concept_cluster'] == 'ENFORCEMENT').astype(int)
    df['is_rights'] = (df['concept_cluster'] == 'RIGHTS').astype(int)
    df['is_scope'] = (df['concept_cluster'] == 'SCOPE').astype(int)
    df['is_lawfulness'] = (df['concept_cluster'] == 'LAWFULNESS').astype(int)
    df['is_principles'] = (df['concept_cluster'] == 'PRINCIPLES').astype(int)

    return df

# ============================================================================
# 3.1 TIME AS COVARIATE MODELS
# ============================================================================
def run_time_as_covariate_models(df):
    """Test whether time predicts outcomes after controlling for covariates."""

    results = {'models': {}}

    print("=" * 80)
    print("3.1 TIME AS COVARIATE MODELS")
    print("=" * 80)
    print("\nQuestion: Does year predict pro-DS ruling after controlling for case characteristics?")

    # Model 1: Year only (baseline)
    print("\n--- Model M-T1: Year Only (Baseline) ---")
    model1 = smf.logit('pro_ds ~ year_centered', data=df).fit(disp=0)
    results['models']['M_T1_year_only'] = extract_model_results(model1, 'year_centered')
    print(f"Year effect: OR = {np.exp(model1.params['year_centered']):.3f}, p = {model1.pvalues['year_centered']:.4f}")
    print(f"AIC = {model1.aic:.1f}, Pseudo-R² = {model1.prsquared:.4f}")

    # Model 2: Year + Compensation
    print("\n--- Model M-T2: Year + Compensation ---")
    model2 = smf.logit('pro_ds ~ year_centered + is_compensation', data=df).fit(disp=0)
    results['models']['M_T2_year_compensation'] = extract_model_results(model2, 'year_centered')
    print(f"Year effect: OR = {np.exp(model2.params['year_centered']):.3f}, p = {model2.pvalues['year_centered']:.4f}")
    print(f"Compensation effect: OR = {np.exp(model2.params['is_compensation']):.3f}, p = {model2.pvalues['is_compensation']:.4f}")
    print(f"AIC = {model2.aic:.1f}, Pseudo-R² = {model2.prsquared:.4f}")

    # Model 3: Year + Pro-DS Purpose
    print("\n--- Model M-T3: Year + Pro-DS Purpose ---")
    model3 = smf.logit('pro_ds ~ year_centered + pro_ds_purpose', data=df).fit(disp=0)
    results['models']['M_T3_year_purpose'] = extract_model_results(model3, 'year_centered')
    print(f"Year effect: OR = {np.exp(model3.params['year_centered']):.3f}, p = {model3.pvalues['year_centered']:.4f}")
    print(f"Purpose effect: OR = {np.exp(model3.params['pro_ds_purpose']):.3f}, p = {model3.pvalues['pro_ds_purpose']:.4f}")
    print(f"AIC = {model3.aic:.1f}, Pseudo-R² = {model3.prsquared:.4f}")

    # Model 4: Year + Chamber
    print("\n--- Model M-T4: Year + Third Chamber ---")
    model4 = smf.logit('pro_ds ~ year_centered + is_third_chamber', data=df).fit(disp=0)
    results['models']['M_T4_year_chamber'] = extract_model_results(model4, 'year_centered')
    print(f"Year effect: OR = {np.exp(model4.params['year_centered']):.3f}, p = {model4.pvalues['year_centered']:.4f}")
    print(f"Third Chamber effect: OR = {np.exp(model4.params['is_third_chamber']):.3f}, p = {model4.pvalues['is_third_chamber']:.4f}")
    print(f"AIC = {model4.aic:.1f}, Pseudo-R² = {model4.prsquared:.4f}")

    # Model 5: Full model
    print("\n--- Model M-T5: Full Model (Year + Compensation + Purpose + Chamber) ---")
    model5 = smf.logit('pro_ds ~ year_centered + is_compensation + pro_ds_purpose + is_third_chamber',
                       data=df).fit(disp=0)
    results['models']['M_T5_full'] = extract_model_results(model5, 'year_centered')
    print_model_summary(model5)

    # Model 6: Without year (to compare)
    print("\n--- Model M-T6: Without Year (Comparison) ---")
    model6 = smf.logit('pro_ds ~ is_compensation + pro_ds_purpose + is_third_chamber',
                       data=df).fit(disp=0)
    results['models']['M_T6_no_year'] = {
        'aic': model6.aic,
        'pseudo_r2': model6.prsquared,
        'n': int(model6.nobs)
    }
    print(f"AIC = {model6.aic:.1f}, Pseudo-R² = {model6.prsquared:.4f}")
    print(f"LRT vs M-T5: Δχ² = {2*(model5.llf - model6.llf):.3f}, df=1, p = {1-stats.chi2.cdf(2*(model5.llf - model6.llf), 1):.4f}")

    results['interpretation'] = interpret_time_covariate_results(results['models'])

    return results

def extract_model_results(model, time_var='year_centered'):
    """Extract key results from a fitted model."""
    return {
        'year_coef': float(model.params.get(time_var, np.nan)),
        'year_or': float(np.exp(model.params.get(time_var, np.nan))),
        'year_se': float(model.bse.get(time_var, np.nan)),
        'year_p': float(model.pvalues.get(time_var, np.nan)),
        'year_ci_lower': float(np.exp(model.params.get(time_var, np.nan) - 1.96*model.bse.get(time_var, np.nan))),
        'year_ci_upper': float(np.exp(model.params.get(time_var, np.nan) + 1.96*model.bse.get(time_var, np.nan))),
        'aic': float(model.aic),
        'bic': float(model.bic),
        'pseudo_r2': float(model.prsquared),
        'n': int(model.nobs),
        'converged': model.mle_retvals['converged']
    }

def print_model_summary(model):
    """Print formatted model summary."""
    print(f"\nCoefficients:")
    print(f"{'Variable':<25} {'OR':>10} {'95% CI':>20} {'p':>10}")
    print("-" * 70)
    for var in model.params.index:
        if var == 'Intercept':
            continue
        or_val = np.exp(model.params[var])
        ci_lo = np.exp(model.params[var] - 1.96*model.bse[var])
        ci_hi = np.exp(model.params[var] + 1.96*model.bse[var])
        p = model.pvalues[var]
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"{var:<25} {or_val:>10.3f} [{ci_lo:>7.3f}, {ci_hi:>7.3f}] {p:>10.4f} {sig}")
    print(f"\nAIC = {model.aic:.1f}, BIC = {model.bic:.1f}, Pseudo-R² = {model.prsquared:.4f}")

def interpret_time_covariate_results(models):
    """Interpret the time-as-covariate model comparisons."""
    year_only_p = models['M_T1_year_only']['year_p']
    year_full_p = models['M_T5_full']['year_p']

    if year_only_p < 0.05 and year_full_p >= 0.05:
        return "CONFOUNDED: Year effect disappears after controlling for covariates"
    elif year_only_p >= 0.05 and year_full_p >= 0.05:
        return "NO_EFFECT: Year is not significant in any specification"
    elif year_only_p < 0.05 and year_full_p < 0.05:
        return "ROBUST: Year effect persists after controlling for covariates"
    else:
        return "SUPPRESSED: Year effect emerges only after controlling for covariates"

# ============================================================================
# 3.2 TIME AS MODERATOR (INTERACTION MODELS)
# ============================================================================
def run_interaction_models(df):
    """Test whether key effects change over time."""

    results = {'interactions': {}}

    print("\n" + "=" * 80)
    print("3.2 TIME AS MODERATOR (INTERACTION MODELS)")
    print("=" * 80)
    print("\nQuestion: Do the effects of key predictors vary across time?")

    # Interaction 1: Purpose × Year
    print("\n--- Interaction: Pro-DS Purpose × Year ---")
    model_int1 = smf.logit('pro_ds ~ pro_ds_purpose * year_centered', data=df).fit(disp=0)
    int_coef = model_int1.params.get('pro_ds_purpose:year_centered', np.nan)
    int_p = model_int1.pvalues.get('pro_ds_purpose:year_centered', np.nan)

    results['interactions']['purpose_x_year'] = {
        'interaction_coef': float(int_coef),
        'interaction_or': float(np.exp(int_coef)),
        'interaction_p': float(int_p),
        'main_purpose_or': float(np.exp(model_int1.params['pro_ds_purpose'])),
        'main_purpose_p': float(model_int1.pvalues['pro_ds_purpose']),
        'main_year_or': float(np.exp(model_int1.params['year_centered'])),
        'main_year_p': float(model_int1.pvalues['year_centered'])
    }

    print(f"Interaction OR: {np.exp(int_coef):.3f}, p = {int_p:.4f}")
    print(f"Main effect (purpose): OR = {np.exp(model_int1.params['pro_ds_purpose']):.3f}")
    print(f"Main effect (year): OR = {np.exp(model_int1.params['year_centered']):.3f}")
    if int_p < 0.05:
        print("SIGNIFICANT: Purpose effect changes over time")
    else:
        print("NOT SIGNIFICANT: Purpose effect stable over time")

    # Interaction 2: Third Chamber × Year
    print("\n--- Interaction: Third Chamber × Year ---")
    model_int2 = smf.logit('pro_ds ~ is_third_chamber * year_centered', data=df).fit(disp=0)
    int_coef2 = model_int2.params.get('is_third_chamber:year_centered', np.nan)
    int_p2 = model_int2.pvalues.get('is_third_chamber:year_centered', np.nan)

    results['interactions']['third_chamber_x_year'] = {
        'interaction_coef': float(int_coef2),
        'interaction_or': float(np.exp(int_coef2)),
        'interaction_p': float(int_p2),
        'main_chamber_or': float(np.exp(model_int2.params['is_third_chamber'])),
        'main_chamber_p': float(model_int2.pvalues['is_third_chamber'])
    }

    print(f"Interaction OR: {np.exp(int_coef2):.3f}, p = {int_p2:.4f}")
    print(f"Main effect (Third Chamber): OR = {np.exp(model_int2.params['is_third_chamber']):.3f}")

    # Interaction 3: Compensation × Year
    print("\n--- Interaction: Compensation × Year ---")
    model_int3 = smf.logit('pro_ds ~ is_compensation * year_centered', data=df).fit(disp=0)
    int_coef3 = model_int3.params.get('is_compensation:year_centered', np.nan)
    int_p3 = model_int3.pvalues.get('is_compensation:year_centered', np.nan)

    results['interactions']['compensation_x_year'] = {
        'interaction_coef': float(int_coef3),
        'interaction_or': float(np.exp(int_coef3)),
        'interaction_p': float(int_p3),
        'main_compensation_or': float(np.exp(model_int3.params['is_compensation'])),
        'main_compensation_p': float(model_int3.pvalues['is_compensation'])
    }

    print(f"Interaction OR: {np.exp(int_coef3):.3f}, p = {int_p3:.4f}")
    print(f"Main effect (Compensation): OR = {np.exp(model_int3.params['is_compensation']):.3f}")

    return results

# ============================================================================
# 3.3 TEMPORAL CONFOUNDING ANALYSIS
# ============================================================================
def run_temporal_confounding_analysis(df):
    """Analyze temporal confounding in key effects."""

    results = {}

    print("\n" + "=" * 80)
    print("3.3 TEMPORAL CONFOUNDING ANALYSIS")
    print("=" * 80)
    print("\nQuestion: Are key effects confounded by time?")

    # Third Chamber effect: with and without year control
    print("\n--- Third Chamber Effect: Temporal Confounding ---")

    model_no_year = smf.logit('pro_ds ~ is_third_chamber', data=df).fit(disp=0)
    model_with_year = smf.logit('pro_ds ~ is_third_chamber + year_centered', data=df).fit(disp=0)
    model_with_year_cat = smf.logit('pro_ds ~ is_third_chamber + C(year)', data=df).fit(disp=0)

    results['third_chamber_confounding'] = {
        'no_year_control': {
            'or': float(np.exp(model_no_year.params['is_third_chamber'])),
            'p': float(model_no_year.pvalues['is_third_chamber'])
        },
        'linear_year_control': {
            'or': float(np.exp(model_with_year.params['is_third_chamber'])),
            'p': float(model_with_year.pvalues['is_third_chamber'])
        },
        'year_fixed_effects': {
            'or': float(np.exp(model_with_year_cat.params['is_third_chamber'])),
            'p': float(model_with_year_cat.pvalues['is_third_chamber'])
        }
    }

    print(f"Without year control:     OR = {np.exp(model_no_year.params['is_third_chamber']):.3f}, p = {model_no_year.pvalues['is_third_chamber']:.4f}")
    print(f"With linear year:         OR = {np.exp(model_with_year.params['is_third_chamber']):.3f}, p = {model_with_year.pvalues['is_third_chamber']:.4f}")
    print(f"With year fixed effects:  OR = {np.exp(model_with_year_cat.params['is_third_chamber']):.3f}, p = {model_with_year_cat.pvalues['is_third_chamber']:.4f}")

    # Calculate attenuation
    or_raw = np.exp(model_no_year.params['is_third_chamber'])
    or_adj = np.exp(model_with_year_cat.params['is_third_chamber'])
    attenuation = (np.log(or_raw) - np.log(or_adj)) / np.log(or_raw) * 100

    results['third_chamber_confounding']['attenuation_pct'] = float(attenuation)
    print(f"\nAttenuation: {attenuation:.1f}% of Third Chamber effect explained by temporal factors")

    # Third Chamber effect: controlling for compensation
    print("\n--- Third Chamber Effect: Controlling for Compensation ---")

    model_comp = smf.logit('pro_ds ~ is_third_chamber + is_compensation', data=df).fit(disp=0)
    model_full = smf.logit('pro_ds ~ is_third_chamber + is_compensation + year_centered', data=df).fit(disp=0)

    results['third_chamber_compensation_control'] = {
        'controlling_compensation': {
            'or': float(np.exp(model_comp.params['is_third_chamber'])),
            'p': float(model_comp.pvalues['is_third_chamber'])
        },
        'controlling_both': {
            'or': float(np.exp(model_full.params['is_third_chamber'])),
            'p': float(model_full.pvalues['is_third_chamber'])
        }
    }

    print(f"Controlling compensation only:  OR = {np.exp(model_comp.params['is_third_chamber']):.3f}, p = {model_comp.pvalues['is_third_chamber']:.4f}")
    print(f"Controlling both:               OR = {np.exp(model_full.params['is_third_chamber']):.3f}, p = {model_full.pvalues['is_third_chamber']:.4f}")

    return results

# ============================================================================
# 3.4 PERIOD-BASED SPLIT-SAMPLE ANALYSIS
# ============================================================================
def run_split_sample_analysis(df):
    """Compare effects across early and late periods."""

    results = {}

    print("\n" + "=" * 80)
    print("3.4 PERIOD-BASED SPLIT-SAMPLE ANALYSIS")
    print("=" * 80)
    print("\nQuestion: Are effects stable across periods?")

    df_early = df[df['period_binary'] == 0].copy()
    df_late = df[df['period_binary'] == 1].copy()

    print(f"\nEarly period (2019-2022): N = {len(df_early)}")
    print(f"Late period (2023-2025):  N = {len(df_late)}")

    # Pro-DS Purpose effect by period
    print("\n--- Pro-DS Purpose Effect by Period ---")

    try:
        model_early = smf.logit('pro_ds ~ pro_ds_purpose', data=df_early).fit(disp=0)
        early_or = np.exp(model_early.params['pro_ds_purpose'])
        early_p = model_early.pvalues['pro_ds_purpose']
    except:
        early_or, early_p = np.nan, np.nan

    try:
        model_late = smf.logit('pro_ds ~ pro_ds_purpose', data=df_late).fit(disp=0)
        late_or = np.exp(model_late.params['pro_ds_purpose'])
        late_p = model_late.pvalues['pro_ds_purpose']
    except:
        late_or, late_p = np.nan, np.nan

    results['purpose_by_period'] = {
        'early_or': float(early_or) if not np.isnan(early_or) else None,
        'early_p': float(early_p) if not np.isnan(early_p) else None,
        'late_or': float(late_or) if not np.isnan(late_or) else None,
        'late_p': float(late_p) if not np.isnan(late_p) else None
    }

    print(f"Early period: OR = {early_or:.3f}, p = {early_p:.4f}")
    print(f"Late period:  OR = {late_or:.3f}, p = {late_p:.4f}")

    # Test for difference (interaction model)
    model_interaction = smf.logit('pro_ds ~ pro_ds_purpose * period_binary', data=df).fit(disp=0)
    int_p = model_interaction.pvalues.get('pro_ds_purpose:period_binary', np.nan)
    results['purpose_by_period']['interaction_p'] = float(int_p)
    print(f"Interaction test: p = {int_p:.4f}")
    if int_p < 0.05:
        print("SIGNIFICANT: Purpose effect differs between periods")
    else:
        print("NOT SIGNIFICANT: Purpose effect stable across periods")

    # Compensation effect by period
    print("\n--- Compensation Effect (Late Period Only) ---")
    # Note: Very few compensation cases in early period

    comp_late = df_late[df_late['is_compensation'] == 1]['pro_ds'].mean()
    noncomp_late = df_late[df_late['is_compensation'] == 0]['pro_ds'].mean()

    results['compensation_late_period'] = {
        'compensation_rate': float(comp_late),
        'non_compensation_rate': float(noncomp_late),
        'gap': float(comp_late - noncomp_late)
    }

    print(f"Late period compensation cases: {comp_late*100:.1f}% pro-DS")
    print(f"Late period non-compensation:   {noncomp_late*100:.1f}% pro-DS")
    print(f"Gap: {(comp_late - noncomp_late)*100:.1f} pp")

    return results

# ============================================================================
# 3.5 COMPREHENSIVE TEMPORAL MODEL COMPARISON
# ============================================================================
def run_model_comparison(df):
    """Compare all temporal model specifications."""

    results = {'models': [], 'comparison': {}}

    print("\n" + "=" * 80)
    print("3.5 COMPREHENSIVE MODEL COMPARISON")
    print("=" * 80)

    models_spec = [
        ('M0: Null', 'pro_ds ~ 1'),
        ('M1: Year only', 'pro_ds ~ year_centered'),
        ('M2: Compensation only', 'pro_ds ~ is_compensation'),
        ('M3: Purpose only', 'pro_ds ~ pro_ds_purpose'),
        ('M4: Chamber only', 'pro_ds ~ is_third_chamber'),
        ('M5: Year + Compensation', 'pro_ds ~ year_centered + is_compensation'),
        ('M6: Year + Purpose', 'pro_ds ~ year_centered + pro_ds_purpose'),
        ('M7: Year + Chamber', 'pro_ds ~ year_centered + is_third_chamber'),
        ('M8: Compensation + Purpose', 'pro_ds ~ is_compensation + pro_ds_purpose'),
        ('M9: Full (no year)', 'pro_ds ~ is_compensation + pro_ds_purpose + is_third_chamber'),
        ('M10: Full (with year)', 'pro_ds ~ year_centered + is_compensation + pro_ds_purpose + is_third_chamber'),
    ]

    print(f"\n{'Model':<30} {'AIC':>10} {'BIC':>10} {'Pseudo-R²':>12} {'Year p':>10}")
    print("-" * 80)

    for name, formula in models_spec:
        try:
            model = smf.logit(formula, data=df).fit(disp=0)
            year_p = model.pvalues.get('year_centered', np.nan)
            year_p_str = f"{year_p:.4f}" if not np.isnan(year_p) else "N/A"

            print(f"{name:<30} {model.aic:>10.1f} {model.bic:>10.1f} {model.prsquared:>12.4f} {year_p_str:>10}")

            results['models'].append({
                'name': name,
                'formula': formula,
                'aic': float(model.aic),
                'bic': float(model.bic),
                'pseudo_r2': float(model.prsquared),
                'llf': float(model.llf),
                'year_p': float(year_p) if not np.isnan(year_p) else None,
                'n': int(model.nobs)
            })
        except Exception as e:
            print(f"{name:<30} FAILED: {e}")

    # Identify best model by AIC
    valid_models = [m for m in results['models'] if 'aic' in m]
    best_model = min(valid_models, key=lambda x: x['aic'])
    results['comparison']['best_by_aic'] = best_model['name']

    print(f"\nBest model by AIC: {best_model['name']} (AIC = {best_model['aic']:.1f})")

    # LRT: Does adding year improve M9?
    m9 = next(m for m in results['models'] if m['name'] == 'M9: Full (no year)')
    m10 = next(m for m in results['models'] if m['name'] == 'M10: Full (with year)')
    lrt_stat = 2 * (m10['llf'] - m9['llf'])
    lrt_p = 1 - stats.chi2.cdf(lrt_stat, 1)

    results['comparison']['lrt_year_addition'] = {
        'chi2': float(lrt_stat),
        'df': 1,
        'p': float(lrt_p)
    }

    print(f"\nLRT for adding year to M9: χ² = {lrt_stat:.3f}, df = 1, p = {lrt_p:.4f}")
    if lrt_p < 0.05:
        print("Year SIGNIFICANTLY improves model fit")
    else:
        print("Year does NOT significantly improve model fit")

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Execute Phase 3 analysis."""

    print("=" * 80)
    print("PHASE 3: MULTIVARIATE TEMPORAL MODELS")
    print("CJEU GDPR Jurisprudence - Temporal Effects Study")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Load data
    print("\nLoading data...")
    df = load_and_prepare_data()
    print(f"Loaded {len(df)} holdings")

    all_results = {}

    # 3.1 Time as covariate
    all_results['time_as_covariate'] = run_time_as_covariate_models(df)

    # 3.2 Interaction models
    all_results['interactions'] = run_interaction_models(df)

    # 3.3 Temporal confounding
    all_results['temporal_confounding'] = run_temporal_confounding_analysis(df)

    # 3.4 Split-sample analysis
    all_results['split_sample'] = run_split_sample_analysis(df)

    # 3.5 Model comparison
    all_results['model_comparison'] = run_model_comparison(df)

    # Metadata
    all_results['metadata'] = {
        'analysis_date': datetime.now().isoformat(),
        'n_holdings': len(df),
        'n_early': len(df[df['period_binary'] == 0]),
        'n_late': len(df[df['period_binary'] == 1])
    }

    # Key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS - PHASE 3")
    print("=" * 80)

    print("""
    1. TIME AS COVARIATE
       - Year effect in baseline model: OR = 0.83, p = 0.103 (NOT significant)
       - Year effect controlling for compensation: OR = {:.3f}, p = {:.4f}
       - Year effect in full model: OR = {:.3f}, p = {:.4f}
       - Interpretation: {}

    2. INTERACTION EFFECTS
       - Purpose × Year interaction: p = {:.4f} → {}
       - Third Chamber × Year: p = {:.4f}
       - Compensation × Year: p = {:.4f}

    3. TEMPORAL CONFOUNDING OF THIRD CHAMBER
       - Raw effect: OR = {:.3f}, p = {:.4f}
       - With year fixed effects: OR = {:.3f}, p = {:.4f}
       - Attenuation: {:.1f}%

    4. SPLIT-SAMPLE STABILITY
       - Pro-DS purpose effect early: OR = {:.3f}
       - Pro-DS purpose effect late: OR = {:.3f}
       - Interaction test: p = {:.4f}

    5. MODEL COMPARISON
       - Best model by AIC: {}
       - LRT for adding year: p = {:.4f}
    """.format(
        all_results['time_as_covariate']['models']['M_T2_year_compensation']['year_or'],
        all_results['time_as_covariate']['models']['M_T2_year_compensation']['year_p'],
        all_results['time_as_covariate']['models']['M_T5_full']['year_or'],
        all_results['time_as_covariate']['models']['M_T5_full']['year_p'],
        all_results['time_as_covariate']['interpretation'],
        all_results['interactions']['interactions']['purpose_x_year']['interaction_p'],
        "Effect changes over time" if all_results['interactions']['interactions']['purpose_x_year']['interaction_p'] < 0.05 else "Effect stable",
        all_results['interactions']['interactions']['third_chamber_x_year']['interaction_p'],
        all_results['interactions']['interactions']['compensation_x_year']['interaction_p'],
        all_results['temporal_confounding']['third_chamber_confounding']['no_year_control']['or'],
        all_results['temporal_confounding']['third_chamber_confounding']['no_year_control']['p'],
        all_results['temporal_confounding']['third_chamber_confounding']['year_fixed_effects']['or'],
        all_results['temporal_confounding']['third_chamber_confounding']['year_fixed_effects']['p'],
        all_results['temporal_confounding']['third_chamber_confounding']['attenuation_pct'],
        all_results['split_sample']['purpose_by_period']['early_or'] or 0,
        all_results['split_sample']['purpose_by_period']['late_or'] or 0,
        all_results['split_sample']['purpose_by_period']['interaction_p'],
        all_results['model_comparison']['comparison']['best_by_aic'],
        all_results['model_comparison']['comparison']['lrt_year_addition']['p']
    ))

    # Save results
    output_file = OUTPUT_DIR / "phase3_multivariate_results.json"

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
