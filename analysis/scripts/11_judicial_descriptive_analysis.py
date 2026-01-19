#!/usr/bin/env python3
"""
11_judicial_descriptive_analysis.py
====================================
Phase 2: Descriptive Analysis for Judicial Effects

This script:
1. Creates rapporteur profiles (pro-DS rate, topics, chambers, temporal)
2. Creates chamber profiles (pro-DS rate, rapporteurs, topics)
3. Creates individual judge exposure summaries
4. Performs network diagnostics on co-occurrence structure
5. Generates tables and preliminary visualizations
"""

import json
import csv
import math
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HOLDINGS_JUDICIAL = PROJECT_ROOT / "analysis" / "output" / "holdings_judicial.csv"
JUDGE_STATS = PROJECT_ROOT / "analysis" / "output" / "judge_statistics.json"
RAPPORTEUR_GROUPINGS = PROJECT_ROOT / "analysis" / "output" / "rapporteur_groupings.json"
COOCCURRENCE_MATRIX = PROJECT_ROOT / "analysis" / "output" / "judge_cooccurrence_matrix.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def wilson_score_interval(successes, n, confidence=0.95):
    """Calculate Wilson score confidence interval for a proportion."""
    if n == 0:
        return 0.0, 0.0, 0.0

    z = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
    p = successes / n

    denominator = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denominator
    spread = z * math.sqrt((p * (1-p) + z**2 / (4*n)) / n) / denominator

    lower = max(0, center - spread)
    upper = min(1, center + spread)

    return p, lower, upper

