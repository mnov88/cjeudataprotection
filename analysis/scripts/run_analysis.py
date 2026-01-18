#!/usr/bin/env python3
"""
run_analysis.py
===============
Master script to run the complete CJEU GDPR statistical analysis pipeline.
"""

import sys
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

def main():
    print("\n" + "=" * 70)
    print("CJEU GDPR EMPIRICAL ANALYSIS PIPELINE")
    print("=" * 70)
    print("\nThis analysis examines factors associated with pro-data subject")
    print("vs. pro-controller rulings in CJEU GDPR decisions.")
    print("=" * 70)

    # Step 1: Data Preparation
    print("\n\n" + "#" * 70)
    print("# STEP 1: DATA PREPARATION")
    print("#" * 70)
    from scripts_01_data_preparation import load_and_prepare_data
    df = load_and_prepare_data()

    # Step 2: Bivariate Analysis
    print("\n\n" + "#" * 70)
    print("# STEP 2: BIVARIATE ANALYSIS")
    print("#" * 70)
    from scripts_02_bivariate_analysis import run_bivariate_analysis
    bivariate_results, bivariate_summary = run_bivariate_analysis(df)

    # Step 3: Multivariate Analysis
    print("\n\n" + "#" * 70)
    print("# STEP 3: MULTIVARIATE ANALYSIS")
    print("#" * 70)
    from scripts_03_multivariate_analysis import run_multivariate_analysis
    models, multivariate_results = run_multivariate_analysis(df)

    # Step 4: Quality Check
    print("\n\n" + "#" * 70)
    print("# STEP 4: QUALITY CHECK")
    print("#" * 70)
    from scripts_04_quality_check import run_quality_check
    quality_findings = run_quality_check(df)

    print("\n\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nAll results saved to: analysis/output/")
    print("\nKey output files:")
    print("  - holdings_prepared.csv: Analysis-ready dataset")
    print("  - bivariate_summary.csv: Chi-square test results")
    print("  - model_comparison.csv: Logistic regression model comparison")
    print("  - final_model_coefficients.csv: Best model coefficients")
    print("  - quality_check_summary.csv: Case review summary")

if __name__ == "__main__":
    main()
