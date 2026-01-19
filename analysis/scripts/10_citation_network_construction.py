#!/usr/bin/env python3
"""
10_citation_network_construction.py
====================================
Phase 1: Citation Network Construction

Builds citation networks from CJEU GDPR holdings data:
1. Case-level citation graph (G_case)
2. Internal-only citation subgraph (G_internal)
3. Holding-level citation data

Computes node attributes and exports network data for subsequent analysis.
"""

import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
# Fixed: Updated path from "parsed-coded" to "data/parsed"
DATA_PATH = PROJECT_ROOT / "data" / "parsed" / "holdings.csv"
PREPARED_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output" / "citation_network"

def load_data():
    """Load holdings data, using prepared if available."""
    if PREPARED_PATH.exists():
        print(f"Loading prepared data from: {PREPARED_PATH}")
        df = pd.read_csv(PREPARED_PATH)
    else:
        print(f"Loading raw data from: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
        # Create basic derived variables
        df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)
        df['judgment_date'] = pd.to_datetime(df['judgment_date'])
        df['year'] = df['judgment_date'].dt.year

    # Ensure date is datetime
    if df['judgment_date'].dtype == 'object':
        df['judgment_date'] = pd.to_datetime(df['judgment_date'])

    return df

def parse_cited_cases(cited_str):
    """Parse the cited_cases string into a list of case IDs."""
    if pd.isna(cited_str) or cited_str == '':
        return []
    return [c.strip() for c in str(cited_str).split(';') if c.strip()]

def build_citation_edges(df):
    """
    Extract all citation edges from holdings data.

    Returns:
        List of tuples: (citing_case, citing_holding_id, cited_case, citing_date)
    """
    edges = []

    for _, row in df.iterrows():
        citing_case = row['case_id']
        holding_id = row['holding_id']
        citing_date = row['judgment_date']

        cited_cases = parse_cited_cases(row.get('cited_cases', ''))

        for cited_case in cited_cases:
            edges.append({
                'citing_case': citing_case,
                'citing_holding_id': holding_id,
                'cited_case': cited_case,
                'citing_date': citing_date,
                'citing_direction': row['ruling_direction'],
                'citing_pro_ds': row.get('pro_ds', None),
                'citing_concept': row.get('primary_concept', None),
                'citing_chamber': row.get('chamber', None),
                'citing_pro_ds_purpose': row.get('pro_ds_purpose', None),
                'citing_teleological': row.get('teleological_present', None),
                'citing_level_shifting': row.get('level_shifting', None)
            })

    return pd.DataFrame(edges)

def identify_internal_cases(df, edge_df):
    """
    Identify which cited cases are within the GDPR corpus (internal).

    Returns:
        set of case IDs that are in the GDPR corpus
    """
    corpus_cases = set(df['case_id'].unique())
    cited_cases = set(edge_df['cited_case'].unique())

    internal_cited = corpus_cases.intersection(cited_cases)
    external_cited = cited_cases - corpus_cases

    print(f"\nCorpus cases: {len(corpus_cases)}")
    print(f"Unique cited cases: {len(cited_cases)}")
    print(f"  Internal (within corpus): {len(internal_cited)}")
    print(f"  External (outside corpus): {len(external_cited)}")

    return corpus_cases, internal_cited, external_cited

def compute_case_attributes(df):
    """
    Compute case-level attributes by aggregating holdings.

    Returns:
        DataFrame with one row per case
    """
    case_attrs = df.groupby('case_id').agg({
        'judgment_date': 'first',
        'chamber': 'first',
        'year': 'first',
        'pro_ds': ['sum', 'count', 'mean'],
        'ruling_direction': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'MIXED',
        'holding_id': 'count',
        'teleological_present': 'mean' if 'teleological_present' in df.columns else 'first',
        'pro_ds_purpose': 'mean' if 'pro_ds_purpose' in df.columns else 'first',
        'level_shifting': 'mean' if 'level_shifting' in df.columns else 'first',
        'primary_concept': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'OTHER'
    }).reset_index()

    # Flatten column names
    case_attrs.columns = ['case_id', 'judgment_date', 'chamber', 'year',
                          'pro_ds_count', 'holding_count', 'pro_ds_rate',
                          'dominant_direction', 'total_holdings',
                          'teleological_rate', 'pro_ds_purpose_rate',
                          'level_shifting_rate', 'dominant_concept']

    # Drop duplicate count column
    case_attrs = case_attrs.drop('total_holdings', axis=1)

    return case_attrs

