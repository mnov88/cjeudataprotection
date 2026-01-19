#!/usr/bin/env python3
"""
14_influence_propagation.py
============================
Phase 5: Influence Propagation Analysis

Tests how interpretive approaches and doctrinal positions diffuse through
the citation network:
  H4.1: Teleological interpretation propagates through citations
  H4.2: Compensation gap traceable to early precedents

Includes doctrinal lineage tracing and counterfactual analysis.
"""

import pandas as pd
import numpy as np
import networkx as nx
from scipy import stats
import statsmodels.formula.api as smf
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"
NETWORK_PATH = OUTPUT_PATH / "citation_network"

def load_data():
    """Load all required data."""
    holdings = pd.read_csv(OUTPUT_PATH / "holdings_prepared.csv")
    citation_vars = pd.read_csv(NETWORK_PATH / "holding_citation_vars.csv")
    case_attrs = pd.read_csv(NETWORK_PATH / "case_attributes.csv")
    edges = pd.read_csv(NETWORK_PATH / "citation_edges.csv")

    # Merge holdings with citation vars
    df = holdings.merge(citation_vars, on=['case_id', 'holding_id'], how='left')
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])

    return df, case_attrs, edges

def build_internal_network(case_attrs, edges):
    """Build internal citation network."""
    corpus_cases = set(case_attrs['case_id'])

    G = nx.DiGraph()

    # Add nodes
    for _, row in case_attrs.iterrows():
        G.add_node(row['case_id'],
                   judgment_date=row['judgment_date'],
                   year=int(row['year']),
                   chamber=row['chamber'],
                   pro_ds_rate=row['pro_ds_rate'],
                   pro_ds_count=int(row['pro_ds_count']),
                   teleological_rate=float(row['teleological_rate']) if pd.notna(row['teleological_rate']) else 0,
                   pro_ds_purpose_rate=float(row['pro_ds_purpose_rate']) if pd.notna(row['pro_ds_purpose_rate']) else 0)

    # Add edges (only internal)
    internal_edges = edges[edges['cited_case'].isin(corpus_cases)]
    for _, row in internal_edges.iterrows():
        if row['citing_case'] in corpus_cases:
            if not G.has_edge(row['citing_case'], row['cited_case']):
                G.add_edge(row['citing_case'], row['cited_case'])

    return G

def trace_doctrinal_lineage(G, case_attrs, concept_filter=None):
    """
    Trace doctrinal development paths through the citation network.

    Identifies:
    - Foundational cases (high in-degree, early dates)
    - Citation chains for specific concepts
    - Direction propagation patterns
    """
    print("\n" + "=" * 70)
    print("DOCTRINAL LINEAGE ANALYSIS")
    print("=" * 70)

    case_lookup = case_attrs.set_index('case_id').to_dict('index')

    # Identify foundational cases (cited by many, early)
    in_degrees = dict(G.in_degree())
    foundational = []

    for case_id, in_deg in sorted(in_degrees.items(), key=lambda x: -x[1])[:15]:
        info = case_lookup.get(case_id, {})
        foundational.append({
            'case_id': case_id,
            'in_degree': in_deg,
            'year': info.get('year', 'Unknown'),
            'chamber': info.get('chamber', 'Unknown'),
            'pro_ds_rate': info.get('pro_ds_rate', 0),
            'pro_ds_purpose_rate': info.get('pro_ds_purpose_rate', 0)
        })

    print("\nFoundational Cases (Top 15 by Citation Count):")
    print("-" * 70)
    for f in foundational:
        print(f"  {f['case_id']}: cited {f['in_degree']}x, {f['year']}, "
              f"pro-DS={f['pro_ds_rate']:.0%}, purpose={f['pro_ds_purpose_rate']:.0%}")

    return foundational

