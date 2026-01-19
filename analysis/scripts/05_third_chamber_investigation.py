#!/usr/bin/env python3
"""
05_third_chamber_investigation.py
=================================
Deep investigation into the Third Chamber effect:
- Why does Third Chamber rule pro-DS only 34.1% vs Grand Chamber 77.6%?
- Is it case allocation, subject matter, or genuine interpretive difference?
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def run_investigation(df):
    """Investigate the Third Chamber effect."""

    print("=" * 70)
    print("THIRD CHAMBER INVESTIGATION")
    print("=" * 70)

    # Split data
    third = df[df['chamber'] == 'THIRD']
    grand = df[df['chamber'] == 'GRAND_CHAMBER']
    other = df[~df['chamber'].isin(['THIRD', 'GRAND_CHAMBER'])]

    print(f"\nSample sizes: Third={len(third)}, Grand={len(grand)}, Other={len(other)}")
    print(f"Pro-DS rates: Third={third['pro_ds'].mean()*100:.1f}%, Grand={grand['pro_ds'].mean()*100:.1f}%, Other={other['pro_ds'].mean()*100:.1f}%")

    # =========================================================================
    # HYPOTHESIS 1: CASE ALLOCATION - Different concept clusters?
    # =========================================================================
    print("\n" + "-" * 70)
    print("HYPOTHESIS 1: CASE ALLOCATION BY CONCEPT CLUSTER")
    print("-" * 70)

    print("\nConcept cluster distribution by chamber:")
    for chamber, chamber_df in [('THIRD', third), ('GRAND_CHAMBER', grand)]:
        print(f"\n{chamber}:")
        dist = chamber_df['concept_cluster'].value_counts(normalize=True) * 100
        for cluster, pct in dist.head(5).items():
            pro_ds_rate = chamber_df[chamber_df['concept_cluster'] == cluster]['pro_ds'].mean() * 100
            n = len(chamber_df[chamber_df['concept_cluster'] == cluster])
            print(f"  {cluster}: {pct:.1f}% of cases, {pro_ds_rate:.1f}% pro-DS (n={n})")

    # Chi-square test for concept cluster distribution
    contingency = pd.crosstab(df[df['chamber'].isin(['THIRD', 'GRAND_CHAMBER'])]['chamber'],
                              df[df['chamber'].isin(['THIRD', 'GRAND_CHAMBER'])]['concept_cluster'])
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square test (cluster distribution differs by chamber): χ²={chi2:.2f}, p={p:.4f}")

    # Key insight: Does Third Chamber get more ENFORCEMENT cases?
    third_enforcement = (third['concept_cluster'] == 'ENFORCEMENT').mean() * 100
    grand_enforcement = (grand['concept_cluster'] == 'ENFORCEMENT').mean() * 100
    print(f"\nENFORCEMENT cases: Third={third_enforcement:.1f}%, Grand={grand_enforcement:.1f}%")

    # =========================================================================
    # HYPOTHESIS 2: SAME CONCEPTS, DIFFERENT INTERPRETATION?
    # =========================================================================
    print("\n" + "-" * 70)
    print("HYPOTHESIS 2: SAME CONCEPT CLUSTER, DIFFERENT OUTCOMES?")
    print("-" * 70)

    # Compare within concept clusters
    print("\nPro-DS rate by chamber WITHIN each concept cluster:")
    for cluster in df['concept_cluster'].unique():
        third_cluster = third[third['concept_cluster'] == cluster]
        grand_cluster = grand[grand['concept_cluster'] == cluster]

        if len(third_cluster) >= 3 and len(grand_cluster) >= 3:
            third_rate = third_cluster['pro_ds'].mean() * 100
            grand_rate = grand_cluster['pro_ds'].mean() * 100
            diff = grand_rate - third_rate
            print(f"  {cluster}: Third={third_rate:.1f}% (n={len(third_cluster)}), Grand={grand_rate:.1f}% (n={len(grand_cluster)}), Δ={diff:+.1f}pp")

    # =========================================================================
    # HYPOTHESIS 3: INTERPRETIVE METHOD DIFFERENCES
    # =========================================================================
    print("\n" + "-" * 70)
    print("HYPOTHESIS 3: INTERPRETIVE METHOD DIFFERENCES")
    print("-" * 70)

    print("\nDominant source distribution:")
    for chamber, chamber_df in [('THIRD', third), ('GRAND_CHAMBER', grand)]:
        print(f"\n{chamber}:")
        dist = chamber_df['dominant_source'].value_counts(normalize=True) * 100
        for source, pct in dist.items():
            print(f"  {source}: {pct:.1f}%")

    # Pro-DS purpose invocation
    third_purpose = third['pro_ds_purpose'].mean() * 100
    grand_purpose = grand['pro_ds_purpose'].mean() * 100
    print(f"\nPro-DS purpose invocation: Third={third_purpose:.1f}%, Grand={grand_purpose:.1f}%")

    # Level shifting
    third_shift = third['level_shifting'].mean() * 100
    grand_shift = grand['level_shifting'].mean() * 100
    print(f"Level-shifting: Third={third_shift:.1f}%, Grand={grand_shift:.1f}%")

    # =========================================================================
    # HYPOTHESIS 4: TEMPORAL PATTERNS
    # =========================================================================
    print("\n" + "-" * 70)
    print("HYPOTHESIS 4: TEMPORAL PATTERNS")
    print("-" * 70)

    print("\nYear distribution and pro-DS rate by chamber:")
    for chamber, chamber_df in [('THIRD', third), ('GRAND_CHAMBER', grand)]:
        year_data = chamber_df.groupby('year').agg({
            'pro_ds': ['count', 'mean']
        }).round(2)
        year_data.columns = ['n', 'pro_ds_rate']
        print(f"\n{chamber}:")
        print(year_data.to_string())

    # =========================================================================
    # HYPOTHESIS 5: SPECIFIC CASE TYPES
    # =========================================================================
    print("\n" + "-" * 70)
    print("HYPOTHESIS 5: SPECIFIC PRIMARY CONCEPTS")
    print("-" * 70)

    # Most common concepts in Third Chamber
    print("\nTop concepts in Third Chamber (with outcomes):")
    third_concepts = third.groupby('primary_concept').agg({
        'pro_ds': ['count', 'mean']
    }).round(2)
    third_concepts.columns = ['n', 'pro_ds_rate']
    third_concepts = third_concepts.sort_values('n', ascending=False)
    print(third_concepts.head(10).to_string())

    print("\nTop concepts in Grand Chamber (with outcomes):")
    grand_concepts = grand.groupby('primary_concept').agg({
        'pro_ds': ['count', 'mean']
    }).round(2)
    grand_concepts.columns = ['n', 'pro_ds_rate']
    grand_concepts = grand_concepts.sort_values('n', ascending=False)
    print(grand_concepts.head(10).to_string())

    # =========================================================================
    # CONTROLLING FOR CONFOUNDERS
    # =========================================================================
    print("\n" + "-" * 70)
    print("CONTROLLED ANALYSIS: THIRD CHAMBER EFFECT")
    print("-" * 70)

    # Simple logistic regression: chamber effect controlling for concept cluster
    import statsmodels.formula.api as smf

    # Create subset with Third and Grand only
    tg_df = df[df['chamber'].isin(['THIRD', 'GRAND_CHAMBER'])].copy()
    tg_df['is_third'] = (tg_df['chamber'] == 'THIRD').astype(int)

    # Unadjusted
    m_unadj = smf.logit("pro_ds ~ is_third", data=tg_df).fit(disp=0)
    or_unadj = np.exp(m_unadj.params['is_third'])
    ci_unadj = np.exp(m_unadj.conf_int().loc['is_third'])

    print(f"\nUnadjusted Third Chamber effect:")
    print(f"  OR = {or_unadj:.3f} [{ci_unadj[0]:.2f}, {ci_unadj[1]:.2f}], p = {m_unadj.pvalues['is_third']:.4f}")

    # Adjusted for concept cluster
    m_adj1 = smf.logit("pro_ds ~ is_third + C(concept_cluster)", data=tg_df).fit(disp=0)
    or_adj1 = np.exp(m_adj1.params['is_third'])
    ci_adj1 = np.exp(m_adj1.conf_int().loc['is_third'])

    print(f"\nAdjusted for concept cluster:")
    print(f"  OR = {or_adj1:.3f} [{ci_adj1[0]:.2f}, {ci_adj1[1]:.2f}], p = {m_adj1.pvalues['is_third']:.4f}")

    # Adjusted for concept cluster + interpretive factors
    m_adj2 = smf.logit("pro_ds ~ is_third + C(concept_cluster) + pro_ds_purpose + C(dominant_source)",
                       data=tg_df).fit(disp=0)
    or_adj2 = np.exp(m_adj2.params['is_third'])
    ci_adj2 = np.exp(m_adj2.conf_int().loc['is_third'])

    print(f"\nAdjusted for concept cluster + interpretive factors:")
    print(f"  OR = {or_adj2:.3f} [{ci_adj2[0]:.2f}, {ci_adj2[1]:.2f}], p = {m_adj2.pvalues['is_third']:.4f}")

    # =========================================================================
    # INDIVIDUAL CASE REVIEW
    # =========================================================================
    print("\n" + "-" * 70)
    print("INDIVIDUAL CASE REVIEW: THIRD CHAMBER PRO-CONTROLLER CASES")
    print("-" * 70)

    third_not_pro_ds = third[third['pro_ds'] == 0]
    print(f"\nThird Chamber non-pro-DS cases (n={len(third_not_pro_ds)}):")

    for _, row in third_not_pro_ds.head(10).iterrows():
        print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
        print(f"    Concept: {row['primary_concept']}")
        print(f"    Ruling: {row['ruling_direction']}")
        print(f"    Dominant source: {row['dominant_source']}")
        print(f"    Core: {str(row['core_holding'])[:100]}...")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("THIRD CHAMBER INVESTIGATION SUMMARY")
    print("=" * 70)

    # Calculate key metrics
    findings = {
        'raw_gap_pp': grand['pro_ds'].mean() * 100 - third['pro_ds'].mean() * 100,
        'third_enforcement_pct': third_enforcement,
        'grand_enforcement_pct': grand_enforcement,
        'third_pro_ds_purpose_pct': third_purpose,
        'grand_pro_ds_purpose_pct': grand_purpose,
        'or_unadjusted': or_unadj,
        'or_adjusted_concept': or_adj1,
        'or_adjusted_full': or_adj2,
        'p_adjusted_full': m_adj2.pvalues['is_third']
    }

    print(f"""
