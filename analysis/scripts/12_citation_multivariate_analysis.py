#!/usr/bin/env python3
"""
12_citation_multivariate_analysis.py
=====================================
Phase 3: Multivariate Analysis with Citation Variables

Tests whether citation effects persist after controlling for case characteristics:
  H2.1: Precedent direction effect persists after controls
  H2.2: Network position independently associated with outcomes

Uses hierarchical logistic regression with cluster-robust standard errors.
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.families import Binomial
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

    # Ensure proper types
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])

    print(f"Loaded {len(df)} holdings from {df['case_id'].nunique()} cases")

    return df

def prepare_analysis_sample(df):
    """
    Prepare analysis sample: holdings with internal citations and complete data.
    """
    # Filter to holdings with internal citations
    df_analysis = df[df['internal_citations'] > 0].copy()

    # Ensure key variables are available
    required_vars = ['pro_ds', 'chamber', 'year', 'concept_cluster',
                     'pro_ds_purpose', 'precedent_direction_score',
                     'predominantly_pro_ds_precedents', 'cites_gc_precedent']

    missing = [v for v in required_vars if v not in df_analysis.columns]
    if missing:
        print(f"WARNING: Missing variables: {missing}")

    # Drop missing
    df_analysis = df_analysis.dropna(subset=['precedent_direction_score', 'pro_ds'])

    print(f"Analysis sample: {len(df_analysis)} holdings with internal citations")

    return df_analysis

def fit_model(formula, df, model_name, use_robust=True):
    """
    Fit logistic regression model with optional cluster-robust SEs.
    """
    try:
        model = smf.logit(formula, data=df).fit(disp=0)

        # Get cluster-robust standard errors
        if use_robust and 'case_id' in df.columns:
            # Create numeric case groups
            df['case_group'] = pd.Categorical(df['case_id']).codes
            model_robust = smf.logit(formula, data=df).fit(
                cov_type='cluster',
                cov_kwds={'groups': df['case_group']},
                disp=0
            )
            return model_robust, model  # Return both for comparison
        else:
            return model, model

    except Exception as e:
        print(f"  Model {model_name} failed: {e}")
        return None, None

def extract_model_results(model, model_name):
    """Extract key results from fitted model."""
    if model is None:
        return None

    results = {
        'model_name': model_name,
        'n_obs': int(model.nobs),
        'pseudo_r2': float(model.prsquared),
        'aic': float(model.aic),
        'bic': float(model.bic),
        'llf': float(model.llf),
        'coefficients': {}
    }

    for var in model.params.index:
        results['coefficients'][var] = {
            'coef': float(model.params[var]),
            'se': float(model.bse[var]),
            'z': float(model.tvalues[var]),
            'p_value': float(model.pvalues[var]),
            'odds_ratio': float(np.exp(model.params[var])),
            'ci_lower': float(np.exp(model.conf_int().loc[var, 0])),
            'ci_upper': float(np.exp(model.conf_int().loc[var, 1]))
        }

    return results

def print_model_summary(results, title):
    """Print model results in formatted table."""
    if results is None:
        print(f"\n{title}: MODEL FAILED")
        return

    print(f"\n{title}")
    print("=" * 80)
    print(f"N = {results['n_obs']}, Pseudo R² = {results['pseudo_r2']:.4f}, "
          f"AIC = {results['aic']:.1f}, BIC = {results['bic']:.1f}")
    print("-" * 80)
    print(f"{'Variable':<40} {'OR':>8} {'95% CI':>16} {'p-value':>10}")
    print("-" * 80)

    for var, coef in results['coefficients'].items():
        ci = f"[{coef['ci_lower']:.2f}, {coef['ci_upper']:.2f}]"
        sig = "***" if coef['p_value'] < 0.001 else "**" if coef['p_value'] < 0.01 else "*" if coef['p_value'] < 0.05 else ""
        print(f"{var:<40} {coef['odds_ratio']:>8.2f} {ci:>16} {coef['p_value']:>8.4f} {sig}")

def run_hierarchical_models(df):
    """
    Run hierarchical logistic regression models.

    Model 0: Baseline (institutional + concept)
    Model 1: + Pro-DS purpose (established predictor)
    Model 2: + Citation variables
    Model 3: + Network position variables
    """
    print("\n" + "=" * 80)
    print("HIERARCHICAL LOGISTIC REGRESSION MODELS")
    print("=" * 80)

    all_results = {}

    # Model 0: Baseline
    formula_0 = "pro_ds ~ C(chamber_grouped) + year + C(concept_cluster)"
    model_0_robust, model_0 = fit_model(formula_0, df, "Model 0: Baseline")
    results_0 = extract_model_results(model_0_robust, "Model 0: Baseline (Institutional + Concept)")
    all_results['model_0'] = results_0
    print_model_summary(results_0, "Model 0: Baseline (Institutional + Concept)")

    # Model 1: + Pro-DS Purpose
    formula_1 = "pro_ds ~ C(chamber_grouped) + year + C(concept_cluster) + pro_ds_purpose"
    model_1_robust, model_1 = fit_model(formula_1, df, "Model 1: + Purpose")
    results_1 = extract_model_results(model_1_robust, "Model 1: + Pro-DS Purpose")
    all_results['model_1'] = results_1
    print_model_summary(results_1, "Model 1: + Pro-DS Purpose")

    # Model 2: + Citation Variables
    formula_2 = ("pro_ds ~ C(chamber_grouped) + year + C(concept_cluster) + pro_ds_purpose + "
                 "precedent_direction_score + cites_gc_precedent")
    model_2_robust, model_2 = fit_model(formula_2, df, "Model 2: + Citations")
    results_2 = extract_model_results(model_2_robust, "Model 2: + Citation Variables")
    all_results['model_2'] = results_2
    print_model_summary(results_2, "Model 2: + Citation Variables")

    # Model 3: + Network Position
    # Only if PageRank available
    if 'citing_case_pagerank' in df.columns and df['citing_case_pagerank'].notna().sum() > 50:
        df_m3 = df.dropna(subset=['avg_cited_pagerank', 'citing_case_pagerank']).copy()

        # Standardize PageRank for interpretability
        df_m3['avg_cited_pagerank_std'] = (df_m3['avg_cited_pagerank'] - df_m3['avg_cited_pagerank'].mean()) / df_m3['avg_cited_pagerank'].std()
        df_m3['citing_pagerank_std'] = (df_m3['citing_case_pagerank'] - df_m3['citing_case_pagerank'].mean()) / df_m3['citing_case_pagerank'].std()

        formula_3 = ("pro_ds ~ C(chamber_grouped) + year + C(concept_cluster) + pro_ds_purpose + "
                     "precedent_direction_score + cites_gc_precedent + avg_cited_pagerank_std")
        model_3_robust, model_3 = fit_model(formula_3, df_m3, "Model 3: + Network Position")
        results_3 = extract_model_results(model_3_robust, "Model 3: + Network Position")
        all_results['model_3'] = results_3
        print_model_summary(results_3, "Model 3: + Network Position (standardized PageRank)")

    return all_results

def test_precedent_effect_robustness(df):
    """
    Test robustness of precedent direction effect with various controls.
    """
    print("\n" + "=" * 80)
    print("ROBUSTNESS: PRECEDENT DIRECTION EFFECT")
    print("=" * 80)

    results = {}

    # Test 1: Simple model (citation only)
    print("\nTest 1: Simple model (precedent direction only)")
    formula = "pro_ds ~ precedent_direction_score"
    model, _ = fit_model(formula, df, "Simple")
    if model:
        print(f"  Precedent direction OR: {np.exp(model.params['precedent_direction_score']):.2f}")
        print(f"  p-value: {model.pvalues['precedent_direction_score']:.4f}")
        results['simple'] = {
            'or': float(np.exp(model.params['precedent_direction_score'])),
            'p': float(model.pvalues['precedent_direction_score'])
        }

    # Test 2: Control for pro-DS purpose only
    print("\nTest 2: Controlling for pro-DS purpose")
    formula = "pro_ds ~ precedent_direction_score + pro_ds_purpose"
    model, _ = fit_model(formula, df, "With purpose")
    if model:
        print(f"  Precedent direction OR: {np.exp(model.params['precedent_direction_score']):.2f}")
        print(f"  p-value: {model.pvalues['precedent_direction_score']:.4f}")
        print(f"  Pro-DS purpose OR: {np.exp(model.params['pro_ds_purpose']):.2f}")
        results['with_purpose'] = {
            'precedent_or': float(np.exp(model.params['precedent_direction_score'])),
            'precedent_p': float(model.pvalues['precedent_direction_score']),
            'purpose_or': float(np.exp(model.params['pro_ds_purpose'])),
            'purpose_p': float(model.pvalues['pro_ds_purpose'])
        }

    # Test 3: Control for concept cluster only
    print("\nTest 3: Controlling for concept cluster")
    formula = "pro_ds ~ precedent_direction_score + C(concept_cluster)"
    model, _ = fit_model(formula, df, "With concept")
    if model:
        print(f"  Precedent direction OR: {np.exp(model.params['precedent_direction_score']):.2f}")
        print(f"  p-value: {model.pvalues['precedent_direction_score']:.4f}")
        results['with_concept'] = {
            'or': float(np.exp(model.params['precedent_direction_score'])),
            'p': float(model.pvalues['precedent_direction_score'])
        }

    # Test 4: Binary predictor (predominantly pro-DS precedents)
    print("\nTest 4: Binary predictor (predominantly_pro_ds_precedents)")
    formula = "pro_ds ~ predominantly_pro_ds_precedents + C(chamber_grouped) + C(concept_cluster)"
    model, _ = fit_model(formula, df, "Binary predictor")
    if model:
        print(f"  Predominantly pro-DS OR: {np.exp(model.params['predominantly_pro_ds_precedents']):.2f}")
        print(f"  p-value: {model.pvalues['predominantly_pro_ds_precedents']:.4f}")
        results['binary'] = {
            'or': float(np.exp(model.params['predominantly_pro_ds_precedents'])),
            'p': float(model.pvalues['predominantly_pro_ds_precedents'])
        }

    return results

def test_purpose_propagation_multivariate(df):
    """
    Test purpose propagation (H1.2) in multivariate context.
    """
    print("\n" + "=" * 80)
    print("H2: PURPOSE PROPAGATION (MULTIVARIATE)")
    print("=" * 80)

    # Outcome: Citing holding invokes pro-DS purpose
    formula = "pro_ds_purpose ~ precedent_purpose_rate + C(chamber_grouped) + C(concept_cluster)"
    model, _ = fit_model(formula, df.dropna(subset=['precedent_purpose_rate']), "Purpose propagation")

    if model:
        print(f"\nOutcome: Citing holding invokes pro-DS purpose")
        print(f"  Precedent purpose rate OR: {np.exp(model.params['precedent_purpose_rate']):.2f}")
        print(f"  p-value: {model.pvalues['precedent_purpose_rate']:.4f}")
        print(f"  Pseudo R²: {model.prsquared:.4f}")

        return {
            'or': float(np.exp(model.params['precedent_purpose_rate'])),
            'p': float(model.pvalues['precedent_purpose_rate']),
            'pseudo_r2': float(model.prsquared)
        }

    return None

def compare_models(all_results):
    """Compare model fit statistics."""
    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)

    comparison = []
    for name, results in all_results.items():
        if results:
            comparison.append({
                'Model': results['model_name'],
                'N': results['n_obs'],
                'Pseudo R²': results['pseudo_r2'],
                'AIC': results['aic'],
                'BIC': results['bic'],
                'Log-Likelihood': results['llf']
            })

    comp_df = pd.DataFrame(comparison)
    print(comp_df.to_string(index=False))

    # Find best model by AIC
    if len(comp_df) > 0:
        best_aic = comp_df.loc[comp_df['AIC'].idxmin(), 'Model']
        best_bic = comp_df.loc[comp_df['BIC'].idxmin(), 'Model']
        print(f"\nBest by AIC: {best_aic}")
        print(f"Best by BIC: {best_bic}")

    return comp_df.to_dict('records')

def analyze_key_predictors(all_results):
    """
    Analyze key predictors across models.
    """
    print("\n" + "=" * 80)
    print("KEY PREDICTOR ANALYSIS ACROSS MODELS")
    print("=" * 80)

    key_vars = ['precedent_direction_score', 'cites_gc_precedent', 'pro_ds_purpose']

    for var in key_vars:
        print(f"\n{var}:")
        print("-" * 60)

        for model_name, results in all_results.items():
            if results and var in results['coefficients']:
                coef = results['coefficients'][var]
                sig = "***" if coef['p_value'] < 0.001 else "**" if coef['p_value'] < 0.01 else "*" if coef['p_value'] < 0.05 else ""
                print(f"  {model_name}: OR={coef['odds_ratio']:.2f} [{coef['ci_lower']:.2f}, {coef['ci_upper']:.2f}], p={coef['p_value']:.4f} {sig}")

def main():
    print("=" * 80)
    print("PHASE 3: MULTIVARIATE ANALYSIS WITH CITATION VARIABLES")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load and prepare data
    print("\n[1/6] Loading data...")
    df = load_data()

    print("\n[2/6] Preparing analysis sample...")
    df_analysis = prepare_analysis_sample(df)

    # Create chamber grouping if not present
    if 'chamber_grouped' not in df_analysis.columns:
        major_chambers = ['GRAND_CHAMBER', 'FIRST', 'THIRD', 'FOURTH']
        df_analysis['chamber_grouped'] = df_analysis['chamber'].apply(
            lambda x: x if x in major_chambers else 'OTHER'
        )

    # Run hierarchical models
    print("\n[3/6] Running hierarchical models...")
    all_results = run_hierarchical_models(df_analysis)

    # Test robustness
    print("\n[4/6] Testing robustness of precedent effect...")
    robustness = test_precedent_effect_robustness(df_analysis)

    # Test purpose propagation
    print("\n[5/6] Testing purpose propagation (multivariate)...")
    purpose_mv = test_purpose_propagation_multivariate(df_analysis)

    # Compare models
    print("\n[6/6] Comparing models...")
    comparison = compare_models(all_results)

    # Analyze key predictors
    analyze_key_predictors(all_results)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY OF MULTIVARIATE FINDINGS")
    print("=" * 80)

    findings = []

    # Check if precedent direction score is significant in full model
    if 'model_2' in all_results and all_results['model_2']:
        coefs = all_results['model_2']['coefficients']
        if 'precedent_direction_score' in coefs:
            pds = coefs['precedent_direction_score']
            if pds['p_value'] < 0.05:
                findings.append(f"H2.1 SUPPORTED: Precedent direction score remains significant")
                findings.append(f"  OR={pds['odds_ratio']:.2f} [{pds['ci_lower']:.2f}, {pds['ci_upper']:.2f}], p={pds['p_value']:.4f}")
            else:
                findings.append(f"H2.1 NOT SUPPORTED: Precedent direction score not significant after controls")
                findings.append(f"  OR={pds['odds_ratio']:.2f}, p={pds['p_value']:.4f}")

        if 'cites_gc_precedent' in coefs:
            gc = coefs['cites_gc_precedent']
            if gc['p_value'] < 0.05:
                findings.append(f"\nGrand Chamber citation effect PERSISTS")
                findings.append(f"  OR={gc['odds_ratio']:.2f} [{gc['ci_lower']:.2f}, {gc['ci_upper']:.2f}], p={gc['p_value']:.4f}")
            else:
                findings.append(f"\nGrand Chamber citation effect ATTENUATES")
                findings.append(f"  OR={gc['odds_ratio']:.2f}, p={gc['p_value']:.4f}")

        if 'pro_ds_purpose' in coefs:
            purpose = coefs['pro_ds_purpose']
            findings.append(f"\nPro-DS purpose effect:")
            findings.append(f"  OR={purpose['odds_ratio']:.2f} [{purpose['ci_lower']:.2f}, {purpose['ci_upper']:.2f}], p={purpose['p_value']:.4f}")

    for f in findings:
        print(f)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'n_analysis_sample': int(len(df_analysis)),
        'n_cases': int(df_analysis['case_id'].nunique()),
        'hierarchical_models': all_results,
        'robustness_tests': robustness,
        'purpose_propagation_mv': purpose_mv,
        'model_comparison': comparison,
        'summary': findings
    }

    # Convert numpy types
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

    output_file = NETWORK_PATH / "multivariate_citation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    # Create summary CSV
    if 'model_2' in all_results and all_results['model_2']:
        coef_df = pd.DataFrame([
            {'variable': var, **coef}
            for var, coef in all_results['model_2']['coefficients'].items()
        ])
        coef_df.to_csv(NETWORK_PATH / "multivariate_coefficients.csv", index=False)
        print(f"Coefficients saved to: multivariate_coefficients.csv")

    print("\n" + "=" * 80)
    print("PHASE 3 COMPLETE: MULTIVARIATE ANALYSIS")
    print("=" * 80)

    return results

if __name__ == "__main__":
    results = main()
