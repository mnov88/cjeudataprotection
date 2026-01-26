#!/usr/bin/env python3
"""
16_coherence_residual_analysis.py
==================================
Direction-Prediction Coherence Analysis of CJEU GDPR Holdings.

Core thesis: if the CJEU's GDPR jurisprudence is internally coherent, the coded
legal variables (concept cluster, interpretive source, reasoning structure,
balancing factors) should predict ruling direction. Holdings where prediction
strongly disagrees with outcome are candidate doctrinal tension points.

Methodology:
- Uses parsimonious model (EPV ~12) to avoid overfitting with N=181
- Leave-one-out cross-validation for out-of-sample predicted probabilities
- Case-level aggregation to address clustering (ICC ~0.295)
- Bootstrap stability checks for flagged holdings
- Calibration analysis instead of Hosmer-Lemeshow
- Stratified prediction error by concept cluster (not within-cluster refitting)
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
from collections import Counter

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output" / "coherence"

# =============================================================================
# SECTION 1: DATA LOADING AND MODEL FITTING
# =============================================================================

def load_data():
    """Load prepared holdings data."""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} holdings from {df['case_id'].nunique()} cases")
    print(f"Base rate: {df['pro_ds'].mean()*100:.1f}% pro-DS")
    return df


def fit_parsimonious_model(df):
    """
    Fit the parsimonious logistic regression model.

    Uses the parsimonious specification from 03_multivariate_analysis.py:
      pro_ds ~ C(dominant_source) + pro_ds_purpose + level_shifting + any_balancing

    This has ~6 parameters for 181 observations (EPV ~12 for minority class),
    which avoids the overfitting problems of the full 22-parameter model.
    """
    formula = ("pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) + "
               "pro_ds_purpose + level_shifting + any_balancing")

    model = smf.logit(formula, data=df).fit(disp=0)

    print("\n" + "=" * 70)
    print("PARSIMONIOUS MODEL FIT")
    print("=" * 70)
    print(f"  N = {int(model.nobs)}")
    print(f"  Log-likelihood = {model.llf:.2f}")
    print(f"  AIC = {model.aic:.1f}")
    print(f"  Pseudo-R² (McFadden) = {model.prsquared:.4f}")
    print(f"  Converged: {model.mle_retvals['converged']}")

    # Coefficients as odds ratios
    print("\n  Coefficients (Odds Ratios):")
    conf_int = model.conf_int()
    for var in model.params.index:
        coef = model.params[var]
        p = model.pvalues[var]
        or_val = np.exp(coef)
        ci_low, ci_high = np.exp(conf_int.loc[var])
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"    {var}: OR={or_val:.3f} [{ci_low:.2f}, {ci_high:.2f}] p={p:.4f} {sig}")

    return model


def fit_full_model(df):
    """
    Fit the full hierarchical model (Model 5 from 03_multivariate_analysis.py).

    Used only for comparison — NOT for residual analysis due to EPV concerns.
    """
    formula = ("pro_ds ~ C(chamber_grouped, Treatment(reference='OTHER')) + year + "
               "C(concept_cluster, Treatment(reference='OTHER')) + "
               "C(dominant_source, Treatment(reference='SEMANTIC')) + pro_ds_purpose + "
               "C(dominant_structure, Treatment(reference='RULE_BASED')) + level_shifting + "
               "any_balancing")

    model = smf.logit(formula, data=df).fit(disp=0)

    print(f"\n  Full model: AIC={model.aic:.1f}, Pseudo-R²={model.prsquared:.4f}, "
          f"K={len(model.params)}")

    return model


# =============================================================================
# SECTION 2: LEAVE-ONE-OUT CROSS-VALIDATION
# =============================================================================

def loocv_predictions(df):
    """
    Compute leave-one-out cross-validated predicted probabilities.

    For each holding, fits the parsimonious model on the remaining 180 holdings
    and predicts the held-out holding. This gives out-of-sample predictions
    free of overfitting contamination.
    """
    formula = ("pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) + "
               "pro_ds_purpose + level_shifting + any_balancing")

    n = len(df)
    loo_probs = np.zeros(n)
    loo_converged = np.zeros(n, dtype=bool)

    print("\n" + "=" * 70)
    print("LEAVE-ONE-OUT CROSS-VALIDATION")
    print("=" * 70)

    for i in range(n):
        train = df.drop(df.index[i])
        test = df.iloc[[i]]

        try:
            model = smf.logit(formula, data=train).fit(disp=0, maxiter=100)
            loo_probs[i] = model.predict(test).values[0]
            loo_converged[i] = model.mle_retvals['converged']
        except Exception:
            # Fallback: use base rate from training set
            loo_probs[i] = train['pro_ds'].mean()
            loo_converged[i] = False

    n_converged = loo_converged.sum()
    print(f"  LOOCV complete: {n_converged}/{n} models converged")
    print(f"  Mean predicted P(pro-DS): {loo_probs.mean():.3f}")
    print(f"  Observed P(pro-DS): {df['pro_ds'].mean():.3f}")

    return loo_probs


# =============================================================================
# SECTION 3: MODEL PERFORMANCE AND CALIBRATION
# =============================================================================

def compute_performance_metrics(df, in_sample_probs, loo_probs):
    """
    Compute comprehensive model performance metrics.

    Focuses on calibration and discrimination, comparing in-sample to LOOCV.
    """
    y = df['pro_ds'].values
    base_rate = y.mean()

    print("\n" + "=" * 70)
    print("MODEL PERFORMANCE METRICS")
    print("=" * 70)

    metrics = {}

    for label, probs in [("In-sample", in_sample_probs), ("LOOCV", loo_probs)]:
        # Brier score
        brier = np.mean((probs - y) ** 2)

        # Brier score of naive model (always predict base rate)
        brier_null = np.mean((base_rate - y) ** 2)

        # Brier skill score (improvement over base rate)
        brier_skill = 1 - (brier / brier_null)

        # Log-loss
        eps = 1e-15
        probs_clipped = np.clip(probs, eps, 1 - eps)
        log_loss = -np.mean(y * np.log(probs_clipped) + (1 - y) * np.log(1 - probs_clipped))
        log_loss_null = -np.mean(y * np.log(base_rate) + (1 - y) * np.log(1 - base_rate))

        # Classification at 0.50
        predicted_class = (probs >= 0.5).astype(int)
        accuracy = np.mean(predicted_class == y)
        accuracy_improvement = accuracy - base_rate

        # Sensitivity and specificity
        tp = np.sum((predicted_class == 1) & (y == 1))
        tn = np.sum((predicted_class == 0) & (y == 0))
        fp = np.sum((predicted_class == 1) & (y == 0))
        fn = np.sum((predicted_class == 0) & (y == 1))
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        # AUC-ROC (Mann-Whitney U approach)
        auc = compute_auc(y, probs)

        # Mean absolute error
        mae = np.mean(np.abs(probs - y))

        metrics[label] = {
            'brier_score': brier,
            'brier_null': brier_null,
            'brier_skill': brier_skill,
            'log_loss': log_loss,
            'log_loss_null': log_loss_null,
            'accuracy': accuracy,
            'accuracy_improvement': accuracy_improvement,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'auc_roc': auc,
            'mae': mae
        }

        print(f"\n  {label} Performance:")
        print(f"    Brier score:        {brier:.4f} (null: {brier_null:.4f})")
        print(f"    Brier skill score:  {brier_skill:.4f}")
        print(f"    Log-loss:           {log_loss:.4f} (null: {log_loss_null:.4f})")
        print(f"    AUC-ROC:            {auc:.4f}")
        print(f"    Accuracy (@0.50):   {accuracy*100:.1f}% (base rate: {base_rate*100:.1f}%)")
        print(f"    Improvement:        +{accuracy_improvement*100:.1f}pp over base rate")
        print(f"    Sensitivity:        {sensitivity*100:.1f}%")
        print(f"    Specificity:        {specificity*100:.1f}%")
        print(f"    MAE:                {mae:.4f}")

    return metrics


def compute_auc(y, probs):
    """Compute AUC-ROC using the Mann-Whitney U statistic."""
    pos = probs[y == 1]
    neg = probs[y == 0]
    n_pos = len(pos)
    n_neg = len(neg)

    if n_pos == 0 or n_neg == 0:
        return 0.5

    auc = 0
    for p in pos:
        auc += np.sum(p > neg) + 0.5 * np.sum(p == neg)
    auc /= (n_pos * n_neg)
    return auc


def calibration_analysis(df, loo_probs, n_bins=5):
    """
    Calibration analysis using binned predicted probabilities.

    Uses 5 bins (quintiles) rather than 10 (deciles) given N=181.
    Reports observed vs. expected event rates per bin.
    """
    y = df['pro_ds'].values

    print("\n" + "-" * 70)
    print("CALIBRATION ANALYSIS (LOOCV Predictions)")
    print("-" * 70)

    # Create bins by predicted probability quintiles
    try:
        bins = pd.qcut(loo_probs, q=n_bins, duplicates='drop')
    except ValueError:
        bins = pd.cut(loo_probs, bins=n_bins)

    cal_data = pd.DataFrame({
        'predicted': loo_probs,
        'observed': y,
        'bin': bins
    })

    cal_table = cal_data.groupby('bin', observed=True).agg(
        n=('observed', 'count'),
        mean_predicted=('predicted', 'mean'),
        mean_observed=('observed', 'mean'),
        std_observed=('observed', 'std')
    ).reset_index()

    print(f"\n  {'Bin':<30} {'N':>5} {'Pred':>8} {'Obs':>8} {'Diff':>8}")
    print("  " + "-" * 65)

    calibration_errors = []
    for _, row in cal_table.iterrows():
        diff = row['mean_observed'] - row['mean_predicted']
        calibration_errors.append(abs(diff))
        print(f"  {str(row['bin']):<30} {row['n']:>5.0f} "
              f"{row['mean_predicted']:>8.3f} {row['mean_observed']:>8.3f} "
              f"{diff:>+8.3f}")

    mean_cal_error = np.mean(calibration_errors)
    max_cal_error = np.max(calibration_errors)
    print(f"\n  Mean calibration error: {mean_cal_error:.4f}")
    print(f"  Max calibration error:  {max_cal_error:.4f}")

    if mean_cal_error < 0.05:
        print("  Assessment: Well-calibrated")
    elif mean_cal_error < 0.10:
        print("  Assessment: Reasonably calibrated")
    else:
        print("  Assessment: Potential miscalibration detected")

    return cal_table, mean_cal_error


# =============================================================================
# SECTION 4: RESIDUAL ANALYSIS AND INCOHERENCE FLAGGING
# =============================================================================

def compute_residuals(df, model, loo_probs):
    """
    Compute multiple types of residuals for each holding.

    Uses in-sample model for Pearson/deviance residuals and Cook's distance,
    and LOOCV probabilities for the main incoherence flagging.
    """
    y = df['pro_ds'].values
    p_hat = model.predict(df)

    # Pearson residuals: (y - p_hat) / sqrt(p_hat * (1 - p_hat))
    pearson_resid = (y - p_hat) / np.sqrt(p_hat * (1 - p_hat) + 1e-10)

    # Deviance residuals: sign(y - p_hat) * sqrt(deviance contribution)
    eps = 1e-10
    d_i = np.where(
        y == 1,
        -2 * np.log(np.clip(p_hat, eps, 1)),
        -2 * np.log(np.clip(1 - p_hat, eps, 1))
    )
    deviance_resid = np.sign(y - p_hat) * np.sqrt(d_i)

    # LOOCV surprise: |y - p_loo|
    loo_surprise = np.abs(y - loo_probs)

    # LOOCV prediction error direction
    # Positive = model predicted pro-DS but outcome was NOT pro-DS
    # Negative = model predicted NOT pro-DS but outcome was pro-DS
    loo_error = loo_probs - y  # positive when overpredicting pro-DS

    # Influence: approximate Cook's distance via hat matrix
    try:
        hat_matrix = model.get_influence().hat_matrix_diag
        cooks_d = model.get_influence().cooks_distance[0]
    except Exception:
        hat_matrix = np.full(len(df), np.nan)
        cooks_d = np.full(len(df), np.nan)

    return {
        'p_hat_insample': p_hat,
        'p_hat_loo': loo_probs,
        'pearson_resid': pearson_resid,
        'deviance_resid': deviance_resid,
        'loo_surprise': loo_surprise,
        'loo_error': loo_error,
        'hat_matrix': hat_matrix,
        'cooks_d': cooks_d
    }


def flag_incoherence(df, loo_probs, thresholds=(0.65, 0.70, 0.75)):
    """
    Flag holdings where LOOCV prediction strongly disagrees with outcome.

    Type A ("Expected pro-DS"): P(pro-DS) >= threshold but outcome is NOT pro-DS.
      The model says "everything about this holding points to pro-DS" but the
      Court ruled otherwise. Candidate for doctrinal tension.

    Type B ("Expected non-pro-DS"): P(pro-DS) <= (1-threshold) but outcome IS pro-DS.
      The model says "nothing about this holding suggests pro-DS" but the Court
      ruled pro-DS. Candidate for unexplained protectiveness.
    """
    y = df['pro_ds'].values

    print("\n" + "=" * 70)
    print("INCOHERENCE FLAGGING (LOOCV-based)")
    print("=" * 70)

    all_flags = {}

    for threshold in thresholds:
        type_a_mask = (loo_probs >= threshold) & (y == 0)
        type_b_mask = (loo_probs <= (1 - threshold)) & (y == 1)

        type_a_idx = np.where(type_a_mask)[0]
        type_b_idx = np.where(type_b_mask)[0]

        print(f"\n  Threshold = {threshold:.2f}:")
        print(f"    Type A (expected pro-DS, got other): {len(type_a_idx)} holdings")
        print(f"    Type B (expected other, got pro-DS): {len(type_b_idx)} holdings")
        print(f"    Total flagged: {len(type_a_idx) + len(type_b_idx)} of {len(df)} "
              f"({(len(type_a_idx) + len(type_b_idx))/len(df)*100:.1f}%)")

        all_flags[threshold] = {
            'type_a': type_a_idx.tolist(),
            'type_b': type_b_idx.tolist(),
        }

    return all_flags


# =============================================================================
# SECTION 5: INCOHERENCE PATTERN ANALYSIS
# =============================================================================

def analyze_incoherence_patterns(df, loo_probs, flags, threshold=0.70):
    """
    Analyze patterns among flagged holdings at the primary threshold.

    Groups flagged holdings by concept cluster, chamber, and case to identify
    whether incoherence clusters in specific doctrinal domains.
    """
    y = df['pro_ds'].values
    flag_data = flags[threshold]

    print("\n" + "=" * 70)
    print(f"INCOHERENCE PATTERN ANALYSIS (threshold={threshold})")
    print("=" * 70)

    results = {'type_a': {}, 'type_b': {}}

    for flag_type, label, indices in [
        ('type_a', 'TYPE A: Expected pro-DS, got other', flag_data['type_a']),
        ('type_b', 'TYPE B: Expected other, got pro-DS', flag_data['type_b'])
    ]:
        if not indices:
            print(f"\n  {label}: No flagged holdings")
            results[flag_type] = {'count': 0}
            continue

        flagged = df.iloc[indices]

        print(f"\n  {label} ({len(flagged)} holdings)")
        print("  " + "-" * 60)

        # By concept cluster
        cluster_dist = flagged['concept_cluster'].value_counts()
        cluster_base = df['concept_cluster'].value_counts()
        print(f"\n  By Concept Cluster:")
        for cluster in cluster_dist.index:
            n_flagged = cluster_dist[cluster]
            n_total = cluster_base.get(cluster, 0)
            pct_flagged = n_flagged / n_total * 100 if n_total > 0 else 0
            print(f"    {cluster}: {n_flagged}/{n_total} flagged ({pct_flagged:.1f}%)")

        # By chamber
        chamber_dist = flagged['chamber_grouped'].value_counts()
        chamber_base = df['chamber_grouped'].value_counts()
        print(f"\n  By Chamber:")
        for chamber in chamber_dist.index:
            n_flagged = chamber_dist[chamber]
            n_total = chamber_base.get(chamber, 0)
            pct_flagged = n_flagged / n_total * 100 if n_total > 0 else 0
            print(f"    {chamber}: {n_flagged}/{n_total} flagged ({pct_flagged:.1f}%)")

        # By case
        case_dist = flagged['case_id'].value_counts()
        print(f"\n  By Case (cases with >1 flagged holding):")
        multi_flag_cases = case_dist[case_dist > 1]
        if len(multi_flag_cases) > 0:
            for case_id, count in multi_flag_cases.items():
                total_in_case = len(df[df['case_id'] == case_id])
                print(f"    {case_id}: {count}/{total_in_case} holdings flagged")
        else:
            print(f"    No cases with multiple flagged holdings")

        # Compensation flag
        n_comp = flagged['is_compensation'].sum()
        pct_comp = n_comp / len(flagged) * 100 if len(flagged) > 0 else 0
        print(f"\n  Compensation holdings: {n_comp}/{len(flagged)} ({pct_comp:.1f}%)")

        results[flag_type] = {
            'count': len(flagged),
            'by_cluster': cluster_dist.to_dict(),
            'by_chamber': chamber_dist.to_dict(),
            'by_case': case_dist.to_dict(),
            'n_compensation': int(n_comp)
        }

    return results


def qualitative_deep_dive(df, loo_probs, flags, threshold=0.70):
    """
    Produce qualitative detail for each flagged holding.

    For each holding flagged as incoherent, extracts case ID, core holding,
    direction justification, predicted probability, and actual outcome for
    manual review.
    """
    y = df['pro_ds'].values
    flag_data = flags[threshold]

    print("\n" + "=" * 70)
    print(f"QUALITATIVE DEEP DIVE (threshold={threshold})")
    print("=" * 70)

    deep_dive_records = []

    for flag_type, label, indices in [
        ('type_a', 'TYPE A: Expected pro-DS, got other', flag_data['type_a']),
        ('type_b', 'TYPE B: Expected other, got pro-DS', flag_data['type_b'])
    ]:
        if not indices:
            continue

        print(f"\n  {label}")
        print("  " + "=" * 60)

        for idx in indices:
            row = df.iloc[idx]
            p_loo = loo_probs[idx]

            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    P(pro-DS) = {p_loo:.3f}, Actual: {row['ruling_direction']}")
            print(f"    Concept: {row['primary_concept']} ({row['concept_cluster']})")
            print(f"    Chamber: {row['chamber']}")
            print(f"    Dominant source: {row['dominant_source']}, "
                  f"Structure: {row['dominant_structure']}")
            print(f"    Pro-DS purpose: {'Yes' if row['pro_ds_purpose'] else 'No'}, "
                  f"Level-shifting: {'Yes' if row['level_shifting'] else 'No'}, "
                  f"Balancing: {'Yes' if row['any_balancing'] else 'No'}")

            core = str(row['core_holding'])
            if len(core) > 200:
                core = core[:200] + "..."
            print(f"    Core holding: {core}")

            justification = str(row.get('direction_justification', 'N/A'))
            if len(justification) > 200:
                justification = justification[:200] + "..."
            print(f"    Justification: {justification}")

            deep_dive_records.append({
                'flag_type': flag_type,
                'case_id': row['case_id'],
                'holding_id': int(row['holding_id']),
                'p_loo': float(p_loo),
                'actual_direction': row['ruling_direction'],
                'primary_concept': row['primary_concept'],
                'concept_cluster': row['concept_cluster'],
                'chamber': row['chamber'],
                'dominant_source': row['dominant_source'],
                'dominant_structure': row['dominant_structure'],
                'pro_ds_purpose': bool(row['pro_ds_purpose']),
                'level_shifting': bool(row['level_shifting']),
                'any_balancing': bool(row['any_balancing']),
                'is_compensation': bool(row['is_compensation']),
                'core_holding': str(row['core_holding']),
                'direction_justification': str(row.get('direction_justification', ''))
            })

    return deep_dive_records


# =============================================================================
# SECTION 6: DOMAIN-SPECIFIC COHERENCE (STRATIFIED ERROR ANALYSIS)
# =============================================================================

def domain_coherence_analysis(df, loo_probs):
    """
    Compare model prediction error across concept clusters.

    Instead of refitting models within each cluster (infeasible due to small N),
    this stratifies the global model's prediction error by cluster. Clusters
    where prediction error is higher are domains where the Court's behavior
    is less well-explained by the coded variables.
    """
    y = df['pro_ds'].values
    base_rate = y.mean()

    print("\n" + "=" * 70)
    print("DOMAIN-SPECIFIC COHERENCE ANALYSIS")
    print("=" * 70)

    domain_results = {}

    # Global metrics for comparison
    global_mae = np.mean(np.abs(loo_probs - y))
    global_brier = np.mean((loo_probs - y) ** 2)
    global_acc = np.mean((loo_probs >= 0.5).astype(int) == y)

    print(f"\n  Global metrics (LOOCV):")
    print(f"    MAE = {global_mae:.4f}, Brier = {global_brier:.4f}, "
          f"Accuracy = {global_acc*100:.1f}%")

    print(f"\n  {'Cluster':<22} {'N':>4} {'Obs%':>6} {'MAE':>7} {'Brier':>7} "
          f"{'Acc%':>6} {'vs Global':>10}")
    print("  " + "-" * 70)

    for cluster in sorted(df['concept_cluster'].unique()):
        mask = df['concept_cluster'] == cluster
        y_c = y[mask]
        p_c = loo_probs[mask]
        n_c = len(y_c)

        if n_c < 5:
            continue

        obs_rate = y_c.mean()
        mae_c = np.mean(np.abs(p_c - y_c))
        brier_c = np.mean((p_c - y_c) ** 2)
        acc_c = np.mean((p_c >= 0.5).astype(int) == y_c)

        # Relative to global: positive means less coherent
        mae_diff = mae_c - global_mae

        label = "LESS coherent" if mae_diff > 0.05 else \
                "MORE coherent" if mae_diff < -0.05 else "~Global"

        print(f"  {cluster:<22} {n_c:>4} {obs_rate*100:>5.1f}% {mae_c:>7.4f} "
              f"{brier_c:>7.4f} {acc_c*100:>5.1f}% {label:>10}")

        domain_results[cluster] = {
            'n': int(n_c),
            'observed_pro_ds_rate': float(obs_rate),
            'mae': float(mae_c),
            'brier': float(brier_c),
            'accuracy': float(acc_c),
            'mae_vs_global': float(mae_diff)
        }

    # Identify least and most coherent domains
    if domain_results:
        sorted_domains = sorted(domain_results.items(), key=lambda x: x[1]['mae'])
        print(f"\n  Most coherent domain:  {sorted_domains[0][0]} "
              f"(MAE={sorted_domains[0][1]['mae']:.4f})")
        print(f"  Least coherent domain: {sorted_domains[-1][0]} "
              f"(MAE={sorted_domains[-1][1]['mae']:.4f})")

    return domain_results


# =============================================================================
# SECTION 7: WITHIN-CASE COHERENCE
# =============================================================================

def within_case_coherence(df, loo_probs):
    """
    Analyze within-case direction consistency.

    When a case has multiple holdings, do they go the same direction?
    Cases with mixed directions within a single judgment reveal doctrinal
    tension within a single judicial decision.
    """
    y = df['pro_ds'].values

    print("\n" + "=" * 70)
    print("WITHIN-CASE COHERENCE ANALYSIS")
    print("=" * 70)

    # Group by case
    case_stats = []
    for case_id, group in df.groupby('case_id'):
        n_holdings = len(group)
        if n_holdings < 2:
            continue

        directions = group['ruling_direction'].values
        pro_ds_count = (group['pro_ds'] == 1).sum()
        non_pro_ds_count = n_holdings - pro_ds_count
        is_unanimous = (pro_ds_count == 0) or (pro_ds_count == n_holdings)

        # Direction entropy (0 = all same direction, 1 = perfectly split)
        p_pro = pro_ds_count / n_holdings
        if p_pro == 0 or p_pro == 1:
            entropy = 0
        else:
            entropy = -(p_pro * np.log2(p_pro) + (1 - p_pro) * np.log2(1 - p_pro))

        # Prediction spread: range of LOOCV predictions within case
        case_mask = df['case_id'] == case_id
        case_probs = loo_probs[case_mask]
        pred_spread = case_probs.max() - case_probs.min()

        # Unique directions
        unique_dirs = group['ruling_direction'].unique()

        case_stats.append({
            'case_id': case_id,
            'n_holdings': n_holdings,
            'pro_ds_count': pro_ds_count,
            'non_pro_ds_count': non_pro_ds_count,
            'is_unanimous': is_unanimous,
            'entropy': entropy,
            'pred_spread': pred_spread,
            'unique_directions': list(unique_dirs),
            'chamber': group['chamber'].iloc[0],
            'year': group['year'].iloc[0]
        })

    case_df = pd.DataFrame(case_stats)

    n_multi = len(case_df)
    n_unanimous = case_df['is_unanimous'].sum()
    n_split = n_multi - n_unanimous

    print(f"\n  Cases with multiple holdings: {n_multi}")
    print(f"    Unanimous (all same direction): {n_unanimous} ({n_unanimous/n_multi*100:.1f}%)")
    print(f"    Split (mixed directions):       {n_split} ({n_split/n_multi*100:.1f}%)")

    if n_split > 0:
        print(f"\n  Split cases (internal doctrinal tension):")
        split_cases = case_df[~case_df['is_unanimous']].sort_values('entropy', ascending=False)

        for _, row in split_cases.iterrows():
            dir_str = ', '.join(row['unique_directions'])
            print(f"    {row['case_id']}: {row['n_holdings']} holdings "
                  f"({row['pro_ds_count']} pro-DS, {row['non_pro_ds_count']} other) "
                  f"| entropy={row['entropy']:.2f} | pred_spread={row['pred_spread']:.3f}")

    # Mean prediction spread
    print(f"\n  Mean prediction spread within cases:")
    print(f"    Unanimous cases: {case_df[case_df['is_unanimous']]['pred_spread'].mean():.3f}")
    if n_split > 0:
        print(f"    Split cases:     {case_df[~case_df['is_unanimous']]['pred_spread'].mean():.3f}")

    return case_df


# =============================================================================
# SECTION 8: TEMPORAL COHERENCE
# =============================================================================

def temporal_coherence(df, loo_probs):
    """
    Is the model's prediction error changing over time?

    Decreasing error = the Court is becoming more predictable/coherent.
    Increasing error = the jurisprudence may be fragmenting.
    """
    y = df['pro_ds'].values

    print("\n" + "=" * 70)
    print("TEMPORAL COHERENCE ANALYSIS")
    print("=" * 70)

    # Prediction error by year
    df_temp = pd.DataFrame({
        'year': df['year'].values,
        'abs_error': np.abs(loo_probs - y),
        'squared_error': (loo_probs - y) ** 2,
        'actual': y,
        'predicted': loo_probs
    })

    year_stats = df_temp.groupby('year').agg(
        n=('actual', 'count'),
        obs_pro_ds=('actual', 'mean'),
        mean_pred=('predicted', 'mean'),
        mae=('abs_error', 'mean'),
        brier=('squared_error', 'mean'),
        accuracy=('actual', lambda x: np.mean(
            (df_temp.loc[x.index, 'predicted'] >= 0.5).astype(int).values == x.values))
    ).reset_index()

    print(f"\n  {'Year':>6} {'N':>4} {'Obs%':>6} {'Pred%':>6} {'MAE':>7} {'Brier':>7} {'Acc%':>6}")
    print("  " + "-" * 50)

    for _, row in year_stats.iterrows():
        print(f"  {row['year']:>6.0f} {row['n']:>4.0f} {row['obs_pro_ds']*100:>5.1f}% "
              f"{row['mean_pred']*100:>5.1f}% {row['mae']:>7.4f} {row['brier']:>7.4f} "
              f"{row['accuracy']*100:>5.1f}%")

    # Trend test: Spearman correlation between year and absolute error
    rho, p_val = stats.spearmanr(df_temp['year'], df_temp['abs_error'])
    print(f"\n  Temporal trend in prediction error:")
    print(f"    Spearman ρ(year, |error|) = {rho:.3f}, p = {p_val:.4f}")

    if p_val < 0.05:
        direction = "increasing" if rho > 0 else "decreasing"
        print(f"    Significant: prediction error is {direction} over time")
    else:
        print(f"    Not significant: no evidence of temporal trend in coherence")

    return year_stats, rho, p_val


# =============================================================================
# SECTION 9: BOOTSTRAP STABILITY OF FLAGS
# =============================================================================

def bootstrap_flag_stability(df, n_boot=500, threshold=0.70):
    """
    Test whether the same holdings are flagged across bootstrap resamples.

    For each bootstrap sample, refits the model and identifies flagged holdings.
    Holdings flagged in >50% of resamples are "stably incoherent."
    """
    formula = ("pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) + "
               "pro_ds_purpose + level_shifting + any_balancing")
    y = df['pro_ds'].values
    n = len(df)

    print("\n" + "=" * 70)
    print(f"BOOTSTRAP STABILITY ANALYSIS (B={n_boot}, threshold={threshold})")
    print("=" * 70)

    flag_counts_a = np.zeros(n)  # Type A flag count
    flag_counts_b = np.zeros(n)  # Type B flag count
    valid_boots = 0

    for b in range(n_boot):
        # Bootstrap resample (with replacement)
        boot_idx = np.random.choice(n, size=n, replace=True)
        boot_df = df.iloc[boot_idx].copy()

        try:
            model = smf.logit(formula, data=boot_df).fit(disp=0, maxiter=100)
            if not model.mle_retvals['converged']:
                continue

            # Predict on ORIGINAL (not bootstrap) data
            probs = model.predict(df)
            valid_boots += 1

            # Flag
            type_a = (probs >= threshold) & (y == 0)
            type_b = (probs <= (1 - threshold)) & (y == 1)
            flag_counts_a += type_a.astype(int)
            flag_counts_b += type_b.astype(int)

        except Exception:
            continue

    if valid_boots == 0:
        print("  ERROR: No valid bootstrap models. Skipping stability analysis.")
        return {}

    # Normalize by number of valid bootstrap runs
    flag_rates_a = flag_counts_a / valid_boots
    flag_rates_b = flag_counts_b / valid_boots

    print(f"  Valid bootstrap models: {valid_boots}/{n_boot}")

    # Stably flagged: flagged in >50% of bootstrap resamples
    stable_a = np.where(flag_rates_a > 0.50)[0]
    stable_b = np.where(flag_rates_b > 0.50)[0]

    print(f"\n  Type A (expected pro-DS, got other):")
    print(f"    Stably flagged (>50% of resamples): {len(stable_a)} holdings")

    if len(stable_a) > 0:
        for idx in stable_a:
            row = df.iloc[idx]
            print(f"      {row['case_id']} H{row['holding_id']}: flagged in "
                  f"{flag_rates_a[idx]*100:.0f}% of resamples "
                  f"({row['ruling_direction']}, {row['primary_concept']})")

    print(f"\n  Type B (expected other, got pro-DS):")
    print(f"    Stably flagged (>50% of resamples): {len(stable_b)} holdings")

    if len(stable_b) > 0:
        for idx in stable_b:
            row = df.iloc[idx]
            print(f"      {row['case_id']} H{row['holding_id']}: flagged in "
                  f"{flag_rates_b[idx]*100:.0f}% of resamples "
                  f"({row['ruling_direction']}, {row['primary_concept']})")

    stability_results = {
        'valid_bootstraps': valid_boots,
        'stable_type_a': [
            {
                'index': int(idx),
                'case_id': df.iloc[idx]['case_id'],
                'holding_id': int(df.iloc[idx]['holding_id']),
                'flag_rate': float(flag_rates_a[idx]),
                'ruling_direction': df.iloc[idx]['ruling_direction'],
                'primary_concept': df.iloc[idx]['primary_concept']
            }
            for idx in stable_a
        ],
        'stable_type_b': [
            {
                'index': int(idx),
                'case_id': df.iloc[idx]['case_id'],
                'holding_id': int(df.iloc[idx]['holding_id']),
                'flag_rate': float(flag_rates_b[idx]),
                'ruling_direction': df.iloc[idx]['ruling_direction'],
                'primary_concept': df.iloc[idx]['primary_concept']
            }
            for idx in stable_b
        ],
        'all_flag_rates_a': flag_rates_a.tolist(),
        'all_flag_rates_b': flag_rates_b.tolist()
    }

    return stability_results


# =============================================================================
# SECTION 10: SENSITIVITY ANALYSES
# =============================================================================

def sensitivity_analyses(df, loo_probs):
    """
    Re-run key coherence metrics under alternative specifications.

    1. Excluding compensation holdings (the known outlier domain)
    2. Using inverse-holding weights (addressing within-case clustering)
    """
    y = df['pro_ds'].values

    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSES")
    print("=" * 70)

    formula = ("pro_ds ~ C(dominant_source, Treatment(reference='SEMANTIC')) + "
               "pro_ds_purpose + level_shifting + any_balancing")

    sensitivity_results = {}

    # --- Sensitivity 1: Exclude compensation ---
    print("\n  SENSITIVITY 1: Excluding Compensation Holdings")
    print("  " + "-" * 50)

    df_nocomp = df[df['is_compensation'] == 0].copy()
    y_nc = df_nocomp['pro_ds'].values
    n_nc = len(df_nocomp)

    # LOOCV on non-compensation subset
    loo_nc = np.zeros(n_nc)
    for i in range(n_nc):
        train = df_nocomp.drop(df_nocomp.index[i])
        test = df_nocomp.iloc[[i]]
        try:
            model = smf.logit(formula, data=train).fit(disp=0, maxiter=100)
            loo_nc[i] = model.predict(test).values[0]
        except Exception:
            loo_nc[i] = train['pro_ds'].mean()

    mae_nc = np.mean(np.abs(loo_nc - y_nc))
    brier_nc = np.mean((loo_nc - y_nc) ** 2)
    acc_nc = np.mean((loo_nc >= 0.5).astype(int) == y_nc)
    auc_nc = compute_auc(y_nc, loo_nc)

    # Compare to full
    mae_full = np.mean(np.abs(loo_probs - y))
    brier_full = np.mean((loo_probs - y) ** 2)

    print(f"    N = {n_nc} (excluded {len(df) - n_nc} compensation holdings)")
    print(f"    Base rate: {y_nc.mean()*100:.1f}% pro-DS")
    print(f"    MAE:   {mae_nc:.4f} (full: {mae_full:.4f})")
    print(f"    Brier: {brier_nc:.4f} (full: {brier_full:.4f})")
    print(f"    Acc:   {acc_nc*100:.1f}% (base: {y_nc.mean()*100:.1f}%)")
    print(f"    AUC:   {auc_nc:.4f}")

    if mae_nc < mae_full:
        print(f"    → Excluding compensation IMPROVES prediction "
              f"(MAE delta = {mae_full - mae_nc:.4f})")
    else:
        print(f"    → Excluding compensation does NOT improve prediction")

    sensitivity_results['excl_compensation'] = {
        'n': int(n_nc),
        'base_rate': float(y_nc.mean()),
        'mae': float(mae_nc),
        'brier': float(brier_nc),
        'accuracy': float(acc_nc),
        'auc': float(auc_nc)
    }

    # --- Sensitivity 2: Inverse-holding weighted model ---
    print("\n  SENSITIVITY 2: Inverse-Holding Weighted Analysis")
    print("  " + "-" * 50)

    try:
        model_wt = smf.logit(formula, data=df).fit(
            disp=0, freq_weights=df['inverse_weight'].values)

        probs_wt = model_wt.predict(df)
        mae_wt = np.mean(np.abs(probs_wt - y))
        brier_wt = np.mean((probs_wt - y) ** 2)
        acc_wt = np.mean((probs_wt >= 0.5).astype(int) == y)

        print(f"    Pseudo-R² (weighted): {model_wt.prsquared:.4f}")
        print(f"    MAE (weighted, in-sample): {mae_wt:.4f} (unweighted: {mae_full:.4f})")
        print(f"    Brier (weighted): {brier_wt:.4f}")
        print(f"    Accuracy: {acc_wt*100:.1f}%")

        # Check if key predictors remain significant
        print(f"\n    Key predictor stability (weighted model):")
        for var in model_wt.params.index:
            if var == 'Intercept':
                continue
            p = model_wt.pvalues[var]
            or_val = np.exp(model_wt.params[var])
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
            print(f"      {var}: OR={or_val:.3f}, p={p:.4f} ({sig})")

        sensitivity_results['inverse_weighted'] = {
            'pseudo_r2': float(model_wt.prsquared),
            'mae': float(mae_wt),
            'brier': float(brier_wt),
            'accuracy': float(acc_wt)
        }

    except Exception as e:
        print(f"    Error in weighted analysis: {e}")
        sensitivity_results['inverse_weighted'] = {'error': str(e)}

    return sensitivity_results


# =============================================================================
# SECTION 11: COHERENCE SCORE SUMMARY
# =============================================================================

def compute_coherence_scores(df, loo_probs, metrics, domain_results,
                              case_df, temporal_rho, stability_results):
    """
    Compute summary coherence scores for the jurisprudence.

    Uses LOOCV accuracy minus base rate as the core operational definition:
    "How much better than chance does the coding scheme predict outcomes?"
    """
    y = df['pro_ds'].values
    base_rate = y.mean()

    print("\n" + "=" * 70)
    print("COHERENCE SCORE SUMMARY")
    print("=" * 70)

    loo_metrics = metrics['LOOCV']

    # 1. Predictive coherence: LOOCV Brier skill score
    brier_skill = loo_metrics['brier_skill']

    # 2. Discriminative coherence: AUC improvement over 0.5
    auc_improvement = loo_metrics['auc_roc'] - 0.5

    # 3. Classification coherence: accuracy improvement over base rate
    acc_improvement = loo_metrics['accuracy_improvement']

    # 4. Within-case coherence: proportion of unanimous multi-holding cases
    if case_df is not None and len(case_df) > 0:
        unanimity_rate = case_df['is_unanimous'].mean()
    else:
        unanimity_rate = np.nan

    # 5. Temporal stability: inverse of |temporal correlation|
    temporal_stability = 1 - abs(temporal_rho) if not np.isnan(temporal_rho) else np.nan

    # 6. Flag stability: proportion of stably flagged holdings
    n_stable = (len(stability_results.get('stable_type_a', [])) +
                len(stability_results.get('stable_type_b', [])))
    stable_incoherence_rate = n_stable / len(df)

    scores = {
        'predictive_coherence': {
            'metric': 'Brier Skill Score',
            'value': float(brier_skill),
            'interpretation': 'Improvement in prediction over naive base rate model'
        },
        'discriminative_coherence': {
            'metric': 'AUC - 0.5',
            'value': float(auc_improvement),
            'interpretation': 'Improvement in discrimination over random'
        },
        'classification_coherence': {
            'metric': 'Accuracy - Base Rate',
            'value': float(acc_improvement),
            'interpretation': 'Additional holdings correctly classified beyond base rate'
        },
        'within_case_coherence': {
            'metric': 'Unanimity Rate',
            'value': float(unanimity_rate) if not np.isnan(unanimity_rate) else None,
            'interpretation': 'Proportion of multi-holding cases with consistent direction'
        },
        'temporal_stability': {
            'metric': '1 - |ρ(year, error)|',
            'value': float(temporal_stability) if not np.isnan(temporal_stability) else None,
            'interpretation': 'Stability of prediction error over time (1 = perfectly stable)'
        },
        'stable_incoherence_rate': {
            'metric': 'Stably flagged holdings / N',
            'value': float(stable_incoherence_rate),
            'interpretation': 'Proportion of holdings robustly flagged as unexplained'
        }
    }

    print(f"\n  {'Dimension':<30} {'Metric':<30} {'Value':>8}")
    print("  " + "-" * 72)
    for dim, data in scores.items():
        val = data['value']
        val_str = f"{val:.4f}" if val is not None else "N/A"
        print(f"  {dim:<30} {data['metric']:<30} {val_str:>8}")

    # Domain-level scores
    print(f"\n  Domain-Specific Coherence (MAE, lower = more coherent):")
    if domain_results:
        for cluster, data in sorted(domain_results.items(), key=lambda x: x[1]['mae']):
            print(f"    {cluster:<22} MAE={data['mae']:.4f} "
                  f"(N={data['n']}, obs={data['observed_pro_ds_rate']*100:.0f}% pro-DS)")

    # Overall assessment
    print(f"\n  OVERALL ASSESSMENT:")
    print(f"  {'='*60}")

    if brier_skill > 0.15 and auc_improvement > 0.15:
        print(f"  The CJEU's GDPR jurisprudence shows MODERATE-TO-GOOD predictive")
        print(f"  coherence: the coded legal variables explain a meaningful share of")
        print(f"  variance in ruling direction (BSS={brier_skill:.3f}, AUC={loo_metrics['auc_roc']:.3f}).")
    elif brier_skill > 0.05:
        print(f"  The CJEU's GDPR jurisprudence shows MODEST predictive coherence:")
        print(f"  the coded variables explain some variance but substantial residual")
        print(f"  variation remains (BSS={brier_skill:.3f}, AUC={loo_metrics['auc_roc']:.3f}).")
    else:
        print(f"  The CJEU's GDPR jurisprudence shows LIMITED predictive coherence:")
        print(f"  the coded variables struggle to predict outcomes beyond base rate")
        print(f"  (BSS={brier_skill:.3f}, AUC={loo_metrics['auc_roc']:.3f}).")

    if stable_incoherence_rate < 0.05:
        print(f"  Very few holdings ({n_stable}) are robustly unexplained, suggesting")
        print(f"  high consistency despite moderate predictive power.")
    elif stable_incoherence_rate < 0.15:
        print(f"  A modest number of holdings ({n_stable}) are robustly unexplained,")
        print(f"  concentrated in identifiable doctrinal domains.")
    else:
        print(f"  A substantial number of holdings ({n_stable}) resist explanation")
        print(f"  by the coded variables, suggesting structural coherence gaps.")

    if unanimity_rate and unanimity_rate > 0.7:
        print(f"  Within-case coherence is strong ({unanimity_rate*100:.0f}% unanimity),")
        print(f"  indicating the Court is internally consistent within decisions.")

    return scores


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run the complete coherence analysis pipeline."""

    print("=" * 70)
    print("DIRECTION-PREDICTION COHERENCE ANALYSIS")
    print("CJEU GDPR Holdings (N=181)")
    print("=" * 70)

    np.random.seed(42)

    # 1. Load data
    df = load_data()

    # 2. Fit models
    parsimonious_model = fit_parsimonious_model(df)
    full_model = fit_full_model(df)

    # 3. LOOCV predictions
    loo_probs = loocv_predictions(df)

    # 4. Model performance and calibration
    in_sample_probs = parsimonious_model.predict(df)
    metrics = compute_performance_metrics(df, in_sample_probs, loo_probs)
    cal_table, mean_cal_error = calibration_analysis(df, loo_probs)

    # 5. Residuals
    residuals = compute_residuals(df, parsimonious_model, loo_probs)

    # 6. Incoherence flagging
    flags = flag_incoherence(df, loo_probs, thresholds=(0.65, 0.70, 0.75))

    # 7. Pattern analysis
    pattern_results = analyze_incoherence_patterns(df, loo_probs, flags, threshold=0.70)

    # 8. Qualitative deep dive
    deep_dive = qualitative_deep_dive(df, loo_probs, flags, threshold=0.70)

    # 9. Domain-specific coherence
    domain_results = domain_coherence_analysis(df, loo_probs)

    # 10. Within-case coherence
    case_df = within_case_coherence(df, loo_probs)

    # 11. Temporal coherence
    year_stats, temporal_rho, temporal_p = temporal_coherence(df, loo_probs)

    # 12. Bootstrap stability
    stability_results = bootstrap_flag_stability(df, n_boot=500, threshold=0.70)

    # 13. Sensitivity analyses
    sensitivity_results = sensitivity_analyses(df, loo_probs)

    # 14. Coherence score summary
    scores = compute_coherence_scores(
        df, loo_probs, metrics, domain_results,
        case_df, temporal_rho, stability_results
    )

    # ==========================================================================
    # SAVE ALL RESULTS
    # ==========================================================================
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Per-holding residual data
    residual_df = df[['case_id', 'holding_id', 'ruling_direction', 'pro_ds',
                       'primary_concept', 'concept_cluster', 'chamber',
                       'chamber_grouped', 'core_holding',
                       'direction_justification']].copy()
    residual_df['p_hat_insample'] = residuals['p_hat_insample']
    residual_df['p_hat_loo'] = residuals['p_hat_loo']
    residual_df['pearson_resid'] = residuals['pearson_resid']
    residual_df['deviance_resid'] = residuals['deviance_resid']
    residual_df['loo_surprise'] = residuals['loo_surprise']
    residual_df['loo_error'] = residuals['loo_error']
    residual_df['cooks_d'] = residuals['cooks_d']
    residual_df.to_csv(OUTPUT_PATH / "holding_residuals.csv", index=False)

    # Comprehensive JSON results
    all_results = {
        'model_info': {
            'formula': ("pro_ds ~ C(dominant_source) + pro_ds_purpose + "
                        "level_shifting + any_balancing"),
            'n': int(parsimonious_model.nobs),
            'pseudo_r2': float(parsimonious_model.prsquared),
            'aic': float(parsimonious_model.aic),
        },
        'performance': {k: {kk: float(vv) if isinstance(vv, (np.floating, float)) else vv
                            for kk, vv in v.items()}
                        for k, v in metrics.items()},
        'calibration': {
            'mean_error': float(mean_cal_error),
        },
        'flags': {str(k): {
            'type_a_count': len(v['type_a']),
            'type_b_count': len(v['type_b']),
            'total_flagged': len(v['type_a']) + len(v['type_b']),
            'type_a_indices': v['type_a'],
            'type_b_indices': v['type_b']
        } for k, v in flags.items()},
        'patterns': pattern_results,
        'deep_dive': deep_dive,
        'domain_coherence': domain_results,
        'within_case': {
            'n_multi_holding_cases': int(len(case_df)) if case_df is not None else 0,
            'unanimity_rate': float(case_df['is_unanimous'].mean()) if case_df is not None and len(case_df) > 0 else None,
            'split_cases': case_df[~case_df['is_unanimous']]['case_id'].tolist() if case_df is not None and len(case_df) > 0 else []
        },
        'temporal': {
            'spearman_rho': float(temporal_rho),
            'spearman_p': float(temporal_p),
        },
        'bootstrap_stability': {
            'n_stable_type_a': len(stability_results.get('stable_type_a', [])),
            'n_stable_type_b': len(stability_results.get('stable_type_b', [])),
            'stable_type_a': stability_results.get('stable_type_a', []),
            'stable_type_b': stability_results.get('stable_type_b', []),
        },
        'sensitivity': sensitivity_results,
        'coherence_scores': scores,
    }

    with open(OUTPUT_PATH / "coherence_analysis.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {OUTPUT_PATH}")
    print(f"  - holding_residuals.csv  (per-holding residuals and predictions)")
    print(f"  - coherence_analysis.json (comprehensive results)")
    print(f"{'='*70}")

    return all_results


if __name__ == "__main__":
    results = main()
    print("\nCoherence analysis complete!")
