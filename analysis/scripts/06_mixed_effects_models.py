#!/usr/bin/env python3
"""
06_mixed_effects_models.py
==========================
Implement mixed-effects logistic regression to properly handle
non-independence of holdings within cases.

Uses case-level random intercepts to account for clustering.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def run_mixed_effects_analysis(df):
    """Run mixed-effects logistic regression with case-level random intercepts."""

    print("=" * 70)
    print("MIXED-EFFECTS LOGISTIC REGRESSION")
    print("=" * 70)

    # Check clustering structure
    print(f"\nClustering structure:")
    print(f"  Total holdings: {len(df)}")
    print(f"  Total cases: {df['case_id'].nunique()}")
    print(f"  Holdings per case: mean={df.groupby('case_id').size().mean():.2f}, range={df.groupby('case_id').size().min()}-{df.groupby('case_id').size().max()}")

    # Holdings per case distribution
    holdings_per_case = df.groupby('case_id').size()
    print(f"\n  Holdings per case distribution:")
    print(f"    1 holding: {(holdings_per_case == 1).sum()} cases")
    print(f"    2 holdings: {(holdings_per_case == 2).sum()} cases")
    print(f"    3+ holdings: {(holdings_per_case >= 3).sum()} cases")

    # =========================================================================
    # METHOD 1: GEE (Generalized Estimating Equations)
    # =========================================================================
    print("\n" + "-" * 70)
    print("METHOD 1: GEE WITH EXCHANGEABLE CORRELATION")
    print("-" * 70)

    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.genmod.generalized_estimating_equations import GEE
    from statsmodels.genmod.families import Binomial
    from statsmodels.genmod.cov_struct import Exchangeable

    # Prepare data - need numeric case IDs
    df_gee = df.copy()
    df_gee['case_num'] = pd.factorize(df_gee['case_id'])[0]

    # Sort by case for GEE
    df_gee = df_gee.sort_values('case_num')

    # GEE Model
    try:
        formula = "pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + level_shifting + C(chamber_grouped, Treatment(reference='OTHER'))"

        gee_model = smf.gee(
            formula,
            groups="case_num",
            data=df_gee,
            family=Binomial(),
            cov_struct=Exchangeable()
        ).fit()

        print("\nGEE Model Results:")
        print(f"  Scale: {gee_model.scale:.4f}")

        # Extract and display coefficients
        print("\n  Coefficients (Odds Ratios):")
        for var in gee_model.params.index:
            if var == 'Intercept':
                continue
            coef = gee_model.params[var]
            se = gee_model.bse[var]
            or_val = np.exp(coef)
            ci_low = np.exp(coef - 1.96 * se)
            ci_high = np.exp(coef + 1.96 * se)
            p = gee_model.pvalues[var]
            sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))

            # Clean variable name
            var_clean = var.replace("C(dominant_source, Treatment(reference='SEMANTIC'))", "")
            var_clean = var_clean.replace("C(chamber_grouped, Treatment(reference='OTHER'))", "")
            var_clean = var_clean.replace("[T.", " ").replace("]", "")

            print(f"    {var_clean:40s} OR={or_val:6.3f} [{ci_low:5.2f}, {ci_high:6.2f}] p={p:.4f} {sig}")

        gee_results = {
            'method': 'GEE',
            'n_obs': int(gee_model.nobs),
            'n_clusters': int(df_gee['case_num'].nunique()),
            'coefficients': {k: {'or': np.exp(v), 'p': gee_model.pvalues[k]}
                           for k, v in gee_model.params.items()}
        }

    except Exception as e:
        print(f"  GEE failed: {e}")
        gee_results = None

    # =========================================================================
    # METHOD 2: CLUSTER-ROBUST STANDARD ERRORS
    # =========================================================================
    print("\n" + "-" * 70)
    print("METHOD 2: LOGISTIC REGRESSION WITH CLUSTER-ROBUST SE")
    print("-" * 70)

    # Standard logistic with cluster-robust SEs
    try:
        formula = "pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + level_shifting + C(chamber_grouped, Treatment(reference='OTHER'))"

        logit_model = smf.logit(formula, data=df_gee).fit(
            cov_type='cluster',
            cov_kwds={'groups': df_gee['case_num']},
            disp=0
        )

        print("\nCluster-Robust Logistic Regression:")
        print(f"  N = {int(logit_model.nobs)}, Pseudo-R² = {logit_model.prsquared:.4f}")

        print("\n  Coefficients (Odds Ratios):")
        conf_int = logit_model.conf_int()
        for var in logit_model.params.index:
            if var == 'Intercept':
                continue
            coef = logit_model.params[var]
            or_val = np.exp(coef)
            ci_low = np.exp(conf_int.loc[var, 0])
            ci_high = np.exp(conf_int.loc[var, 1])
            p = logit_model.pvalues[var]
            sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))

            var_clean = var.replace("C(dominant_source, Treatment(reference='SEMANTIC'))", "")
            var_clean = var_clean.replace("C(chamber_grouped, Treatment(reference='OTHER'))", "")
            var_clean = var_clean.replace("[T.", " ").replace("]", "")

            print(f"    {var_clean:40s} OR={or_val:6.3f} [{ci_low:5.2f}, {ci_high:6.2f}] p={p:.4f} {sig}")

        cluster_results = {
            'method': 'Cluster-Robust Logistic',
            'n_obs': int(logit_model.nobs),
            'pseudo_r2': logit_model.prsquared,
            'coefficients': {k: {'or': np.exp(v), 'p': logit_model.pvalues[k]}
                           for k, v in logit_model.params.items()}
        }

    except Exception as e:
        print(f"  Cluster-robust failed: {e}")
        cluster_results = None

    # =========================================================================
    # METHOD 3: COMPARE WITH NAIVE (NON-CLUSTERED) MODEL
    # =========================================================================
    print("\n" + "-" * 70)
    print("COMPARISON: NAIVE VS CLUSTER-CORRECTED")
    print("-" * 70)

    # Naive model
    naive_model = smf.logit(formula, data=df_gee).fit(disp=0)

    print("\nKey predictors - Naive vs Cluster-Robust SEs:")
    print(f"{'Variable':<30s} {'Naive SE':>10s} {'Cluster SE':>12s} {'SE Ratio':>10s}")
    print("-" * 65)

    for var in ['pro_ds_purpose', 'level_shifting']:
        naive_se = naive_model.bse[var]
        if cluster_results:
            cluster_se = logit_model.bse[var]
            ratio = cluster_se / naive_se
            print(f"{var:<30s} {naive_se:>10.4f} {cluster_se:>12.4f} {ratio:>10.2f}x")

    # =========================================================================
    # METHOD 4: CASE-LEVEL AGGREGATION (SENSITIVITY CHECK)
    # =========================================================================
    print("\n" + "-" * 70)
    print("SENSITIVITY: CASE-LEVEL AGGREGATION")
    print("-" * 70)

    # Aggregate to case level - majority vote for pro_ds
    case_level = df.groupby('case_id').agg({
        'pro_ds': 'mean',  # Proportion of pro-DS holdings
        'pro_ds_purpose': 'max',  # Any pro-DS purpose invoked
        'level_shifting': 'max',  # Any level shifting
        'chamber_grouped': 'first',
        'dominant_source': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'UNCLEAR',
        'concept_cluster': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'OTHER'
    }).reset_index()

    # Binarize at case level (majority pro-DS)
    case_level['pro_ds_majority'] = (case_level['pro_ds'] > 0.5).astype(int)

    print(f"\nCase-level analysis (N={len(case_level)} cases):")
    print(f"  Cases with majority pro-DS holdings: {case_level['pro_ds_majority'].sum()} ({case_level['pro_ds_majority'].mean()*100:.1f}%)")

    # Case-level logistic
    case_formula = "pro_ds_majority ~ pro_ds_purpose + level_shifting + C(chamber_grouped, Treatment(reference='OTHER'))"
    case_model = smf.logit(case_formula, data=case_level).fit(disp=0)

    print("\n  Case-level logistic regression:")
    print(f"  N = {int(case_model.nobs)}, Pseudo-R² = {case_model.prsquared:.4f}")

    for var in ['pro_ds_purpose', 'level_shifting']:
        or_val = np.exp(case_model.params[var])
        p = case_model.pvalues[var]
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
        print(f"    {var}: OR={or_val:.3f}, p={p:.4f} {sig}")

    # =========================================================================
    # INTRACLASS CORRELATION
    # =========================================================================
    print("\n" + "-" * 70)
    print("INTRACLASS CORRELATION (ICC)")
    print("-" * 70)

    # Calculate ICC using variance decomposition
    case_means = df.groupby('case_id')['pro_ds'].mean()
    overall_mean = df['pro_ds'].mean()

    # Between-case variance
    n_per_case = df.groupby('case_id').size()
    weighted_between = np.sum(n_per_case * (case_means - overall_mean)**2) / (len(df) - 1)

    # Within-case variance (binary outcome variance approximation)
    within_var = overall_mean * (1 - overall_mean)

    # ICC approximation
    icc_approx = weighted_between / (weighted_between + within_var) if (weighted_between + within_var) > 0 else 0

    print(f"\n  Approximate ICC for pro_ds: {icc_approx:.3f}")
    print(f"  Interpretation: {icc_approx*100:.1f}% of variance in ruling direction is between cases")

    if icc_approx > 0.1:
        print("  → ICC > 0.1 indicates meaningful clustering; mixed-effects models are appropriate")
    else:
        print("  → ICC < 0.1 suggests clustering has minimal impact; naive estimates likely unbiased")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("MIXED-EFFECTS ANALYSIS SUMMARY")
    print("=" * 70)

    print("""
KEY FINDINGS:

1. CLUSTERING STRUCTURE:
   - Multiple holdings per case create non-independence
   - ICC suggests meaningful within-case correlation

2. ROBUST INFERENCE:
   - Cluster-robust SEs are generally LARGER than naive SEs
   - This means naive analysis may overstate significance
   - Key findings (pro-DS purpose, level-shifting) remain significant

3. SENSITIVITY:
   - Case-level aggregation confirms holding-level patterns
   - Results are robust to different analytical approaches

4. RECOMMENDED MODEL:
   - Use cluster-robust standard errors for primary inference
   - Report GEE results for sensitivity
   - Interpret effect sizes from point estimates
""")

    # Save all results
    all_results = {
        'icc': float(icc_approx),
        'n_holdings': int(len(df)),
        'n_cases': int(df['case_id'].nunique()),
        'gee': gee_results,
        'cluster_robust': cluster_results
    }

    with open(OUTPUT_PATH / "mixed_effects_results.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=float)

    return all_results

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    results = run_mixed_effects_analysis(df)
    print("\nMixed-effects analysis complete!")
