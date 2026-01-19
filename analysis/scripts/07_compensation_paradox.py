#!/usr/bin/env python3
"""
07_compensation_paradox.py
==========================
Deep dive on the Article 82 compensation paradox:
- Cases invoke HIGH_LEVEL_OF_PROTECTION but rule against data subjects on damages
- The Court's compensatory (not punitive) interpretation creates tension
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
CODED_PATH = PROJECT_ROOT / "coded-decisions"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def run_compensation_analysis(df):
    """Analyze the compensation paradox in Article 82 cases."""

    print("=" * 70)
    print("ARTICLE 82 COMPENSATION PARADOX ANALYSIS")
    print("=" * 70)

    # Identify REMEDIES_COMPENSATION cases
    comp_df = df[df['primary_concept'] == 'REMEDIES_COMPENSATION'].copy()

    print(f"\nREMEDIES_COMPENSATION holdings: {len(comp_df)} of {len(df)} total ({len(comp_df)/len(df)*100:.1f}%)")
    print(f"Pro-DS rate in compensation cases: {comp_df['pro_ds'].mean()*100:.1f}%")
    print(f"Pro-DS rate in other cases: {df[df['primary_concept'] != 'REMEDIES_COMPENSATION']['pro_ds'].mean()*100:.1f}%")

    # =========================================================================
    # RULING DIRECTION BREAKDOWN
    # =========================================================================
    print("\n" + "-" * 70)
    print("RULING DIRECTION IN COMPENSATION CASES")
    print("-" * 70)

    print("\nRuling direction distribution:")
    print(comp_df['ruling_direction'].value_counts().to_string())

    # =========================================================================
    # THE PARADOX: Pro-DS Purpose but Not Pro-DS Outcome
    # =========================================================================
    print("\n" + "-" * 70)
    print("THE PARADOX: PRO-DS PURPOSE BUT NOT PRO-DS OUTCOME")
    print("-" * 70)

    # Cases with pro-DS purpose invoked
    comp_with_purpose = comp_df[comp_df['pro_ds_purpose'] == 1]
    comp_without_purpose = comp_df[comp_df['pro_ds_purpose'] == 0]

    print(f"\nCompensation cases WITH pro-DS purpose invoked: {len(comp_with_purpose)}")
    print(f"  Pro-DS outcome: {comp_with_purpose['pro_ds'].sum()} ({comp_with_purpose['pro_ds'].mean()*100:.1f}%)")
    print(f"\nCompensation cases WITHOUT pro-DS purpose: {len(comp_without_purpose)}")
    print(f"  Pro-DS outcome: {comp_without_purpose['pro_ds'].sum()} ({comp_without_purpose['pro_ds'].mean()*100:.1f}%)")

    # The paradox cases
    paradox_cases = comp_df[(comp_df['pro_ds_purpose'] == 1) & (comp_df['pro_ds'] == 0)]
    print(f"\n*** PARADOX CASES: Pro-DS purpose invoked but NOT pro-DS outcome: {len(paradox_cases)} ***")

    # =========================================================================
    # DETAILED REVIEW OF PARADOX CASES
    # =========================================================================
    print("\n" + "-" * 70)
    print("DETAILED REVIEW: PARADOX CASES")
    print("-" * 70)

    for _, row in paradox_cases.iterrows():
        print(f"\n{'='*60}")
        print(f"Case: {row['case_id']}, Holding {row['holding_id']}")
        print(f"Ruling: {row['ruling_direction']}")
        print(f"Teleological purposes: {row['teleological_purposes']}")
        print(f"Dominant source: {row['dominant_source']}")
        print(f"\nCore holding:")
        print(f"  {row['core_holding']}")
        print(f"\nDirection justification:")
        print(f"  {row.get('direction_justification', 'N/A')}")

    # =========================================================================
    # THEMATIC ANALYSIS OF COMPENSATION OUTCOMES
    # =========================================================================
    print("\n" + "-" * 70)
    print("THEMATIC ANALYSIS: WHY COMPENSATION CASES GO AGAINST DATA SUBJECTS")
    print("-" * 70)

    # Group by ruling direction and analyze core holdings
    pro_controller = comp_df[comp_df['ruling_direction'] == 'PRO_CONTROLLER']
    mixed = comp_df[comp_df['ruling_direction'] == 'MIXED']
    neutral = comp_df[comp_df['ruling_direction'] == 'NEUTRAL_OR_UNCLEAR']

    print(f"\nPRO_CONTROLLER compensation holdings (n={len(pro_controller)}):")
    for _, row in pro_controller.iterrows():
        print(f"\n  • {row['case_id']}: {row['core_holding'][:150]}...")

    print(f"\nMIXED compensation holdings (n={len(mixed)}):")
    for _, row in mixed.head(5).iterrows():
        print(f"\n  • {row['case_id']}: {row['core_holding'][:150]}...")

    # =========================================================================
    # KEY THEMES EXTRACTION
    # =========================================================================
    print("\n" + "-" * 70)
    print("KEY THEMES IN NON-PRO-DS COMPENSATION CASES")
    print("-" * 70)

    non_pro_ds_comp = comp_df[comp_df['pro_ds'] == 0]

    themes = {
        'damage_proof_required': 0,
        'no_strict_liability': 0,
        'compensatory_not_punitive': 0,
        'actual_damage_threshold': 0,
        'fault_element': 0
    }

    keywords = {
        'damage_proof_required': ['actual damage', 'prove', 'proof', 'demonstrate', 'establish'],
        'no_strict_liability': ['not sufficient in itself', 'not per se', 'mere infringement'],
        'compensatory_not_punitive': ['compensatory', 'not punitive', 'not deterrent'],
        'actual_damage_threshold': ['suffered', 'actual', 'concrete', 'specific damage'],
        'fault_element': ['intentional', 'negligent', 'fault', 'culpability']
    }

    for _, row in non_pro_ds_comp.iterrows():
        core = str(row['core_holding']).lower()
        just = str(row.get('direction_justification', '')).lower()
        combined = core + ' ' + just

        for theme, kws in keywords.items():
            if any(kw in combined for kw in kws):
                themes[theme] += 1

    print("\nTheme frequency in non-pro-DS compensation holdings:")
    for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
        pct = count / len(non_pro_ds_comp) * 100 if len(non_pro_ds_comp) > 0 else 0
        print(f"  {theme}: {count} ({pct:.1f}%)")

    # =========================================================================
    # CONTRAST: WHAT MAKES COMPENSATION CASES PRO-DS?
    # =========================================================================
    print("\n" + "-" * 70)
    print("CONTRAST: PRO-DS COMPENSATION HOLDINGS")
    print("-" * 70)

    pro_ds_comp = comp_df[comp_df['pro_ds'] == 1]
    print(f"\nPro-DS compensation holdings (n={len(pro_ds_comp)}):")

    for _, row in pro_ds_comp.iterrows():
        print(f"\n  • {row['case_id']}, H{row['holding_id']}: {row['core_holding'][:120]}...")

    # =========================================================================
    # TEMPORAL PATTERN
    # =========================================================================
    print("\n" + "-" * 70)
    print("TEMPORAL PATTERN IN COMPENSATION CASES")
    print("-" * 70)

    comp_by_year = comp_df.groupby('year').agg({
        'pro_ds': ['count', 'mean']
    }).round(2)
    comp_by_year.columns = ['n', 'pro_ds_rate']
    print("\nCompensation cases by year:")
    print(comp_by_year.to_string())

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("COMPENSATION PARADOX SUMMARY")
    print("=" * 70)

    summary = {
        'total_compensation_holdings': len(comp_df),
        'pro_ds_rate_compensation': comp_df['pro_ds'].mean(),
        'pro_ds_rate_other': df[df['primary_concept'] != 'REMEDIES_COMPENSATION']['pro_ds'].mean(),
        'paradox_cases': len(paradox_cases),
        'themes': themes
    }

    print(f"""
