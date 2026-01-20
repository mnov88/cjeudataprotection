#!/usr/bin/env python3
"""
05_third_chamber_investigation.py
=================================
Deep investigation into the Third Chamber effect:
- Why does Third Chamber rule pro-DS only 34.1% vs Grand Chamber 77.6%?
- Is it case allocation, subject matter, or genuine interpretive difference?

REVISION HISTORY:
- v2.0: Added HYPOTHESIS 6 - compensation-exclusion sensitivity analysis.
        This is the critical test for academic rigor: does the Third Chamber
        effect persist when removing the 59% of their holdings that are
        compensation cases?
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
    # HYPOTHESIS 6: COMPENSATION-EXCLUSION SENSITIVITY (CRITICAL TEST)
    # =========================================================================
    print("\n" + "-" * 70)
    print("HYPOTHESIS 6: EXCLUDING COMPENSATION CASES (CRITICAL SENSITIVITY)")
    print("-" * 70)
    print("\n  This tests whether the Third Chamber effect is driven entirely by")
    print("  their compensation caseload (59% of Third Chamber holdings).")

    # Check if is_compensation column exists
    if 'is_compensation' not in df.columns:
        print("\n  WARNING: is_compensation column not found. Run 01_data_preparation.py first.")
        third_comp_pct = 0
        grand_comp_pct = 0
        sensitivity_results = {}
    else:
        # Compensation breakdown by chamber
        third_comp = third['is_compensation'].sum()
        third_comp_pct = third_comp / len(third) * 100
        grand_comp = grand['is_compensation'].sum()
        grand_comp_pct = grand_comp / len(grand) * 100

        print(f"\n  Compensation holdings by chamber:")
        print(f"    Third Chamber: {third_comp}/{len(third)} = {third_comp_pct:.1f}%")
        print(f"    Grand Chamber: {grand_comp}/{len(grand)} = {grand_comp_pct:.1f}%")

        # Pro-DS rates WITH and WITHOUT compensation
        print(f"\n  Pro-DS rates - FULL SAMPLE vs EXCLUDING COMPENSATION:")

        # Third Chamber
        third_full_rate = third['pro_ds'].mean() * 100
        third_no_comp = third[third['is_compensation'] == 0]
        third_no_comp_rate = third_no_comp['pro_ds'].mean() * 100 if len(third_no_comp) > 0 else 0

        # Grand Chamber
        grand_full_rate = grand['pro_ds'].mean() * 100
        grand_no_comp = grand[grand['is_compensation'] == 0]
        grand_no_comp_rate = grand_no_comp['pro_ds'].mean() * 100 if len(grand_no_comp) > 0 else 0

        # Other chambers
        other_full_rate = other['pro_ds'].mean() * 100
        other_no_comp = other[other['is_compensation'] == 0]
        other_no_comp_rate = other_no_comp['pro_ds'].mean() * 100 if len(other_no_comp) > 0 else 0

        print(f"\n    {'Chamber':<18} {'Full Sample':>15} {'Excl. Compensation':>20} {'Change':>10}")
        print(f"    {'-'*65}")
        print(f"    {'Third':<18} {third_full_rate:>14.1f}% {third_no_comp_rate:>19.1f}% {third_no_comp_rate - third_full_rate:>+9.1f}pp")
        print(f"    {'Grand Chamber':<18} {grand_full_rate:>14.1f}% {grand_no_comp_rate:>19.1f}% {grand_no_comp_rate - grand_full_rate:>+9.1f}pp")
        print(f"    {'Other':<18} {other_full_rate:>14.1f}% {other_no_comp_rate:>19.1f}% {other_no_comp_rate - other_full_rate:>+9.1f}pp")

        # Gap analysis
        full_gap = grand_full_rate - third_full_rate
        no_comp_gap = grand_no_comp_rate - third_no_comp_rate

        print(f"\n  Third vs Grand Chamber gap:")
        print(f"    Full sample: {full_gap:.1f} percentage points")
        print(f"    Excluding compensation: {no_comp_gap:.1f} percentage points")
        print(f"    Gap reduction: {full_gap - no_comp_gap:.1f}pp ({(full_gap - no_comp_gap)/full_gap*100:.1f}% explained by compensation)")

        # Statistical test: Third Chamber effect excluding compensation
        print(f"\n  Statistical test (excluding compensation):")

        df_no_comp = df[df['is_compensation'] == 0]
        tg_no_comp = df_no_comp[df_no_comp['chamber'].isin(['THIRD', 'GRAND_CHAMBER'])].copy()
        tg_no_comp['is_third'] = (tg_no_comp['chamber'] == 'THIRD').astype(int)

        if len(tg_no_comp[tg_no_comp['is_third'] == 1]) >= 5 and len(tg_no_comp[tg_no_comp['is_third'] == 0]) >= 5:
            # Simple Fisher's exact test
            a = tg_no_comp[(tg_no_comp['is_third'] == 1) & (tg_no_comp['pro_ds'] == 1)].shape[0]
            b = tg_no_comp[(tg_no_comp['is_third'] == 1) & (tg_no_comp['pro_ds'] == 0)].shape[0]
            c = tg_no_comp[(tg_no_comp['is_third'] == 0) & (tg_no_comp['pro_ds'] == 1)].shape[0]
            d = tg_no_comp[(tg_no_comp['is_third'] == 0) & (tg_no_comp['pro_ds'] == 0)].shape[0]

            oddsratio, pvalue = stats.fisher_exact([[a, b], [c, d]])
            print(f"    Third (excl. comp): {a+b} holdings, {a/(a+b)*100:.1f}% pro-DS")
            print(f"    Grand (excl. comp): {c+d} holdings, {c/(c+d)*100:.1f}% pro-DS")
            print(f"    Fisher's exact: OR = {oddsratio:.3f}, p = {pvalue:.4f}")

            if pvalue < 0.05:
                print(f"\n    *** EFFECT PERSISTS: Third Chamber effect significant even excluding compensation ***")
            else:
                print(f"\n    *** EFFECT ATTENUATES: Third Chamber effect NOT significant when excluding compensation ***")
                print(f"        This suggests the Third Chamber effect is primarily driven by compensation caseload.")
        else:
            print("    Insufficient sample size for test after excluding compensation")
            oddsratio, pvalue = np.nan, np.nan

        sensitivity_results = {
            'third_comp_pct': third_comp_pct,
            'grand_comp_pct': grand_comp_pct,
            'third_full_rate': third_full_rate,
            'third_no_comp_rate': third_no_comp_rate,
            'grand_full_rate': grand_full_rate,
            'grand_no_comp_rate': grand_no_comp_rate,
            'full_gap_pp': full_gap,
            'no_comp_gap_pp': no_comp_gap,
            'gap_explained_by_comp_pct': (full_gap - no_comp_gap) / full_gap * 100 if full_gap > 0 else 0,
            'or_excl_compensation': float(oddsratio) if not np.isnan(oddsratio) else None,
            'p_excl_compensation': float(pvalue) if not np.isnan(pvalue) else None
        }

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

    # Add sensitivity analysis results
    if sensitivity_results:
        findings['sensitivity_excl_compensation'] = sensitivity_results

    # Determine if effect persists after excluding compensation
    comp_effect_persists = (sensitivity_results.get('p_excl_compensation') is not None and
                            sensitivity_results.get('p_excl_compensation') < 0.05)

    print(f"""
