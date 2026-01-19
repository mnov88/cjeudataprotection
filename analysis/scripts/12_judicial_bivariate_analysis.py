#!/usr/bin/env python3
"""
12_judicial_bivariate_analysis.py
==================================
Phase 3: Bivariate Analysis for Judicial Effects

This script:
1. Performs omnibus chi-square tests (rapporteur × outcome, chamber × outcome)
2. Conducts pairwise comparisons (each vs. rest)
3. Applies Benjamini-Hochberg FDR correction
4. Calculates effect sizes (phi, Cramér's V, odds ratios)
5. Uses Fisher's exact test for small cell counts
"""

import json
import csv
import math
from pathlib import Path
from collections import defaultdict
from functools import reduce

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HOLDINGS_JUDICIAL = PROJECT_ROOT / "analysis" / "output" / "holdings_judicial.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

# =============================================================================
# STATISTICAL FUNCTIONS
# =============================================================================

def factorial(n):
    """Calculate factorial."""
    if n <= 1:
        return 1
    return reduce(lambda x, y: x * y, range(2, n + 1))

def comb(n, k):
    """Calculate combination C(n, k)."""
    if k > n or k < 0:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

def fisher_exact_2x2(table):
    """
    Fisher's exact test for 2x2 contingency table.
    table = [[a, b], [c, d]]
    Returns two-tailed p-value.
    """
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d
    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d

    # Calculate probability of observed table
    def hypergeom_pmf(x, M, n, N):
        """Hypergeometric PMF: P(X=x) given M total, n successes in pop, N draws"""
        return comb(n, x) * comb(M - n, N - x) / comb(M, N)

    # Calculate p-value (two-tailed)
    observed_prob = hypergeom_pmf(a, n, col1, row1)

    p_value = 0.0
    for x in range(max(0, row1 - col2), min(row1, col1) + 1):
        prob = hypergeom_pmf(x, n, col1, row1)
        if prob <= observed_prob + 1e-10:  # Small epsilon for floating point
            p_value += prob

    return min(p_value, 1.0)

def chi_square_2x2(table):
    """
    Chi-square test for 2x2 contingency table with Yates correction.
    table = [[a, b], [c, d]]
    Returns chi-square statistic and p-value.
    """
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d

    if n == 0:
        return 0, 1.0

    # Expected values
    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d

    if row1 == 0 or row2 == 0 or col1 == 0 or col2 == 0:
        return 0, 1.0

    e_a = row1 * col1 / n
    e_b = row1 * col2 / n
    e_c = row2 * col1 / n
    e_d = row2 * col2 / n

    # Chi-square with Yates correction
    chi2 = 0
    for obs, exp in [(a, e_a), (b, e_b), (c, e_c), (d, e_d)]:
        if exp > 0:
            chi2 += (abs(obs - exp) - 0.5) ** 2 / exp

    # P-value from chi-square distribution (df=1)
    # Using approximation for chi-square CDF
    p_value = chi_square_pvalue(chi2, 1)

    return chi2, p_value

def chi_square_pvalue(chi2, df):
    """Approximate p-value for chi-square distribution."""
    if chi2 <= 0:
        return 1.0

    # Use Wilson-Hilferty approximation for chi-square
    if df == 1:
        # For df=1, use standard normal approximation
        z = math.sqrt(chi2)
        # Standard normal CDF approximation
        p = 0.5 * math.erfc(z / math.sqrt(2))
        return 2 * p  # Two-tailed

    # General approximation
    x = chi2
    k = df
    # Regularized incomplete gamma function approximation
    if x > k + 10 * math.sqrt(2 * k):
        return 0.0
    elif x < max(0, k - 10 * math.sqrt(2 * k)):
        return 1.0
    else:
        # Simple approximation using normal
        z = ((x / k) ** (1/3) - (1 - 2/(9*k))) / math.sqrt(2/(9*k))
        p = 0.5 * math.erfc(z / math.sqrt(2))
        return p