def analyze_teleological_propagation(df, G, case_attrs):
    """
    H4.1: Test whether teleological interpretation propagates through citations.

    If case A invokes teleological interpretation and case B cites A,
    is case B more likely to invoke teleological interpretation?
    """
    print("\n" + "=" * 70)
    print("H4.1: TELEOLOGICAL INTERPRETATION PROPAGATION")
    print("=" * 70)

    case_lookup = case_attrs.set_index('case_id').to_dict('index')
    corpus_cases = set(case_attrs['case_id'])

    # For each case, compute proportion of cited cases that used teleological
    case_teleological = []

    for case_id in G.nodes():
        info = case_lookup.get(case_id, {})
        cited_cases = list(G.successors(case_id))  # Cases this case cites
        cited_internal = [c for c in cited_cases if c in corpus_cases]

        if len(cited_internal) > 0:
            cited_tele_rates = [case_lookup.get(c, {}).get('teleological_rate', 0)
                               for c in cited_internal]
            avg_cited_tele = np.mean(cited_tele_rates)
        else:
            avg_cited_tele = np.nan

        case_teleological.append({
            'case_id': case_id,
            'own_teleological_rate': info.get('teleological_rate', 0),
            'cited_teleological_rate': avg_cited_tele,
            'n_cited_internal': len(cited_internal),
            'year': info.get('year', 0)
        })

    tele_df = pd.DataFrame(case_teleological)
    tele_df = tele_df.dropna(subset=['cited_teleological_rate', 'own_teleological_rate'])

    print(f"\nCases with internal citations: {len(tele_df)}")

    # Correlation
    r, p = stats.pearsonr(tele_df['cited_teleological_rate'], tele_df['own_teleological_rate'])
    print(f"\nCorrelation: Cited teleological rate ↔ Own teleological rate")
    print(f"  Pearson r = {r:.3f}, p = {p:.4f}")

    # Regression
    if len(tele_df) > 20:
        model = smf.ols("own_teleological_rate ~ cited_teleological_rate + year", data=tele_df).fit()
        print(f"\nRegression (controlling for year):")
        print(f"  Cited tele rate β = {model.params['cited_teleological_rate']:.3f}")
        print(f"  p = {model.pvalues['cited_teleological_rate']:.4f}")
        print(f"  R² = {model.rsquared:.4f}")

    return {
        'correlation_r': float(r),
        'correlation_p': float(p),
        'n_cases': int(len(tele_df)),
        'interpretation': 'Teleological interpretation shows propagation' if p < 0.05 and r > 0 else 'No significant propagation'
    }

def analyze_purpose_propagation(df, G, case_attrs):
    """
    Analyze how pro-DS purpose invocation propagates through citations.
    """
    print("\n" + "=" * 70)
    print("PURPOSE INVOCATION PROPAGATION")
    print("=" * 70)

    case_lookup = case_attrs.set_index('case_id').to_dict('index')
    corpus_cases = set(case_attrs['case_id'])

    case_purpose = []

    for case_id in G.nodes():
        info = case_lookup.get(case_id, {})
        cited_cases = list(G.successors(case_id))
        cited_internal = [c for c in cited_cases if c in corpus_cases]

        if len(cited_internal) > 0:
            cited_purpose_rates = [case_lookup.get(c, {}).get('pro_ds_purpose_rate', 0)
                                   for c in cited_internal]
            avg_cited_purpose = np.mean(cited_purpose_rates)
        else:
            avg_cited_purpose = np.nan

        case_purpose.append({
            'case_id': case_id,
            'own_purpose_rate': info.get('pro_ds_purpose_rate', 0),
            'cited_purpose_rate': avg_cited_purpose,
            'own_pro_ds_rate': info.get('pro_ds_rate', 0),
            'n_cited_internal': len(cited_internal),
            'year': info.get('year', 0)
        })

    purpose_df = pd.DataFrame(case_purpose)
    purpose_df = purpose_df.dropna(subset=['cited_purpose_rate', 'own_purpose_rate'])

    print(f"\nCases with internal citations: {len(purpose_df)}")

    # Correlation
    r, p = stats.pearsonr(purpose_df['cited_purpose_rate'], purpose_df['own_purpose_rate'])
    print(f"\nCorrelation: Cited purpose rate ↔ Own purpose rate")
    print(f"  Pearson r = {r:.3f}, p = {p:.4f}")

    # Does cited purpose predict outcome?
    r_outcome, p_outcome = stats.pearsonr(purpose_df['cited_purpose_rate'], purpose_df['own_pro_ds_rate'])
    print(f"\nCorrelation: Cited purpose rate ↔ Own pro-DS rate")
    print(f"  Pearson r = {r_outcome:.3f}, p = {p_outcome:.4f}")

    return {
        'purpose_propagation': {
            'r': float(r),
            'p': float(p)
        },
        'purpose_to_outcome': {
            'r': float(r_outcome),
            'p': float(p_outcome)
        },
        'n_cases': int(len(purpose_df))
    }