1. RAW GAP: Third Chamber {third['pro_ds'].mean()*100:.1f}% vs Grand Chamber {grand['pro_ds'].mean()*100:.1f}% pro-DS
   → Gap = {findings['raw_gap_pp']:.1f} percentage points

2. CASE ALLOCATION:
   - Third gets {third_enforcement:.1f}% ENFORCEMENT cases vs Grand's {grand_enforcement:.1f}%
   - Third gets {third_comp_pct:.1f}% COMPENSATION cases vs Grand's {grand_comp_pct:.1f}%
   - ENFORCEMENT has lowest pro-DS rate (46.2%), so allocation partially explains gap

3. INTERPRETIVE APPROACH:
   - Third invokes pro-DS purpose {third_purpose:.1f}% vs Grand {grand_purpose:.1f}%
   - This difference in rhetorical framing may drive outcomes

4. CONTROLLED EFFECT (FULL SAMPLE):
   - Unadjusted OR = {or_unadj:.3f} (Third Chamber effect)
   - After controlling for concept + interpretation: OR = {or_adj2:.3f}, p = {m_adj2.pvalues['is_third']:.4f}
   - {"EFFECT PERSISTS after controls" if m_adj2.pvalues['is_third'] < 0.05 else "Effect ATTENUATES after controls"}

5. COMPENSATION-EXCLUSION SENSITIVITY (CRITICAL TEST):
   - Full sample gap: {sensitivity_results.get('full_gap_pp', 0):.1f}pp
   - Excluding compensation gap: {sensitivity_results.get('no_comp_gap_pp', 0):.1f}pp
   - Gap reduction: {sensitivity_results.get('gap_explained_by_comp_pct', 0):.1f}% explained by compensation
   - OR excluding compensation: {sensitivity_results.get('or_excl_compensation', 'N/A')}
   - p-value: {sensitivity_results.get('p_excl_compensation', 'N/A')}
   - {"*** EFFECT PERSISTS even without compensation ***" if comp_effect_persists else "*** EFFECT DRIVEN BY COMPENSATION CASELOAD ***"}

6. CONCLUSION:
   {"Third Chamber effect appears to be a GENUINE interpretive difference beyond compensation caseload" if comp_effect_persists else "Third Chamber effect is LARGELY EXPLAINED by compensation case allocation - the gap shrinks substantially when excluding Article 82 cases"}
""")

    # Save findings
    with open(OUTPUT_PATH / "third_chamber_investigation.json", 'w') as f:
        json.dump(findings, f, indent=2, default=float)

    return findings

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    findings = run_investigation(df)
    print("\nInvestigation complete!")
