#!/usr/bin/env python3
"""
03_multivariate_analysis.py
===========================
Multivariate logistic regression analysis of pro-data subject rulings.

Implements hierarchical model building with mixed-effects specification.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def calculate_vif(df, features):
    """Calculate Variance Inflation Factors for multicollinearity check."""
    X = df[features].dropna()
    vif_data = []
    for i, col in enumerate(features):
        try:
            vif = variance_inflation_factor(X.values, i)
            vif_data.append({'Variable': col, 'VIF': vif})
        except:
            vif_data.append({'Variable': col, 'VIF': np.nan})
    return pd.DataFrame(vif_data)

def logistic_regression(df, formula, model_name):
    """Fit logistic regression and return results summary."""
    try:
        model = smf.logit(formula, data=df).fit(disp=0)

        # Extract results
        results = {
            'model_name': model_name,
            'formula': formula,
            'n': int(model.nobs),
            'aic': model.aic,
            'bic': model.bic,
            'pseudo_r2': model.prsquared,
            'llf': model.llf,
            'llnull': model.llnull,
            'converged': model.mle_retvals['converged'],
            'coefficients': {}
        }

        # Get coefficients with CIs
        conf_int = model.conf_int()
        for var in model.params.index:
            coef = model.params[var]
            se = model.bse[var]
            z = model.tvalues[var]
            p = model.pvalues[var]
            ci_low, ci_high = conf_int.loc[var]
            or_val = np.exp(coef)
            or_ci_low = np.exp(ci_low)
            or_ci_high = np.exp(ci_high)

            results['coefficients'][var] = {
                'coef': coef,
                'se': se,
                'z': z,
                'p': p,
                'ci_low': ci_low,
                'ci_high': ci_high,
                'odds_ratio': or_val,
                'or_ci_low': or_ci_low,
                'or_ci_high': or_ci_high
            }

        return model, results

    except Exception as e:
        print(f"Error fitting {model_name}: {e}")
        return None, None

def run_multivariate_analysis(df):
    """Run hierarchical multivariate logistic regression models."""

    print("=" * 70)
    print("MULTIVARIATE ANALYSIS: LOGISTIC REGRESSION MODELS")
    print("=" * 70)

    # Store all model results
    all_results = []
    models = {}

    # =========================================================================
    # MODEL 0: NULL MODEL
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 0: NULL (Intercept Only)")
    print("-" * 70)

    m0, r0 = logistic_regression(df, "pro_ds ~ 1", "Model 0: Null")
    if r0:
        all_results.append(r0)
        models['m0'] = m0
        print(f"  N = {r0['n']}, Log-likelihood = {r0['llf']:.2f}")
        print(f"  Base rate pro-DS: {df['pro_ds'].mean()*100:.1f}%")

    # =========================================================================
    # MODEL 1: INSTITUTIONAL FACTORS
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 1: + Institutional Factors (Chamber, Year)")
    print("-" * 70)

    m1, r1 = logistic_regression(
        df,
        "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year",
        "Model 1: Institutional"
    )
    if r1:
        all_results.append(r1)
        models['m1'] = m1
        print(f"  N = {r1['n']}, AIC = {r1['aic']:.1f}, Pseudo-R² = {r1['pseudo_r2']:.4f}")

        # LR test vs null
        if m0:
            lr_stat = 2 * (r1['llf'] - r0['llf'])
            df_diff = len(r1['coefficients']) - len(r0['coefficients'])
            p_val = 1 - stats.chi2.cdf(lr_stat, df_diff)
            print(f"  LR test vs. null: χ²({df_diff}) = {lr_stat:.2f}, p = {p_val:.4f}")

    # =========================================================================
    # MODEL 2: + CONCEPTUAL FACTORS
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 2: + Conceptual Factors (Concept Cluster)")
    print("-" * 70)

    m2, r2 = logistic_regression(
        df,
        "pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + C(concept_cluster, Treatment(reference='OTHER'))",
        "Model 2: + Conceptual"
    )
    if r2:
        all_results.append(r2)
        models['m2'] = m2
        print(f"  N = {r2['n']}, AIC = {r2['aic']:.1f}, Pseudo-R² = {r2['pseudo_r2']:.4f}")

        if r1:
            lr_stat = 2 * (r2['llf'] - r1['llf'])
            df_diff = len(r2['coefficients']) - len(r1['coefficients'])
            p_val = 1 - stats.chi2.cdf(lr_stat, df_diff)
            print(f"  LR test vs. Model 1: χ²({df_diff}) = {lr_stat:.2f}, p = {p_val:.4f}")

    # =========================================================================
    # MODEL 3: + INTERPRETIVE SOURCES
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 3: + Interpretive Sources")
    print("-" * 70)

    m3, r3 = logistic_regression(
        df,
        """pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
           C(concept_cluster, Treatment(reference='OTHER')) +
           C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose""",
        "Model 3: + Interpretive"
    )
    if r3:
        all_results.append(r3)
        models['m3'] = m3
        print(f"  N = {r3['n']}, AIC = {r3['aic']:.1f}, Pseudo-R² = {r3['pseudo_r2']:.4f}")

        if r2:
            lr_stat = 2 * (r3['llf'] - r2['llf'])
            df_diff = len(r3['coefficients']) - len(r2['coefficients'])
            p_val = 1 - stats.chi2.cdf(lr_stat, df_diff)
            print(f"  LR test vs. Model 2: χ²({df_diff}) = {lr_stat:.2f}, p = {p_val:.4f}")

    # =========================================================================
    # MODEL 4: + REASONING STRUCTURE
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 4: + Reasoning Structure")
    print("-" * 70)

    m4, r4 = logistic_regression(
        df,
        """pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
           C(concept_cluster, Treatment(reference='OTHER')) +
           C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose +
           C(dominant_structure, Treatment(reference='RULE_BASED')) + level_shifting""",
        "Model 4: + Reasoning"
    )
    if r4:
        all_results.append(r4)
        models['m4'] = m4
        print(f"  N = {r4['n']}, AIC = {r4['aic']:.1f}, Pseudo-R² = {r4['pseudo_r2']:.4f}")

        if r3:
            lr_stat = 2 * (r4['llf'] - r3['llf'])
            df_diff = len(r4['coefficients']) - len(r3['coefficients'])
            p_val = 1 - stats.chi2.cdf(lr_stat, df_diff)
            print(f"  LR test vs. Model 3: χ²({df_diff}) = {lr_stat:.2f}, p = {p_val:.4f}")

    # =========================================================================
    # MODEL 5: + BALANCING FACTORS (FULL MODEL)
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 5: + Balancing (Full Model)")
    print("-" * 70)

    m5, r5 = logistic_regression(
        df,
        """pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year +
           C(concept_cluster, Treatment(reference='OTHER')) +
           C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose +
           C(dominant_structure, Treatment(reference='RULE_BASED')) + level_shifting +
           any_balancing""",
        "Model 5: Full"
    )
    if r5:
        all_results.append(r5)
        models['m5'] = m5
        print(f"  N = {r5['n']}, AIC = {r5['aic']:.1f}, Pseudo-R² = {r5['pseudo_r2']:.4f}")

        if r4:
            lr_stat = 2 * (r5['llf'] - r4['llf'])
            df_diff = len(r5['coefficients']) - len(r4['coefficients'])
            p_val = 1 - stats.chi2.cdf(lr_stat, df_diff)
            print(f"  LR test vs. Model 4: χ²({df_diff}) = {lr_stat:.2f}, p = {p_val:.4f}")

    # =========================================================================
    # PARSIMONIOUS MODEL (Based on significant predictors)
    # =========================================================================
    print("\n" + "-" * 70)
    print("MODEL 6: PARSIMONIOUS (Key Predictors Only)")
    print("-" * 70)

    m6, r6 = logistic_regression(
        df,
        """pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) +
           pro_ds_purpose + level_shifting + any_balancing""",
        "Model 6: Parsimonious"
    )
    if r6:
        all_results.append(r6)
        models['m6'] = m6
        print(f"  N = {r6['n']}, AIC = {r6['aic']:.1f}, Pseudo-R² = {r6['pseudo_r2']:.4f}")

    # =========================================================================
    # MODEL COMPARISON TABLE
    # =========================================================================
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)

    comparison_data = []
    for r in all_results:
        comparison_data.append({
            'Model': r['model_name'],
            'N': r['n'],
            'K': len(r['coefficients']),
            'Log-lik': f"{r['llf']:.2f}",
            'AIC': f"{r['aic']:.1f}",
            'BIC': f"{r['bic']:.1f}",
            'Pseudo-R²': f"{r['pseudo_r2']:.4f}"
        })

    comparison_df = pd.DataFrame(comparison_data)
    print("\n" + comparison_df.to_string(index=False))

    # Find best model by AIC
    best_aic_idx = np.argmin([r['aic'] for r in all_results])
    best_model = all_results[best_aic_idx]
    print(f"\nBest model by AIC: {best_model['model_name']}")

    # =========================================================================
    # FINAL MODEL COEFFICIENTS
    # =========================================================================
    print("\n" + "=" * 70)
    print(f"FINAL MODEL COEFFICIENTS: {best_model['model_name']}")
    print("=" * 70)

    coef_data = []
    for var, stats_dict in best_model['coefficients'].items():
        sig = ''
        if stats_dict['p'] < 0.001:
            sig = '***'
        elif stats_dict['p'] < 0.01:
            sig = '**'
        elif stats_dict['p'] < 0.05:
            sig = '*'

        coef_data.append({
            'Variable': var,
            'OR': f"{stats_dict['odds_ratio']:.3f}",
            '95% CI': f"[{stats_dict['or_ci_low']:.2f}, {stats_dict['or_ci_high']:.2f}]",
            'p': f"{stats_dict['p']:.4f}",
            'Sig': sig
        })

    coef_df = pd.DataFrame(coef_data)
    print("\n" + coef_df.to_string(index=False))

    # =========================================================================
    # MULTICOLLINEARITY CHECK
    # =========================================================================
    print("\n" + "-" * 70)
    print("MULTICOLLINEARITY CHECK (VIF)")
    print("-" * 70)

    numeric_features = ['year', 'pro_ds_purpose', 'level_shifting', 'any_balancing',
                        'dominant_teleological', 'dominant_systematic']
    vif_df = calculate_vif(df, [f for f in numeric_features if f in df.columns])
    print(vif_df.to_string(index=False))

    if vif_df['VIF'].max() > 5:
        print("\n  WARNING: Some VIF values > 5 suggest potential multicollinearity")
    else:
        print("\n  All VIF values < 5: No concerning multicollinearity detected")

    # =========================================================================
    # PREDICTED PROBABILITIES BY KEY PREDICTORS
    # =========================================================================
    print("\n" + "-" * 70)
    print("PREDICTED PROBABILITIES")
    print("-" * 70)

    if 'm6' in models and models['m6'] is not None:
        model = models['m6']

        # By dominant source
        print("\nPredicted P(Pro-DS) by Dominant Source:")
        for source in ['SEMANTIC', 'SYSTEMATIC', 'TELEOLOGICAL']:
            subset = df[df['dominant_source'] == source]
            if len(subset) > 0:
                pred_prob = model.predict(subset).mean()
                print(f"  {source}: {pred_prob*100:.1f}%")

        # By pro-DS purpose
        print("\nPredicted P(Pro-DS) by Pro-DS Purpose Invoked:")
        for val in [0, 1]:
            subset = df[df['pro_ds_purpose'] == val]
            if len(subset) > 0:
                pred_prob = model.predict(subset).mean()
                label = "Yes" if val == 1 else "No"
                print(f"  {label}: {pred_prob*100:.1f}%")

        # By level shifting
        print("\nPredicted P(Pro-DS) by Level Shifting:")
        for val in [0, 1]:
            subset = df[df['level_shifting'] == val]
            if len(subset) > 0:
                pred_prob = model.predict(subset).mean()
                label = "Yes" if val == 1 else "No"
                print(f"  {label}: {pred_prob*100:.1f}%")

    # =========================================================================
    # SAVE RESULTS
    # =========================================================================
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Save comparison table
    comparison_df.to_csv(OUTPUT_PATH / "model_comparison.csv", index=False)

    # Save final model coefficients
    coef_df.to_csv(OUTPUT_PATH / "final_model_coefficients.csv", index=False)

    # Save all results as JSON
    with open(OUTPUT_PATH / "multivariate_results.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to {OUTPUT_PATH}")

    return models, all_results

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    models, results = run_multivariate_analysis(df)
    print("\nMultivariate analysis complete!")