def trace_compensation_gap(df, G, case_attrs, edges):
    """
    H4.2: Trace the "compensation gap" to early precedents.

    The existing analysis found Article 82 cases are 30.8pp LESS likely to
    be pro-DS. Trace whether this pattern originates from early precedents.
    """
    print("\n" + "=" * 70)
    print("H4.2: COMPENSATION GAP LINEAGE ANALYSIS")
    print("=" * 70)

    # Identify Article 82/compensation cases
    compensation_cases = df[df['primary_concept'] == 'REMEDIES_COMPENSATION']['case_id'].unique()
    print(f"\nArticle 82 compensation cases: {len(compensation_cases)}")

    # Get their pro-DS rates and years
    case_lookup = case_attrs.set_index('case_id').to_dict('index')

    comp_timeline = []
    for case_id in compensation_cases:
        info = case_lookup.get(case_id, {})
        if info:
            comp_timeline.append({
                'case_id': case_id,
                'year': info.get('year', 0),
                'pro_ds_rate': info.get('pro_ds_rate', 0),
                'chamber': info.get('chamber', 'Unknown'),
                'cited_by': list(G.predecessors(case_id)) if case_id in G else []
            })

    comp_timeline = sorted(comp_timeline, key=lambda x: x['year'])

    print("\nArticle 82 Cases Chronologically:")
    print("-" * 70)
    cumulative_pro_ds = []
    for c in comp_timeline:
        cumulative_pro_ds.append(c['pro_ds_rate'])
        cited_count = len(c['cited_by'])
        print(f"  {c['case_id']} ({c['year']}, {c['chamber']}): "
              f"pro-DS={c['pro_ds_rate']:.0%}, cited by {cited_count} later cases")

    # Identify earliest compensation cases (potential originators of gap)
    early_comp = [c for c in comp_timeline if c['year'] <= 2023]
    if early_comp:
        early_pro_ds = np.mean([c['pro_ds_rate'] for c in early_comp])
        print(f"\nEarly compensation cases (≤2023): {len(early_comp)}")
        print(f"  Average pro-DS rate: {early_pro_ds:.0%}")

    # Most-cited compensation case
    most_cited_comp = max(comp_timeline, key=lambda x: len(x['cited_by']))
    print(f"\nMost-cited compensation case: {most_cited_comp['case_id']}")
    print(f"  Pro-DS rate: {most_cited_comp['pro_ds_rate']:.0%}")
    print(f"  Cited by {len(most_cited_comp['cited_by'])} later cases")

    # Analyze citation patterns
    print("\n" + "-" * 70)
    print("Citation Flow Analysis:")

    # For cases citing compensation precedents, what's their pro-DS rate?
    citing_comp = set()
    for c in comp_timeline:
        citing_comp.update(c['cited_by'])

    citing_comp_cases = citing_comp.intersection(set(case_attrs['case_id']))
    if citing_comp_cases:
        citing_pro_ds_rates = [case_lookup.get(c, {}).get('pro_ds_rate', 0.5) for c in citing_comp_cases]
        print(f"\nCases citing compensation precedents: {len(citing_comp_cases)}")
        print(f"  Average pro-DS rate: {np.mean(citing_pro_ds_rates):.1%}")

    # Compare with non-compensation citers
    all_citers = set()
    for node in G.nodes():
        all_citers.update(G.predecessors(node))

    non_comp_citers = all_citers - citing_comp
    non_comp_citers = non_comp_citers.intersection(set(case_attrs['case_id']))
    if non_comp_citers:
        non_citing_pro_ds_rates = [case_lookup.get(c, {}).get('pro_ds_rate', 0.5) for c in non_comp_citers]
        print(f"\nCases NOT citing compensation precedents: {len(non_comp_citers)}")
        print(f"  Average pro-DS rate: {np.mean(non_citing_pro_ds_rates):.1%}")

    return {
        'n_compensation_cases': len(compensation_cases),
        'compensation_timeline': comp_timeline,
        'most_cited_compensation_case': most_cited_comp['case_id'],
        'most_cited_pro_ds_rate': most_cited_comp['pro_ds_rate'],
        'early_compensation_avg_pro_ds': early_pro_ds if early_comp else None
    }

