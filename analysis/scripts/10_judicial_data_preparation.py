#!/usr/bin/env python3
"""
10_judicial_data_preparation.py
================================
Phase 1: Data Preparation for Judicial Effects Analysis

This script:
1. Merges judge/rapporteur data into the holdings dataset
2. Creates rapporteur grouping variables (HIGH/MEDIUM/LOW volume)
3. Generates individual judge exposure indicators
4. Builds judge co-occurrence matrix for network analysis
5. Saves prepared dataset for subsequent analysis phases
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CASES_JSON = PROJECT_ROOT / "parsed-coded" / "cases.json"
HOLDINGS_CSV = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def load_cases_json():
    """Load cases with judge information."""
    with open(CASES_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_holdings_csv():
    """Load prepared holdings data."""
    holdings = []
    with open(HOLDINGS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            holdings.append(row)
    return holdings

def create_case_judge_lookup(cases):
    """Create lookup from case_id to judge information."""
    lookup = {}
    for case in cases:
        case_id = case.get('case_id', '')
        lookup[case_id] = {
            'judges': case.get('judges', []) or [],
            'judge_rapporteur': case.get('judge_rapporteur', ''),
            'advocate_general': case.get('advocate_general', ''),
            'chamber': case.get('chamber', '')
        }
    return lookup

def analyze_rapporteur_distribution(cases):
    """Analyze rapporteur case counts and create groupings."""
    rapporteur_cases = defaultdict(list)
    rapporteur_holdings = defaultdict(int)

    for case in cases:
        rap = case.get('judge_rapporteur', '')
        if rap:
            rapporteur_cases[rap].append(case.get('case_id'))
            rapporteur_holdings[rap] += len(case.get('holdings', []))

    # Create groupings based on case count
    groupings = {}
    for rap, case_list in rapporteur_cases.items():
        n_cases = len(case_list)
        n_holdings = rapporteur_holdings[rap]

        if n_cases >= 10:
            group = 'HIGH_VOLUME'
        elif n_cases >= 3:
            group = 'MEDIUM_VOLUME'
        else:
            group = 'LOW_VOLUME'

        groupings[rap] = {
            'n_cases': n_cases,
            'n_holdings': n_holdings,
            'group': group,
            'cases': case_list
        }

    return groupings

def get_all_unique_judges(cases):
    """Get set of all unique judges across all panels."""
    all_judges = set()
    for case in cases:
        judges = case.get('judges', []) or []
        all_judges.update(judges)
    return sorted(all_judges)

def build_cooccurrence_matrix(cases, all_judges):
    """Build judge co-occurrence matrix."""
    # Initialize matrix
    judge_to_idx = {j: i for i, j in enumerate(all_judges)}
    n = len(all_judges)
    matrix = [[0] * n for _ in range(n)]

    # Count co-occurrences
    for case in cases:
        judges = case.get('judges', []) or []
        for i, j1 in enumerate(judges):
            for j2 in judges[i:]:
                idx1 = judge_to_idx.get(j1)
                idx2 = judge_to_idx.get(j2)
                if idx1 is not None and idx2 is not None:
                    matrix[idx1][idx2] += 1
                    if idx1 != idx2:
                        matrix[idx2][idx1] += 1

    return matrix, judge_to_idx

def analyze_judge_participation(cases):
    """Analyze individual judge participation statistics."""
    judge_stats = defaultdict(lambda: {
        'n_cases': 0,
        'n_holdings': 0,
        'cases': [],
        'chambers': defaultdict(int),
        'as_rapporteur': 0,
        'years': []
    })

    for case in cases:
        judges = case.get('judges', []) or []
        rapporteur = case.get('judge_rapporteur', '')
        chamber = case.get('chamber', '')
        n_holdings = len(case.get('holdings', []))
        case_id = case.get('case_id', '')

        # Extract year
        date_str = case.get('judgment_date', '')
        try:
            year = int(date_str[:4]) if date_str else 0
        except:
            year = 0

        for judge in judges:
            judge_stats[judge]['n_cases'] += 1
            judge_stats[judge]['n_holdings'] += n_holdings
            judge_stats[judge]['cases'].append(case_id)
            judge_stats[judge]['chambers'][chamber] += 1
            if year:
                judge_stats[judge]['years'].append(year)

            if judge == rapporteur:
                judge_stats[judge]['as_rapporteur'] += 1

    # Calculate derived stats
    for judge, stats in judge_stats.items():
        stats['primary_chamber'] = max(stats['chambers'], key=stats['chambers'].get) if stats['chambers'] else ''
        stats['year_range'] = f"{min(stats['years'])}-{max(stats['years'])}" if stats['years'] else ''
        stats['chambers'] = dict(stats['chambers'])  # Convert defaultdict

    return dict(judge_stats)

def merge_judge_data_into_holdings(holdings, case_lookup, rapporteur_groupings, all_judges):
    """Merge judge information into holdings dataset."""
    enhanced_holdings = []

    for holding in holdings:
        case_id = holding.get('case_id', '')
        case_info = case_lookup.get(case_id, {})

        # Create enhanced holding
        enhanced = dict(holding)

        # Add judge information
        judges = case_info.get('judges', [])
        enhanced['judges'] = ';'.join(judges) if judges else ''
        enhanced['judge_rapporteur'] = case_info.get('judge_rapporteur', '')
        enhanced['advocate_general'] = case_info.get('advocate_general', '')
        enhanced['panel_size'] = len(judges)

        # Add rapporteur grouping
        rap = enhanced['judge_rapporteur']
        if rap and rap in rapporteur_groupings:
            enhanced['rapporteur_group'] = rapporteur_groupings[rap]['group']
            enhanced['rapporteur_n_cases'] = rapporteur_groupings[rap]['n_cases']
        else:
            enhanced['rapporteur_group'] = 'UNKNOWN'
            enhanced['rapporteur_n_cases'] = 0

        # Add individual judge exposure indicators
        for judge in all_judges:
            col_name = f"judge_{judge.replace(' ', '_').replace('.', '').replace('-', '_')}"
            enhanced[col_name] = 1 if judge in judges else 0

        enhanced_holdings.append(enhanced)

    return enhanced_holdings

def save_enhanced_holdings(holdings, output_path):
    """Save enhanced holdings to CSV."""
    if not holdings:
        return

    fieldnames = list(holdings[0].keys())

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(holdings)

def save_cooccurrence_matrix(matrix, judges, output_path):
    """Save co-occurrence matrix to CSV."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow([''] + judges)
        # Data rows
        for i, judge in enumerate(judges):
            writer.writerow([judge] + matrix[i])

