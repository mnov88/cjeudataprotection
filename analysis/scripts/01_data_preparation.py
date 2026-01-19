#!/usr/bin/env python3
"""
01_data_preparation.py
======================
Data preparation and variable transformation for CJEU GDPR analysis.

Creates derived variables and exports analysis-ready dataset.

REVISION HISTORY:
- v2.0: Fixed data path, added DATA_MINIMISATION to PRINCIPLES, added is_compensation flag,
        added data quality validation, added FIFTH to major chambers, added derived variables
        for inverse weighting and year centering.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "parsed" / "holdings.csv"  # FIXED: was "parsed-coded"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def load_and_prepare_data():
    """Load holdings data and create derived variables."""

    print("=" * 70)
    print("CJEU GDPR ANALYSIS: DATA PREPARATION (v2.0)")
    print("=" * 70)

    # Load data
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded {len(df)} holdings from {len(df['case_id'].unique())} cases")

    # === DEPENDENT VARIABLE ===
    # Binary: PRO_DATA_SUBJECT vs OTHER
    df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)

    # Trichotomous for sensitivity analysis
    df['direction_3cat'] = df['ruling_direction'].map({
        'PRO_DATA_SUBJECT': 'PRO_DATA_SUBJECT',
        'PRO_CONTROLLER': 'PRO_CONTROLLER',
        'MIXED': 'INDETERMINATE',
        'NEUTRAL_OR_UNCLEAR': 'INDETERMINATE'
    })

    print(f"\nDependent Variable Distribution:")
    print(df['ruling_direction'].value_counts())
    print(f"\nBinary DV: PRO_DATA_SUBJECT={df['pro_ds'].sum()}, OTHER={len(df) - df['pro_ds'].sum()}")

    # === TEMPORAL VARIABLE ===
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])
    df['year'] = df['judgment_date'].dt.year

    # Year centered (useful for regression models)
    median_year = df['year'].median()
    df['year_centered'] = df['year'] - median_year

    print(f"\nYear range: {df['year'].min()} - {df['year'].max()} (median: {median_year})")

    # === CHAMBER GROUPING ===
    # FIXED: Added FIFTH (15 holdings) to major chambers
    major_chambers = ['GRAND_CHAMBER', 'FIRST', 'THIRD', 'FOURTH', 'FIFTH']
    df['chamber_grouped'] = df['chamber'].apply(
        lambda x: x if x in major_chambers else 'OTHER'
    )

    print(f"\nChamber Distribution:")
    print(df['chamber'].value_counts())

    # === CONCEPT CLUSTERING ===
    # FIXED: Added DATA_MINIMISATION to PRINCIPLES cluster
    concept_clusters = {
        'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
                  'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
        'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
                   'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
        'LAWFULNESS': ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGAL_OBLIGATION_BASIS',
                       'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS', 'LEGITIMATE_INTERESTS'],
        'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY',
                       'DATA_MINIMISATION'],  # FIXED: Added DATA_MINIMISATION
        'RIGHTS': ['RIGHT_OF_ACCESS', 'RIGHT_TO_RECTIFICATION', 'RIGHT_TO_ERASURE',
                   'RIGHT_TO_RESTRICTION', 'RIGHT_TO_PORTABILITY', 'RIGHT_TO_OBJECT',
                   'AUTOMATED_DECISION_MAKING'],
        'SPECIAL_CATEGORIES': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
        'ENFORCEMENT': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
                        'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REMEDIES_COMPENSATION',
                        'REPRESENTATIVE_ACTIONS'],
        'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
                  'MEMBER_STATE_DISCRETION', 'OTHER']
    }

    # Build reverse lookup and track all defined concepts
    concept_to_cluster = {}
    for cluster, concepts in concept_clusters.items():
        for concept in concepts:
            concept_to_cluster[concept] = cluster

    all_defined_concepts = set(concept_to_cluster.keys())

    def get_concept_cluster(concept):
        return concept_to_cluster.get(concept, 'OTHER')

    df['concept_cluster'] = df['primary_concept'].apply(get_concept_cluster)

    # VALIDATION: Check for unmapped concepts
    actual_concepts = set(df['primary_concept'].unique())
    unmapped_concepts = actual_concepts - all_defined_concepts
    if unmapped_concepts:
        warnings.warn(f"WARNING: Unmapped concepts falling to OTHER: {unmapped_concepts}")
        print(f"\n*** WARNING: {len(unmapped_concepts)} unmapped concepts: {unmapped_concepts} ***")

    print(f"\nConcept Cluster Distribution:")
    cluster_dist = df['concept_cluster'].value_counts()
    print(cluster_dist)

    # === NEW: COMPENSATION FLAG AND ENFORCEMENT DECOMPOSITION ===
    # Critical for sensitivity analyses - compensation cases are outliers
    df['is_compensation'] = (df['primary_concept'] == 'REMEDIES_COMPENSATION').astype(int)
    df['is_enforcement_non_comp'] = ((df['concept_cluster'] == 'ENFORCEMENT') &
                                      (df['is_compensation'] == 0)).astype(int)

    n_comp = df['is_compensation'].sum()
    n_enf = (df['concept_cluster'] == 'ENFORCEMENT').sum()
    print(f"\nCompensation Analysis:")
    print(f"  REMEDIES_COMPENSATION holdings: {n_comp} ({n_comp/len(df)*100:.1f}% of total)")
    print(f"  ENFORCEMENT cluster total: {n_enf}")
    print(f"  Compensation as % of ENFORCEMENT: {n_comp/n_enf*100:.1f}%")
    print(f"  Non-compensation ENFORCEMENT: {n_enf - n_comp}")

    # === NEW: HOLDINGS PER CASE AND INVERSE WEIGHTING ===
    # For addressing unit of analysis issues (ICC = 29.5%)
    df['holdings_in_case'] = df.groupby('case_id')['holding_id'].transform('count')
    df['inverse_weight'] = 1.0 / df['holdings_in_case']

    print(f"\nWithin-Case Clustering:")
    print(f"  Mean holdings per case: {df['holdings_in_case'].mean():.2f}")
    print(f"  Max holdings per case: {df['holdings_in_case'].max()}")
    print(f"  Cases with >3 holdings: {(df.groupby('case_id').size() > 3).sum()}")

    # === INTERPRETIVE SOURCE VARIABLES ===
    # Convert boolean strings to actual booleans
    bool_cols = ['semantic_present', 'systematic_present', 'teleological_present',
                 'rule_based_present', 'case_law_present', 'principle_based_present',
                 'level_shifting', 'necessity_discussed', 'controller_ds_balancing',
                 'other_rights_balancing', 'dominant_confident']

    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().map({'TRUE': 1, 'FALSE': 0, 'NAN': 0, 'NONE': 0})
            df[col] = df[col].fillna(0).astype(int)

    # Interpretation count (how many methods used)
    df['interpretation_count'] = (df['semantic_present'] + df['systematic_present'] +
                                   df['teleological_present'])

    # Reasoning count
    df['reasoning_count'] = (df['rule_based_present'] + df['case_law_present'] +
                             df['principle_based_present'])

    # === DATA QUALITY FLAGS ===
    # Check for cross-contamination between dominant_source and dominant_structure
    valid_sources = {'SEMANTIC', 'SYSTEMATIC', 'TELEOLOGICAL', 'UNCLEAR', ''}
    valid_structures = {'RULE_BASED', 'CASE_LAW_BASED', 'PRINCIPLE_BASED', 'MIXED', ''}

    df['dq_source_invalid'] = (~df['dominant_source'].isin(valid_sources)).astype(int)
    df['dq_structure_invalid'] = (~df['dominant_structure'].isin(valid_structures)).astype(int)
    df['dq_any_issue'] = ((df['dq_source_invalid'] == 1) | (df['dq_structure_invalid'] == 1)).astype(int)

    n_source_issues = df['dq_source_invalid'].sum()
    n_structure_issues = df['dq_structure_invalid'].sum()

    if n_source_issues > 0 or n_structure_issues > 0:
        print(f"\n*** DATA QUALITY WARNING ***")
        print(f"  Holdings with invalid dominant_source: {n_source_issues}")
        print(f"  Holdings with invalid dominant_structure: {n_structure_issues}")

        problem_holdings = df[df['dq_any_issue'] == 1][['case_id', 'holding_id', 'dominant_source', 'dominant_structure']]
        print("  Affected holdings:")
        for _, row in problem_holdings.iterrows():
            print(f"    {row['case_id']} H{row['holding_id']}: source='{row['dominant_source']}', structure='{row['dominant_structure']}'")

    # === TELEOLOGICAL PURPOSE INDICATORS ===
    df['teleological_purposes'] = df['teleological_purposes'].fillna('')

    df['purpose_high_protection'] = df['teleological_purposes'].str.contains(
        'HIGH_LEVEL_OF_PROTECTION', case=False, na=False).astype(int)
    df['purpose_fundamental_rights'] = df['teleological_purposes'].str.contains(
        'FUNDAMENTAL_RIGHTS', case=False, na=False).astype(int)
    df['purpose_effective_enforcement'] = df['teleological_purposes'].str.contains(
        'EFFECTIVE_ENFORCEMENT', case=False, na=False).astype(int)
    df['purpose_harmonization'] = df['teleological_purposes'].str.contains(
        'HARMONIZATION', case=False, na=False).astype(int)
    df['purpose_free_flow'] = df['teleological_purposes'].str.contains(
        'FREE_FLOW_OF_DATA', case=False, na=False).astype(int)

    # Any pro-DS purpose (high protection OR fundamental rights)
    df['pro_ds_purpose'] = ((df['purpose_high_protection'] == 1) |
                            (df['purpose_fundamental_rights'] == 1)).astype(int)

    # === BALANCING VARIABLES ===
    # Any balancing discussed
    df['any_balancing'] = ((df['necessity_discussed'] == 1) |
                           (df['controller_ds_balancing'] == 1) |
                           (df['other_rights_balancing'] == 1)).astype(int)

    # Necessity standard as ordinal
    df['necessity_ordinal'] = df['necessity_standard'].map({
        'NONE': 0, 'REGULAR': 1, 'STRICT': 2
    }).fillna(0).astype(int)

    # Interest prevails indicators
    df['ds_interest_prevails'] = (df['interest_prevails'] == 'DATA_SUBJECT').astype(int)
    df['controller_interest_prevails'] = (df['interest_prevails'] == 'CONTROLLER').astype(int)

    # === CITED CASE COUNT ===
    df['cited_case_count'] = df['cited_case_count'].fillna(0).astype(int)
    df['has_case_citations'] = (df['cited_case_count'] > 0).astype(int)

    # === DOMINANT SOURCE DUMMIES ===
    df['dominant_teleological'] = (df['dominant_source'] == 'TELEOLOGICAL').astype(int)
    df['dominant_systematic'] = (df['dominant_source'] == 'SYSTEMATIC').astype(int)
    df['dominant_semantic'] = (df['dominant_source'] == 'SEMANTIC').astype(int)

    # === DOMINANT STRUCTURE DUMMIES ===
    df['structure_principle'] = (df['dominant_structure'] == 'PRINCIPLE_BASED').astype(int)
    df['structure_rule'] = (df['dominant_structure'] == 'RULE_BASED').astype(int)
    df['structure_caselaw'] = (df['dominant_structure'] == 'CASE_LAW_BASED').astype(int)

    # === SAVE PREPARED DATA ===
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_PATH / "holdings_prepared.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved prepared data to: {output_file}")

    # === SUMMARY STATISTICS ===
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    # Key variable summary
    summary = {
        'N_holdings': int(len(df)),
        'N_cases': int(df['case_id'].nunique()),
        'Pro_DS_count': int(df['pro_ds'].sum()),
        'Pro_DS_pct': float(round(df['pro_ds'].mean() * 100, 1)),
        'Year_range': f"{df['year'].min()}-{df['year'].max()}",
        'Year_median': int(median_year),
        'Teleological_present_pct': float(round(df['teleological_present'].mean() * 100, 1)),
        'Level_shifting_pct': float(round(df['level_shifting'].mean() * 100, 1)),
        'Any_balancing_pct': float(round(df['any_balancing'].mean() * 100, 1)),
        'Compensation_holdings': int(df['is_compensation'].sum()),
        'Compensation_pct': float(round(df['is_compensation'].mean() * 100, 1)),
        'Data_quality_issues': int(df['dq_any_issue'].sum()),
    }

    for key, val in summary.items():
        print(f"  {key}: {val}")

    # === CLUSTER COMPOSITION REPORT ===
    print("\n" + "=" * 70)
    print("CONCEPT CLUSTER COMPOSITION")
    print("=" * 70)

    for cluster in ['SCOPE', 'ACTORS', 'LAWFULNESS', 'PRINCIPLES', 'RIGHTS',
                    'SPECIAL_CATEGORIES', 'ENFORCEMENT', 'OTHER']:
        cluster_df = df[df['concept_cluster'] == cluster]
        n = len(cluster_df)
        pro_ds_rate = cluster_df['pro_ds'].mean() * 100 if n > 0 else 0
        print(f"\n{cluster}: {n} holdings ({pro_ds_rate:.1f}% pro-DS)")

        concept_breakdown = cluster_df['primary_concept'].value_counts()
        for concept, count in concept_breakdown.items():
            pct = count / n * 100 if n > 0 else 0
            concept_pro_ds = cluster_df[cluster_df['primary_concept'] == concept]['pro_ds'].mean() * 100
            print(f"    {concept}: {count} ({pct:.1f}%) - {concept_pro_ds:.1f}% pro-DS")

    # Save summary
    with open(OUTPUT_PATH / "data_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    # Save concept cluster mapping for reference
    cluster_info = {
        'concept_clusters': concept_clusters,
        'unmapped_concepts': list(unmapped_concepts) if unmapped_concepts else [],
        'enforcement_composition': {
            'total': int(n_enf),
            'compensation': int(n_comp),
            'compensation_pct': float(round(n_comp/n_enf*100, 1)) if n_enf > 0 else 0,
            'non_compensation': int(n_enf - n_comp)
        }
    }
    with open(OUTPUT_PATH / "concept_cluster_info.json", 'w') as f:
        json.dump(cluster_info, f, indent=2)

    return df

if __name__ == "__main__":
    df = load_and_prepare_data()
    print("\n" + "=" * 70)
    print("DATA PREPARATION COMPLETE!")
    print("=" * 70)