1. RAW GAP: Third Chamber {third['pro_ds'].mean()*100:.1f}% vs Grand Chamber {grand['pro_ds'].mean()*100:.1f}% pro-DS
   → Gap = {findings['raw_gap_pp']:.1f} percentage points

2. CASE ALLOCATION:
   - Third gets {third_enforcement:.1f}% ENFORCEMENT cases vs Grand's {grand_enforcement:.1f}%
   - ENFORCEMENT has lowest pro-DS rate (46.2%), so allocation partially explains gap

3. INTERPRETIVE APPROACH:
   - Third invokes pro-DS purpose {third_purpose:.1f}% vs Grand {grand_purpose:.1f}%
   - This difference in rhetorical framing may drive outcomes

4. CONTROLLED EFFECT:
   - Unadjusted OR = {or_unadj:.3f} (Third Chamber effect)
   - After controlling for concept + interpretation: OR = {or_adj2:.3f}, p = {m_adj2.pvalues['is_third']:.4f}
   - {"EFFECT PERSISTS after controls" if m_adj2.pvalues['is_third'] < 0.05 else "Effect ATTENUATES after controls"}

5. CONCLUSION:
   {"Third Chamber effect appears to be a GENUINE interpretive difference beyond case allocation" if m_adj2.pvalues['is_third'] < 0.05 else "Third Chamber effect is LARGELY EXPLAINED by case allocation and interpretive framing differences"}
""")

    # Save findings
    with open(OUTPUT_PATH / "third_chamber_investigation.json", 'w') as f:
        json.dump(findings, f, indent=2, default=float)

    return findings

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    findings = run_investigation(df)
    print("\nInvestigation complete!")