def build_case_level_graph(edge_df, case_attrs, corpus_cases):
    """
    Build case-level directed citation graph.

    Nodes: All cases (corpus + external cited)
    Edges: Citation relationships (aggregated from holdings)
    """
    G = nx.DiGraph()

    # Add corpus nodes with attributes
    for _, row in case_attrs.iterrows():
        G.add_node(row['case_id'],
                   is_gdpr_corpus=True,
                   judgment_date=str(row['judgment_date']),
                   chamber=row['chamber'],
                   year=int(row['year']),
                   pro_ds_rate=float(row['pro_ds_rate']),
                   pro_ds_count=int(row['pro_ds_count']),
                   holding_count=int(row['holding_count']),
                   dominant_direction=row['dominant_direction'],
                   teleological_rate=float(row['teleological_rate']) if pd.notna(row['teleological_rate']) else 0.0,
                   pro_ds_purpose_rate=float(row['pro_ds_purpose_rate']) if pd.notna(row['pro_ds_purpose_rate']) else 0.0)

    # Add external cited cases (limited attributes)
    external_cases = set(edge_df['cited_case'].unique()) - corpus_cases
    for case_id in external_cases:
        G.add_node(case_id, is_gdpr_corpus=False)

    # Aggregate edges at case level
    case_edges = edge_df.groupby(['citing_case', 'cited_case']).agg({
        'citing_holding_id': 'count',  # Number of holdings citing this case
        'citing_direction': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'MIXED',
        'citing_pro_ds': 'mean'
    }).reset_index()

    case_edges.columns = ['citing_case', 'cited_case', 'citation_weight',
                          'citing_dominant_direction', 'citing_pro_ds_rate']

    # Add edges
    for _, row in case_edges.iterrows():
        G.add_edge(row['citing_case'], row['cited_case'],
                   weight=int(row['citation_weight']),
                   citing_dominant_direction=row['citing_dominant_direction'],
                   citing_pro_ds_rate=float(row['citing_pro_ds_rate']) if pd.notna(row['citing_pro_ds_rate']) else None)

    return G, case_edges

def build_internal_graph(G_case, corpus_cases):
    """
    Extract subgraph of internal citations only.
    """
    internal_nodes = [n for n in G_case.nodes() if G_case.nodes[n].get('is_gdpr_corpus', False)]
    G_internal = G_case.subgraph(internal_nodes).copy()
    return G_internal

def compute_network_metrics(G, name=""):
    """Compute basic network metrics."""
    metrics = {
        'name': name,
        'n_nodes': G.number_of_nodes(),
        'n_edges': G.number_of_edges(),
        'density': nx.density(G),
        'is_dag': nx.is_directed_acyclic_graph(G),
    }

    # Only compute for DAGs (should always be true for citation networks)
    if metrics['is_dag'] and G.number_of_nodes() > 0:
        # Weakly connected components
        wcc = list(nx.weakly_connected_components(G))
        metrics['n_weakly_connected_components'] = len(wcc)
        metrics['largest_wcc_size'] = max(len(c) for c in wcc) if wcc else 0

    # Degree statistics
    if G.number_of_nodes() > 0:
        in_degrees = [d for n, d in G.in_degree()]
        out_degrees = [d for n, d in G.out_degree()]

        metrics['avg_in_degree'] = np.mean(in_degrees)
        metrics['max_in_degree'] = max(in_degrees)
        metrics['avg_out_degree'] = np.mean(out_degrees)
        metrics['max_out_degree'] = max(out_degrees)

    return metrics