def load_holdings():
    """Load enhanced holdings data."""
    holdings = []
    with open(HOLDINGS_JUDICIAL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert pro_ds to int
            row['pro_ds'] = int(row.get('pro_ds', 0))
            holdings.append(row)
    return holdings

def load_judge_stats():
    """Load judge statistics."""
    with open(JUDGE_STATS, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rapporteur_groupings():
    """Load rapporteur groupings."""
    with open(RAPPORTEUR_GROUPINGS, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_cooccurrence_matrix():
    """Load co-occurrence matrix."""
    matrix = []
    judges = []
    with open(COOCCURRENCE_MATRIX, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        judges = header[1:]  # Skip first empty column
        for row in reader:
            judge = row[0]
            values = [int(x) for x in row[1:]]
            matrix.append(values)
    return matrix, judges

# =============================================================================
# RAPPORTEUR PROFILES
# =============================================================================

def analyze_rapporteur_profiles(holdings):
    """Create detailed rapporteur profiles."""
    profiles = defaultdict(lambda: {
        'n_holdings': 0,
        'pro_ds_count': 0,
        'concepts': defaultdict(int),
        'chambers': defaultdict(int),
        'years': [],
        'case_ids': set()
    })

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        if not rap:
            continue

        profiles[rap]['n_holdings'] += 1
        profiles[rap]['pro_ds_count'] += h['pro_ds']
        profiles[rap]['concepts'][h.get('concept_cluster', 'OTHER')] += 1
        profiles[rap]['chambers'][h.get('chamber', 'UNKNOWN')] += 1
        profiles[rap]['case_ids'].add(h.get('case_id', ''))

        try:
            year = int(h.get('year', 0))
            if year:
                profiles[rap]['years'].append(year)
        except:
            pass

    # Calculate derived statistics
    results = {}
    for rap, data in profiles.items():
        n = data['n_holdings']
        pro_ds = data['pro_ds_count']
        rate, ci_low, ci_high = wilson_score_interval(pro_ds, n)

        # Topic concentration (Herfindahl index)
        total_concepts = sum(data['concepts'].values())
        hhi = sum((c/total_concepts)**2 for c in data['concepts'].values()) if total_concepts > 0 else 0

        # Primary concept
        primary_concept = max(data['concepts'], key=data['concepts'].get) if data['concepts'] else 'NONE'
        primary_concept_pct = data['concepts'][primary_concept] / n * 100 if n > 0 else 0

        # Primary chamber
        primary_chamber = max(data['chambers'], key=data['chambers'].get) if data['chambers'] else 'NONE'

        results[rap] = {
            'n_cases': len(data['case_ids']),
            'n_holdings': n,
            'pro_ds_count': pro_ds,
            'pro_ds_rate': rate,
            'ci_lower': ci_low,
            'ci_upper': ci_high,
            'primary_concept': primary_concept,
            'primary_concept_pct': primary_concept_pct,
            'concept_hhi': hhi,
            'concepts': dict(data['concepts']),
            'primary_chamber': primary_chamber,
            'chambers': dict(data['chambers']),
            'mean_year': sum(data['years']) / len(data['years']) if data['years'] else 0,
            'year_range': f"{min(data['years'])}-{max(data['years'])}" if data['years'] else ''
        }

    return results

def print_rapporteur_profiles(profiles, groupings):
    """Print formatted rapporteur profiles."""
    print("\n" + "=" * 80)
    print("RAPPORTEUR PROFILES")
    print("=" * 80)

    # Sort by holdings count
    sorted_raps = sorted(profiles.items(), key=lambda x: -x[1]['n_holdings'])

    print(f"\n{'Rapporteur':<22} {'Grp':^4} {'N':>4} {'Pro-DS':>8} {'95% CI':>16} {'Primary Concept':<20}")
    print("-" * 80)

    for rap, data in sorted_raps:
        group = groupings.get(rap, {}).get('group', '?')[0]  # First letter
        ci = f"[{data['ci_lower']:.1%}, {data['ci_upper']:.1%}]"
        print(f"{rap:<22} {group:^4} {data['n_holdings']:>4} {data['pro_ds_rate']:>7.1%} {ci:>16} {data['primary_concept']:<20}")

    print("-" * 80)

    # Summary statistics
    total_holdings = sum(p['n_holdings'] for p in profiles.values())
    total_pro_ds = sum(p['pro_ds_count'] for p in profiles.values())
    overall_rate = total_pro_ds / total_holdings if total_holdings > 0 else 0

    print(f"\nOverall pro-DS rate: {overall_rate:.1%} ({total_pro_ds}/{total_holdings})")

    # Identify outliers (rapporteurs significantly different from overall)
    print("\n" + "-" * 80)
    print("NOTABLE DEVIATIONS FROM OVERALL RATE:")
    print("-" * 80)

    for rap, data in sorted_raps:
        if data['n_holdings'] >= 5:  # Only consider rapporteurs with enough data
            if data['ci_upper'] < overall_rate:
                diff = (data['pro_ds_rate'] - overall_rate) * 100
                print(f"  {rap}: {data['pro_ds_rate']:.1%} - BELOW average by {abs(diff):.1f}pp (CI excludes {overall_rate:.1%})")
            elif data['ci_lower'] > overall_rate:
                diff = (data['pro_ds_rate'] - overall_rate) * 100
                print(f"  {rap}: {data['pro_ds_rate']:.1%} - ABOVE average by {diff:.1f}pp (CI excludes {overall_rate:.1%})")

# =============================================================================
# CHAMBER PROFILES
# =============================================================================

def analyze_chamber_profiles(holdings):
    """Create detailed chamber profiles."""
    profiles = defaultdict(lambda: {
        'n_holdings': 0,
        'pro_ds_count': 0,
        'rapporteurs': defaultdict(int),
        'concepts': defaultdict(int),
        'case_ids': set(),
        'years': []
    })

    for h in holdings:
        chamber = h.get('chamber', 'UNKNOWN')
        if not chamber:
            chamber = 'UNKNOWN'

        profiles[chamber]['n_holdings'] += 1
        profiles[chamber]['pro_ds_count'] += h['pro_ds']
        profiles[chamber]['rapporteurs'][h.get('judge_rapporteur', 'UNKNOWN')] += 1
        profiles[chamber]['concepts'][h.get('concept_cluster', 'OTHER')] += 1
        profiles[chamber]['case_ids'].add(h.get('case_id', ''))

        try:
            year = int(h.get('year', 0))
            if year:
                profiles[chamber]['years'].append(year)
        except:
            pass

    results = {}
    for chamber, data in profiles.items():
        n = data['n_holdings']
        pro_ds = data['pro_ds_count']
        rate, ci_low, ci_high = wilson_score_interval(pro_ds, n)

        # Count distinct rapporteurs
        n_rapporteurs = len([r for r in data['rapporteurs'] if r != 'UNKNOWN'])

        # Primary rapporteur
        primary_rap = max(data['rapporteurs'], key=data['rapporteurs'].get) if data['rapporteurs'] else 'NONE'

        # Primary concept
        primary_concept = max(data['concepts'], key=data['concepts'].get) if data['concepts'] else 'NONE'

        results[chamber] = {
            'n_cases': len(data['case_ids']),
            'n_holdings': n,
            'pro_ds_count': pro_ds,
            'pro_ds_rate': rate,
            'ci_lower': ci_low,
            'ci_upper': ci_high,
            'n_rapporteurs': n_rapporteurs,
            'rapporteurs': dict(data['rapporteurs']),
            'primary_rapporteur': primary_rap,
            'concepts': dict(data['concepts']),
            'primary_concept': primary_concept,
            'mean_year': sum(data['years']) / len(data['years']) if data['years'] else 0
        }

    return results

def print_chamber_profiles(profiles):
    """Print formatted chamber profiles."""
    print("\n" + "=" * 80)
    print("CHAMBER PROFILES")
    print("=" * 80)

    # Sort by holdings count
    sorted_chambers = sorted(profiles.items(), key=lambda x: -x[1]['n_holdings'])

    print(f"\n{'Chamber':<18} {'Cases':>6} {'Hold':>5} {'Pro-DS':>8} {'95% CI':>18} {'Rapp':>5} {'Mean Yr':>8}")
    print("-" * 80)

    for chamber, data in sorted_chambers:
        ci = f"[{data['ci_lower']:.1%}, {data['ci_upper']:.1%}]"
        print(f"{chamber:<18} {data['n_cases']:>6} {data['n_holdings']:>5} {data['pro_ds_rate']:>7.1%} {ci:>18} {data['n_rapporteurs']:>5} {data['mean_year']:>8.1f}")

    print("-" * 80)

    # Calculate overall rate for comparison
    total_holdings = sum(p['n_holdings'] for p in profiles.values())
    total_pro_ds = sum(p['pro_ds_count'] for p in profiles.values())
    overall_rate = total_pro_ds / total_holdings if total_holdings > 0 else 0

    print(f"\nOverall: {overall_rate:.1%}")

    # Identify significant deviations
    print("\n" + "-" * 80)
    print("CHAMBER DEVIATIONS FROM OVERALL:")
    print("-" * 80)

    for chamber, data in sorted_chambers:
        if data['n_holdings'] >= 5:
            diff_pp = (data['pro_ds_rate'] - overall_rate) * 100
            sig_marker = ""
            if data['ci_upper'] < overall_rate:
                sig_marker = " *** SIGNIFICANTLY BELOW"
            elif data['ci_lower'] > overall_rate:
                sig_marker = " *** SIGNIFICANTLY ABOVE"

            print(f"  {chamber:<18}: {diff_pp:+6.1f}pp from overall{sig_marker}")

# =============================================================================
# INDIVIDUAL JUDGE EXPOSURE ANALYSIS
# =============================================================================

def analyze_judge_exposure(holdings, judge_stats):
    """Analyze outcomes when each judge is present vs. absent."""
    results = {}

    # Get all judge columns from holdings
    sample_holding = holdings[0] if holdings else {}
    judge_columns = [c for c in sample_holding.keys() if c.startswith('judge_')]

    # Also track by original judge names
    judge_name_mapping = {}
    for col in judge_columns:
        # Reverse the column name transformation
        name = col.replace('judge_', '').replace('_', ' ').replace('  ', '. ').replace(' ', '.')
        judge_name_mapping[col] = col  # Keep column name for now

    for col in judge_columns:
        present_pro_ds = 0
        present_total = 0
        absent_pro_ds = 0
        absent_total = 0

        for h in holdings:
            try:
                is_present = int(h.get(col, 0))
            except:
                is_present = 0

            if is_present:
                present_total += 1
                present_pro_ds += h['pro_ds']
            else:
                absent_total += 1
                absent_pro_ds += h['pro_ds']

        # Calculate rates and CIs
        if present_total > 0:
            present_rate, present_ci_low, present_ci_high = wilson_score_interval(present_pro_ds, present_total)
        else:
            present_rate, present_ci_low, present_ci_high = 0, 0, 0

        if absent_total > 0:
            absent_rate, absent_ci_low, absent_ci_high = wilson_score_interval(absent_pro_ds, absent_total)
        else:
            absent_rate, absent_ci_low, absent_ci_high = 0, 0, 0

        # Calculate difference
        diff = present_rate - absent_rate if present_total > 0 and absent_total > 0 else 0

        # Calculate odds ratio
        if present_total > 0 and absent_total > 0 and present_pro_ds > 0 and absent_pro_ds > 0:
            # Avoid division by zero
            a = present_pro_ds
            b = present_total - present_pro_ds
            c = absent_pro_ds
            d = absent_total - absent_pro_ds

            if b > 0 and c > 0:
                odds_ratio = (a * d) / (b * c)
            else:
                odds_ratio = None
        else:
            odds_ratio = None

        results[col] = {
            'present_n': present_total,
            'present_pro_ds': present_pro_ds,
            'present_rate': present_rate,
            'present_ci': (present_ci_low, present_ci_high),
            'absent_n': absent_total,
            'absent_pro_ds': absent_pro_ds,
            'absent_rate': absent_rate,
            'absent_ci': (absent_ci_low, absent_ci_high),
            'rate_diff': diff,
            'odds_ratio': odds_ratio
        }

    return results

def print_judge_exposure(exposure_results, min_cases=10):
    """Print judge exposure analysis."""
    print("\n" + "=" * 80)
    print("INDIVIDUAL JUDGE EXPOSURE ANALYSIS")
    print("=" * 80)
    print(f"(Showing judges with ≥{min_cases} cases when present)")

    # Filter and sort by rate difference
    filtered = {k: v for k, v in exposure_results.items() if v['present_n'] >= min_cases}
    sorted_judges = sorted(filtered.items(), key=lambda x: -x[1]['rate_diff'])

    print(f"\n{'Judge':<30} {'When Present':>20} {'When Absent':>20} {'Diff':>8} {'OR':>8}")
    print(f"{'':30} {'n':>6} {'Pro-DS':>12} {'n':>6} {'Pro-DS':>12}")
    print("-" * 90)

    for judge_col, data in sorted_judges:
        # Clean up judge name for display
        judge_name = judge_col.replace('judge_', '').replace('_', ' ')

        present_str = f"{data['present_rate']:.1%}"
        absent_str = f"{data['absent_rate']:.1%}"
        diff_str = f"{data['rate_diff']:+.1%}"
        or_str = f"{data['odds_ratio']:.2f}" if data['odds_ratio'] else "N/A"

        print(f"{judge_name:<30} {data['present_n']:>6} {present_str:>12} {data['absent_n']:>6} {absent_str:>12} {diff_str:>8} {or_str:>8}")

    print("-" * 90)

    # Identify potential high-impact judges
    print("\n" + "-" * 80)
    print("JUDGES WITH NOTABLE EFFECTS (|diff| > 15pp, n≥10):")
    print("-" * 80)

    notable = [(k, v) for k, v in filtered.items() if abs(v['rate_diff']) > 0.15]
    notable_sorted = sorted(notable, key=lambda x: abs(x[1]['rate_diff']), reverse=True)

    if notable:
        for judge_col, data in notable_sorted:
            judge_name = judge_col.replace('judge_', '').replace('_', ' ')
            direction = "MORE pro-DS" if data['rate_diff'] > 0 else "LESS pro-DS"
            print(f"  {judge_name}: {direction} by {abs(data['rate_diff']):.1%} when present")
            print(f"    Present: {data['present_rate']:.1%} ({data['present_n']} holdings)")
            print(f"    Absent:  {data['absent_rate']:.1%} ({data['absent_n']} holdings)")
    else:
        print("  No judges show differences exceeding 15 percentage points.")

# =============================================================================
# NETWORK DIAGNOSTICS
# =============================================================================

def analyze_network(matrix, judges):
    """Analyze co-occurrence network structure."""
    n = len(judges)

    print("\n" + "=" * 80)
    print("CO-OCCURRENCE NETWORK DIAGNOSTICS")
    print("=" * 80)

    # Basic stats
    total_cooccurrences = sum(sum(row) for row in matrix) // 2  # Divide by 2 for symmetry
    diagonal_sum = sum(matrix[i][i] for i in range(n))

    # Count edges (non-zero off-diagonal)
    edges = 0
    for i in range(n):
        for j in range(i+1, n):
            if matrix[i][j] > 0:
                edges += 1

    max_edges = n * (n - 1) // 2
    density = edges / max_edges if max_edges > 0 else 0

    print(f"\n  Network size: {n} judges")
    print(f"  Total co-occurrences: {total_cooccurrences}")
    print(f"  Edges (unique pairs): {edges}")
    print(f"  Max possible edges: {max_edges}")
    print(f"  Density: {density:.3f}")

    # Degree distribution
    degrees = []
    for i in range(n):
        deg = sum(1 for j in range(n) if i != j and matrix[i][j] > 0)
        degrees.append((judges[i], deg, sum(matrix[i][j] for j in range(n) if i != j)))

    degrees_sorted = sorted(degrees, key=lambda x: -x[1])

    print(f"\n  Degree statistics:")
    print(f"    Mean degree: {sum(d[1] for d in degrees) / n:.1f}")
    print(f"    Max degree: {max(d[1] for d in degrees)}")
    print(f"    Min degree: {min(d[1] for d in degrees)}")

    print(f"\n  Top 10 judges by connectivity:")
    for judge, deg, weight in degrees_sorted[:10]:
        print(f"    {judge}: {deg} connections, {weight} total co-occurrences")

    # Find strongest pairs
    print(f"\n  Strongest judge pairs (most co-occurrences):")
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            if matrix[i][j] > 0:
                pairs.append((judges[i], judges[j], matrix[i][j]))

    pairs_sorted = sorted(pairs, key=lambda x: -x[2])[:10]
    for j1, j2, count in pairs_sorted:
        print(f"    {j1} - {j2}: {count} cases together")

    # Clustering coefficient (simplified)
    # For each node, what fraction of its neighbors are connected to each other?
    clustering_coeffs = []
    for i in range(n):
        neighbors = [j for j in range(n) if i != j and matrix[i][j] > 0]
        k = len(neighbors)
        if k < 2:
            continue

        # Count edges among neighbors
        neighbor_edges = 0
        for ni in range(len(neighbors)):
            for nj in range(ni+1, len(neighbors)):
                if matrix[neighbors[ni]][neighbors[nj]] > 0:
                    neighbor_edges += 1

        max_neighbor_edges = k * (k - 1) // 2
        cc = neighbor_edges / max_neighbor_edges if max_neighbor_edges > 0 else 0
        clustering_coeffs.append(cc)

    avg_clustering = sum(clustering_coeffs) / len(clustering_coeffs) if clustering_coeffs else 0

    print(f"\n  Average clustering coefficient: {avg_clustering:.3f}")
    if avg_clustering > 0.5:
        print("    → High clustering indicates judges form tight-knit groups")
        print("    → This increases confounding in individual judge analysis")

    # Interpretation
    print("\n" + "-" * 80)
    print("NETWORK INTERPRETATION:")
    print("-" * 80)

    if density > 0.6:
        print("  ⚠ HIGH DENSITY: Most judges have co-occurred with most others.")
        print("    Individual judge effects are HEAVILY CONFOUNDED.")
        print("    Consider: Panel-level analysis or dropping individual judge analysis.")
    elif density > 0.4:
        print("  ⚠ MODERATE DENSITY: Substantial co-occurrence.")
        print("    Individual judge effects require careful interpretation.")
    else:
        print("  ✓ LOW DENSITY: Judges have distinct co-occurrence patterns.")
        print("    Individual judge effects may be more identifiable.")

    return {
        'n_judges': n,
        'n_edges': edges,
        'density': density,
        'avg_clustering': avg_clustering,
        'avg_degree': sum(d[1] for d in degrees) / n
    }

# =============================================================================
# SAVE RESULTS
# =============================================================================

def save_descriptive_results(rapporteur_profiles, chamber_profiles, judge_exposure, network_stats):
    """Save all descriptive results to JSON."""
    results = {
        'rapporteur_profiles': rapporteur_profiles,
        'chamber_profiles': chamber_profiles,
        'judge_exposure': judge_exposure,
        'network_stats': network_stats,
        'metadata': {
            'generated_at': str(Path(__file__).name),
            'description': 'Phase 2: Descriptive Analysis Results'
        }
    }

    with open(OUTPUT_PATH / "descriptive_judicial_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved to: {OUTPUT_PATH / 'descriptive_judicial_analysis.json'}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Loading data...")
    holdings = load_holdings()
    judge_stats = load_judge_stats()
    rapporteur_groupings = load_rapporteur_groupings()
    cooccurrence_matrix, judges = load_cooccurrence_matrix()

    print(f"Loaded {len(holdings)} holdings")

    print("\n" + "=" * 80)
    print("PHASE 2: DESCRIPTIVE ANALYSIS FOR JUDICIAL EFFECTS")
    print("=" * 80)

    # 1. Rapporteur profiles
    print("\nAnalyzing rapporteur profiles...")
    rapporteur_profiles = analyze_rapporteur_profiles(holdings)
    print_rapporteur_profiles(rapporteur_profiles, rapporteur_groupings)

    # 2. Chamber profiles
    print("\nAnalyzing chamber profiles...")
    chamber_profiles = analyze_chamber_profiles(holdings)
    print_chamber_profiles(chamber_profiles)

    # 3. Judge exposure analysis
    print("\nAnalyzing individual judge exposure...")
    judge_exposure = analyze_judge_exposure(holdings, judge_stats)
    print_judge_exposure(judge_exposure, min_cases=10)

    # 4. Network diagnostics
    print("\nAnalyzing co-occurrence network...")
    network_stats = analyze_network(cooccurrence_matrix, judges)

    # Save results
    save_descriptive_results(rapporteur_profiles, chamber_profiles, judge_exposure, network_stats)

    print("\n" + "=" * 80)
    print("PHASE 2 COMPLETE: Descriptive analysis finished!")
    print("=" * 80)

    # Key findings summary
    print("\n" + "=" * 80)
    print("KEY FINDINGS SUMMARY")
    print("=" * 80)

    # Rapporteur findings
    print("\n1. RAPPORTEUR FINDINGS:")
    overall_rate = sum(p['pro_ds_count'] for p in rapporteur_profiles.values()) / sum(p['n_holdings'] for p in rapporteur_profiles.values())

    high_raps = [(r, p) for r, p in rapporteur_profiles.items() if p['n_holdings'] >= 10 and p['ci_lower'] > overall_rate]
    low_raps = [(r, p) for r, p in rapporteur_profiles.items() if p['n_holdings'] >= 10 and p['ci_upper'] < overall_rate]

    if high_raps:
        print(f"   Significantly ABOVE average ({overall_rate:.1%}):")
        for r, p in high_raps:
            print(f"     - {r}: {p['pro_ds_rate']:.1%} [{p['ci_lower']:.1%}, {p['ci_upper']:.1%}]")
    if low_raps:
        print(f"   Significantly BELOW average ({overall_rate:.1%}):")
        for r, p in low_raps:
            print(f"     - {r}: {p['pro_ds_rate']:.1%} [{p['ci_lower']:.1%}, {p['ci_upper']:.1%}]")
    if not high_raps and not low_raps:
        print(f"   No rapporteur CIs exclude overall rate ({overall_rate:.1%})")

    # Chamber findings
    print("\n2. CHAMBER FINDINGS:")
    sig_above = [(c, p) for c, p in chamber_profiles.items() if p['n_holdings'] >= 10 and p['ci_lower'] > overall_rate]
    sig_below = [(c, p) for c, p in chamber_profiles.items() if p['n_holdings'] >= 10 and p['ci_upper'] < overall_rate]

    if sig_above:
        print(f"   Significantly ABOVE average:")
        for c, p in sig_above:
            print(f"     - {c}: {p['pro_ds_rate']:.1%}")
    if sig_below:
        print(f"   Significantly BELOW average:")
        for c, p in sig_below:
            print(f"     - {c}: {p['pro_ds_rate']:.1%}")

    # Network findings
    print(f"\n3. NETWORK FINDINGS:")
    print(f"   Density: {network_stats['density']:.3f}")
    print(f"   Avg clustering: {network_stats['avg_clustering']:.3f}")
    if network_stats['density'] > 0.5:
        print("   ⚠ High density limits ability to isolate individual judge effects")

    return {
        'rapporteur_profiles': rapporteur_profiles,
        'chamber_profiles': chamber_profiles,
        'judge_exposure': judge_exposure,
        'network_stats': network_stats
    }

if __name__ == "__main__":
    results = main()
