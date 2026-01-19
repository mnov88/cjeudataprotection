#!/usr/bin/env python3
"""
09_advanced_topic_analysis.py
Advanced analysis of underexplored variables in CJEU GDPR holdings

High-priority analyses:
1. Necessity standard effect (STRICT vs REGULAR) - 86% vs 37% preliminary
2. Secondary concepts and interactions
3. Level-shifting effect re-examination
4. Balancing dynamics and competing rights
5. Article 82 doctrinal deep dive
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.generalized_linear_model import GLM
import json
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('/home/user/cjeudataprotection/analysis/output/holdings_prepared.csv')

results = {
    'n_holdings': int(len(df)),
    'n_cases': int(df['case_id'].nunique()),
    'analyses': {}
}

print("=" * 70)
print("ADVANCED TOPIC ANALYSIS: UNDEREXPLORED VARIABLES")
print("=" * 70)

# =============================================================================
# 1. NECESSITY STANDARD ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("1. NECESSITY STANDARD ANALYSIS")
print("=" * 70)

# Check necessity_standard distribution
necessity_dist = df['necessity_standard'].value_counts()
print(f"\nNecessity Standard Distribution:")
print(necessity_dist)

# Create necessity categories
df['necessity_cat'] = df['necessity_standard'].fillna('NOT_DISCUSSED')
df.loc[df['necessity_discussed'] == False, 'necessity_cat'] = 'NOT_DISCUSSED'

# Pro-DS rates by necessity standard
necessity_rates = df.groupby('necessity_cat').agg({
    'pro_ds': ['sum', 'count', 'mean']
}).round(3)
necessity_rates.columns = ['pro_ds_count', 'total', 'pro_ds_rate']
necessity_rates = necessity_rates.sort_values('pro_ds_rate', ascending=False)

print(f"\nPro-DS Rate by Necessity Standard:")
print(necessity_rates)

# Key comparison: STRICT vs REGULAR
strict_df = df[df['necessity_cat'] == 'STRICT']
regular_df = df[df['necessity_cat'] == 'REGULAR']

if len(strict_df) > 0 and len(regular_df) > 0:
    strict_rate = strict_df['pro_ds'].mean()
    regular_rate = regular_df['pro_ds'].mean()

    # Fisher's exact test
    contingency = pd.crosstab(
        df[df['necessity_cat'].isin(['STRICT', 'REGULAR'])]['necessity_cat'],
        df[df['necessity_cat'].isin(['STRICT', 'REGULAR'])]['pro_ds']
    )
    if contingency.shape == (2, 2):
        odds_ratio, p_value = stats.fisher_exact(contingency)

        print(f"\n*** KEY FINDING: STRICT vs REGULAR Necessity ***")
        print(f"STRICT necessity: {strict_rate:.1%} pro-DS (n={len(strict_df)})")
        print(f"REGULAR necessity: {regular_rate:.1%} pro-DS (n={len(regular_df)})")
        print(f"Gap: {(strict_rate - regular_rate)*100:.1f} percentage points")
        print(f"Fisher's exact OR: {odds_ratio:.2f}, p = {p_value:.4f}")

        results['analyses']['necessity_standard'] = {
            'strict_pro_ds_rate': float(round(strict_rate, 3)),
            'strict_n': int(len(strict_df)),
            'regular_pro_ds_rate': float(round(regular_rate, 3)),
            'regular_n': int(len(regular_df)),
            'gap_pp': float(round((strict_rate - regular_rate) * 100, 1)),
            'odds_ratio': float(round(odds_ratio, 2)),
            'p_value': float(round(p_value, 4)),
            'interpretation': 'STRICT necessity strongly associated with pro-DS outcomes'
        }

# Multivariate: Does necessity standard predict outcomes controlling for concept cluster?
necessity_mv = df[df['necessity_cat'].isin(['STRICT', 'REGULAR', 'NOT_DISCUSSED'])].copy()
necessity_mv['is_strict'] = (necessity_mv['necessity_cat'] == 'STRICT').astype(int)
necessity_mv['is_regular'] = (necessity_mv['necessity_cat'] == 'REGULAR').astype(int)

try:
    model_necessity = smf.logit(
        "pro_ds ~ is_strict + is_regular + C(concept_cluster)",
        data=necessity_mv
    ).fit(disp=0)

    print(f"\nMultivariate Model (controlling for concept cluster):")
    print(f"STRICT necessity OR: {np.exp(model_necessity.params['is_strict']):.2f} "
          f"(p={model_necessity.pvalues['is_strict']:.4f})")
    print(f"REGULAR necessity OR: {np.exp(model_necessity.params['is_regular']):.2f} "
          f"(p={model_necessity.pvalues['is_regular']:.4f})")

    results['analyses']['necessity_standard']['mv_strict_or'] = float(round(np.exp(model_necessity.params['is_strict']), 2))
    results['analyses']['necessity_standard']['mv_strict_p'] = float(round(model_necessity.pvalues['is_strict'], 4))
    results['analyses']['necessity_standard']['mv_regular_or'] = float(round(np.exp(model_necessity.params['is_regular']), 2))
    results['analyses']['necessity_standard']['mv_regular_p'] = float(round(model_necessity.pvalues['is_regular'], 4))
except Exception as e:
    print(f"Multivariate model failed: {e}")

# =============================================================================
# 2. SECONDARY CONCEPTS ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("2. SECONDARY CONCEPTS ANALYSIS")
print("=" * 70)

# Parse secondary concepts
df['has_secondary'] = df['secondary_concepts'].notna() & (df['secondary_concepts'] != '')
print(f"\nHoldings with secondary concepts: {df['has_secondary'].sum()} / {len(df)} ({df['has_secondary'].mean():.1%})")

# Extract individual secondary concepts
def parse_secondary(x):
    if pd.isna(x) or x == '':
        return []
    return [c.strip() for c in str(x).split(',')]

df['secondary_list'] = df['secondary_concepts'].apply(parse_secondary)

# Count secondary concept frequencies
secondary_counts = {}
for concepts in df['secondary_list']:
    for c in concepts:
        if c:
            secondary_counts[c] = secondary_counts.get(c, 0) + 1

print(f"\nTop 10 Secondary Concepts:")
for concept, count in sorted(secondary_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {concept}: {count}")

# Pro-DS rates by secondary concept presence
key_secondary = ['DATA_PROTECTION_PRINCIPLES', 'MEMBER_STATE_DISCRETION',
                 'TRANSPARENCY', 'PERSONAL_DATA_SCOPE', 'CONTROLLER_PROCESSOR']

secondary_effects = {}
print(f"\nPro-DS Rates by Secondary Concept Presence:")

for concept in key_secondary:
    df[f'has_{concept}'] = df['secondary_list'].apply(lambda x: concept in x)
    with_concept = df[df[f'has_{concept}']]
    without_concept = df[~df[f'has_{concept}']]

    if len(with_concept) >= 5:  # Minimum sample size
        with_rate = with_concept['pro_ds'].mean()
        without_rate = without_concept['pro_ds'].mean()

        print(f"\n{concept}:")
        print(f"  With: {with_rate:.1%} pro-DS (n={len(with_concept)})")
        print(f"  Without: {without_rate:.1%} pro-DS (n={len(without_concept)})")
        print(f"  Gap: {(with_rate - without_rate)*100:+.1f}pp")

        secondary_effects[concept] = {
            'with_rate': float(round(with_rate, 3)),
            'with_n': int(len(with_concept)),
            'without_rate': float(round(without_rate, 3)),
            'gap_pp': float(round((with_rate - without_rate) * 100, 1))
        }

# KEY FINDING: DATA_PROTECTION_PRINCIPLES vs MEMBER_STATE_DISCRETION
if 'has_DATA_PROTECTION_PRINCIPLES' in df.columns and 'has_MEMBER_STATE_DISCRETION' in df.columns:
    dpp = df[df['has_DATA_PROTECTION_PRINCIPLES']]['pro_ds'].mean()
    msd = df[df['has_MEMBER_STATE_DISCRETION']]['pro_ds'].mean()

    print(f"\n*** KEY FINDING: Contrasting Secondary Concepts ***")
    print(f"DATA_PROTECTION_PRINCIPLES as secondary: {dpp:.1%} pro-DS")
    print(f"MEMBER_STATE_DISCRETION as secondary: {msd:.1%} pro-DS")
    print(f"Gap: {(dpp - msd)*100:.1f} percentage points")

results['analyses']['secondary_concepts'] = {
    'holdings_with_secondary': int(df['has_secondary'].sum()),
    'pct_with_secondary': float(round(df['has_secondary'].mean(), 3)),
    'effects': secondary_effects
}

# =============================================================================
# 3. LEVEL-SHIFTING RE-EXAMINATION
# =============================================================================
print("\n" + "=" * 70)
print("3. LEVEL-SHIFTING RE-EXAMINATION")
print("=" * 70)

# Bivariate
level_shift_yes = df[df['level_shifting'] == True]
level_shift_no = df[df['level_shifting'] == False]

ls_yes_rate = level_shift_yes['pro_ds'].mean() if len(level_shift_yes) > 0 else 0
ls_no_rate = level_shift_no['pro_ds'].mean() if len(level_shift_no) > 0 else 0

print(f"\nLevel-Shifting Bivariate Analysis:")
print(f"With level-shifting: {ls_yes_rate:.1%} pro-DS (n={len(level_shift_yes)})")
print(f"Without level-shifting: {ls_no_rate:.1%} pro-DS (n={len(level_shift_no)})")
print(f"Gap: {(ls_yes_rate - ls_no_rate)*100:.1f} percentage points")

# Chi-square test
contingency_ls = pd.crosstab(df['level_shifting'].fillna(False), df['pro_ds'])
if contingency_ls.shape == (2, 2):
    chi2, p, dof, expected = stats.chi2_contingency(contingency_ls)
    phi = np.sqrt(chi2 / len(df))
    print(f"Chi-square: {chi2:.2f}, p = {p:.4f}, Phi = {phi:.3f}")

# Why was it dropped? Check collinearity with pro_ds_purpose
df['level_shifting_bool'] = df['level_shifting'].fillna(False).astype(bool)
df['pro_ds_purpose'] = (df['purpose_high_protection'] == True) | (df['purpose_fundamental_rights'] == True)

# Cross-tabulation
ls_purpose_crosstab = pd.crosstab(df['level_shifting_bool'], df['pro_ds_purpose'])
print(f"\nLevel-Shifting vs Pro-DS Purpose Cross-tabulation:")
print(ls_purpose_crosstab)

# Correlation
ls_purpose_corr = df['level_shifting_bool'].astype(int).corr(df['pro_ds_purpose'].astype(int))
print(f"Correlation between level-shifting and pro-DS purpose: {ls_purpose_corr:.3f}")

# Multivariate with both
try:
    df['ls_int'] = df['level_shifting_bool'].astype(int)
    df['purpose_int'] = df['pro_ds_purpose'].astype(int)

    model_ls = smf.logit("pro_ds ~ ls_int + purpose_int + C(concept_cluster)", data=df).fit(disp=0)

    print(f"\nMultivariate Model (level-shifting + pro-DS purpose + concept cluster):")
    print(f"Level-shifting OR: {np.exp(model_ls.params['ls_int']):.2f} (p={model_ls.pvalues['ls_int']:.4f})")
    print(f"Pro-DS purpose OR: {np.exp(model_ls.params['purpose_int']):.2f} (p={model_ls.pvalues['purpose_int']:.4f})")

    results['analyses']['level_shifting'] = {
        'bivariate_with_rate': float(round(ls_yes_rate, 3)),
        'bivariate_without_rate': float(round(ls_no_rate, 3)),
        'bivariate_gap_pp': float(round((ls_yes_rate - ls_no_rate) * 100, 1)),
        'phi': float(round(phi, 3)),
        'p_value': float(round(p, 4)),
        'correlation_with_purpose': float(round(ls_purpose_corr, 3)),
        'mv_or': float(round(np.exp(model_ls.params['ls_int']), 2)),
        'mv_p': float(round(model_ls.pvalues['ls_int'], 4)),
        'purpose_mv_or': float(round(np.exp(model_ls.params['purpose_int']), 2)),
        'purpose_mv_p': float(round(model_ls.pvalues['purpose_int'], 4))
    }

    # Check if level-shifting is significant when purpose is NOT in model
    model_ls_only = smf.logit("pro_ds ~ ls_int + C(concept_cluster)", data=df).fit(disp=0)
    print(f"\nLevel-shifting alone (no purpose control):")
    print(f"Level-shifting OR: {np.exp(model_ls_only.params['ls_int']):.2f} (p={model_ls_only.pvalues['ls_int']:.4f})")

    results['analyses']['level_shifting']['alone_or'] = float(round(np.exp(model_ls_only.params['ls_int']), 2))
    results['analyses']['level_shifting']['alone_p'] = float(round(model_ls_only.pvalues['ls_int'], 4))

except Exception as e:
    print(f"Level-shifting model failed: {e}")

# =============================================================================
# 4. BALANCING DYNAMICS ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("4. BALANCING DYNAMICS ANALYSIS")
print("=" * 70)

# Controller vs DS balancing
balancing_dist = df['controller_ds_balancing'].value_counts()
print(f"\nController-DS Balancing Distribution:")
print(balancing_dist)

# Interest prevails
interest_dist = df['interest_prevails'].value_counts()
print(f"\nInterest Prevails Distribution:")
print(interest_dist)

# Pro-DS rates by balancing outcome
balancing_analysis = df[df['controller_ds_balancing'] == True].copy()
print(f"\nAmong holdings WITH balancing analysis (n={len(balancing_analysis)}):")

if len(balancing_analysis) > 0:
    interest_rates = balancing_analysis.groupby('interest_prevails').agg({
        'pro_ds': ['sum', 'count', 'mean']
    }).round(3)
    interest_rates.columns = ['pro_ds_count', 'total', 'pro_ds_rate']
    print(interest_rates)

    results['analyses']['balancing'] = {
        'holdings_with_balancing': int(len(balancing_analysis)),
        'interest_prevails_distribution': {str(k): int(v) for k, v in interest_dist.items()},
        'pro_ds_when_ds_prevails': float(balancing_analysis[balancing_analysis['interest_prevails'] == 'DATA_SUBJECT']['pro_ds'].mean())
            if len(balancing_analysis[balancing_analysis['interest_prevails'] == 'DATA_SUBJECT']) > 0 else None,
        'pro_ds_when_controller_prevails': float(balancing_analysis[balancing_analysis['interest_prevails'] == 'CONTROLLER']['pro_ds'].mean())
            if len(balancing_analysis[balancing_analysis['interest_prevails'] == 'CONTROLLER']) > 0 else None
    }

# Other rights balancing
other_rights_dist = df['other_rights_balancing'].value_counts()
print(f"\nOther Rights Balancing Distribution:")
print(other_rights_dist)

# Which "other rights" are balanced?
other_rights_series = df[df['other_rights_balancing'] == True]['other_rights']
print(f"\nOther Rights Mentioned (when balancing present):")
for rights in other_rights_series.dropna().unique()[:10]:
    count = (other_rights_series == rights).sum()
    print(f"  {rights}: {count}")

# =============================================================================
# 5. ARTICLE 82 DOCTRINAL DEEP DIVE
# =============================================================================
print("\n" + "=" * 70)
print("5. ARTICLE 82 COMPENSATION DOCTRINAL ANALYSIS")
print("=" * 70)

# Filter to compensation cases
comp_df = df[df['primary_concept'] == 'REMEDIES_COMPENSATION'].copy()
print(f"\nArticle 82 Compensation Holdings: {len(comp_df)}")

if len(comp_df) > 0:
    # Overall rate
    comp_rate = comp_df['pro_ds'].mean()
    other_rate = df[df['primary_concept'] != 'REMEDIES_COMPENSATION']['pro_ds'].mean()
    print(f"Pro-DS rate (compensation): {comp_rate:.1%}")
    print(f"Pro-DS rate (other concepts): {other_rate:.1%}")
    print(f"Gap: {(comp_rate - other_rate)*100:.1f}pp")

    # Breakdown by ruling direction
    comp_direction = comp_df['ruling_direction'].value_counts()
    print(f"\nCompensation Holdings by Ruling Direction:")
    print(comp_direction)

    # Pro-controller and mixed compensation cases - extract justifications
    pro_controller_comp = comp_df[comp_df['ruling_direction'] == 'PRO_CONTROLLER']
    mixed_comp = comp_df[comp_df['ruling_direction'] == 'MIXED']

    print(f"\nPRO_CONTROLLER Compensation Holdings (n={len(pro_controller_comp)}):")

    # Analyze doctrinal themes in justifications
    all_non_pro_ds = comp_df[comp_df['pro_ds'] == 0]

    # Key doctrinal indicators
    themes = {
        'actual_damage': 0,
        'burden_of_proof': 0,
        'not_punitive': 0,
        'fault_required': 0,
        'no_strict_liability': 0,
        'mere_infringement_insufficient': 0
    }

    for idx, row in all_non_pro_ds.iterrows():
        justification = str(row['direction_justification']).lower() if pd.notna(row['direction_justification']) else ''
        core = str(row['core_holding']).lower() if pd.notna(row['core_holding']) else ''
        text = justification + ' ' + core

        if 'actual damage' in text or 'concrete damage' in text or 'prove damage' in text:
            themes['actual_damage'] += 1
        if 'burden' in text and 'proof' in text:
            themes['burden_of_proof'] += 1
        if 'not punitive' in text or 'purely compensatory' in text or 'compensatory function' in text:
            themes['not_punitive'] += 1
        if 'fault' in text:
            themes['fault_required'] += 1
        if 'strict liability' in text:
            themes['no_strict_liability'] += 1
        if 'mere infringement' in text or 'infringement alone' in text:
            themes['mere_infringement_insufficient'] += 1

    n_non_pro_ds = len(all_non_pro_ds)
    print(f"\nDoctrinal Themes in Non-Pro-DS Compensation Holdings (n={n_non_pro_ds}):")
    for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
        pct = count / n_non_pro_ds * 100 if n_non_pro_ds > 0 else 0
        print(f"  {theme}: {count} ({pct:.1f}%)")

    # Secondary concepts in compensation cases
    comp_secondary = comp_df['secondary_list'].explode().value_counts()
    print(f"\nSecondary Concepts in Compensation Holdings:")
    print(comp_secondary.head(10))

    # Temporal pattern
    comp_by_year = comp_df.groupby('year').agg({
        'pro_ds': ['count', 'mean']
    }).round(3)
    comp_by_year.columns = ['n', 'pro_ds_rate']
    print(f"\nCompensation Holdings by Year:")
    print(comp_by_year)

    results['analyses']['article_82'] = {
        'n_holdings': int(len(comp_df)),
        'pro_ds_rate': float(round(comp_rate, 3)),
        'other_concepts_rate': float(round(other_rate, 3)),
        'gap_pp': float(round((comp_rate - other_rate) * 100, 1)),
        'direction_distribution': {str(k): int(v) for k, v in comp_direction.items()},
        'doctrinal_themes': {k: int(v) for k, v in themes.items()},
        'n_non_pro_ds': int(n_non_pro_ds)
    }

# =============================================================================
# 6. PRECEDENT CITATION ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("6. PRECEDENT CITATION PATTERNS")
print("=" * 70)

# Citation count distribution
cite_dist = df['cited_case_count'].describe()
print(f"\nCitation Count Distribution:")
print(cite_dist)

# Pro-DS rate by citation intensity
df['cite_category'] = pd.cut(df['cited_case_count'],
                              bins=[-1, 0, 2, 5, 100],
                              labels=['0', '1-2', '3-5', '6+'])

cite_rates = df.groupby('cite_category').agg({
    'pro_ds': ['count', 'mean']
}).round(3)
cite_rates.columns = ['n', 'pro_ds_rate']
print(f"\nPro-DS Rate by Citation Count:")
print(cite_rates)

results['analyses']['citations'] = {
    'mean_citations': float(round(df['cited_case_count'].mean(), 2)),
    'median_citations': float(df['cited_case_count'].median()),
    'max_citations': int(df['cited_case_count'].max()),
    'rates_by_category': cite_rates.to_dict()
}

# =============================================================================
# SUMMARY OF KEY FINDINGS
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY OF KEY FINDINGS")
print("=" * 70)

findings = []

# Necessity standard
if 'necessity_standard' in results['analyses']:
    ns = results['analyses']['necessity_standard']
    findings.append(f"1. STRICT vs REGULAR necessity: {ns['gap_pp']}pp gap (OR={ns['odds_ratio']}, p={ns['p_value']})")

# Secondary concepts
if 'secondary_concepts' in results['analyses']:
    sc = results['analyses']['secondary_concepts']['effects']
    if 'DATA_PROTECTION_PRINCIPLES' in sc and 'MEMBER_STATE_DISCRETION' in sc:
        dpp_gap = sc['DATA_PROTECTION_PRINCIPLES']['gap_pp']
        msd_gap = sc['MEMBER_STATE_DISCRETION']['gap_pp']
        findings.append(f"2. DATA_PROTECTION_PRINCIPLES secondary: {dpp_gap:+.1f}pp effect")
        findings.append(f"   MEMBER_STATE_DISCRETION secondary: {msd_gap:+.1f}pp effect")

# Level-shifting
if 'level_shifting' in results['analyses']:
    ls = results['analyses']['level_shifting']
    findings.append(f"3. Level-shifting bivariate gap: {ls['bivariate_gap_pp']}pp")
    findings.append(f"   Correlation with pro-DS purpose: {ls['correlation_with_purpose']:.3f}")
    findings.append(f"   Alone (no purpose): OR={ls['alone_or']}, p={ls['alone_p']}")
    findings.append(f"   With purpose control: OR={ls['mv_or']}, p={ls['mv_p']}")

# Article 82
if 'article_82' in results['analyses']:
    a82 = results['analyses']['article_82']
    findings.append(f"4. Article 82 compensation gap: {a82['gap_pp']}pp below other concepts")
    top_theme = max(a82['doctrinal_themes'].items(), key=lambda x: x[1])
    findings.append(f"   Top doctrinal barrier: {top_theme[0]} ({top_theme[1]}/{a82['n_non_pro_ds']} non-pro-DS)")

for f in findings:
    print(f)

# Save results
with open('/home/user/cjeudataprotection/analysis/output/advanced_topic_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to analysis/output/advanced_topic_analysis.json")