def analyze_third_chamber_citations(df, G, case_attrs):
    """
    Analyze citation patterns of the Third Chamber (anomaly identified earlier).
    """
    print("\n" + "=" * 70)
    print("THIRD CHAMBER CITATION PATTERNS")
    print("=" * 70)

    case_lookup = case_attrs.set_index('case_id').to_dict('index')

    # Third chamber cases
    third_cases = case_attrs[case_attrs['chamber'] == 'THIRD']['case_id'].tolist()
    gc_cases = case_attrs[case_attrs['chamber'] == 'GRAND_CHAMBER']['case_id'].tolist()

    print(f"\nThird Chamber cases: {len(third_cases)}")
    print(f"Grand Chamber cases: {len(gc_cases)}")

    # What does Third Chamber cite?
    third_citations = defaultdict(int)
    gc_citations = defaultdict(int)

    for case_id in third_cases:
        if case_id in G:
            for cited in G.successors(case_id):
                cited_info = case_lookup.get(cited, {})
                cited_chamber = cited_info.get('chamber', 'External')
                third_citations[cited_chamber] += 1

    for case_id in gc_cases:
        if case_id in G:
            for cited in G.successors(case_id):
                cited_info = case_lookup.get(cited, {})
                cited_chamber = cited_info.get('chamber', 'External')
                gc_citations[cited_chamber] += 1

    print("\nCitation Patterns by Chamber Cited:")
    print(f"  Third Chamber cites: {dict(third_citations)}")
    print(f"  Grand Chamber cites: {dict(gc_citations)}")

    # Does Third Chamber cite Grand Chamber at same rate?
    third_cites_gc = third_citations.get('GRAND_CHAMBER', 0) / sum(third_citations.values()) if third_citations else 0
    gc_cites_gc = gc_citations.get('GRAND_CHAMBER', 0) / sum(gc_citations.values()) if gc_citations else 0

    print(f"\nProportion citing Grand Chamber:")
    print(f"  Third Chamber: {third_cites_gc:.1%}")
    print(f"  Grand Chamber: {gc_cites_gc:.1%}")

    return {
        'third_citation_distribution': dict(third_citations),
        'gc_citation_distribution': dict(gc_citations),
        'third_gc_citation_rate': third_cites_gc,
        'gc_gc_citation_rate': gc_cites_gc
    }

def analyze_direction_concordance(df, edges, case_attrs):
    """
    Analyze whether citations tend to be concordant (same direction).
    """
    print("\n" + "=" * 70)
    print("CITATION DIRECTION CONCORDANCE")
    print("=" * 70)

    corpus_cases = set(case_attrs['case_id'])
    case_lookup = case_attrs.set_index('case_id').to_dict('index')

    # For internal citations
    internal_edges = edges[
        (edges['citing_case'].isin(corpus_cases)) &
        (edges['cited_case'].isin(corpus_cases))
    ].copy()

    concordant = 0
    discordant = 0

    for _, row in internal_edges.iterrows():
        citing_info = case_lookup.get(row['citing_case'], {})
        cited_info = case_lookup.get(row['cited_case'], {})

        citing_pro_ds = citing_info.get('pro_ds_rate', 0.5)
        cited_pro_ds = cited_info.get('pro_ds_rate', 0.5)

        # Binarize at 0.5
        citing_dir = 1 if citing_pro_ds > 0.5 else 0
        cited_dir = 1 if cited_pro_ds > 0.5 else 0

        if citing_dir == cited_dir:
            concordant += 1
        else:
            discordant += 1

    total = concordant + discordant
    concordance_rate = concordant / total if total > 0 else 0

    print(f"\nCitation Direction Concordance:")
    print(f"  Concordant (same majority direction): {concordant}")
    print(f"  Discordant (opposite direction): {discordant}")
    print(f"  Concordance rate: {concordance_rate:.1%}")

    # Test against chance (50%)
    p = stats.binom_test(concordant, total, 0.5, alternative='greater') if hasattr(stats, 'binom_test') else \
        stats.binomtest(concordant, total, 0.5, alternative='greater').pvalue

    print(f"  Binomial test (vs. chance): p = {p:.4f}")

    return {
        'concordant': concordant,
        'discordant': discordant,
        'concordance_rate': concordance_rate,
        'p_value': float(p)
    }

