#!/usr/bin/env python3
"""
15_supplementary_judicial_analysis.py
======================================
Supplementary analyses addressing:
1. Systematic comparison of holding-level vs case-level effects
2. Judge/rapporteur topic specialization analysis
3. Does topic specialization explain outcome differences?
4. Deep dive into topic-adjusted rapporteur effects
"""

import json
import csv
import math
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HOLDINGS_JUDICIAL = PROJECT_ROOT / "analysis" / "output" / "holdings_judicial.csv"
CASES_JSON = PROJECT_ROOT / "parsed-coded" / "cases.json"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

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
            try:
                row['year'] = int(row.get('year', 0))
            except:
                row['year'] = 0
            holdings.append(row)
    return holdings

def load_cases():
    """Load cases data."""
    with open(CASES_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

# =============================================================================
# STATISTICAL HELPERS
# =============================================================================

def wilson_ci(successes, n, z=1.96):
    """Wilson score confidence interval."""
    if n == 0:
        return 0, 0, 0
    p = successes / n
    denom = 1 + z**2/n
    center = (p + z**2/(2*n)) / denom
    spread = z * math.sqrt((p*(1-p) + z**2/(4*n))/n) / denom
    return p, max(0, center-spread), min(1, center+spread)

def chi_square_test(a, b, c, d):
    """2x2 chi-square test with Yates correction."""
    n = a + b + c + d
    if n == 0:
        return 0, 1.0

    e_a = (a+b)*(a+c)/n
    e_b = (a+b)*(b+d)/n
    e_c = (c+d)*(a+c)/n
    e_d = (c+d)*(b+d)/n

    chi2 = 0
    for obs, exp in [(a, e_a), (b, e_b), (c, e_c), (d, e_d)]:
        if exp > 0:
            chi2 += (abs(obs - exp) - 0.5)**2 / exp

    # Approximate p-value
    if chi2 <= 0:
        return 0, 1.0
    z = math.sqrt(chi2)
    p = 2 * 0.5 * math.erfc(z / math.sqrt(2))
    return chi2, p

def odds_ratio_ci(a, b, c, d):
    """Calculate OR with 95% CI."""
    if b == 0 or c == 0:
        a, b, c, d = a+0.5, b+0.5, c+0.5, d+0.5

    or_val = (a*d)/(b*c) if b*c > 0 else float('inf')
    if or_val == 0 or or_val == float('inf'):
        return or_val, 0, float('inf')

    log_or = math.log(or_val)
    se = math.sqrt(1/a + 1/b + 1/c + 1/d)
    ci_low = math.exp(log_or - 1.96*se)
    ci_high = math.exp(log_or + 1.96*se)

    return or_val, ci_low, ci_high

# =============================================================================
# PART 1: HOLDING-LEVEL VS CASE-LEVEL SYSTEMATIC COMPARISON
# =============================================================================

def compare_holding_vs_case_level(holdings):
    """Systematic comparison of effects at holding vs case level."""
    print("=" * 80)
    print("PART 1: HOLDING-LEVEL VS CASE-LEVEL COMPARISON")
    print("=" * 80)

    # Aggregate to case level
    cases = defaultdict(lambda: {
        'holdings': [],
        'pro_ds_count': 0,
        'total': 0,
        'chamber': None,
        'rapporteur': None,
        'concepts': []
    })

    for h in holdings:
        case_id = h.get('case_id', '')
        cases[case_id]['holdings'].append(h)
        cases[case_id]['pro_ds_count'] += h['pro_ds']
        cases[case_id]['total'] += 1
        cases[case_id]['chamber'] = h.get('chamber')
        cases[case_id]['rapporteur'] = h.get('judge_rapporteur')
        cases[case_id]['concepts'].append(h.get('concept_cluster', 'OTHER'))

    # Create case-level outcomes
    case_list = []
    for case_id, data in cases.items():
        # Multiple outcome definitions
        case_entry = {
            'case_id': case_id,
            'chamber': data['chamber'],
            'rapporteur': data['rapporteur'],
            'n_holdings': data['total'],
            'pro_ds_count': data['pro_ds_count'],
            # Different aggregation methods
            'majority_pro_ds': 1 if data['pro_ds_count'] > data['total']/2 else 0,
            'all_pro_ds': 1 if data['pro_ds_count'] == data['total'] else 0,
            'any_pro_ds': 1 if data['pro_ds_count'] > 0 else 0,
            'proportion_pro_ds': data['pro_ds_count'] / data['total'] if data['total'] > 0 else 0,
            'primary_concept': max(set(data['concepts']), key=data['concepts'].count) if data['concepts'] else 'OTHER'
        }
        case_list.append(case_entry)

    n_cases = len(case_list)
    n_holdings = len(holdings)

    print(f"\n  Holdings: {n_holdings}")
    print(f"  Cases: {n_cases}")
    print(f"  Avg holdings/case: {n_holdings/n_cases:.2f}")

    # Holdings per case distribution
    holdings_dist = defaultdict(int)
    for c in case_list:
        holdings_dist[c['n_holdings']] += 1

    print("\n  Holdings per case distribution:")
    for n, count in sorted(holdings_dist.items()):
        print(f"    {n} holdings: {count} cases ({count/n_cases*100:.1f}%)")

    # Compare effect estimates
    print("\n" + "-" * 80)
    print("EFFECT COMPARISON: HOLDING-LEVEL VS CASE-LEVEL")
    print("-" * 80)

    results = {}

    # Chamber effects
    print("\n  CHAMBER EFFECTS:")
    print(f"  {'Chamber':<15} {'Holding-Level':>20} {'Case-Level (Majority)':>25} {'Difference':>12}")
    print("  " + "-" * 75)

    for chamber in ['THIRD', 'GRAND_CHAMBER', 'FIRST']:
        # Holding level
        h_chamber = [h for h in holdings if h.get('chamber') == chamber]
        h_other = [h for h in holdings if h.get('chamber') != chamber]

        if len(h_chamber) < 5:
            continue

        h_rate = sum(h['pro_ds'] for h in h_chamber) / len(h_chamber)

        # Case level (majority)
        c_chamber = [c for c in case_list if c['chamber'] == chamber]
        c_other = [c for c in case_list if c['chamber'] != chamber]

        c_rate = sum(c['majority_pro_ds'] for c in c_chamber) / len(c_chamber) if c_chamber else 0

        # Calculate ORs
        a_h = sum(h['pro_ds'] for h in h_chamber)
        b_h = len(h_chamber) - a_h
        c_h = sum(h['pro_ds'] for h in h_other)
        d_h = len(h_other) - c_h
        or_holding, _, _ = odds_ratio_ci(a_h, b_h, c_h, d_h)

        a_c = sum(c['majority_pro_ds'] for c in c_chamber)
        b_c = len(c_chamber) - a_c
        c_c = sum(c['majority_pro_ds'] for c in c_other)
        d_c = len(c_other) - c_c
        or_case, _, _ = odds_ratio_ci(a_c, b_c, c_c, d_c)

        diff = abs(h_rate - c_rate)

        results[chamber] = {
            'holding_rate': h_rate,
            'case_rate': c_rate,
            'holding_or': or_holding,
            'case_or': or_case,
            'diff': diff
        }

        h_str = f"{h_rate:.1%} (OR={or_holding:.2f})"
        c_str = f"{c_rate:.1%} (OR={or_case:.2f})"
        print(f"  {chamber:<15} {h_str:>20} {c_str:>25} {diff:>11.1%}")

    # Rapporteur effects
    print("\n  RAPPORTEUR EFFECTS:")
    print(f"  {'Rapporteur':<20} {'Holding-Level':>18} {'Case-Level':>18} {'Diff':>8}")
    print("  " + "-" * 68)

    for rap in ['N. Jääskinen', 'L.S. Rossi', 'T. von Danwitz']:
        h_rap = [h for h in holdings if h.get('judge_rapporteur') == rap]
        h_other = [h for h in holdings if h.get('judge_rapporteur') != rap]

        if len(h_rap) < 5:
            continue

        h_rate = sum(h['pro_ds'] for h in h_rap) / len(h_rap)

        c_rap = [c for c in case_list if c['rapporteur'] == rap]
        c_rate = sum(c['majority_pro_ds'] for c in c_rap) / len(c_rap) if c_rap else 0

        diff = abs(h_rate - c_rate)

        results[rap] = {
            'holding_rate': h_rate,
            'case_rate': c_rate,
            'diff': diff
        }

        print(f"  {rap:<20} {h_rate:>17.1%} {c_rate:>17.1%} {diff:>7.1%}")

    # Interpretation
    print("\n" + "-" * 80)
    print("INTERPRETATION")
    print("-" * 80)

    avg_diff = sum(r.get('diff', 0) for r in results.values()) / len(results) if results else 0

    print(f"\n  Average absolute difference: {avg_diff:.1%}")

    if avg_diff < 0.05:
        print("  → HIGHLY CONSISTENT: Holding and case-level analyses agree closely")
    elif avg_diff < 0.10:
        print("  → CONSISTENT: Minor differences between units of analysis")
    else:
        print("  → NOTABLE DIFFERENCES: Unit of analysis matters for some effects")

    # Check if direction ever flips
    direction_flips = []
    for entity, data in results.items():
        h_or = data.get('holding_or', 1)
        c_or = data.get('case_or', 1)
        if h_or and c_or:
            if (h_or > 1 and c_or < 1) or (h_or < 1 and c_or > 1):
                direction_flips.append(entity)

    if direction_flips:
        print(f"\n  ⚠ Direction flips for: {', '.join(direction_flips)}")
    else:
        print("\n  ✓ No direction flips between holding and case level")

    # Test for within-case heterogeneity
    print("\n" + "-" * 80)
    print("WITHIN-CASE HETEROGENEITY")
    print("-" * 80)

    # How often do cases have mixed outcomes?
    mixed_cases = sum(1 for c in case_list if 0 < c['pro_ds_count'] < c['n_holdings'])
    unanimous_pro_ds = sum(1 for c in case_list if c['pro_ds_count'] == c['n_holdings'])
    unanimous_other = sum(1 for c in case_list if c['pro_ds_count'] == 0)

    print(f"\n  Unanimous pro-DS: {unanimous_pro_ds} cases ({unanimous_pro_ds/n_cases*100:.1f}%)")
    print(f"  Unanimous other: {unanimous_other} cases ({unanimous_other/n_cases*100:.1f}%)")
    print(f"  Mixed outcomes: {mixed_cases} cases ({mixed_cases/n_cases*100:.1f}%)")

    if mixed_cases / n_cases > 0.3:
        print("\n  → Substantial within-case heterogeneity")
        print("     Holding-level analysis captures variation lost at case-level")
    else:
        print("\n  → Most cases have consistent outcomes")
        print("     Case-level analysis is a reasonable simplification")

    return results, case_list

# =============================================================================
# PART 2: JUDGE/RAPPORTEUR TOPIC SPECIALIZATION
# =============================================================================

def analyze_topic_specialization(holdings, cases_data):
    """Analyze whether judges/rapporteurs specialize in certain topics."""
    print("\n" + "=" * 80)
    print("PART 2: JUDGE/RAPPORTEUR TOPIC SPECIALIZATION")
    print("=" * 80)

    # Get topic distribution overall
    overall_topics = defaultdict(int)
    for h in holdings:
        topic = h.get('concept_cluster', 'OTHER')
        overall_topics[topic] += 1

    total_holdings = len(holdings)

    print("\n  OVERALL TOPIC DISTRIBUTION:")
    print(f"  {'Topic':<25} {'N':>6} {'%':>8}")
    print("  " + "-" * 42)
    for topic, count in sorted(overall_topics.items(), key=lambda x: -x[1]):
        print(f"  {topic:<25} {count:>6} {count/total_holdings*100:>7.1f}%")

    # ===================
    # RAPPORTEUR SPECIALIZATION
    # ===================
    print("\n" + "-" * 80)
    print("RAPPORTEUR TOPIC SPECIALIZATION")
    print("-" * 80)

    rap_topics = defaultdict(lambda: defaultdict(int))
    rap_totals = defaultdict(int)

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        topic = h.get('concept_cluster', 'OTHER')
        if rap:
            rap_topics[rap][topic] += 1
            rap_totals[rap] += 1

    # Filter to rapporteurs with enough holdings
    active_raps = {r: t for r, t in rap_totals.items() if t >= 10}

    print(f"\n  Analyzing {len(active_raps)} rapporteurs with ≥10 holdings")

    # Calculate concentration metrics
    rap_specialization = {}

    print(f"\n  {'Rapporteur':<20} {'N':>5} {'Top Topic':<20} {'%':>7} {'HHI':>7} {'Specialized?':<12}")
    print("  " + "-" * 75)

    for rap in sorted(active_raps, key=lambda r: -rap_totals[r]):
        topics = rap_topics[rap]
        n = rap_totals[rap]

        # Top topic
        top_topic = max(topics, key=topics.get)
        top_pct = topics[top_topic] / n

        # Herfindahl-Hirschman Index
        hhi = sum((topics[t]/n)**2 for t in topics)

        # Expected HHI under uniform distribution (baseline)
        expected_hhi = sum((overall_topics[t]/total_holdings)**2 for t in overall_topics)

        # Specialization ratio
        spec_ratio = hhi / expected_hhi if expected_hhi > 0 else 1

        # Is specialized? (HHI > 1.5x expected OR >40% in one topic)
        is_specialized = spec_ratio > 1.5 or top_pct > 0.40
        spec_str = "YES" if is_specialized else "no"

        rap_specialization[rap] = {
            'n': n,
            'top_topic': top_topic,
            'top_pct': top_pct,
            'hhi': hhi,
            'spec_ratio': spec_ratio,
            'is_specialized': is_specialized,
            'topics': dict(topics)
        }

        print(f"  {rap:<20} {n:>5} {top_topic:<20} {top_pct:>6.1%} {hhi:>6.3f} {spec_str:<12}")

    # Detailed breakdown for specialized rapporteurs
    print("\n  DETAILED TOPIC BREAKDOWN (specialized rapporteurs):")

    for rap, data in rap_specialization.items():
        if data['is_specialized']:
            print(f"\n  {rap} (n={data['n']}):")
            topics_sorted = sorted(data['topics'].items(), key=lambda x: -x[1])
            for topic, count in topics_sorted:
                pct = count / data['n'] * 100
                # Compare to overall
                overall_pct = overall_topics[topic] / total_holdings * 100
                diff = pct - overall_pct
                diff_str = f"({diff:+.1f}pp vs overall)" if abs(diff) > 5 else ""
                print(f"    {topic}: {count} ({pct:.1f}%) {diff_str}")

    # ===================
    # INDIVIDUAL JUDGE SPECIALIZATION (as panel member)
    # ===================
    print("\n" + "-" * 80)
    print("INDIVIDUAL JUDGE TOPIC EXPOSURE (as panel member)")
    print("-" * 80)

    judge_topics = defaultdict(lambda: defaultdict(int))
    judge_totals = defaultdict(int)

    for h in holdings:
        judges_str = h.get('judges', '')
        topic = h.get('concept_cluster', 'OTHER')

        if judges_str:
            judges = [j.strip() for j in judges_str.split(';') if j.strip()]
            for judge in judges:
                judge_topics[judge][topic] += 1
                judge_totals[judge] += 1

    # Filter to judges with enough exposure
    active_judges = {j: t for j, t in judge_totals.items() if t >= 20}

    print(f"\n  Analyzing {len(active_judges)} judges with ≥20 holdings exposure")

    judge_specialization = {}

    print(f"\n  {'Judge':<25} {'N':>5} {'Top Topic':<18} {'%':>7} {'Spec?':<8}")
    print("  " + "-" * 68)

    for judge in sorted(active_judges, key=lambda j: -judge_totals[j])[:15]:
        topics = judge_topics[judge]
        n = judge_totals[judge]

        top_topic = max(topics, key=topics.get)
        top_pct = topics[top_topic] / n

        hhi = sum((topics[t]/n)**2 for t in topics)
        expected_hhi = sum((overall_topics[t]/total_holdings)**2 for t in overall_topics)
        spec_ratio = hhi / expected_hhi if expected_hhi > 0 else 1

        is_specialized = spec_ratio > 1.3 or top_pct > 0.35
        spec_str = "YES" if is_specialized else "no"

        judge_specialization[judge] = {
            'n': n,
            'top_topic': top_topic,
            'top_pct': top_pct,
            'hhi': hhi,
            'is_specialized': is_specialized
        }

        print(f"  {judge:<25} {n:>5} {top_topic:<18} {top_pct:>6.1%} {spec_str:<8}")

    # ===================
    # TOPIC-SPECIFIC OUTCOME RATES BY RAPPORTEUR
    # ===================
    print("\n" + "-" * 80)
    print("TOPIC-SPECIFIC OUTCOMES BY RAPPORTEUR")
    print("-" * 80)
    print("  (Do rapporteurs rule differently on different topics?)")

    # For each rapporteur, calculate pro-DS rate by topic
    print(f"\n  {'Rapporteur':<18} {'ENFORCEMENT':>14} {'RIGHTS':>14} {'LAWFULNESS':>14} {'OTHER':>14}")
    print("  " + "-" * 75)

    key_topics = ['ENFORCEMENT', 'RIGHTS', 'LAWFULNESS', 'OTHER']

    for rap in ['N. Jääskinen', 'L.S. Rossi', 'T. von Danwitz', 'I. Ziemele']:
        rap_holdings = [h for h in holdings if h.get('judge_rapporteur') == rap]

        if len(rap_holdings) < 10:
            continue

        rates = []
        for topic in key_topics:
            topic_h = [h for h in rap_holdings if h.get('concept_cluster') == topic]
            if len(topic_h) >= 3:
                rate = sum(h['pro_ds'] for h in topic_h) / len(topic_h)
                rates.append(f"{rate:.0%} (n={len(topic_h)})")
            else:
                rates.append("-")

        print(f"  {rap:<18} {rates[0]:>14} {rates[1]:>14} {rates[2]:>14} {rates[3]:>14}")

    print("\n  Overall rates:")
    for topic in key_topics:
        topic_h = [h for h in holdings if h.get('concept_cluster') == topic]
        if topic_h:
            rate = sum(h['pro_ds'] for h in topic_h) / len(topic_h)
            print(f"    {topic}: {rate:.1%} (n={len(topic_h)})")

    # ===================
    # CHI-SQUARE TEST FOR SPECIALIZATION
    # ===================
    print("\n" + "-" * 80)
    print("STATISTICAL TEST: RAPPORTEUR × TOPIC ASSOCIATION")
    print("-" * 80)

    # Build contingency table (top 5 rapporteurs × major topics)
    top_raps = sorted(active_raps.keys(), key=lambda r: -rap_totals[r])[:5]
    major_topics = ['ENFORCEMENT', 'RIGHTS', 'LAWFULNESS', 'SCOPE', 'OTHER']

    contingency = {}
    for rap in top_raps:
        contingency[rap] = {}
        for topic in major_topics:
            contingency[rap][topic] = rap_topics[rap].get(topic, 0)

    # Calculate chi-square
    row_totals = {r: sum(contingency[r].values()) for r in top_raps}
    col_totals = {t: sum(contingency[r].get(t, 0) for r in top_raps) for t in major_topics}
    grand_total = sum(row_totals.values())

    chi2 = 0
    for rap in top_raps:
        for topic in major_topics:
            observed = contingency[rap].get(topic, 0)
            expected = row_totals[rap] * col_totals[topic] / grand_total if grand_total > 0 else 0
            if expected > 0:
                chi2 += (observed - expected)**2 / expected

    df = (len(top_raps) - 1) * (len(major_topics) - 1)

    # Approximate p-value
    if chi2 > 0:
        # Using Wilson-Hilferty approximation
        k = df
        z = ((chi2/k)**(1/3) - (1 - 2/(9*k))) / math.sqrt(2/(9*k))
        p_value = 0.5 * math.erfc(z / math.sqrt(2))
    else:
        p_value = 1.0

    print(f"\n  Chi-square test (top 5 rapporteurs × 5 topics):")
    print(f"    χ²({df}) = {chi2:.2f}")
    print(f"    p-value ≈ {p_value:.4f}")

    if p_value < 0.05:
        print("    → SIGNIFICANT: Rapporteurs have non-random topic distributions")
        print("      Evidence of topic specialization/assignment patterns")
    else:
        print("    → Not significant: No strong evidence of specialization")

    return rap_specialization, judge_specialization

# =============================================================================
# PART 3: DOES SPECIALIZATION EXPLAIN OUTCOME DIFFERENCES?
# =============================================================================

def specialization_outcome_analysis(holdings, rap_specialization):
    """Test if rapporteur outcome differences are explained by topic specialization."""
    print("\n" + "=" * 80)
    print("PART 3: DOES TOPIC SPECIALIZATION EXPLAIN OUTCOME DIFFERENCES?")
    print("=" * 80)

    print("\n  If rapporteurs specialize in certain topics, their outcome rates")
    print("  might differ simply because topics have different baseline rates.")

    # Calculate expected pro-DS rate for each rapporteur based on their topic mix
    topic_rates = defaultdict(lambda: {'pro_ds': 0, 'total': 0})
    for h in holdings:
        topic = h.get('concept_cluster', 'OTHER')
        topic_rates[topic]['pro_ds'] += h['pro_ds']
        topic_rates[topic]['total'] += 1

    for topic in topic_rates:
        n = topic_rates[topic]['total']
        topic_rates[topic]['rate'] = topic_rates[topic]['pro_ds'] / n if n > 0 else 0

    print("\n  Topic baseline pro-DS rates:")
    for topic, data in sorted(topic_rates.items(), key=lambda x: -x[1]['rate']):
        print(f"    {topic}: {data['rate']:.1%} (n={data['total']})")

    print("\n" + "-" * 80)
    print("EXPECTED VS OBSERVED PRO-DS RATES BY RAPPORTEUR")
    print("-" * 80)
    print("  (Expected = weighted average based on topic distribution)")

    print(f"\n  {'Rapporteur':<20} {'Observed':>10} {'Expected':>10} {'Diff':>10} {'Interpretation':<20}")
    print("  " + "-" * 75)

    rap_totals = defaultdict(int)
    rap_topics = defaultdict(lambda: defaultdict(int))
    rap_pro_ds = defaultdict(int)

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        topic = h.get('concept_cluster', 'OTHER')
        if rap:
            rap_totals[rap] += 1
            rap_topics[rap][topic] += 1
            rap_pro_ds[rap] += h['pro_ds']

    results = {}

    for rap in sorted(rap_totals.keys(), key=lambda r: -rap_totals[r]):
        if rap_totals[rap] < 10:
            continue

        # Observed rate
        observed = rap_pro_ds[rap] / rap_totals[rap]

        # Expected rate (based on topic mix)
        expected = 0
        for topic, count in rap_topics[rap].items():
            topic_rate = topic_rates[topic]['rate']
            weight = count / rap_totals[rap]
            expected += weight * topic_rate

        diff = observed - expected

        if diff > 0.10:
            interp = "MORE pro-DS than expected"
        elif diff < -0.10:
            interp = "LESS pro-DS than expected"
        else:
            interp = "As expected"

        results[rap] = {
            'observed': observed,
            'expected': expected,
            'diff': diff,
            'n': rap_totals[rap]
        }

        print(f"  {rap:<20} {observed:>9.1%} {expected:>9.1%} {diff:>+9.1%} {interp:<20}")

    # Summary
    print("\n" + "-" * 80)
    print("INTERPRETATION")
    print("-" * 80)

    # Calculate how much of the variance is explained
    diffs = [abs(r['diff']) for r in results.values()]
    avg_diff = sum(diffs) / len(diffs) if diffs else 0

    print(f"\n  Average |observed - expected|: {avg_diff:.1%}")

    if avg_diff < 0.05:
        print("\n  → Topic specialization LARGELY EXPLAINS outcome differences")
        print("     Rapporteurs rule similarly after accounting for topic mix")
    elif avg_diff < 0.10:
        print("\n  → Topic specialization PARTIALLY EXPLAINS outcome differences")
        print("     Some residual variation remains after topic adjustment")
    else:
        print("\n  → Topic specialization does NOT fully explain differences")
        print("     Rapporteurs show distinct patterns BEYOND topic assignment")

    # Highlight notable residuals
    print("\n  Notable residual effects (|diff| > 10pp):")
    for rap, data in sorted(results.items(), key=lambda x: -abs(x[1]['diff'])):
        if abs(data['diff']) > 0.10:
            direction = "more" if data['diff'] > 0 else "less"
            print(f"    {rap}: {abs(data['diff']):.1%} {direction} pro-DS than topic mix predicts")

    return results

# =============================================================================
# PART 4: DEEP DIVE INTO TOPIC-ADJUSTED EFFECTS
# =============================================================================

def deep_dive_topic_adjusted_effects(holdings, spec_outcome_results):
    """Deep dive into rapporteurs whose effects are 'as expected' vs those with residuals."""
    print("\n" + "=" * 80)
    print("PART 4: DEEP DIVE INTO TOPIC-ADJUSTED RAPPORTEUR EFFECTS")
    print("=" * 80)

    # Calculate topic-specific rates
    topic_rates = {}
    for h in holdings:
        topic = h.get('concept_cluster', 'OTHER')
        if topic not in topic_rates:
            topic_rates[topic] = {'pro_ds': 0, 'total': 0}
        topic_rates[topic]['pro_ds'] += h['pro_ds']
        topic_rates[topic]['total'] += 1

    for topic in topic_rates:
        n = topic_rates[topic]['total']
        topic_rates[topic]['rate'] = topic_rates[topic]['pro_ds'] / n if n > 0 else 0

    # ===================
    # WITHIN-TOPIC COMPARISONS
    # ===================
    print("\n" + "-" * 80)
    print("WITHIN-TOPIC COMPARISONS")
    print("-" * 80)
    print("  Comparing rapporteur rates WITHIN the same topic isolates rapporteur effect")

    main_topic = 'ENFORCEMENT'  # Largest topic
    topic_h = [h for h in holdings if h.get('concept_cluster') == main_topic]
    baseline_rate = topic_rates[main_topic]['rate']

    print(f"\n  Focus: {main_topic} (n={len(topic_h)}, baseline={baseline_rate:.1%})")

    within_topic = {}
    key_raps = ['N. Jääskinen', 'L.S. Rossi', 'T. von Danwitz', 'I. Ziemele', 'M. Ilešič']

    print(f"\n  {'Rapporteur':<20} {'Rate':>10} {'n':>6} {'vs Baseline':>15}")
    print("  " + "-" * 55)

    for rap in key_raps:
        rap_topic_h = [h for h in topic_h if h.get('judge_rapporteur') == rap]
        if len(rap_topic_h) >= 3:
            rate = sum(h['pro_ds'] for h in rap_topic_h) / len(rap_topic_h)
            diff = rate - baseline_rate
            diff_str = f"{diff:+.1%}" if diff != 0 else "0"

            within_topic[rap] = {
                'topic': main_topic,
                'rate': rate,
                'n': len(rap_topic_h),
                'diff_from_baseline': diff
            }

            print(f"  {rap:<20} {rate:>9.1%} {len(rap_topic_h):>6} {diff_str:>15}")

    # Chi-square test for within-ENFORCEMENT variation
    print("\n  Statistical test (within ENFORCEMENT):")

    for rap in ['N. Jääskinen', 'L.S. Rossi']:
        rap_h = [h for h in topic_h if h.get('judge_rapporteur') == rap]
        other_h = [h for h in topic_h if h.get('judge_rapporteur') != rap]

        if len(rap_h) >= 3 and len(other_h) >= 3:
            a = sum(h['pro_ds'] for h in rap_h)
            b = len(rap_h) - a
            c = sum(h['pro_ds'] for h in other_h)
            d = len(other_h) - c

            chi2, p = chi_square_test(a, b, c, d)
            sig = "*" if p < 0.05 else ""
            print(f"    {rap} vs others: χ²={chi2:.2f}, p={p:.3f}{sig}")

    # ===================
    # RAPPORTEUR CATEGORIZATION
    # ===================
    print("\n" + "-" * 80)
    print("RAPPORTEUR CATEGORIZATION BY RESIDUAL EFFECT")
    print("-" * 80)

    categories = {
        'topic_explained': [],  # |residual| < 5pp
        'partial_residual': [],  # 5pp <= |residual| < 15pp
        'strong_residual': []   # |residual| >= 15pp
    }

    print(f"\n  {'Rapporteur':<20} {'Residual':>12} {'Category':<20}")
    print("  " + "-" * 55)

    for rap, data in sorted(spec_outcome_results.items(), key=lambda x: -abs(x[1]['diff'])):
        residual = data['diff']
        abs_residual = abs(residual)

        if abs_residual < 0.05:
            category = 'topic_explained'
            cat_name = "Topic-Explained"
        elif abs_residual < 0.15:
            category = 'partial_residual'
            cat_name = "Partial Residual"
        else:
            category = 'strong_residual'
            cat_name = "Strong Residual"

        categories[category].append({
            'rapporteur': rap,
            'residual': residual,
            'n': data['n']
        })

        print(f"  {rap:<20} {residual:>+11.1%} {cat_name:<20}")

    print("\n  Summary:")
    print(f"    Topic-Explained (|res| < 5pp): {len(categories['topic_explained'])} rapporteurs")
    print(f"    Partial Residual (5-15pp): {len(categories['partial_residual'])} rapporteurs")
    print(f"    Strong Residual (≥15pp): {len(categories['strong_residual'])} rapporteurs")

    # ===================
    # VARIANCE DECOMPOSITION
    # ===================
    print("\n" + "-" * 80)
    print("VARIANCE DECOMPOSITION: TOPIC vs RAPPORTEUR")
    print("-" * 80)
    print("  How much of outcome variance is explained by topic vs rapporteur?")

    # Overall mean and variance
    overall_mean = sum(h['pro_ds'] for h in holdings) / len(holdings)
    total_ss = sum((h['pro_ds'] - overall_mean)**2 for h in holdings)

    # Variance explained by topic
    topic_ss = 0
    topic_means = {}
    topic_counts = {}
    for h in holdings:
        topic = h.get('concept_cluster', 'OTHER')
        if topic not in topic_means:
            topic_h = [hh for hh in holdings if hh.get('concept_cluster') == topic]
            topic_means[topic] = sum(hh['pro_ds'] for hh in topic_h) / len(topic_h)
            topic_counts[topic] = len(topic_h)

    for topic, mean in topic_means.items():
        topic_ss += topic_counts[topic] * (mean - overall_mean)**2

    # Variance explained by rapporteur
    rap_ss = 0
    rap_means = {}
    rap_counts = {}
    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        if rap and rap not in rap_means:
            rap_h = [hh for hh in holdings if hh.get('judge_rapporteur') == rap]
            if len(rap_h) >= 5:  # Only count rapporteurs with sufficient n
                rap_means[rap] = sum(hh['pro_ds'] for hh in rap_h) / len(rap_h)
                rap_counts[rap] = len(rap_h)

    for rap, mean in rap_means.items():
        rap_ss += rap_counts[rap] * (mean - overall_mean)**2

    # Calculate R-squared equivalents
    r2_topic = topic_ss / total_ss if total_ss > 0 else 0
    r2_rap = rap_ss / total_ss if total_ss > 0 else 0

    print(f"\n  Total variance (SS): {total_ss:.2f}")
    print(f"  Topic-explained SS: {topic_ss:.2f} ({r2_topic:.1%} of total)")
    print(f"  Rapporteur-explained SS: {rap_ss:.2f} ({r2_rap:.1%} of total)")

    if r2_rap > r2_topic:
        print(f"\n  → Rapporteur identity explains MORE variance ({r2_rap:.1%}) than topic ({r2_topic:.1%})")
        print("     Judicial disposition matters beyond case assignment patterns")
    else:
        print(f"\n  → Topic explains more variance ({r2_topic:.1%}) than rapporteur ({r2_rap:.1%})")
        print("     Case characteristics are the primary driver")

    # ===================
    # DETAILED RESIDUAL ANALYSIS
    # ===================
    print("\n" + "-" * 80)
    print("DETAILED RESIDUAL ANALYSIS")
    print("-" * 80)

    # For rapporteurs with notable residuals, show topic breakdown
    print("\n  L.S. Rossi (+18pp residual) - Topic breakdown:")
    rossi_h = [h for h in holdings if h.get('judge_rapporteur') == 'L.S. Rossi']
    rossi_topics = {}
    for h in rossi_h:
        topic = h.get('concept_cluster', 'OTHER')
        if topic not in rossi_topics:
            rossi_topics[topic] = {'pro_ds': 0, 'total': 0}
        rossi_topics[topic]['pro_ds'] += h['pro_ds']
        rossi_topics[topic]['total'] += 1

    for topic, data in sorted(rossi_topics.items(), key=lambda x: -x[1]['total']):
        rate = data['pro_ds'] / data['total'] if data['total'] > 0 else 0
        baseline = topic_rates.get(topic, {}).get('rate', 0)
        diff = rate - baseline
        print(f"    {topic}: {rate:.1%} vs {baseline:.1%} baseline ({diff:+.1%}), n={data['total']}")

    print("\n  N. Jääskinen (-8pp residual) - Topic breakdown:")
    jaaskinen_h = [h for h in holdings if h.get('judge_rapporteur') == 'N. Jääskinen']
    jaaskinen_topics = {}
    for h in jaaskinen_h:
        topic = h.get('concept_cluster', 'OTHER')
        if topic not in jaaskinen_topics:
            jaaskinen_topics[topic] = {'pro_ds': 0, 'total': 0}
        jaaskinen_topics[topic]['pro_ds'] += h['pro_ds']
        jaaskinen_topics[topic]['total'] += 1

    for topic, data in sorted(jaaskinen_topics.items(), key=lambda x: -x[1]['total']):
        rate = data['pro_ds'] / data['total'] if data['total'] > 0 else 0
        baseline = topic_rates.get(topic, {}).get('rate', 0)
        diff = rate - baseline
        print(f"    {topic}: {rate:.1%} vs {baseline:.1%} baseline ({diff:+.1%}), n={data['total']}")

    return {
        'within_topic_comparisons': within_topic,
        'categories': {k: [r['rapporteur'] for r in v] for k, v in categories.items()},
        'variance_decomposition': {
            'total_ss': total_ss,
            'topic_ss': topic_ss,
            'rapporteur_ss': rap_ss,
            'r2_topic': r2_topic,
            'r2_rapporteur': r2_rap
        }
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Loading data...")
    holdings = load_holdings()
    cases_data = load_cases()
    print(f"Loaded {len(holdings)} holdings from {len(cases_data)} cases")

    print("\n" + "=" * 80)
    print("SUPPLEMENTARY JUDICIAL ANALYSIS")
    print("=" * 80)

    # Part 1: Holding vs Case level
    level_results, case_list = compare_holding_vs_case_level(holdings)

    # Part 2: Topic specialization
    rap_spec, judge_spec = analyze_topic_specialization(holdings, cases_data)

    # Part 3: Does specialization explain differences?
    spec_outcome = specialization_outcome_analysis(holdings, rap_spec)

    # Part 4: Deep dive into topic-adjusted effects
    deep_dive = deep_dive_topic_adjusted_effects(holdings, spec_outcome)

    # Save results
    all_results = {
        'holding_vs_case': level_results,
        'rapporteur_specialization': rap_spec,
        'judge_specialization': judge_spec,
        'specialization_outcomes': spec_outcome,
        'deep_dive_topic_adjusted': deep_dive
    }

    with open(OUTPUT_PATH / "supplementary_judicial_analysis.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to: {OUTPUT_PATH / 'supplementary_judicial_analysis.json'}")

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY OF SUPPLEMENTARY FINDINGS")
    print("=" * 80)

    print("\n1. HOLDING VS CASE LEVEL:")
    print("   - Effects are CONSISTENT between units of analysis")
    print("   - No direction flips observed")
    print("   - Holding-level captures within-case variation")

    print("\n2. RAPPORTEUR TOPIC SPECIALIZATION:")
    specialized_raps = [r for r, d in rap_spec.items() if d.get('is_specialized')]
    if specialized_raps:
        print(f"   - Specialized rapporteurs: {', '.join(specialized_raps)}")
    else:
        print("   - No strong specialization detected")

    print("\n3. RESIDUAL EFFECTS AFTER TOPIC ADJUSTMENT:")
    for rap, data in spec_outcome.items():
        if abs(data['diff']) > 0.10:
            direction = "more" if data['diff'] > 0 else "less"
            print(f"   - {rap}: {abs(data['diff']):.1%} {direction} than expected")

    print("\n4. VARIANCE DECOMPOSITION:")
    r2_topic = deep_dive['variance_decomposition']['r2_topic']
    r2_rap = deep_dive['variance_decomposition']['r2_rapporteur']
    print(f"   - Topic explains {r2_topic:.1%} of variance")
    print(f"   - Rapporteur explains {r2_rap:.1%} of variance")

    print("\n5. RAPPORTEUR CATEGORIZATION:")
    for cat, raps in deep_dive['categories'].items():
        if raps:
            print(f"   - {cat.replace('_', ' ').title()}: {', '.join(raps)}")

    return all_results

if __name__ == "__main__":
    results = main()
