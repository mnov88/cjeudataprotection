#!/usr/bin/env python3
"""
01_data_preparation.py
======================
Data preparation and variable transformation for CJEU GDPR analysis.

Creates derived variables and exports analysis-ready dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "parsed-coded" / "holdings.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def load_and_prepare_data():
    """Load holdings data and create derived variables."""

    print("=" * 60)
    print("CJEU GDPR ANALYSIS: DATA PREPARATION")
    print("=" * 60)

    # Load data
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

    print(f"\nYear range: {df['year'].min()} - {df['year'].max()}")

    # === CHAMBER GROUPING ===
    major_chambers = ['GRAND_CHAMBER', 'FIRST', 'THIRD', 'FOURTH']
    df['chamber_grouped'] = df['chamber'].apply(
        lambda x: x if x in major_chambers else 'OTHER'
    )

    # === CONCEPT CLUSTERING ===
    concept_clusters = {
        'SCOPE': ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE',
                  'HOUSEHOLD_EXEMPTION', 'OTHER_EXEMPTION'],
        'ACTORS': ['CONTROLLER_DEFINITION', 'JOINT_CONTROLLERS_DEFINITION',
                   'PROCESSOR_OBLIGATIONS', 'RECIPIENT_DEFINITION'],
        'LAWFULNESS': ['CONSENT_BASIS', 'CONTRACT_BASIS', 'LEGAL_OBLIGATION_BASIS',
                       'VITAL_INTERESTS_BASIS', 'PUBLIC_INTEREST_BASIS', 'LEGITIMATE_INTERESTS'],
        'PRINCIPLES': ['DATA_PROTECTION_PRINCIPLES', 'ACCOUNTABILITY', 'TRANSPARENCY'],
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

    def get_concept_cluster(concept):
        for cluster, concepts in concept_clusters.items():
            if concept in concepts:
                return cluster
        return 'OTHER'

    df['concept_cluster'] = df['primary_concept'].apply(get_concept_cluster)

    print(f"\nConcept Cluster Distribution:")
    print(df['concept_cluster'].value_counts())

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
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    # Key variable summary
    summary = {
        'N_holdings': int(len(df)),
        'N_cases': int(df['case_id'].nunique()),
        'Pro_DS_count': int(df['pro_ds'].sum()),
        'Pro_DS_pct': float(round(df['pro_ds'].mean() * 100, 1)),
        'Year_range': f"{df['year'].min()}-{df['year'].max()}",
        'Teleological_present_pct': float(round(df['teleological_present'].mean() * 100, 1)),
        'Level_shifting_pct': float(round(df['level_shifting'].mean() * 100, 1)),
        'Any_balancing_pct': float(round(df['any_balancing'].mean() * 100, 1)),
    }

    for key, val in summary.items():
        print(f"  {key}: {val}")

    # Save summary
    with open(OUTPUT_PATH / "data_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    return df

if __name__ == "__main__":
    df = load_and_prepare_data()
    print("\nData preparation complete!")