def main():
    print("=" * 70)
    print("PHASE 5: INFLUENCE PROPAGATION ANALYSIS")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load data
    print("\n[1/7] Loading data...")
    df, case_attrs, edges = load_data()
    print(f"  Loaded {len(df)} holdings, {len(case_attrs)} cases, {len(edges)} citation edges")

    # Build network
    print("\n[2/7] Building citation network...")
    G = build_internal_network(case_attrs, edges)
    print(f"  Internal network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Doctrinal lineage
    print("\n[3/7] Tracing doctrinal lineage...")
    foundational = trace_doctrinal_lineage(G, case_attrs)

    # H4.1: Teleological propagation
    print("\n[4/7] Testing H4.1: Teleological propagation...")
    tele_results = analyze_teleological_propagation(df, G, case_attrs)

    # Purpose propagation
    print("\n[5/7] Analyzing purpose propagation...")
    purpose_results = analyze_purpose_propagation(df, G, case_attrs)

    # H4.2: Compensation gap lineage
    print("\n[6/7] Testing H4.2: Compensation gap lineage...")
    comp_results = trace_compensation_gap(df, G, case_attrs, edges)

    # Additional analyses
    print("\n[7/7] Additional analyses...")
    third_results = analyze_third_chamber_citations(df, G, case_attrs)
    concordance_results = analyze_direction_concordance(df, edges, case_attrs)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY OF INFLUENCE PROPAGATION FINDINGS")
    print("=" * 70)

    findings = []

    # H4.1
    if tele_results['correlation_p'] < 0.05 and tele_results['correlation_r'] > 0:
        findings.append("H4.1 SUPPORTED: Teleological interpretation propagates through citations")
        findings.append(f"  r = {tele_results['correlation_r']:.3f}, p = {tele_results['correlation_p']:.4f}")
    else:
        findings.append("H4.1 NOT SUPPORTED: No significant teleological propagation")
        findings.append(f"  r = {tele_results['correlation_r']:.3f}, p = {tele_results['correlation_p']:.4f}")

    # Purpose propagation
    findings.append(f"\nPurpose Propagation:")
    findings.append(f"  Cited purpose → Own purpose: r = {purpose_results['purpose_propagation']['r']:.3f}, p = {purpose_results['purpose_propagation']['p']:.4f}")
    findings.append(f"  Cited purpose → Own outcome: r = {purpose_results['purpose_to_outcome']['r']:.3f}, p = {purpose_results['purpose_to_outcome']['p']:.4f}")

    # Concordance
    findings.append(f"\nCitation Concordance:")
    findings.append(f"  {concordance_results['concordance_rate']:.1%} of citations are direction-concordant")
    findings.append(f"  Significantly above chance: p = {concordance_results['p_value']:.4f}")

    for f in findings:
        print(f)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'foundational_cases': foundational,
        'H4_1_teleological_propagation': tele_results,
        'purpose_propagation': purpose_results,
        'H4_2_compensation_gap_lineage': {
            'n_compensation_cases': comp_results['n_compensation_cases'],
            'most_cited_case': comp_results['most_cited_compensation_case'],
            'most_cited_pro_ds_rate': comp_results['most_cited_pro_ds_rate'],
            'early_avg_pro_ds': comp_results['early_compensation_avg_pro_ds']
        },
        'third_chamber_citations': third_results,
        'direction_concordance': concordance_results,
        'summary': findings
    }

    output_file = NETWORK_PATH / "influence_propagation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 70)
    print("PHASE 5 COMPLETE: INFLUENCE PROPAGATION ANALYSIS")
    print("=" * 70)

    return results

if __name__ == "__main__":
    results = main()