def compute_node_centralities(G):
    """Compute centrality metrics for each node."""
    centralities = {}

    if G.number_of_nodes() == 0:
        return centralities

    # In-degree (citation count - how often cited)
    in_degree = dict(G.in_degree())

    # Out-degree (how many cases cited)
    out_degree = dict(G.out_degree())

    # PageRank
    try:
        pagerank = nx.pagerank(G, alpha=0.85)
    except:
        pagerank = {n: 0 for n in G.nodes()}

    # Betweenness (for DAGs)
    try:
        betweenness = nx.betweenness_centrality(G)
    except:
        betweenness = {n: 0 for n in G.nodes()}

    # HITS (hubs and authorities)
    try:
        hubs, authorities = nx.hits(G, max_iter=100)
    except:
        hubs = {n: 0 for n in G.nodes()}
        authorities = {n: 0 for n in G.nodes()}

    for node in G.nodes():
        centralities[node] = {
            'in_degree': in_degree.get(node, 0),
            'out_degree': out_degree.get(node, 0),
            'pagerank': pagerank.get(node, 0),
            'betweenness': betweenness.get(node, 0),
            'hub_score': hubs.get(node, 0),
            'authority_score': authorities.get(node, 0)
        }

    return centralities

def compute_citation_derived_variables(df, edge_df, case_attrs, G_internal, centralities):
    """
    Compute citation-derived variables for each holding.

    These variables will be used in regression analysis.
    """
    # Create case-level lookup for cited case attributes
    case_lookup = case_attrs.set_index('case_id').to_dict('index')
    corpus_cases = set(case_attrs['case_id'])

    # New columns to add
    new_vars = []

    for idx, row in df.iterrows():
        citing_case = row['case_id']
        cited_cases_list = parse_cited_cases(row.get('cited_cases', ''))

        # Basic citation counts
        total_citations = len(cited_cases_list)
        internal_citations = [c for c in cited_cases_list if c in corpus_cases]
        n_internal = len(internal_citations)

        # Precedent direction score (weighted avg pro-DS rate of cited internal cases)
        if n_internal > 0:
            pro_ds_rates = [case_lookup.get(c, {}).get('pro_ds_rate', 0.5)
                          for c in internal_citations]
            precedent_direction_score = np.mean(pro_ds_rates)
            predominantly_pro_ds_precedents = 1 if precedent_direction_score > 0.5 else 0
        else:
            precedent_direction_score = np.nan
            predominantly_pro_ds_precedents = np.nan

        # Cites Grand Chamber precedent
        cites_gc = any(case_lookup.get(c, {}).get('chamber') == 'GRAND_CHAMBER'
                      for c in internal_citations)

        # Precedent purpose invocation rate
        if n_internal > 0:
            purpose_rates = [case_lookup.get(c, {}).get('pro_ds_purpose_rate', 0)
                           for c in internal_citations]
            precedent_purpose_rate = np.mean(purpose_rates)
        else:
            precedent_purpose_rate = np.nan

        # Average centrality of cited cases
        if n_internal > 0:
            cited_pageranks = [centralities.get(c, {}).get('pagerank', 0)
                             for c in internal_citations]
            avg_cited_pagerank = np.mean(cited_pageranks)
            max_cited_pagerank = max(cited_pageranks)
        else:
            avg_cited_pagerank = np.nan
            max_cited_pagerank = np.nan

        # Citing case centrality
        citing_centrality = centralities.get(citing_case, {})

        new_vars.append({
            'case_id': citing_case,
            'holding_id': row['holding_id'],
            'total_citations': total_citations,
            'internal_citations': n_internal,
            'external_citations': total_citations - n_internal,
            'precedent_direction_score': precedent_direction_score,
            'predominantly_pro_ds_precedents': predominantly_pro_ds_precedents,
            'cites_gc_precedent': int(cites_gc),
            'precedent_purpose_rate': precedent_purpose_rate,
            'avg_cited_pagerank': avg_cited_pagerank,
            'max_cited_pagerank': max_cited_pagerank,
            'citing_case_pagerank': citing_centrality.get('pagerank', np.nan),
            'citing_case_in_degree': citing_centrality.get('in_degree', 0),
            'citing_case_authority': citing_centrality.get('authority_score', np.nan)
        })

    return pd.DataFrame(new_vars)