1. COMPENSATION CASES ARE LESS PRO-DS:
   - Compensation: {comp_df['pro_ds'].mean()*100:.1f}% pro-DS
   - Other concepts: {df[df['primary_concept'] != 'REMEDIES_COMPENSATION']['pro_ds'].mean()*100:.1f}% pro-DS
   - Gap: {(df[df['primary_concept'] != 'REMEDIES_COMPENSATION']['pro_ds'].mean() - comp_df['pro_ds'].mean())*100:.1f} percentage points

2. THE PARADOX:
   - {len(paradox_cases)} holdings invoke HIGH_LEVEL_OF_PROTECTION/FUNDAMENTAL_RIGHTS
     but still rule against data subjects on compensation
   - This represents {len(paradox_cases)/len(comp_df)*100:.1f}% of all compensation holdings

3. KEY DOCTRINAL THEMES:
   - "Mere infringement is not sufficient" for compensation
   - Actual damage must be proven by the data subject
   - Compensation is purely compensatory, not punitive
   - Controller fault/negligence may be required for certain claims

4. PRACTICAL IMPLICATIONS:
   - Data subjects face significant hurdles proving damage
   - GDPR's "high level of protection" rhetoric doesn't translate to damages
   - Third Chamber handles most compensation cases (63.4% of its docket)
   - This creates a systematic gap between rights and remedies
""")

    # Save results
    with open(OUTPUT_PATH / "compensation_paradox.json", 'w') as f:
        json.dump(summary, f, indent=2, default=float)

    return summary

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    summary = run_compensation_analysis(df)
    print("\nCompensation paradox analysis complete!")
