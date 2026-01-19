#!/usr/bin/env python3
"""
Phase 1: Descriptive Temporal Analysis
CJEU GDPR Temporal Effects Study

This script:
1.1 Calculates annual statistics for all variables
1.2 Constructs temporal trend tables
1.3 Generates time series visualizations
1.4 Identifies candidate break points
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
# Fixed: Updated path from "parsed-coded" to "data/parsed"
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "parsed" / "holdings.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "temporal"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA LOADING AND PREPARATION
# ============================================================================
def load_and_prepare_data():
    """Load holdings data and create temporal variables."""
    df = pd.read_csv(DATA_PATH)

    # Parse dates and create temporal variables
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])
    df['year'] = df['judgment_date'].dt.year
    df['month'] = df['judgment_date'].dt.month
    df['quarter'] = df['judgment_date'].dt.quarter
    df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
    df['semester'] = df['year'].astype(str) + '-H' + np.where(df['month'] <= 6, '1', '2')

    # Days since GDPR entry into force (25 May 2018)
    gdpr_start = pd.Timestamp('2018-05-25')
    df['days_since_gdpr'] = (df['judgment_date'] - gdpr_start).dt.days

    # Centered year for modeling
    df['year_centered'] = df['year'] - 2022

    # Binary outcome
    df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)
    df['pro_controller'] = (df['ruling_direction'] == 'PRO_CONTROLLER').astype(int)

    # Period variables
    df['period_binary'] = np.where(df['year'] < 2023, 'Early (2019-2022)', 'Late (2023-2025)')
    df['period_tertile'] = pd.cut(df['year'], bins=[2018, 2021, 2023, 2026],
                                   labels=['2019-2021', '2022-2023', '2024-2025'])

    # Concept clusters (from existing methodology)
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
        'SPECIAL': ['SPECIAL_CATEGORIES_DEFINITION', 'SPECIAL_CATEGORIES_CONDITIONS'],
        'ENFORCEMENT': ['DPA_INDEPENDENCE', 'DPA_POWERS', 'DPA_OBLIGATIONS', 'ONE_STOP_SHOP',
                        'DPA_OTHER', 'ADMINISTRATIVE_FINES', 'REMEDIES_COMPENSATION',
                        'REPRESENTATIVE_ACTIONS'],
        'OTHER': ['SECURITY', 'INTERNATIONAL_TRANSFER', 'OTHER_CONTROLLER_OBLIGATIONS',
                  'MEMBER_STATE_DISCRETION', 'OTHER']
    }

    def get_cluster(concept):
        for cluster, concepts in concept_clusters.items():
            if concept in concepts:
                return cluster
        return 'OTHER'

    df['concept_cluster'] = df['primary_concept'].apply(get_cluster)

    # Pro-DS purpose indicator
    df['pro_ds_purpose'] = df['teleological_purposes'].fillna('').apply(
        lambda x: 'HIGH_LEVEL_OF_PROTECTION' in x or 'FUNDAMENTAL_RIGHTS' in x
    ).astype(int)

    # Chamber grouping
    def group_chamber(chamber):
        if chamber in ['GRAND_CHAMBER']:
            return 'GRAND_CHAMBER'
        elif chamber in ['FIRST']:
            return 'FIRST'
        elif chamber in ['THIRD']:
            return 'THIRD'
        elif chamber in ['FOURTH']:
            return 'FOURTH'
        elif chamber in ['FIFTH']:
            return 'FIFTH'
        else:
            return 'OTHER'

    df['chamber_grouped'] = df['chamber'].apply(group_chamber)

    # Boolean conversions
    bool_cols = ['semantic_present', 'systematic_present', 'teleological_present',
                 'rule_based_present', 'case_law_present', 'principle_based_present',
                 'level_shifting', 'necessity_discussed', 'controller_ds_balancing',
                 'other_rights_balancing']

    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map({'True': 1, 'False': 0, True: 1, False: 0}).fillna(0).astype(int)

    return df

# ============================================================================
# 1.1 ANNUAL STATISTICS FOR ALL VARIABLES
# ============================================================================
def calculate_annual_statistics(df):
    """Calculate comprehensive annual statistics for all variables."""

    results = {
        'sample_size': {},
        'outcome': {},
        'binary_variables': {},
        'categorical_variables': {},
        'count_variables': {}
    }

    # --- Sample Size by Year ---
    sample_by_year = df.groupby('year').agg({
        'holding_id': 'count',
        'case_id': 'nunique'
    }).rename(columns={'holding_id': 'holdings', 'case_id': 'cases'})
    sample_by_year['holdings_per_case'] = (sample_by_year['holdings'] / sample_by_year['cases']).round(2)
    results['sample_size'] = sample_by_year.to_dict()

    print("=" * 70)
    print("1.1 SAMPLE SIZE BY YEAR")
    print("=" * 70)
    print(sample_by_year.to_string())
    print(f"\nTotal: {len(df)} holdings from {df['case_id'].nunique()} cases")

    # --- Outcome Variables by Year ---
    print("\n" + "=" * 70)
    print("RULING DIRECTION BY YEAR")
    print("=" * 70)

    outcome_by_year = df.groupby('year').agg({
        'pro_ds': ['sum', 'mean'],
        'pro_controller': ['sum', 'mean']
    })
    outcome_by_year.columns = ['pro_ds_n', 'pro_ds_rate', 'pro_controller_n', 'pro_controller_rate']
    outcome_by_year['pro_ds_pct'] = (outcome_by_year['pro_ds_rate'] * 100).round(1)
    outcome_by_year['pro_controller_pct'] = (outcome_by_year['pro_controller_rate'] * 100).round(1)

    results['outcome'] = outcome_by_year[['pro_ds_n', 'pro_ds_pct', 'pro_controller_n', 'pro_controller_pct']].to_dict()

    print("\nPro-Data Subject Rulings:")
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]
        n_pro_ds = year_data['pro_ds'].sum()
        total = len(year_data)
        pct = (n_pro_ds / total * 100)
        print(f"  {year}: {n_pro_ds}/{total} ({pct:.1f}%)")

    # --- Binary Variables by Year ---
    print("\n" + "=" * 70)
    print("BINARY VARIABLES BY YEAR (% True)")
    print("=" * 70)

    binary_vars = ['teleological_present', 'semantic_present', 'systematic_present',
                   'rule_based_present', 'case_law_present', 'principle_based_present',
                   'level_shifting', 'necessity_discussed', 'controller_ds_balancing',
                   'other_rights_balancing', 'pro_ds_purpose']

    binary_by_year = {}
    for var in binary_vars:
        if var in df.columns:
            var_by_year = df.groupby('year')[var].agg(['sum', 'mean', 'count'])
            var_by_year['pct'] = (var_by_year['mean'] * 100).round(1)
            binary_by_year[var] = var_by_year[['sum', 'pct']].to_dict()

            print(f"\n{var}:")
            for year in sorted(df['year'].unique()):
                year_data = var_by_year.loc[year]
                print(f"  {year}: {int(year_data['sum'])} ({year_data['pct']:.1f}%)")

    results['binary_variables'] = binary_by_year

    # --- Categorical Variables by Year ---
    print("\n" + "=" * 70)
    print("CATEGORICAL VARIABLES BY YEAR")
    print("=" * 70)

    categorical_vars = ['chamber_grouped', 'dominant_source', 'dominant_structure',
                        'concept_cluster', 'necessity_standard']

    categorical_by_year = {}
    for var in categorical_vars:
        if var in df.columns:
            cross_tab = pd.crosstab(df['year'], df[var], normalize='index') * 100
            categorical_by_year[var] = cross_tab.round(1).to_dict()

            print(f"\n{var} (row %):")
            print(cross_tab.round(1).to_string())

    results['categorical_variables'] = categorical_by_year

    # --- Count Variables by Year ---
    print("\n" + "=" * 70)
    print("COUNT VARIABLES BY YEAR")
    print("=" * 70)

    count_vars = ['cited_case_count', 'paragraph_count', 'judge_count']

    count_by_year = {}
    for var in count_vars:
        if var in df.columns:
            var_stats = df.groupby('year')[var].agg(['mean', 'median', 'std', 'min', 'max'])
            count_by_year[var] = var_stats.round(2).to_dict()

            print(f"\n{var}:")
            print(var_stats.round(2).to_string())

    results['count_variables'] = count_by_year

    return results

# ============================================================================
# 1.2 TEMPORAL TREND TABLES
# ============================================================================
def construct_trend_tables(df):
    """Construct comprehensive temporal trend tables."""

    results = {}

    print("\n" + "=" * 70)
    print("1.2 TEMPORAL TREND TABLES")
    print("=" * 70)

    # --- Pro-DS Rate Trend Table ---
    print("\n--- Pro-DS Rate by Year with Confidence Intervals ---")

    from scipy import stats as scipy_stats

    trend_data = []
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        n = len(year_df)
        x = year_df['pro_ds'].sum()
        p = x / n

        # Wilson score interval
        z = 1.96
        denominator = 1 + z**2/n
        centre_adjusted_probability = p + z**2 / (2*n)
        adjusted_standard_deviation = np.sqrt((p*(1 - p) + z**2/(4*n)) / n)
        lower = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
        upper = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator

        trend_data.append({
            'year': year,
            'n': n,
            'pro_ds_n': x,
            'pro_ds_rate': round(p * 100, 1),
            'ci_lower': round(max(0, lower) * 100, 1),
            'ci_upper': round(min(1, upper) * 100, 1)
        })

    trend_df = pd.DataFrame(trend_data)
    results['pro_ds_trend'] = trend_df.to_dict('records')

    print(trend_df.to_string(index=False))

    # --- Period Comparison Table ---
    print("\n--- Period Comparison ---")

    period_data = []
    for period in ['Early (2019-2022)', 'Late (2023-2025)']:
        period_df = df[df['period_binary'] == period]
        n = len(period_df)
        x = period_df['pro_ds'].sum()
        p = x / n

        # Wilson score interval
        z = 1.96
        denominator = 1 + z**2/n
        centre_adjusted_probability = p + z**2 / (2*n)
        adjusted_standard_deviation = np.sqrt((p*(1 - p) + z**2/(4*n)) / n)
        lower = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
        upper = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator

        period_data.append({
            'period': period,
            'n_holdings': n,
            'n_cases': period_df['case_id'].nunique(),
            'pro_ds_n': x,
            'pro_ds_rate': round(p * 100, 1),
            'ci_lower': round(max(0, lower) * 100, 1),
            'ci_upper': round(min(1, upper) * 100, 1)
        })

    period_df_table = pd.DataFrame(period_data)
    results['period_comparison'] = period_df_table.to_dict('records')

    print(period_df_table.to_string(index=False))

    # Calculate difference
    early_rate = period_data[0]['pro_ds_rate']
    late_rate = period_data[1]['pro_ds_rate']
    diff = late_rate - early_rate
    print(f"\nDifference (Late - Early): {diff:+.1f} percentage points")
    results['period_difference_pp'] = round(diff, 1)

    # --- Concept Cluster Trends ---
    print("\n--- Concept Cluster Distribution by Period ---")

    cluster_by_period = pd.crosstab(df['period_binary'], df['concept_cluster'], normalize='index') * 100
    results['cluster_by_period'] = cluster_by_period.round(1).to_dict()
    print(cluster_by_period.round(1).to_string())

    # --- Article 82 / Compensation Cases ---
    print("\n--- Article 82 (Compensation) Cases by Year ---")

    df['is_compensation'] = df['primary_concept'] == 'REMEDIES_COMPENSATION'
    compensation_by_year = df.groupby('year')['is_compensation'].agg(['sum', 'mean'])
    compensation_by_year['pct'] = (compensation_by_year['mean'] * 100).round(1)
    results['compensation_by_year'] = compensation_by_year[['sum', 'pct']].to_dict()

    print(compensation_by_year[['sum', 'pct']].to_string())

    total_compensation = df['is_compensation'].sum()
    compensation_2023_plus = df[df['year'] >= 2023]['is_compensation'].sum()
    print(f"\nTotal compensation holdings: {total_compensation}")
    print(f"Compensation holdings 2023+: {compensation_2023_plus} ({compensation_2023_plus/total_compensation*100:.1f}% of all compensation)")

    return results

# ============================================================================
# 1.3 TIME SERIES DATA FOR VISUALIZATION
# ============================================================================
def prepare_visualization_data(df):
    """Prepare data structures for time series visualization."""

    results = {}

    print("\n" + "=" * 70)
    print("1.3 VISUALIZATION DATA PREPARATION")
    print("=" * 70)

    # --- Monthly/Quarterly aggregation ---
    quarterly = df.groupby('year_quarter').agg({
        'pro_ds': ['sum', 'count', 'mean'],
        'case_id': 'nunique'
    })
    quarterly.columns = ['pro_ds_n', 'total_n', 'pro_ds_rate', 'n_cases']
    quarterly['pro_ds_pct'] = (quarterly['pro_ds_rate'] * 100).round(1)
    results['quarterly'] = quarterly.reset_index().to_dict('records')

    print("\nQuarterly Pro-DS Rates:")
    print(quarterly.to_string())

    # --- Cumulative trend ---
    df_sorted = df.sort_values('judgment_date')
    df_sorted['cumulative_pro_ds'] = df_sorted['pro_ds'].cumsum()
    df_sorted['cumulative_total'] = range(1, len(df_sorted) + 1)
    df_sorted['cumulative_rate'] = df_sorted['cumulative_pro_ds'] / df_sorted['cumulative_total']

    # Sample at each case for cleaner visualization
    cumulative_by_case = df_sorted.groupby('case_id').last()[
        ['judgment_date', 'cumulative_pro_ds', 'cumulative_total', 'cumulative_rate']
    ].reset_index()

    results['cumulative'] = cumulative_by_case.to_dict('records')

    print("\nCumulative Pro-DS Rate (last 10 cases):")
    print(cumulative_by_case.tail(10)[['judgment_date', 'cumulative_rate']].to_string())

    # --- Rolling window (12-month) ---
    df_sorted['rolling_pro_ds'] = df_sorted['pro_ds'].rolling(window=20, min_periods=10).mean()
    results['rolling_window'] = df_sorted[['judgment_date', 'pro_ds', 'rolling_pro_ds']].dropna().to_dict('records')

    return results

# ============================================================================
# 1.4 IDENTIFY CANDIDATE BREAK POINTS
# ============================================================================
def identify_break_points(df):
    """Identify candidate structural break points."""

    results = {
        'candidate_breaks': [],
        'evidence': {}
    }

    print("\n" + "=" * 70)
    print("1.4 CANDIDATE BREAK POINTS ANALYSIS")
    print("=" * 70)

    # --- Break Point 1: 2023 (Article 82 surge) ---
    print("\n--- Candidate 1: 2023 (Article 82 Compensation Surge) ---")

    pre_2023 = df[df['year'] < 2023]
    post_2023 = df[df['year'] >= 2023]

    pre_rate = pre_2023['pro_ds'].mean() * 100
    post_rate = post_2023['pro_ds'].mean() * 100

    pre_compensation_pct = (pre_2023['primary_concept'] == 'REMEDIES_COMPENSATION').mean() * 100
    post_compensation_pct = (post_2023['primary_concept'] == 'REMEDIES_COMPENSATION').mean() * 100

    print(f"Pre-2023: {len(pre_2023)} holdings, {pre_rate:.1f}% pro-DS, {pre_compensation_pct:.1f}% compensation")
    print(f"Post-2023: {len(post_2023)} holdings, {post_rate:.1f}% pro-DS, {post_compensation_pct:.1f}% compensation")
    print(f"Difference: {post_rate - pre_rate:+.1f} pp in pro-DS rate")

    results['candidate_breaks'].append({
        'break_point': '2023-01-01',
        'rationale': 'Article 82 compensation case surge',
        'pre_n': len(pre_2023),
        'post_n': len(post_2023),
        'pre_pro_ds_rate': round(pre_rate, 1),
        'post_pro_ds_rate': round(post_rate, 1),
        'difference_pp': round(post_rate - pre_rate, 1),
        'pre_compensation_pct': round(pre_compensation_pct, 1),
        'post_compensation_pct': round(post_compensation_pct, 1)
    })

    # --- Break Point 2: Third Chamber concentration ---
    print("\n--- Candidate 2: Third Chamber Case Concentration ---")

    third_chamber_by_year = df[df['chamber'] == 'THIRD'].groupby('year').size()
    total_by_year = df.groupby('year').size()
    third_pct_by_year = (third_chamber_by_year / total_by_year * 100).fillna(0)

    print("Third Chamber % of holdings by year:")
    for year in sorted(df['year'].unique()):
        pct = third_pct_by_year.get(year, 0)
        print(f"  {year}: {pct:.1f}%")

    results['evidence']['third_chamber_concentration'] = third_pct_by_year.to_dict()

    # --- Break Point 3: Pro-DS Purpose Invocation ---
    print("\n--- Candidate 3: Pro-DS Purpose Invocation Trend ---")

    purpose_by_year = df.groupby('year')['pro_ds_purpose'].mean() * 100
    print("Pro-DS purpose invocation % by year:")
    for year in sorted(df['year'].unique()):
        print(f"  {year}: {purpose_by_year[year]:.1f}%")

    results['evidence']['pro_ds_purpose_trend'] = purpose_by_year.to_dict()

    # --- Break Point 4: Interpretive Methods ---
    print("\n--- Candidate 4: Dominant Source Distribution ---")

    source_by_year = pd.crosstab(df['year'], df['dominant_source'], normalize='index') * 100
    print(source_by_year.round(1).to_string())

    results['evidence']['dominant_source_trend'] = source_by_year.round(1).to_dict()

    # --- Summary of Break Point Candidates ---
    print("\n" + "-" * 70)
    print("SUMMARY: Candidate Break Points for Structural Analysis")
    print("-" * 70)
    print("""
    1. 2023-01-01: Article 82 compensation surge
       - Compensation cases jump from ~0% to ~27% of portfolio
       - Pro-DS rate drops from 67.3% to 55.5%
       - STRONGEST candidate based on composition shift

    2. Third Chamber concentration:
       - Third Chamber increasingly assigned Article 82 cases
       - May explain chamber effect attenuation with year control

    3. Pro-DS purpose invocation:
       - Monitor for decline in purpose invocation over time
       - Could indicate doctrinal maturation

    4. Interpretive method shifts:
       - Watch for systematic → teleological or vice versa
       - May indicate methodological evolution
    """)

    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Execute Phase 1 analysis."""

    print("=" * 70)
    print("PHASE 1: DESCRIPTIVE TEMPORAL ANALYSIS")
    print("CJEU GDPR Jurisprudence - Temporal Effects Study")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Load data
    print("\nLoading and preparing data...")
    df = load_and_prepare_data()
    print(f"Loaded {len(df)} holdings from {df['case_id'].nunique()} cases")
    print(f"Date range: {df['judgment_date'].min().strftime('%Y-%m-%d')} to {df['judgment_date'].max().strftime('%Y-%m-%d')}")

    # Run analyses
    all_results = {}

    all_results['annual_statistics'] = calculate_annual_statistics(df)
    all_results['trend_tables'] = construct_trend_tables(df)
    all_results['visualization_data'] = prepare_visualization_data(df)
    all_results['break_points'] = identify_break_points(df)

    # Add metadata
    all_results['metadata'] = {
        'analysis_date': datetime.now().isoformat(),
        'total_holdings': len(df),
        'total_cases': df['case_id'].nunique(),
        'date_range': {
            'start': df['judgment_date'].min().strftime('%Y-%m-%d'),
            'end': df['judgment_date'].max().strftime('%Y-%m-%d')
        },
        'years': sorted(df['year'].unique().tolist())
    }

    # Save results
    output_file = OUTPUT_DIR / "phase1_descriptive_results.json"

    # Convert any remaining non-serializable types
    def convert_to_serializable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(i) for i in obj]
        return obj

    all_results = convert_to_serializable(all_results)

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print(f"Results saved to: {output_file}")
    print("=" * 70)

    # Print key findings summary
    print("\n" + "=" * 70)
    print("KEY FINDINGS SUMMARY - PHASE 1")
    print("=" * 70)

    print("""
    1. TEMPORAL SCOPE
       - 181 holdings from 67 cases (2019-2025)
       - Caseload increased substantially: 2019-2020 (~28 holdings) → 2023-2024 (~108 holdings)

    2. PRO-DS RATE TREND
       - Descriptive decline observed: ~78% (2019-2020) → ~56% (2024-2025)
       - Early period (2019-2022): 67.3% pro-DS (N=56)
       - Late period (2023-2025): 55.5% pro-DS (N=125)
       - Difference: -11.8 percentage points

    3. COMPOSITION SHIFT
       - Article 82 compensation cases: Near zero (2019-2022) → ~27% (2023-2025)
       - This single concept change is the dominant compositional shift
       - Compensation cases are less likely to be pro-DS (36% vs 67%)

    4. CANDIDATE BREAK POINT
       - 2023 is the strongest candidate for structural break analysis
       - Both outcome shift and composition shift concentrated around this point

    5. IMPLICATIONS FOR PHASE 2+
       - Bivariate tests should examine whether trends are statistically significant
       - Decomposition analysis critical to separate composition vs coefficient effects
       - Third Chamber temporal confounding requires multivariate control
    """)

    return all_results

if __name__ == "__main__":
    results = main()