def find_most_cited_cases(G_internal, case_attrs, n=15):
    """Find the most frequently cited cases within the corpus."""
    in_degrees = dict(G_internal.in_degree())

    # Sort by in-degree
    sorted_cases = sorted(in_degrees.items(), key=lambda x: -x[1])[:n]

    results = []
    case_lookup = case_attrs.set_index('case_id').to_dict('index')

    for case_id, citations in sorted_cases:
        info = case_lookup.get(case_id, {})
        results.append({
            'case_id': case_id,
            'times_cited': citations,
            'chamber': info.get('chamber', 'Unknown'),
            'year': info.get('year', 'Unknown'),
            'pro_ds_rate': info.get('pro_ds_rate', 0),
            'holding_count': info.get('holding_count', 0)
        })

    return pd.DataFrame(results)

def find_most_citing_cases(G_internal, case_attrs, n=15):
    """Find cases that cite the most other cases."""
    out_degrees = dict(G_internal.out_degree())

    sorted_cases = sorted(out_degrees.items(), key=lambda x: -x[1])[:n]

    results = []
    case_lookup = case_attrs.set_index('case_id').to_dict('index')

    for case_id, citations in sorted_cases:
        info = case_lookup.get(case_id, {})
        results.append({
            'case_id': case_id,
            'cases_cited': citations,
            'chamber': info.get('chamber', 'Unknown'),
            'year': info.get('year', 'Unknown'),
            'pro_ds_rate': info.get('pro_ds_rate', 0),
            'holding_count': info.get('holding_count', 0)
        })

    return pd.DataFrame(results)

