#!/usr/bin/env python3
"""
17_citation_concordance_analysis.py
=====================================
Citation-Direction Concordance Analysis of CJEU GDPR Holdings.

Core thesis: a coherent jurisprudence should cite precedent that supports its
conclusion. When the Court cites a pro-DS precedent while ruling pro-controller
(or vice versa), this is a "discordant citation" — either a principled
distinction (coherent) or a silent tension (incoherent).

This script extends the existing citation network analysis (scripts 10-15)
by examining:
1. Individual holding→cited case concordance/discordance pairs
2. Qualitative analysis of discordant citations
3. Concordance variation by domain, chamber, and temporal period
4. Anchor case analysis: which foundational cases generate the most discord
5. Cross-referencing with Approach 1 (coherence residual analysis) flags
6. Citation coherence scores per domain

Builds on existing data in analysis/output/citation_network/.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HOLDINGS_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
EDGES_PATH = PROJECT_ROOT / "analysis" / "output" / "citation_network" / "citation_edges.csv"
CASE_ATTRS_PATH = PROJECT_ROOT / "analysis" / "output" / "citation_network" / "case_attributes.csv"
INTERNAL_EDGES_PATH = PROJECT_ROOT / "analysis" / "output" / "citation_network" / "internal_citation_edges.csv"
COHERENCE_PATH = PROJECT_ROOT / "analysis" / "output" / "coherence" / "coherence_analysis.json"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output" / "citation_concordance"


# =============================================================================
# SECTION 1: DATA LOADING AND CITATION PAIR CONSTRUCTION
# =============================================================================

def load_all_data():
    """Load holdings, citation edges, and case attributes."""
    holdings = pd.read_csv(HOLDINGS_PATH)
    edges = pd.read_csv(EDGES_PATH)
    case_attrs = pd.read_csv(CASE_ATTRS_PATH)
    internal_edges = pd.read_csv(INTERNAL_EDGES_PATH)

    # Load coherence analysis results if available
    coherence_flags = None
    if COHERENCE_PATH.exists():
        with open(COHERENCE_PATH) as f:
            coherence_flags = json.load(f)

    print(f"Loaded {len(holdings)} holdings, {len(edges)} citation edges, "
          f"{len(case_attrs)} cases, {len(internal_edges)} internal edges")
    return holdings, edges, case_attrs, internal_edges, coherence_flags


def build_citation_pairs(edges, case_attrs, holdings):
    """
    Build individual holding→cited case citation pairs with direction data.

    For each citation edge (citing_holding → cited_case), attaches:
    - Citing holding direction
    - Cited case dominant direction and pro-DS rate
    - Concordance classification

    Only includes internal citations (cited case is within the GDPR corpus).
    """
    corpus_cases = set(case_attrs['case_id'])

    # Filter to internal citations only
    internal = edges[edges['cited_case'].isin(corpus_cases)].copy()

    # Build cited case direction lookup
    case_direction = case_attrs.set_index('case_id')[
        ['dominant_direction', 'pro_ds_rate', 'pro_ds_count', 'holding_count',
         'chamber', 'year', 'dominant_concept', 'pro_ds_purpose_rate']
    ].to_dict('index')

    # Build holding-level lookup for richer citing info
    holding_lookup = {}
    for _, row in holdings.iterrows():
        key = (row['case_id'], row['holding_id'])
        holding_lookup[key] = {
            'concept_cluster': row.get('concept_cluster', ''),
            'primary_concept': row.get('primary_concept', ''),
            'is_compensation': row.get('is_compensation', 0),
            'dominant_source': row.get('dominant_source', ''),
            'dominant_structure': row.get('dominant_structure', ''),
            'core_holding': str(row.get('core_holding', '')),
            'direction_justification': str(row.get('direction_justification', '')),
        }

    pairs = []
    for _, row in internal.iterrows():
        cited_info = case_direction.get(row['cited_case'], {})
        citing_key = (row['citing_case'], row['citing_holding_id'])
        citing_holding_info = holding_lookup.get(citing_key, {})

        cited_pro_ds_rate = cited_info.get('pro_ds_rate', None)
        citing_pro_ds = row['citing_pro_ds']

        # Concordance classification
        if cited_pro_ds_rate is None or pd.isna(citing_pro_ds):
            concordance = 'UNKNOWN'
        else:
            # Cited case is "pro-DS" if majority of its holdings are pro-DS
            cited_is_pro_ds = cited_pro_ds_rate > 0.5
            # Cited case is "pro-controller" if majority are not pro-DS
            cited_is_pro_controller = cited_pro_ds_rate < 0.5
            # Cited case is "mixed" if exactly 50/50
            citing_is_pro_ds = citing_pro_ds == 1

            if cited_is_pro_ds and citing_is_pro_ds:
                concordance = 'CONCORDANT_PRO_DS'  # Both pro-DS
            elif cited_is_pro_controller and not citing_is_pro_ds:
                concordance = 'CONCORDANT_PRO_CTRL'  # Both pro-controller
            elif cited_is_pro_ds and not citing_is_pro_ds:
                concordance = 'DISCORDANT_CITED_PRO_DS'  # Cited pro-DS, citing not
            elif cited_is_pro_controller and citing_is_pro_ds:
                concordance = 'DISCORDANT_CITED_PRO_CTRL'  # Cited pro-ctrl, citing pro-DS
            else:
                concordance = 'MIXED_CITED'  # Cited case is exactly 50/50

        pairs.append({
            # Citing holding info
            'citing_case': row['citing_case'],
            'citing_holding_id': row['citing_holding_id'],
            'citing_direction': row['citing_direction'],
            'citing_pro_ds': citing_pro_ds,
            'citing_concept': row.get('citing_concept', ''),
            'citing_chamber': row.get('citing_chamber', ''),
            'citing_pro_ds_purpose': row.get('citing_pro_ds_purpose', None),
            'citing_concept_cluster': citing_holding_info.get('concept_cluster', ''),
            'citing_is_compensation': citing_holding_info.get('is_compensation', 0),
            'citing_core_holding': citing_holding_info.get('core_holding', ''),
            'citing_justification': citing_holding_info.get('direction_justification', ''),
            # Cited case info
            'cited_case': row['cited_case'],
            'cited_direction': cited_info.get('dominant_direction', ''),
            'cited_pro_ds_rate': cited_pro_ds_rate,
            'cited_chamber': cited_info.get('chamber', ''),
            'cited_year': cited_info.get('year', None),
            'cited_concept': cited_info.get('dominant_concept', ''),
            'cited_purpose_rate': cited_info.get('pro_ds_purpose_rate', None),
            # Concordance
            'concordance': concordance,
            'is_concordant': concordance in ('CONCORDANT_PRO_DS', 'CONCORDANT_PRO_CTRL'),
            'is_discordant': concordance in ('DISCORDANT_CITED_PRO_DS',
                                              'DISCORDANT_CITED_PRO_CTRL'),
        })

    pairs_df = pd.DataFrame(pairs)

    print(f"\nBuilt {len(pairs_df)} internal citation pairs")
    print(f"  Concordance distribution:")
    for conc, count in pairs_df['concordance'].value_counts().items():
        pct = count / len(pairs_df) * 100
        print(f"    {conc}: {count} ({pct:.1f}%)")

    return pairs_df


# =============================================================================
# SECTION 2: AGGREGATE CONCORDANCE ANALYSIS
# =============================================================================

def aggregate_concordance(pairs_df):
    """
    Compute aggregate concordance statistics.

    Tests whether concordance is significantly above chance (50%).
    """
    print("\n" + "=" * 70)
    print("AGGREGATE CONCORDANCE ANALYSIS")
    print("=" * 70)

    # Exclude UNKNOWN and MIXED_CITED
    classified = pairs_df[pairs_df['concordance'].isin([
        'CONCORDANT_PRO_DS', 'CONCORDANT_PRO_CTRL',
        'DISCORDANT_CITED_PRO_DS', 'DISCORDANT_CITED_PRO_CTRL'
    ])].copy()

    n_total = len(classified)
    n_concordant = classified['is_concordant'].sum()
    n_discordant = classified['is_discordant'].sum()
    concordance_rate = n_concordant / n_total if n_total > 0 else 0

    # Binomial test: is concordance > 50%?
    binom_result = stats.binomtest(n_concordant, n_total, 0.5, alternative='greater')
    binom_p = binom_result.pvalue

    print(f"\n  Total classifiable citation pairs: {n_total}")
    print(f"  Concordant: {n_concordant} ({n_concordant/n_total*100:.1f}%)")
    print(f"  Discordant: {n_discordant} ({n_discordant/n_total*100:.1f}%)")
    print(f"  Binomial test (H₀: concordance ≤ 50%): p = {binom_p:.6f}")

    if binom_p < 0.05:
        print(f"  → Concordance is SIGNIFICANTLY above chance")
    else:
        print(f"  → Concordance is NOT significantly above chance")

    # Breakdown by type
    print(f"\n  Concordance breakdown:")
    for conc_type in ['CONCORDANT_PRO_DS', 'CONCORDANT_PRO_CTRL',
                       'DISCORDANT_CITED_PRO_DS', 'DISCORDANT_CITED_PRO_CTRL']:
        n = (classified['concordance'] == conc_type).sum()
        print(f"    {conc_type}: {n} ({n/n_total*100:.1f}%)")

    results = {
        'n_total': int(n_total),
        'n_concordant': int(n_concordant),
        'n_discordant': int(n_discordant),
        'concordance_rate': float(concordance_rate),
        'binom_p': float(binom_p),
    }

    return results, classified


# =============================================================================
# SECTION 3: DISCORDANT CITATION DEEP DIVE
# =============================================================================

def analyze_discordant_citations(pairs_df, classified):
    """
    Deep dive into discordant citations.

    For each discordant pair, identifies what kind of tension exists and
    whether the citing holding's reasoning engages with the cited precedent.
    """
    print("\n" + "=" * 70)
    print("DISCORDANT CITATION ANALYSIS")
    print("=" * 70)

    discordant = classified[classified['is_discordant']].copy()

    if len(discordant) == 0:
        print("  No discordant citations found.")
        return {}

    # --- Type 1: Cited pro-DS, citing NOT pro-DS ---
    type1 = discordant[discordant['concordance'] == 'DISCORDANT_CITED_PRO_DS']
    print(f"\n  TYPE 1: Cited pro-DS precedent, citing holding NOT pro-DS "
          f"({len(type1)} pairs)")
    print("  " + "-" * 60)
    print(f"  These represent potential tension: the Court cites a pro-data subject")
    print(f"  case while reaching a different conclusion.")

    type1_details = []
    if len(type1) > 0:
        # Group by citing holding for deduplicated view
        citing_groups = type1.groupby(['citing_case', 'citing_holding_id'])

        for (citing_case, holding_id), group in citing_groups:
            row = group.iloc[0]
            cited_cases = group['cited_case'].tolist()
            cited_rates = group['cited_pro_ds_rate'].tolist()

            print(f"\n    {citing_case} H{holding_id} ({row['citing_direction']}, "
                  f"{row['citing_concept']})")
            print(f"      Cites pro-DS: {', '.join(cited_cases)}")

            core = str(row.get('citing_core_holding', ''))[:150]
            print(f"      Holding: {core}...")

            type1_details.append({
                'citing_case': citing_case,
                'citing_holding_id': int(holding_id),
                'citing_direction': row['citing_direction'],
                'citing_concept': row['citing_concept'],
                'citing_concept_cluster': row.get('citing_concept_cluster', ''),
                'citing_chamber': row['citing_chamber'],
                'cited_cases': cited_cases,
                'cited_pro_ds_rates': [float(r) for r in cited_rates],
                'core_holding': str(row.get('citing_core_holding', '')),
                'justification': str(row.get('citing_justification', ''))
            })

    # --- Type 2: Cited pro-controller, citing IS pro-DS ---
    type2 = discordant[discordant['concordance'] == 'DISCORDANT_CITED_PRO_CTRL']
    print(f"\n\n  TYPE 2: Cited pro-controller precedent, citing holding IS pro-DS "
          f"({len(type2)} pairs)")
    print("  " + "-" * 60)
    print(f"  These represent the Court building on restrictive precedent while")
    print(f"  reaching a protective conclusion — potentially expanding protection.")

    type2_details = []
    if len(type2) > 0:
        citing_groups = type2.groupby(['citing_case', 'citing_holding_id'])

        for (citing_case, holding_id), group in citing_groups:
            row = group.iloc[0]
            cited_cases = group['cited_case'].tolist()
            cited_rates = group['cited_pro_ds_rate'].tolist()

            print(f"\n    {citing_case} H{holding_id} ({row['citing_direction']}, "
                  f"{row['citing_concept']})")
            print(f"      Cites pro-ctrl: {', '.join(cited_cases)}")

            core = str(row.get('citing_core_holding', ''))[:150]
            print(f"      Holding: {core}...")

            type2_details.append({
                'citing_case': citing_case,
                'citing_holding_id': int(holding_id),
                'citing_direction': row['citing_direction'],
                'citing_concept': row['citing_concept'],
                'citing_concept_cluster': row.get('citing_concept_cluster', ''),
                'citing_chamber': row['citing_chamber'],
                'cited_cases': cited_cases,
                'cited_pro_ds_rates': [float(r) for r in cited_rates],
                'core_holding': str(row.get('citing_core_holding', '')),
                'justification': str(row.get('citing_justification', ''))
            })

    return {
        'type1_cited_pro_ds_citing_not': type1_details,
        'type2_cited_pro_ctrl_citing_pro_ds': type2_details,
        'n_type1': len(type1),
        'n_type2': len(type2)
    }


# =============================================================================
# SECTION 4: CONCORDANCE BY DOMAIN, CHAMBER, AND TEMPORAL PERIOD
# =============================================================================

def concordance_by_dimension(pairs_df, classified):
    """
    Test whether concordance varies by concept cluster, chamber, and year.
    """
    print("\n" + "=" * 70)
    print("CONCORDANCE BY DIMENSION")
    print("=" * 70)

    dimension_results = {}

    # --- By citing concept cluster ---
    print("\n  By Citing Concept Cluster:")
    print(f"  {'Cluster':<22} {'N':>5} {'Conc':>5} {'Rate':>7} {'Disc':>5}")
    print("  " + "-" * 50)

    cluster_results = {}
    for cluster in sorted(classified['citing_concept_cluster'].dropna().unique()):
        mask = classified['citing_concept_cluster'] == cluster
        n = mask.sum()
        if n < 5:
            continue
        conc = classified.loc[mask, 'is_concordant'].sum()
        rate = conc / n if n > 0 else 0
        disc = n - conc

        print(f"  {cluster:<22} {n:>5} {conc:>5} {rate*100:>6.1f}% {disc:>5}")

        cluster_results[cluster] = {
            'n': int(n), 'concordant': int(conc),
            'rate': float(rate), 'discordant': int(disc)
        }

    dimension_results['by_cluster'] = cluster_results

    # Statistical test: is concordance associated with cluster?
    cluster_conc = classified.dropna(subset=['citing_concept_cluster'])
    if len(cluster_conc) > 0 and cluster_conc['citing_concept_cluster'].nunique() > 1:
        contingency = pd.crosstab(cluster_conc['citing_concept_cluster'],
                                   cluster_conc['is_concordant'])
        if contingency.shape[0] > 1 and contingency.shape[1] > 1:
            chi2, p, dof, expected = stats.chi2_contingency(contingency)
            n_ct = contingency.sum().sum()
            cramers_v = np.sqrt(chi2 / (n_ct * (min(contingency.shape) - 1)))
            print(f"\n  Chi-square test: χ²={chi2:.2f}, p={p:.4f}, Cramér's V={cramers_v:.3f}")
            dimension_results['cluster_chi2'] = {'chi2': float(chi2), 'p': float(p),
                                                  'cramers_v': float(cramers_v)}

    # --- By citing chamber ---
    print(f"\n  By Citing Chamber:")
    print(f"  {'Chamber':<20} {'N':>5} {'Conc':>5} {'Rate':>7} {'Disc':>5}")
    print("  " + "-" * 50)

    chamber_results = {}
    for chamber in sorted(classified['citing_chamber'].dropna().unique()):
        mask = classified['citing_chamber'] == chamber
        n = mask.sum()
        if n < 5:
            continue
        conc = classified.loc[mask, 'is_concordant'].sum()
        rate = conc / n if n > 0 else 0
        disc = n - conc

        print(f"  {chamber:<20} {n:>5} {conc:>5} {rate*100:>6.1f}% {disc:>5}")

        chamber_results[chamber] = {
            'n': int(n), 'concordant': int(conc),
            'rate': float(rate), 'discordant': int(disc)
        }

    dimension_results['by_chamber'] = chamber_results

    # --- By temporal period ---
    print(f"\n  By Temporal Period (citing holding's year):")

    # Parse year from citing_date if available
    if 'citing_date' in classified.columns:
        classified = classified.copy()
        classified['citing_year'] = pd.to_datetime(
            classified['citing_date'], errors='coerce').dt.year
    elif 'citing_case' in classified.columns:
        # Approximate from case_id
        pass

    # Use citing_date from the edges data
    edges_for_year = pd.read_csv(EDGES_PATH)
    edges_for_year['citing_year'] = pd.to_datetime(
        edges_for_year['citing_date'], errors='coerce').dt.year

    # Merge year into classified
    merge_keys = ['citing_case', 'citing_holding_id', 'cited_case']
    if all(k in classified.columns for k in merge_keys):
        year_map = edges_for_year.drop_duplicates(
            subset=merge_keys)[merge_keys + ['citing_year']]
        classified = classified.merge(year_map, on=merge_keys, how='left',
                                       suffixes=('', '_from_edges'))
        if 'citing_year_from_edges' in classified.columns:
            classified['citing_year'] = classified['citing_year_from_edges']

    if 'citing_year' in classified.columns:
        print(f"  {'Year':>6} {'N':>5} {'Conc':>5} {'Rate':>7}")
        print("  " + "-" * 30)

        year_results = {}
        for year in sorted(classified['citing_year'].dropna().unique()):
            mask = classified['citing_year'] == year
            n = mask.sum()
            if n < 3:
                continue
            conc = classified.loc[mask, 'is_concordant'].sum()
            rate = conc / n if n > 0 else 0

            print(f"  {int(year):>6} {n:>5} {conc:>5} {rate*100:>6.1f}%")
            year_results[int(year)] = {'n': int(n), 'concordant': int(conc),
                                        'rate': float(rate)}

        dimension_results['by_year'] = year_results

        # Temporal trend test
        years = classified.dropna(subset=['citing_year'])
        if len(years) > 10:
            rho, p = stats.spearmanr(years['citing_year'], years['is_concordant'].astype(int))
            print(f"\n  Temporal trend: Spearman ρ(year, concordance) = {rho:.3f}, p = {p:.4f}")
            dimension_results['temporal_trend'] = {'rho': float(rho), 'p': float(p)}

    return dimension_results


# =============================================================================
# SECTION 5: ANCHOR CASE ANALYSIS
# =============================================================================

def anchor_case_analysis(pairs_df, case_attrs, classified):
    """
    Analyze "anchor cases" — highly cited cases that generate the most
    discordant citations.

    An anchor case that generates many discordant citations may be a
    doctrinal pivot point: a precedent the Court relies on even when
    reaching different conclusions.
    """
    print("\n" + "=" * 70)
    print("ANCHOR CASE ANALYSIS")
    print("=" * 70)

    # Count citations per cited case
    cite_counts = classified.groupby('cited_case').agg(
        total_citations=('is_concordant', 'count'),
        concordant=('is_concordant', 'sum'),
        discordant=('is_discordant', 'sum'),
    ).reset_index()

    cite_counts['concordance_rate'] = cite_counts['concordant'] / cite_counts['total_citations']
    cite_counts['discord_rate'] = cite_counts['discordant'] / cite_counts['total_citations']

    # Merge case attributes
    case_info = case_attrs.set_index('case_id')[
        ['chamber', 'year', 'pro_ds_rate', 'dominant_direction', 'dominant_concept']
    ]
    cite_counts = cite_counts.merge(case_info, left_on='cited_case',
                                     right_index=True, how='left')

    # Sort by total citations
    cite_counts = cite_counts.sort_values('total_citations', ascending=False)

    print(f"\n  Top Anchor Cases (≥5 internal citations):")
    print(f"  {'Case':<35} {'Cited':>5} {'Conc':>5} {'Disc':>5} {'Rate':>7} "
          f"{'DS%':>5} {'Chamber':<15}")
    print("  " + "-" * 90)

    anchor_results = []
    for _, row in cite_counts.iterrows():
        if row['total_citations'] < 5:
            continue

        print(f"  {row['cited_case']:<35} {row['total_citations']:>5} "
              f"{row['concordant']:>5} {row['discordant']:>5} "
              f"{row['concordance_rate']*100:>6.1f}% "
              f"{row['pro_ds_rate']*100:>4.0f}% {row['chamber']:<15}")

        anchor_results.append({
            'case_id': row['cited_case'],
            'total_citations': int(row['total_citations']),
            'concordant': int(row['concordant']),
            'discordant': int(row['discordant']),
            'concordance_rate': float(row['concordance_rate']),
            'pro_ds_rate': float(row['pro_ds_rate']),
            'chamber': row['chamber'],
            'year': int(row['year']) if pd.notna(row['year']) else None,
            'dominant_direction': row['dominant_direction'],
            'dominant_concept': row['dominant_concept']
        })

    # Identify most discordant anchors
    most_discordant = cite_counts[cite_counts['total_citations'] >= 5].nlargest(
        5, 'discord_rate')

    print(f"\n  Most Discordant Anchor Cases (highest discord rate, ≥5 citations):")
    for _, row in most_discordant.iterrows():
        print(f"    {row['cited_case']}: {row['discordant']}/{row['total_citations']} "
              f"discordant ({row['discord_rate']*100:.1f}%), "
              f"DS rate={row['pro_ds_rate']*100:.0f}%")

    # Analyze discordant citations FROM most-discordant anchors
    print(f"\n  Discordant citations from top anchor cases:")
    for _, anchor_row in most_discordant.iterrows():
        anchor_id = anchor_row['cited_case']
        disc_from_anchor = classified[
            (classified['cited_case'] == anchor_id) &
            (classified['is_discordant'])
        ]

        if len(disc_from_anchor) == 0:
            continue

        print(f"\n    {anchor_id} (DS rate={anchor_row['pro_ds_rate']*100:.0f}%, "
              f"{anchor_row['dominant_direction']}):")

        for _, row in disc_from_anchor.iterrows():
            direction = row['citing_direction']
            concept = row.get('citing_concept', '')
            core = str(row.get('citing_core_holding', ''))[:100]
            print(f"      → {row['citing_case']} H{row['citing_holding_id']} "
                  f"({direction}, {concept})")
            if core:
                print(f"        {core}...")

    return anchor_results


# =============================================================================
# SECTION 6: CROSS-DOMAIN CITATION CONCORDANCE
# =============================================================================

def cross_domain_concordance(pairs_df, classified):
    """
    Analyze concordance when citations cross concept domains.

    Tests whether within-domain citations (same concept cluster) are more
    concordant than cross-domain citations.
    """
    print("\n" + "=" * 70)
    print("CROSS-DOMAIN CITATION CONCORDANCE")
    print("=" * 70)

    # We need citing concept cluster and cited concept
    # cited_concept comes from the case_attrs dominant_concept
    # We need to map cited_concept to its cluster
    concept_to_cluster = {
        # SCOPE
        'MATERIAL_SCOPE': 'SCOPE', 'TERRITORIAL_SCOPE': 'SCOPE',
        'HOUSEHOLD_EXEMPTION': 'SCOPE', 'MEDIA_EXEMPTION': 'SCOPE',
        'LAW_ENFORCEMENT': 'SCOPE',
        # ACTORS
        'CONTROLLER_DEFINITION': 'ACTORS', 'PROCESSOR_DEFINITION': 'ACTORS',
        'JOINT_CONTROLLERS_DEFINITION': 'ACTORS', 'DPO_STATUS': 'ACTORS',
        # LAWFULNESS
        'CONSENT_BASIS': 'LAWFULNESS', 'CONTRACT_BASIS': 'LAWFULNESS',
        'LEGAL_OBLIGATION_BASIS': 'LAWFULNESS', 'PUBLIC_INTEREST_BASIS': 'LAWFULNESS',
        'LEGITIMATE_INTERESTS': 'LAWFULNESS', 'CONSENT_DEFINITION': 'LAWFULNESS',
        # PRINCIPLES
        'DATA_PROTECTION_PRINCIPLES': 'PRINCIPLES', 'TRANSPARENCY': 'PRINCIPLES',
        'DATA_MINIMISATION': 'PRINCIPLES',
        # RIGHTS
        'RIGHT_OF_ACCESS': 'RIGHTS', 'RIGHT_TO_ERASURE': 'RIGHTS',
        'RIGHT_TO_OBJECT': 'RIGHTS', 'RIGHT_TO_RECTIFICATION': 'RIGHTS',
        'RIGHT_TO_RESTRICTION': 'RIGHTS', 'RIGHT_TO_PORTABILITY': 'RIGHTS',
        'RIGHT_NOT_AUTOMATED': 'RIGHTS',
        # SPECIAL_CATEGORIES
        'SPECIAL_CATEGORIES_CONDITIONS': 'SPECIAL_CATEGORIES',
        'SPECIAL_CATEGORIES_SCOPE': 'SPECIAL_CATEGORIES',
        # ENFORCEMENT
        'DPA_POWERS': 'ENFORCEMENT', 'DPA_INDEPENDENCE': 'ENFORCEMENT',
        'DPA_COOPERATION': 'ENFORCEMENT', 'ADMINISTRATIVE_FINES': 'ENFORCEMENT',
        'REMEDIES_COMPENSATION': 'ENFORCEMENT', 'JUDICIAL_REMEDY': 'ENFORCEMENT',
        'SUPERVISORY_AUTHORITY': 'ENFORCEMENT', 'DPA_OTHER': 'ENFORCEMENT',
        # OTHER
        'INTERNATIONAL_TRANSFERS': 'OTHER', 'MEMBER_STATE_DISCRETION': 'OTHER',
        'SECURITY': 'OTHER', 'OTHER': 'OTHER',
    }

    classified = classified.copy()
    classified['cited_cluster'] = classified['cited_concept'].map(concept_to_cluster)

    # Classify as within-domain or cross-domain
    classified['same_domain'] = (
        classified['citing_concept_cluster'] == classified['cited_cluster']
    )

    valid = classified.dropna(subset=['citing_concept_cluster', 'cited_cluster'])

    within = valid[valid['same_domain']]
    cross = valid[~valid['same_domain']]

    within_rate = within['is_concordant'].mean() if len(within) > 0 else 0
    cross_rate = cross['is_concordant'].mean() if len(cross) > 0 else 0

    print(f"\n  Within-domain citations: {len(within)}, concordance rate: {within_rate*100:.1f}%")
    print(f"  Cross-domain citations:  {len(cross)}, concordance rate: {cross_rate*100:.1f}%")

    # Fisher's exact test
    if len(within) > 0 and len(cross) > 0:
        contingency = pd.crosstab(valid['same_domain'], valid['is_concordant'])
        if contingency.shape == (2, 2):
            odds_ratio, fisher_p = stats.fisher_exact(contingency)
            print(f"\n  Fisher's exact test: OR={odds_ratio:.3f}, p={fisher_p:.4f}")

            if fisher_p < 0.05:
                if within_rate > cross_rate:
                    print(f"  → Within-domain citations are SIGNIFICANTLY more concordant")
                else:
                    print(f"  → Cross-domain citations are SIGNIFICANTLY more concordant")
            else:
                print(f"  → No significant difference in concordance by domain match")
        else:
            fisher_p = None
            odds_ratio = None
    else:
        fisher_p = None
        odds_ratio = None

    # Cross-domain concordance matrix
    print(f"\n  Concordance rate by citing→cited domain pairs (≥3 citations):")
    print(f"  {'Citing→Cited':<40} {'N':>4} {'Rate':>7}")
    print("  " + "-" * 55)

    domain_pairs = valid.groupby(
        ['citing_concept_cluster', 'cited_cluster']
    ).agg(
        n=('is_concordant', 'count'),
        concordant=('is_concordant', 'sum')
    ).reset_index()
    domain_pairs['rate'] = domain_pairs['concordant'] / domain_pairs['n']
    domain_pairs = domain_pairs.sort_values('n', ascending=False)

    pair_results = {}
    for _, row in domain_pairs.iterrows():
        if row['n'] < 3:
            continue
        pair_key = f"{row['citing_concept_cluster']}→{row['cited_cluster']}"
        print(f"  {pair_key:<40} {row['n']:>4} {row['rate']*100:>6.1f}%")
        pair_results[pair_key] = {'n': int(row['n']),
                                   'rate': float(row['rate'])}

    return {
        'within_domain': {'n': int(len(within)), 'rate': float(within_rate)},
        'cross_domain': {'n': int(len(cross)), 'rate': float(cross_rate)},
        'fisher_p': float(fisher_p) if fisher_p is not None else None,
        'odds_ratio': float(odds_ratio) if odds_ratio is not None else None,
        'domain_pair_rates': pair_results
    }


# =============================================================================
# SECTION 7: CROSS-REFERENCE WITH COHERENCE FLAGS
# =============================================================================

def cross_reference_coherence_flags(pairs_df, classified, coherence_flags):
    """
    Cross-reference discordant citations with the holdings flagged as
    incoherent in the direction-prediction analysis (Approach 1).

    Tests whether flagged holdings are disproportionately involved in
    discordant citations.
    """
    print("\n" + "=" * 70)
    print("CROSS-REFERENCE: COHERENCE FLAGS AND DISCORDANT CITATIONS")
    print("=" * 70)

    if coherence_flags is None:
        print("  No coherence analysis results available. Skipping.")
        return {}

    # Extract flagged holdings from coherence analysis
    deep_dive = coherence_flags.get('deep_dive', [])
    flagged_holdings = set()
    for record in deep_dive:
        flagged_holdings.add((record['case_id'], record['holding_id']))

    print(f"  Holdings flagged as incoherent (Approach 1): {len(flagged_holdings)}")

    # Check which flagged holdings participate in discordant citations
    classified = classified.copy()
    classified['is_coherence_flagged'] = classified.apply(
        lambda row: (row['citing_case'], int(row['citing_holding_id']))
        in flagged_holdings, axis=1
    )

    n_flagged_citing = classified['is_coherence_flagged'].sum()
    n_unflagged_citing = len(classified) - n_flagged_citing

    if n_flagged_citing == 0:
        print("  No flagged holdings found among citing holdings.")
        return {'n_flagged_in_citations': 0}

    # Concordance rate for flagged vs unflagged
    flagged_rate = classified[classified['is_coherence_flagged']]['is_concordant'].mean()
    unflagged_rate = classified[~classified['is_coherence_flagged']]['is_concordant'].mean()

    print(f"\n  Flagged holdings as citers: {n_flagged_citing} citation pairs")
    print(f"    Concordance rate (flagged):   {flagged_rate*100:.1f}%")
    print(f"    Concordance rate (unflagged): {unflagged_rate*100:.1f}%")

    # Fisher's exact test
    contingency = pd.crosstab(classified['is_coherence_flagged'],
                               classified['is_concordant'])
    if contingency.shape == (2, 2):
        odds_ratio, fisher_p = stats.fisher_exact(contingency)
        print(f"    Fisher's exact: OR={odds_ratio:.3f}, p={fisher_p:.4f}")

        if fisher_p < 0.05:
            print(f"    → Flagged holdings have SIGNIFICANTLY different concordance")
        else:
            print(f"    → No significant difference in concordance for flagged holdings")
    else:
        fisher_p = None
        odds_ratio = None

    # List specific flagged holdings involved in discordant citations
    flagged_discordant = classified[
        classified['is_coherence_flagged'] & classified['is_discordant']
    ]

    if len(flagged_discordant) > 0:
        print(f"\n  Flagged holdings with discordant citations ({len(flagged_discordant)}):")
        for _, row in flagged_discordant.iterrows():
            print(f"    {row['citing_case']} H{row['citing_holding_id']} "
                  f"({row['citing_direction']}) → cites {row['cited_case']} "
                  f"({row['cited_direction']})")

    return {
        'n_flagged_in_citations': int(n_flagged_citing),
        'flagged_concordance_rate': float(flagged_rate),
        'unflagged_concordance_rate': float(unflagged_rate),
        'fisher_p': float(fisher_p) if fisher_p is not None else None,
        'n_flagged_discordant': int(len(flagged_discordant)),
    }


# =============================================================================
# SECTION 8: CITATION COHERENCE SCORES
# =============================================================================

def compute_citation_coherence_scores(aggregate_results, dimension_results,
                                       anchor_results, cross_domain_results,
                                       cross_ref_results, classified):
    """
    Compute summary citation coherence scores.
    """
    print("\n" + "=" * 70)
    print("CITATION COHERENCE SCORE SUMMARY")
    print("=" * 70)

    scores = {}

    # 1. Overall concordance
    concordance = aggregate_results['concordance_rate']
    scores['overall_concordance'] = {
        'metric': 'Citation concordance rate',
        'value': float(concordance),
        'interpretation': f'{concordance*100:.1f}% of internal citations are direction-concordant'
    }

    # 2. Concordance above chance
    conc_above_chance = concordance - 0.5
    scores['concordance_above_chance'] = {
        'metric': 'Concordance - 50%',
        'value': float(conc_above_chance),
        'p_value': float(aggregate_results['binom_p']),
        'interpretation': f'{conc_above_chance*100:.1f}pp above random'
    }

    # 3. Within vs cross-domain gap
    if cross_domain_results.get('within_domain') and cross_domain_results.get('cross_domain'):
        domain_gap = (cross_domain_results['within_domain']['rate'] -
                      cross_domain_results['cross_domain']['rate'])
        scores['domain_consistency'] = {
            'metric': 'Within-domain concordance - Cross-domain concordance',
            'value': float(domain_gap),
            'interpretation': ('Within-domain citations more concordant'
                             if domain_gap > 0 else
                             'Cross-domain citations more concordant')
        }

    # 4. Anchor stability (are top anchors mostly concordant?)
    if anchor_results:
        anchor_concordances = [a['concordance_rate'] for a in anchor_results
                              if a['total_citations'] >= 5]
        if anchor_concordances:
            mean_anchor_conc = np.mean(anchor_concordances)
            scores['anchor_concordance'] = {
                'metric': 'Mean concordance of anchor cases (≥5 cites)',
                'value': float(mean_anchor_conc),
                'interpretation': (f'{mean_anchor_conc*100:.1f}% concordance '
                                 f'for the most cited precedents')
            }

    # 5. Temporal stability
    temporal = dimension_results.get('temporal_trend', {})
    if temporal:
        scores['temporal_stability'] = {
            'metric': 'Spearman ρ(year, concordance)',
            'value': float(temporal.get('rho', 0)),
            'p_value': float(temporal.get('p', 1)),
            'interpretation': ('Concordance changing over time'
                             if temporal.get('p', 1) < 0.05 else
                             'Concordance stable over time')
        }

    # Display
    print(f"\n  {'Dimension':<30} {'Value':>8} {'Detail'}")
    print("  " + "-" * 70)
    for dim, data in scores.items():
        val = data['value']
        detail = data['interpretation']
        print(f"  {dim:<30} {val:>8.4f}  {detail}")

    # Overall assessment
    print(f"\n  CITATION COHERENCE ASSESSMENT:")
    print(f"  {'='*60}")

    if concordance > 0.65:
        print(f"  The CJEU's GDPR citation practice shows STRONG concordance:")
        print(f"  precedents are predominantly cited in direction-consistent contexts.")
    elif concordance > 0.55:
        print(f"  The CJEU's GDPR citation practice shows MODERATE concordance:")
        print(f"  precedents are more often cited concordantly than not, but")
        print(f"  substantial cross-direction citation occurs.")
    else:
        print(f"  The CJEU's GDPR citation practice shows WEAK concordance:")
        print(f"  citation direction is only marginally above chance.")

    n_disc = aggregate_results['n_discordant']
    n_total = aggregate_results['n_total']
    print(f"  {n_disc} of {n_total} classified citation pairs are discordant,")
    print(f"  indicating the Court regularly cites precedent while reaching")
    print(f"  different directional conclusions — though this may reflect")
    print(f"  legitimate distinguishing rather than doctrinal tension.")

    return scores


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("CITATION-DIRECTION CONCORDANCE ANALYSIS")
    print("CJEU GDPR Holdings")
    print("=" * 70)

    # 1. Load data
    holdings, edges, case_attrs, internal_edges, coherence_flags = load_all_data()

    # 2. Build citation pairs
    pairs_df = build_citation_pairs(edges, case_attrs, holdings)

    # 3. Aggregate concordance
    aggregate_results, classified = aggregate_concordance(pairs_df)

    # 4. Discordant citation deep dive
    discordant_results = analyze_discordant_citations(pairs_df, classified)

    # 5. Concordance by dimension
    dimension_results = concordance_by_dimension(pairs_df, classified)

    # 6. Anchor case analysis
    anchor_results = anchor_case_analysis(pairs_df, case_attrs, classified)

    # 7. Cross-domain concordance
    cross_domain_results = cross_domain_concordance(pairs_df, classified)

    # 8. Cross-reference with coherence flags
    cross_ref_results = cross_reference_coherence_flags(
        pairs_df, classified, coherence_flags)

    # 9. Citation coherence scores
    scores = compute_citation_coherence_scores(
        aggregate_results, dimension_results, anchor_results,
        cross_domain_results, cross_ref_results, classified)

    # ==========================================================================
    # SAVE RESULTS
    # ==========================================================================
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    # Per-pair data
    pairs_df.to_csv(OUTPUT_PATH / "citation_pairs.csv", index=False)

    # Comprehensive JSON
    all_results = {
        'aggregate': aggregate_results,
        'discordant_analysis': discordant_results,
        'by_dimension': dimension_results,
        'anchor_cases': anchor_results,
        'cross_domain': cross_domain_results,
        'cross_reference_coherence': cross_ref_results,
        'coherence_scores': scores,
    }

    with open(OUTPUT_PATH / "citation_concordance_analysis.json", 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {OUTPUT_PATH}")
    print(f"  - citation_pairs.csv   (per-pair concordance data)")
    print(f"  - citation_concordance_analysis.json (comprehensive results)")
    print(f"{'='*70}")

    return all_results


if __name__ == "__main__":
    results = main()
    print("\nCitation concordance analysis complete!")