def save_judge_stats(judge_stats, output_path):
    """Save judge statistics to JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(judge_stats, f, indent=2, ensure_ascii=False)

def save_rapporteur_groupings(groupings, output_path):
    """Save rapporteur groupings to JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(groupings, f, indent=2, ensure_ascii=False)

def print_summary_report(cases, rapporteur_groupings, judge_stats, all_judges):
    """Print summary of data preparation."""
    print("=" * 70)
    print("PHASE 1: JUDICIAL DATA PREPARATION - SUMMARY REPORT")
    print("=" * 70)

    print(f"\n{'='*70}")
    print("1. DATA OVERVIEW")
    print("=" * 70)
    print(f"  Total cases: {len(cases)}")
    total_holdings = sum(len(c.get('holdings', [])) for c in cases)
    print(f"  Total holdings: {total_holdings}")
    print(f"  Unique judges: {len(all_judges)}")
    print(f"  Unique rapporteurs: {len(rapporteur_groupings)}")

    print(f"\n{'='*70}")
    print("2. RAPPORTEUR GROUPINGS")
    print("=" * 70)

    for group in ['HIGH_VOLUME', 'MEDIUM_VOLUME', 'LOW_VOLUME']:
        raps_in_group = [r for r, info in rapporteur_groupings.items() if info['group'] == group]
        total_cases = sum(rapporteur_groupings[r]['n_cases'] for r in raps_in_group)
        total_holdings = sum(rapporteur_groupings[r]['n_holdings'] for r in raps_in_group)
        print(f"\n  {group} (n={len(raps_in_group)} rapporteurs, {total_cases} cases, {total_holdings} holdings):")

        sorted_raps = sorted(raps_in_group, key=lambda r: -rapporteur_groupings[r]['n_cases'])
        for rap in sorted_raps:
            info = rapporteur_groupings[rap]
            print(f"    - {rap}: {info['n_cases']} cases, {info['n_holdings']} holdings")

    print(f"\n{'='*70}")
    print("3. PANEL SIZE DISTRIBUTION")
    print("=" * 70)

    panel_sizes = defaultdict(int)
    for case in cases:
        size = len(case.get('judges', []) or [])
        panel_sizes[size] += 1

    for size in sorted(panel_sizes.keys()):
        print(f"  {size} judges: {panel_sizes[size]} cases")

    print(f"\n{'='*70}")
    print("4. TOP JUDGES BY PANEL APPEARANCES")
    print("=" * 70)

    sorted_judges = sorted(judge_stats.items(), key=lambda x: -x[1]['n_cases'])[:15]
    print(f"\n  {'Judge':<25} {'Cases':>6} {'Holdings':>9} {'As Rapp':>8} {'Primary Chamber':<15}")
    print("  " + "-" * 65)
    for judge, stats in sorted_judges:
        print(f"  {judge:<25} {stats['n_cases']:>6} {stats['n_holdings']:>9} {stats['as_rapporteur']:>8} {stats['primary_chamber']:<15}")

    print(f"\n{'='*70}")
    print("5. CHAMBER DISTRIBUTION")
    print("=" * 70)

    chamber_counts = defaultdict(lambda: {'cases': 0, 'holdings': 0})
    for case in cases:
        chamber = case.get('chamber', 'UNKNOWN')
        chamber_counts[chamber]['cases'] += 1
        chamber_counts[chamber]['holdings'] += len(case.get('holdings', []))

    print(f"\n  {'Chamber':<20} {'Cases':>6} {'Holdings':>9}")
    print("  " + "-" * 37)
    for chamber in sorted(chamber_counts.keys(), key=lambda c: -chamber_counts[c]['cases']):
        print(f"  {chamber:<20} {chamber_counts[chamber]['cases']:>6} {chamber_counts[chamber]['holdings']:>9}")

    print(f"\n{'='*70}")
    print("6. CO-OCCURRENCE NETWORK SUMMARY")
    print("=" * 70)

    # Calculate network density
    n_judges = len(all_judges)
    max_edges = n_judges * (n_judges - 1) / 2

    # Count actual edges (co-occurrences)
    judge_pairs = set()
    for case in cases:
        judges = case.get('judges', []) or []
        for i, j1 in enumerate(judges):
            for j2 in judges[i+1:]:
                pair = tuple(sorted([j1, j2]))
                judge_pairs.add(pair)

    actual_edges = len(judge_pairs)
    density = actual_edges / max_edges if max_edges > 0 else 0

    print(f"\n  Nodes (judges): {n_judges}")
    print(f"  Possible edges: {int(max_edges)}")
    print(f"  Actual edges (co-occurrences): {actual_edges}")
    print(f"  Network density: {density:.3f}")

    if density > 0.5:
        print("\n  WARNING: High network density suggests substantial confounding")
        print("           Individual judge effects may be difficult to isolate")

    print(f"\n{'='*70}")
    print("7. OUTPUT FILES CREATED")
    print("=" * 70)
    print(f"\n  - holdings_judicial.csv: Enhanced holdings with judge data")
    print(f"  - judge_cooccurrence_matrix.csv: Judge co-occurrence matrix")
    print(f"  - judge_statistics.json: Individual judge participation stats")
    print(f"  - rapporteur_groupings.json: Rapporteur volume groupings")

