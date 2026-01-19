# CJEU GDPR Statistical Analysis

Empirical analysis of factors predicting pro-data subject vs. pro-controller outcomes in CJEU GDPR decisions.

## Quick Start

```bash
# Run complete analysis pipeline
python3 scripts/01_data_preparation.py
python3 scripts/02_bivariate_analysis.py
python3 scripts/03_multivariate_analysis.py
python3 scripts/04_quality_check.py
```

## Directory Structure

```
analysis/
├── README.md                    # This file
├── ANALYSIS_REPORT.md          # Full findings report
├── scripts/
│   ├── 01_data_preparation.py  # Variable transformation
│   ├── 02_bivariate_analysis.py # Chi-square tests
│   ├── 03_multivariate_analysis.py # Logistic regression
│   └── 04_quality_check.py     # Case validation
├── output/
│   ├── holdings_prepared.csv   # Analysis-ready data
│   ├── bivariate_summary.csv   # Test results
│   ├── model_comparison.csv    # Model fit statistics
│   └── ...                     # Additional outputs
└── figures/                    # (Placeholder for visualizations)
```

## Key Findings

1. **60.8% of holdings favor data subjects**
2. **Pro-DS purpose invocation (HIGH_LEVEL_OF_PROTECTION/FUNDAMENTAL_RIGHTS) increases odds 4.5x**
3. **RIGHTS and SCOPE concept clusters predict pro-DS outcomes (OR≈7.7)**
4. **Grand Chamber more pro-DS (77.6%) than Third Chamber (34.1%)**
5. **Balancing does NOT predict fewer pro-DS outcomes** (contrary to hypothesis)

## Dependencies

```
pandas >= 2.0
numpy >= 1.24
scipy >= 1.10
statsmodels >= 0.14
scikit-learn >= 1.3
```

Install: `pip install pandas numpy scipy statsmodels scikit-learn`

## Methodology

- **Unit of analysis**: Individual holding (N=181)
- **Dependent variable**: Binary (PRO_DATA_SUBJECT=1, OTHER=0)
- **Bivariate**: Chi-square/Fisher's exact with Benjamini-Hochberg FDR
- **Multivariate**: Hierarchical logistic regression (6 nested models)
- **Validation**: Individual case review for each finding

See `ANALYSIS_REPORT.md` for complete methodology and results.