def export_network_data(G_case, G_internal, edge_df, case_attrs,
                        citation_vars, centralities, metrics):
    """Export all network data to files."""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # 1. Edge list (all citations)
    edge_df.to_csv(OUTPUT_PATH / "citation_edges.csv", index=False)
    print(f"  Saved: citation_edges.csv ({len(edge_df)} edges)")

    # 2. Case attributes with centralities
    case_centralities = pd.DataFrame([
        {'case_id': case_id, **cent}
        for case_id, cent in centralities.items()
    ])
    case_full = case_attrs.merge(case_centralities, on='case_id', how='left')
    case_full.to_csv(OUTPUT_PATH / "case_attributes.csv", index=False)
    print(f"  Saved: case_attributes.csv ({len(case_full)} cases)")

    # 3. Citation-derived variables for holdings
    citation_vars.to_csv(OUTPUT_PATH / "holding_citation_vars.csv", index=False)
    print(f"  Saved: holding_citation_vars.csv ({len(citation_vars)} holdings)")

    # 4. Network metrics summary
    with open(OUTPUT_PATH / "network_metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"  Saved: network_metrics.json")

    # 5. Graph objects (edge lists for reconstruction)
    # Internal graph edges
    internal_edges = []
    for u, v, data in G_internal.edges(data=True):
        internal_edges.append({
            'citing_case': u,
            'cited_case': v,
            **data
        })
    pd.DataFrame(internal_edges).to_csv(OUTPUT_PATH / "internal_citation_edges.csv", index=False)
    print(f"  Saved: internal_citation_edges.csv ({len(internal_edges)} edges)")

    # 6. Node centralities (JSON for easy lookup)
    with open(OUTPUT_PATH / "node_centralities.json", 'w') as f:
        json.dump(centralities, f, indent=2)
    print(f"  Saved: node_centralities.json")

def main():
    print("=" * 70)
    print("PHASE 1: CITATION NETWORK CONSTRUCTION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # 1. Load data
    print("\n[1/8] Loading data...")
    df = load_data()
    print(f"  Loaded {len(df)} holdings from {df['case_id'].nunique()} cases")

    # 2. Build citation edges
    print("\n[2/8] Extracting citation edges...")
    edge_df = build_citation_edges(df)
    print(f"  Extracted {len(edge_df)} citation edges")

    if len(edge_df) == 0:
        print("\n  WARNING: No citation edges found!")
        print("  Checking cited_cases column...")
        print(df['cited_cases'].head(20))
        return

    # 3. Identify internal vs external cases
    print("\n[3/8] Identifying internal vs external citations...")
    corpus_cases, internal_cited, external_cited = identify_internal_cases(df, edge_df)

    # 4. Compute case-level attributes
    print("\n[4/8] Computing case-level attributes...")
    case_attrs = compute_case_attributes(df)
    print(f"  Computed attributes for {len(case_attrs)} cases")

    # 5. Build graphs
    print("\n[5/8] Building citation graphs...")
    G_case, case_edges = build_case_level_graph(edge_df, case_attrs, corpus_cases)
    G_internal = build_internal_graph(G_case, corpus_cases)

    print(f"  G_case: {G_case.number_of_nodes()} nodes, {G_case.number_of_edges()} edges")
    print(f"  G_internal: {G_internal.number_of_nodes()} nodes, {G_internal.number_of_edges()} edges")

    # 6. Compute network metrics
    print("\n[6/8] Computing network metrics...")
    metrics_case = compute_network_metrics(G_case, "G_case (full)")
    metrics_internal = compute_network_metrics(G_internal, "G_internal (corpus only)")

    metrics = {
        'full_network': metrics_case,
        'internal_network': metrics_internal,
        'summary': {
            'total_corpus_cases': len(corpus_cases),
            'total_citation_edges': len(edge_df),
            'internal_citations': len(edge_df[edge_df['cited_case'].isin(corpus_cases)]),
            'external_citations': len(edge_df[~edge_df['cited_case'].isin(corpus_cases)]),
            'cases_with_internal_citations': G_internal.number_of_edges()
        }
    }

    print(f"\n  Full Network Metrics:")
    for k, v in metrics_case.items():
        print(f"    {k}: {v}")

    print(f"\n  Internal Network Metrics:")
    for k, v in metrics_internal.items():
        print(f"    {k}: {v}")

    # 7. Compute centralities
    print("\n[7/8] Computing node centralities...")
    centralities = compute_node_centralities(G_internal)
    print(f"  Computed centralities for {len(centralities)} nodes")

    # Most cited cases
    print("\n  Top 10 Most-Cited Cases (within corpus):")
    most_cited = find_most_cited_cases(G_internal, case_attrs, n=10)
    print(most_cited.to_string(index=False))

    print("\n  Top 10 Most-Citing Cases:")
    most_citing = find_most_citing_cases(G_internal, case_attrs, n=10)
    print(most_citing.to_string(index=False))

    # Add to metrics
    metrics['most_cited_cases'] = most_cited.to_dict('records')
    metrics['most_citing_cases'] = most_citing.to_dict('records')

    # 8. Compute citation-derived variables
    print("\n[8/8] Computing citation-derived variables for holdings...")
    citation_vars = compute_citation_derived_variables(
        df, edge_df, case_attrs, G_internal, centralities
    )
    print(f"  Created {len(citation_vars.columns)} new variables for {len(citation_vars)} holdings")

    # Variable summary
    print("\n  Citation Variable Summary:")
    for col in citation_vars.columns:
        if col not in ['case_id', 'holding_id']:
            if citation_vars[col].dtype in ['float64', 'int64']:
                valid = citation_vars[col].dropna()
                print(f"    {col}: mean={valid.mean():.3f}, range=[{valid.min():.3f}, {valid.max():.3f}]")

    # Export
    print("\n" + "=" * 70)
    print("EXPORTING NETWORK DATA")
    print("=" * 70)
    export_network_data(G_case, G_internal, edge_df, case_attrs,
                       citation_vars, centralities, metrics)

    # Final summary
    print("\n" + "=" * 70)
    print("PHASE 1 COMPLETE: CITATION NETWORK CONSTRUCTION")
    print("=" * 70)
    print(f"\nKey Statistics:")
    print(f"  Total holdings analyzed: {len(df)}")
    print(f"  Total citation edges: {len(edge_df)}")
    print(f"  Internal citations: {metrics['summary']['internal_citations']}")
    print(f"  External citations: {metrics['summary']['external_citations']}")
    print(f"  Cases in internal network: {G_internal.number_of_nodes()}")
    print(f"  Internal network density: {metrics_internal['density']:.4f}")
    print(f"  Network is DAG: {metrics_internal['is_dag']}")

    print(f"\nOutput files saved to: {OUTPUT_PATH}")

    return df, edge_df, G_case, G_internal, case_attrs, citation_vars, centralities, metrics

if __name__ == "__main__":
    results = main()