def main():
    print("Loading data...")
    cases = load_cases_json()
    holdings = load_holdings_csv()

    print("Creating case-judge lookup...")
    case_lookup = create_case_judge_lookup(cases)

    print("Analyzing rapporteur distribution...")
    rapporteur_groupings = analyze_rapporteur_distribution(cases)

    print("Getting unique judges...")
    all_judges = get_all_unique_judges(cases)

    print("Analyzing judge participation...")
    judge_stats = analyze_judge_participation(cases)

    print("Building co-occurrence matrix...")
    cooccurrence_matrix, judge_to_idx = build_cooccurrence_matrix(cases, all_judges)

    print("Merging judge data into holdings...")
    enhanced_holdings = merge_judge_data_into_holdings(
        holdings, case_lookup, rapporteur_groupings, all_judges
    )

    # Save outputs
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    print("Saving enhanced holdings...")
    save_enhanced_holdings(enhanced_holdings, OUTPUT_PATH / "holdings_judicial.csv")

    print("Saving co-occurrence matrix...")
    save_cooccurrence_matrix(cooccurrence_matrix, all_judges, OUTPUT_PATH / "judge_cooccurrence_matrix.csv")

    print("Saving judge statistics...")
    save_judge_stats(judge_stats, OUTPUT_PATH / "judge_statistics.json")

    print("Saving rapporteur groupings...")
    save_rapporteur_groupings(rapporteur_groupings, OUTPUT_PATH / "rapporteur_groupings.json")

    # Print summary report
    print_summary_report(cases, rapporteur_groupings, judge_stats, all_judges)

    print(f"\n{'='*70}")
    print("PHASE 1 COMPLETE: Data preparation finished successfully!")
    print("=" * 70)

    return {
        'n_cases': len(cases),
        'n_holdings': len(enhanced_holdings),
        'n_judges': len(all_judges),
        'n_rapporteurs': len(rapporteur_groupings),
        'rapporteur_groupings': rapporteur_groupings,
        'judge_stats': judge_stats
    }

if __name__ == "__main__":
    results = main()