def chi_square_kxm(contingency_table):
    """
    Chi-square test for k×m contingency table.
    contingency_table = dict of {row_label: {col_label: count}}
    Returns chi-square statistic, df, and p-value.
    """
    # Get all labels
    row_labels = list(contingency_table.keys())
    col_labels = set()
    for row_data in contingency_table.values():
        col_labels.update(row_data.keys())
    col_labels = sorted(col_labels)

    # Build matrix
    matrix = []
    for row in row_labels:
        row_data = [contingency_table[row].get(col, 0) for col in col_labels]
        matrix.append(row_data)

    # Calculate totals
    n_rows = len(matrix)
    n_cols = len(matrix[0]) if matrix else 0
    n = sum(sum(row) for row in matrix)

    if n == 0:
        return 0, (n_rows - 1) * (n_cols - 1), 1.0

    row_totals = [sum(row) for row in matrix]
    col_totals = [sum(matrix[i][j] for i in range(n_rows)) for j in range(n_cols)]

    # Calculate chi-square
    chi2 = 0
    for i in range(n_rows):
        for j in range(n_cols):
            expected = row_totals[i] * col_totals[j] / n
            if expected > 0:
                observed = matrix[i][j]
                chi2 += (observed - expected) ** 2 / expected

    df = (n_rows - 1) * (n_cols - 1)
    p_value = chi_square_pvalue(chi2, df)

    return chi2, df, p_value

def phi_coefficient(table):
    """Calculate phi coefficient for 2x2 table."""
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d

    numerator = a * d - b * c
    denominator = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))

    if denominator == 0:
        return 0

    return numerator / denominator

def cramers_v(contingency_table, chi2, n):
    """Calculate Cramér's V from chi-square statistic."""
    n_rows = len(contingency_table)
    n_cols = len(set().union(*[set(v.keys()) for v in contingency_table.values()]))

    k = min(n_rows - 1, n_cols - 1)
    if k == 0 or n == 0:
        return 0

    return math.sqrt(chi2 / (n * k))

def odds_ratio(table):
    """Calculate odds ratio for 2x2 table with CI."""
    a, b = table[0]
    c, d = table[1]

    # Add 0.5 to avoid division by zero
    if a == 0 or b == 0 or c == 0 or d == 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5

    or_val = (a * d) / (b * c)

    # Log odds ratio SE
    se_log_or = math.sqrt(1/a + 1/b + 1/c + 1/d)

    # 95% CI
    log_or = math.log(or_val)
    ci_low = math.exp(log_or - 1.96 * se_log_or)
    ci_high = math.exp(log_or + 1.96 * se_log_or)

    return or_val, ci_low, ci_high

def benjamini_hochberg(p_values, alpha=0.10):
    """
    Apply Benjamini-Hochberg FDR correction.
    Returns dict of {label: (original_p, adjusted_p, significant)}
    """
    n = len(p_values)
    if n == 0:
        return {}

    # Sort by p-value
    sorted_items = sorted(p_values.items(), key=lambda x: x[1])

    results = {}
    prev_adjusted = 0

    # Process in reverse order for step-up procedure
    adjusted_ps = []
    for i, (label, p) in enumerate(reversed(sorted_items)):
        rank = n - i
        adjusted = min(1.0, p * n / rank)
        adjusted = max(adjusted, prev_adjusted)  # Ensure monotonicity
        prev_adjusted = adjusted
        adjusted_ps.append((label, p, adjusted))

    # Reverse back
    adjusted_ps.reverse()

    for label, original_p, adjusted_p in adjusted_ps:
        results[label] = {
            'p_original': original_p,
            'p_adjusted': adjusted_p,
            'significant': adjusted_p < alpha
        }

    return results

# =============================================================================
# DATA LOADING
# =============================================================================

def load_holdings():
    """Load enhanced holdings data."""
    holdings = []
    with open(HOLDINGS_JUDICIAL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['pro_ds'] = int(row.get('pro_ds', 0))
            holdings.append(row)
    return holdings

# =============================================================================
# OMNIBUS TESTS
# =============================================================================

def omnibus_rapporteur_test(holdings):
    """Test if rapporteur is associated with pro_ds (omnibus chi-square)."""
    print("\n" + "=" * 80)
    print("OMNIBUS TEST: RAPPORTEUR × PRO-DS")
    print("=" * 80)

    # Build contingency table
    contingency = defaultdict(lambda: {'pro_ds': 0, 'other': 0})

    for h in holdings:
        rap = h.get('judge_rapporteur', 'UNKNOWN')
        if rap:
            if h['pro_ds']:
                contingency[rap]['pro_ds'] += 1
            else:
                contingency[rap]['other'] += 1

    # Convert to format for chi-square test
    cont_dict = {k: {'PRO_DS': v['pro_ds'], 'OTHER': v['other']} for k, v in contingency.items()}

    chi2, df, p_value = chi_square_kxm(cont_dict)
    n = sum(v['pro_ds'] + v['other'] for v in contingency.values())
    v = cramers_v(cont_dict, chi2, n)

    print(f"\n  N = {n} holdings, {len(contingency)} rapporteurs")
    print(f"  Chi-square({df}) = {chi2:.2f}")
    print(f"  p-value = {p_value:.4f}")
    print(f"  Cramér's V = {v:.3f}")

    if p_value < 0.05:
        print("\n  *** SIGNIFICANT at α=0.05: Rapporteur is associated with ruling direction")
        print("      Proceed to pairwise comparisons.")
    else:
        print("\n  Not significant at α=0.05: No evidence of rapporteur effect")
        print("      Pairwise comparisons are exploratory only.")

    return {
        'chi2': chi2,
        'df': df,
        'p_value': p_value,
        'cramers_v': v,
        'n': n,
        'significant': p_value < 0.05
    }

def omnibus_chamber_test(holdings):
    """Test if chamber is associated with pro_ds (omnibus chi-square)."""
    print("\n" + "=" * 80)
    print("OMNIBUS TEST: CHAMBER × PRO-DS")
    print("=" * 80)

    # Build contingency table
    contingency = defaultdict(lambda: {'pro_ds': 0, 'other': 0})

    for h in holdings:
        chamber = h.get('chamber', 'UNKNOWN')
        if chamber:
            if h['pro_ds']:
                contingency[chamber]['pro_ds'] += 1
            else:
                contingency[chamber]['other'] += 1

    cont_dict = {k: {'PRO_DS': v['pro_ds'], 'OTHER': v['other']} for k, v in contingency.items()}

    chi2, df, p_value = chi_square_kxm(cont_dict)
    n = sum(v['pro_ds'] + v['other'] for v in contingency.values())
    v = cramers_v(cont_dict, chi2, n)

    print(f"\n  N = {n} holdings, {len(contingency)} chambers")
    print(f"  Chi-square({df}) = {chi2:.2f}")
    print(f"  p-value = {p_value:.4f}")
    print(f"  Cramér's V = {v:.3f}")

    if p_value < 0.05:
        print("\n  *** SIGNIFICANT at α=0.05: Chamber is associated with ruling direction")
        print("      Proceed to pairwise comparisons.")
    else:
        print("\n  Not significant at α=0.05: No evidence of chamber effect")

    return {
        'chi2': chi2,
        'df': df,
        'p_value': p_value,
        'cramers_v': v,
        'n': n,
        'significant': p_value < 0.05
    }

# =============================================================================
# PAIRWISE COMPARISONS
# =============================================================================

def pairwise_rapporteur_tests(holdings, min_holdings=5):
    """Test each rapporteur vs. rest."""
    print("\n" + "=" * 80)
    print("PAIRWISE TESTS: EACH RAPPORTEUR VS. REST")
    print("=" * 80)
    print(f"(Minimum {min_holdings} holdings to include in analysis)")

    # Count by rapporteur
    rap_counts = defaultdict(lambda: {'pro_ds': 0, 'other': 0, 'total': 0})
    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        if rap:
            rap_counts[rap]['total'] += 1
            if h['pro_ds']:
                rap_counts[rap]['pro_ds'] += 1
            else:
                rap_counts[rap]['other'] += 1

    # Filter to those with enough data
    eligible = {k: v for k, v in rap_counts.items() if v['total'] >= min_holdings}

    print(f"\n  {len(eligible)} rapporteurs with ≥{min_holdings} holdings")

    # Overall totals
    total_pro_ds = sum(v['pro_ds'] for v in rap_counts.values())
    total_other = sum(v['other'] for v in rap_counts.values())

    results = {}
    p_values = {}

    for rap, counts in eligible.items():
        # 2x2 table: this rapporteur vs. rest
        a = counts['pro_ds']  # This rap, pro-DS
        b = counts['other']   # This rap, other
        c = total_pro_ds - a  # Other raps, pro-DS
        d = total_other - b   # Other raps, other

        table = [[a, b], [c, d]]

        # Use Fisher's exact for small cells
        min_expected = min(
            (a + b) * (a + c) / (a + b + c + d),
            (a + b) * (b + d) / (a + b + c + d),
            (c + d) * (a + c) / (a + b + c + d),
            (c + d) * (b + d) / (a + b + c + d)
        ) if (a + b + c + d) > 0 else 0

        if min_expected < 5:
            p_value = fisher_exact_2x2(table)
            test_used = 'Fisher'
        else:
            _, p_value = chi_square_2x2(table)
            test_used = 'Chi-sq'

        phi = phi_coefficient(table)
        or_val, or_ci_low, or_ci_high = odds_ratio(table)

        rate_this = a / (a + b) if (a + b) > 0 else 0
        rate_rest = c / (c + d) if (c + d) > 0 else 0

        results[rap] = {
            'n': a + b,
            'pro_ds': a,
            'rate': rate_this,
            'rate_rest': rate_rest,
            'diff': rate_this - rate_rest,
            'test': test_used,
            'p_value': p_value,
            'phi': phi,
            'odds_ratio': or_val,
            'or_ci': (or_ci_low, or_ci_high)
        }
        p_values[rap] = p_value

    # Apply FDR correction
    fdr_results = benjamini_hochberg(p_values, alpha=0.10)

    # Print results
    print(f"\n{'Rapporteur':<22} {'N':>4} {'Rate':>7} {'Rest':>7} {'Diff':>8} {'Test':>7} {'p':>8} {'q':>8} {'Sig':>5} {'OR':>8}")
    print("-" * 100)

    sorted_raps = sorted(results.items(), key=lambda x: -abs(x[1]['diff']))

    for rap, data in sorted_raps:
        fdr = fdr_results.get(rap, {})
        q = fdr.get('p_adjusted', data['p_value'])
        sig = '**' if fdr.get('significant', False) else ('*' if data['p_value'] < 0.05 else '')

        print(f"{rap:<22} {data['n']:>4} {data['rate']:>6.1%} {data['rate_rest']:>6.1%} "
              f"{data['diff']:>+7.1%} {data['test']:>7} {data['p_value']:>8.4f} {q:>8.4f} {sig:>5} "
              f"{data['odds_ratio']:>7.2f}")

    print("-" * 100)
    print("* p < 0.05 (unadjusted), ** q < 0.10 (FDR-adjusted)")

    # Merge FDR results
    for rap in results:
        results[rap]['p_adjusted'] = fdr_results.get(rap, {}).get('p_adjusted', results[rap]['p_value'])
        results[rap]['significant_fdr'] = fdr_results.get(rap, {}).get('significant', False)

    return results

def pairwise_chamber_tests(holdings, min_holdings=5):
    """Test each chamber vs. rest."""
    print("\n" + "=" * 80)
    print("PAIRWISE TESTS: EACH CHAMBER VS. REST")
    print("=" * 80)

    # Count by chamber
    chamber_counts = defaultdict(lambda: {'pro_ds': 0, 'other': 0, 'total': 0})
    for h in holdings:
        chamber = h.get('chamber', '')
        if chamber:
            chamber_counts[chamber]['total'] += 1
            if h['pro_ds']:
                chamber_counts[chamber]['pro_ds'] += 1
            else:
                chamber_counts[chamber]['other'] += 1

    eligible = {k: v for k, v in chamber_counts.items() if v['total'] >= min_holdings}

    print(f"\n  {len(eligible)} chambers with ≥{min_holdings} holdings")

    total_pro_ds = sum(v['pro_ds'] for v in chamber_counts.values())
    total_other = sum(v['other'] for v in chamber_counts.values())

    results = {}
    p_values = {}

    for chamber, counts in eligible.items():
        a = counts['pro_ds']
        b = counts['other']
        c = total_pro_ds - a
        d = total_other - b

        table = [[a, b], [c, d]]

        min_expected = min(
            (a + b) * (a + c) / (a + b + c + d),
            (a + b) * (b + d) / (a + b + c + d),
            (c + d) * (a + c) / (a + b + c + d),
            (c + d) * (b + d) / (a + b + c + d)
        ) if (a + b + c + d) > 0 else 0

        if min_expected < 5:
            p_value = fisher_exact_2x2(table)
            test_used = 'Fisher'
        else:
            _, p_value = chi_square_2x2(table)
            test_used = 'Chi-sq'

        phi = phi_coefficient(table)
        or_val, or_ci_low, or_ci_high = odds_ratio(table)

        rate_this = a / (a + b) if (a + b) > 0 else 0
        rate_rest = c / (c + d) if (c + d) > 0 else 0

        results[chamber] = {
            'n': a + b,
            'pro_ds': a,
            'rate': rate_this,
            'rate_rest': rate_rest,
            'diff': rate_this - rate_rest,
            'test': test_used,
            'p_value': p_value,
            'phi': phi,
            'odds_ratio': or_val,
            'or_ci': (or_ci_low, or_ci_high)
        }
        p_values[chamber] = p_value

    fdr_results = benjamini_hochberg(p_values, alpha=0.10)

    print(f"\n{'Chamber':<18} {'N':>5} {'Rate':>7} {'Rest':>7} {'Diff':>8} {'Test':>7} {'p':>8} {'q':>8} {'Sig':>5} {'OR':>8}")
    print("-" * 95)

    sorted_chambers = sorted(results.items(), key=lambda x: -abs(x[1]['diff']))

    for chamber, data in sorted_chambers:
        fdr = fdr_results.get(chamber, {})
        q = fdr.get('p_adjusted', data['p_value'])
        sig = '**' if fdr.get('significant', False) else ('*' if data['p_value'] < 0.05 else '')

        print(f"{chamber:<18} {data['n']:>5} {data['rate']:>6.1%} {data['rate_rest']:>6.1%} "
              f"{data['diff']:>+7.1%} {data['test']:>7} {data['p_value']:>8.4f} {q:>8.4f} {sig:>5} "
              f"{data['odds_ratio']:>7.2f}")

    print("-" * 95)
    print("* p < 0.05 (unadjusted), ** q < 0.10 (FDR-adjusted)")

    for chamber in results:
        results[chamber]['p_adjusted'] = fdr_results.get(chamber, {}).get('p_adjusted', results[chamber]['p_value'])
        results[chamber]['significant_fdr'] = fdr_results.get(chamber, {}).get('significant', False)

    return results

def pairwise_judge_tests(holdings, min_holdings=10):
    """Test each judge's presence vs. absence."""
    print("\n" + "=" * 80)
    print("PAIRWISE TESTS: JUDGE PRESENCE VS. ABSENCE")
    print("=" * 80)
    print(f"(Minimum {min_holdings} holdings when present)")
    print("NOTE: High network density means these tests are exploratory only.")

    # Get judge columns
    sample = holdings[0] if holdings else {}
    judge_cols = [c for c in sample.keys() if c.startswith('judge_')]

    results = {}
    p_values = {}

    for col in judge_cols:
        present_pro_ds = 0
        present_other = 0
        absent_pro_ds = 0
        absent_other = 0

        for h in holdings:
            try:
                is_present = int(h.get(col, 0))
            except:
                is_present = 0

            if is_present:
                if h['pro_ds']:
                    present_pro_ds += 1
                else:
                    present_other += 1
            else:
                if h['pro_ds']:
                    absent_pro_ds += 1
                else:
                    absent_other += 1

        present_total = present_pro_ds + present_other

        if present_total < min_holdings:
            continue

        table = [[present_pro_ds, present_other], [absent_pro_ds, absent_other]]

        n = present_pro_ds + present_other + absent_pro_ds + absent_other
        min_expected = min(
            (present_pro_ds + present_other) * (present_pro_ds + absent_pro_ds) / n,
            (present_pro_ds + present_other) * (present_other + absent_other) / n,
            (absent_pro_ds + absent_other) * (present_pro_ds + absent_pro_ds) / n,
            (absent_pro_ds + absent_other) * (present_other + absent_other) / n
        ) if n > 0 else 0

        if min_expected < 5:
            p_value = fisher_exact_2x2(table)
            test_used = 'Fisher'
        else:
            _, p_value = chi_square_2x2(table)
            test_used = 'Chi-sq'

        phi = phi_coefficient(table)
        or_val, or_ci_low, or_ci_high = odds_ratio(table)

        rate_present = present_pro_ds / present_total if present_total > 0 else 0
        absent_total = absent_pro_ds + absent_other
        rate_absent = absent_pro_ds / absent_total if absent_total > 0 else 0

        results[col] = {
            'n_present': present_total,
            'n_absent': absent_total,
            'rate_present': rate_present,
            'rate_absent': rate_absent,
            'diff': rate_present - rate_absent,
            'test': test_used,
            'p_value': p_value,
            'phi': phi,
            'odds_ratio': or_val,
            'or_ci': (or_ci_low, or_ci_high)
        }
        p_values[col] = p_value

    fdr_results = benjamini_hochberg(p_values, alpha=0.10)

    # Print top results (sorted by absolute difference)
    print(f"\n{'Judge':<28} {'Pres':>5} {'Abs':>5} {'P.Rate':>7} {'A.Rate':>7} {'Diff':>8} {'p':>8} {'q':>8} {'Sig':>5}")
    print("-" * 95)

    sorted_judges = sorted(results.items(), key=lambda x: -abs(x[1]['diff']))[:20]

    for judge_col, data in sorted_judges:
        judge_name = judge_col.replace('judge_', '').replace('_', ' ')[:26]
        fdr = fdr_results.get(judge_col, {})
        q = fdr.get('p_adjusted', data['p_value'])
        sig = '**' if fdr.get('significant', False) else ('*' if data['p_value'] < 0.05 else '')

        print(f"{judge_name:<28} {data['n_present']:>5} {data['n_absent']:>5} "
              f"{data['rate_present']:>6.1%} {data['rate_absent']:>6.1%} "
              f"{data['diff']:>+7.1%} {data['p_value']:>8.4f} {q:>8.4f} {sig:>5}")

    print("-" * 95)
    print(f"(Showing top 20 of {len(results)} judges by |difference|)")
    print("* p < 0.05 (unadjusted), ** q < 0.10 (FDR-adjusted)")

    # Count significant
    n_sig_unadj = sum(1 for d in results.values() if d['p_value'] < 0.05)
    n_sig_fdr = sum(1 for j in results if fdr_results.get(j, {}).get('significant', False))

    print(f"\n  Significant at p < 0.05 (unadjusted): {n_sig_unadj}")
    print(f"  Significant at q < 0.10 (FDR-adjusted): {n_sig_fdr}")

    for judge in results:
        results[judge]['p_adjusted'] = fdr_results.get(judge, {}).get('p_adjusted', results[judge]['p_value'])
        results[judge]['significant_fdr'] = fdr_results.get(judge, {}).get('significant', False)

    return results

# =============================================================================
# SUMMARY
# =============================================================================

def print_summary(omnibus_rap, omnibus_chamber, pairwise_rap, pairwise_chamber, pairwise_judge):
    """Print summary of all bivariate findings."""
    print("\n" + "=" * 80)
    print("BIVARIATE ANALYSIS SUMMARY")
    print("=" * 80)

    print("\n1. OMNIBUS TESTS:")
    print(f"   Rapporteur × Pro-DS: χ²({omnibus_rap['df']}) = {omnibus_rap['chi2']:.2f}, "
          f"p = {omnibus_rap['p_value']:.4f}, V = {omnibus_rap['cramers_v']:.3f}")
    print(f"   → {'SIGNIFICANT' if omnibus_rap['significant'] else 'Not significant'}")

    print(f"\n   Chamber × Pro-DS: χ²({omnibus_chamber['df']}) = {omnibus_chamber['chi2']:.2f}, "
          f"p = {omnibus_chamber['p_value']:.4f}, V = {omnibus_chamber['cramers_v']:.3f}")
    print(f"   → {'SIGNIFICANT' if omnibus_chamber['significant'] else 'Not significant'}")

    print("\n2. SIGNIFICANT RAPPORTEUR EFFECTS (FDR q < 0.10):")
    sig_raps = [(r, d) for r, d in pairwise_rap.items() if d.get('significant_fdr', False)]
    if sig_raps:
        for rap, data in sorted(sig_raps, key=lambda x: x[1]['diff']):
            direction = "MORE pro-DS" if data['diff'] > 0 else "LESS pro-DS"
            print(f"   - {rap}: {direction} by {abs(data['diff']):.1%} (OR = {data['odds_ratio']:.2f}, q = {data['p_adjusted']:.4f})")
    else:
        print("   None after FDR correction")
        # Show marginally significant
        marginal = [(r, d) for r, d in pairwise_rap.items() if d['p_value'] < 0.05]
        if marginal:
            print("   Marginally significant (p < 0.05, unadjusted):")
            for rap, data in sorted(marginal, key=lambda x: x[1]['diff']):
                direction = "MORE" if data['diff'] > 0 else "LESS"
                print(f"     - {rap}: {direction} by {abs(data['diff']):.1%} (p = {data['p_value']:.4f})")

    print("\n3. SIGNIFICANT CHAMBER EFFECTS (FDR q < 0.10):")
    sig_chambers = [(c, d) for c, d in pairwise_chamber.items() if d.get('significant_fdr', False)]
    if sig_chambers:
        for chamber, data in sorted(sig_chambers, key=lambda x: x[1]['diff']):
            direction = "MORE pro-DS" if data['diff'] > 0 else "LESS pro-DS"
            print(f"   - {chamber}: {direction} by {abs(data['diff']):.1%} (OR = {data['odds_ratio']:.2f}, q = {data['p_adjusted']:.4f})")
    else:
        print("   None after FDR correction")
        marginal = [(c, d) for c, d in pairwise_chamber.items() if d['p_value'] < 0.05]
        if marginal:
            print("   Marginally significant (p < 0.05, unadjusted):")
            for chamber, data in sorted(marginal, key=lambda x: x[1]['diff']):
                direction = "MORE" if data['diff'] > 0 else "LESS"
                print(f"     - {chamber}: {direction} by {abs(data['diff']):.1%} (p = {data['p_value']:.4f})")

    print("\n4. INDIVIDUAL JUDGE EFFECTS:")
    sig_judges = [(j, d) for j, d in pairwise_judge.items() if d.get('significant_fdr', False)]
    print(f"   Judges tested: {len(pairwise_judge)}")
    print(f"   Significant (FDR q < 0.10): {len(sig_judges)}")
    if sig_judges:
        print("   Notable judges:")
        for judge, data in sorted(sig_judges, key=lambda x: -abs(x[1]['diff']))[:5]:
            judge_name = judge.replace('judge_', '').replace('_', ' ')
            direction = "MORE" if data['diff'] > 0 else "LESS"
            print(f"     - {judge_name}: {direction} by {abs(data['diff']):.1%}")
    print("   ⚠ CAUTION: Individual judge effects heavily confounded by co-occurrence")

# =============================================================================
# SAVE RESULTS
# =============================================================================

def save_results(omnibus_rap, omnibus_chamber, pairwise_rap, pairwise_chamber, pairwise_judge):
    """Save all bivariate analysis results."""
    results = {
        'omnibus_tests': {
            'rapporteur': omnibus_rap,
            'chamber': omnibus_chamber
        },
        'pairwise_tests': {
            'rapporteur': pairwise_rap,
            'chamber': pairwise_chamber,
            'judge': pairwise_judge
        },
        'metadata': {
            'fdr_alpha': 0.10,
            'min_holdings_rapporteur': 5,
            'min_holdings_chamber': 5,
            'min_holdings_judge': 10
        }
    }

    with open(OUTPUT_PATH / "bivariate_judicial_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {OUTPUT_PATH / 'bivariate_judicial_analysis.json'}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Loading data...")
    holdings = load_holdings()
    print(f"Loaded {len(holdings)} holdings")

    print("\n" + "=" * 80)
    print("PHASE 3: BIVARIATE ANALYSIS FOR JUDICIAL EFFECTS")
    print("=" * 80)

    # Omnibus tests
    omnibus_rap = omnibus_rapporteur_test(holdings)
    omnibus_chamber = omnibus_chamber_test(holdings)

    # Pairwise tests
    pairwise_rap = pairwise_rapporteur_tests(holdings, min_holdings=5)
    pairwise_chamber = pairwise_chamber_tests(holdings, min_holdings=5)
    pairwise_judge = pairwise_judge_tests(holdings, min_holdings=10)

    # Summary
    print_summary(omnibus_rap, omnibus_chamber, pairwise_rap, pairwise_chamber, pairwise_judge)

    # Save results
    save_results(omnibus_rap, omnibus_chamber, pairwise_rap, pairwise_chamber, pairwise_judge)

    print("\n" + "=" * 80)
    print("PHASE 3 COMPLETE: Bivariate analysis finished!")
    print("=" * 80)

    return {
        'omnibus_rapporteur': omnibus_rap,
        'omnibus_chamber': omnibus_chamber,
        'pairwise_rapporteur': pairwise_rap,
        'pairwise_chamber': pairwise_chamber,
        'pairwise_judge': pairwise_judge
    }

if __name__ == "__main__":
    results = main()
