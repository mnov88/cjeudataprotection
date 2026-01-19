# CJEU GDPR Statistical Analysis

Empirical analysis of factors predicting pro-data subject vs. pro-controller outcomes in CJEU GDPR decisions.

## Quick Start

```bash
# Install dependencies
pip install pandas numpy scipy statsmodels scikit-learn

# Run complete analysis pipeline
python scripts/01_data_preparation.py
python scripts/02_bivariate_analysis.py
python scripts/03_multivariate_analysis.py
python scripts/04_quality_check.py
```

## Directory Structure

```
analysis/
├── README.md                    # This file
├── ANALYSIS_REPORT.md          # Full findings report
├── SUPPLEMENTARY_FINDINGS.md   # Additional analyses
├── scripts/
│   ├── 01_data_preparation.py  # Variable transformation
│   ├── 02_bivariate_analysis.py # Chi-square tests
│   ├── 03_multivariate_analysis.py # Logistic regression
│   ├── 04_quality_check.py     # Case validation
│   ├── 05_third_chamber_investigation.py
│   ├── 06_mixed_effects_models.py
│   ├── 07_compensation_paradox.py
│   ├── 08_reviewer_response_analysis.py
│   ├── 09_advanced_topic_analysis.py
│   ├── 10-15_*.py              # Citation & judicial analyses
│   └── run_analysis.py         # Pipeline runner
└── output/
    ├── holdings_prepared.csv   # Analysis-ready data
    ├── bivariate_*.csv/json    # Bivariate test results
    ├── multivariate_*.csv/json # Regression results
    ├── citation_network/       # Citation analysis outputs
    └── temporal/               # Temporal analysis outputs
```

## Key Findings

1. **60.8% of holdings favor data subjects**
2. **Teleological interpretation** (HIGH_LEVEL_OF_PROTECTION/FUNDAMENTAL_RIGHTS) increases odds 4.5x
3. **RIGHTS and SCOPE concept clusters** predict pro-DS outcomes (OR≈7.7)
4. **Grand Chamber** more pro-DS (77.6%) than Third Chamber (34.1%)
5. **Balancing does NOT predict fewer pro-DS outcomes** (contrary to hypothesis)

## Analysis Pipeline

### Phase 1: Data Preparation
`01_data_preparation.py` - Transforms raw coded data into analysis-ready format:
- Binary outcome coding
- Variable recoding and grouping
- Missing value handling

### Phase 2: Bivariate Analysis
`02_bivariate_analysis.py` - Tests individual predictors:
- Chi-square tests for categorical variables
- Fisher's exact test for small cells
- Benjamini-Hochberg FDR correction

### Phase 3: Multivariate Analysis
`03_multivariate_analysis.py` - Logistic regression:
- Hierarchical model building (6 nested models)
- Odds ratios with 95% confidence intervals
- Model comparison (AIC, BIC, pseudo-R²)

### Phase 4: Robustness Checks
`04_quality_check.py` and beyond - Validation:
- Individual case review
- Third Chamber investigation
- Mixed effects for case clustering
- Compensation paradox analysis

## Data Sources

Input: `../data/parsed/holdings.csv` (from parser.py)

Output files in `output/`:
| File | Description |
|------|-------------|
| `holdings_prepared.csv` | Transformed analysis data |
| `bivariate_summary.csv` | All bivariate test results |
| `model_comparison.csv` | Nested model fit statistics |
| `final_model_coefficients.csv` | Final model parameters |

## Methodology

- **Unit of analysis**: Individual holding (N=181)
- **Dependent variable**: Binary (PRO_DATA_SUBJECT=1, OTHER=0)
- **Bivariate tests**: Chi-square/Fisher's exact with FDR correction (α=0.05)
- **Multivariate**: Hierarchical logistic regression
- **Clustering**: Mixed effects models account for within-case correlation

## Dependencies

```
pandas >= 2.0
numpy >= 1.24
scipy >= 1.10
statsmodels >= 0.14
scikit-learn >= 1.3
```

## Extended Analyses

### Citation Network (`scripts/10-15_citation_*.py`)
- Network construction and metrics
- Bivariate/multivariate analysis of citation patterns
- Influence propagation analysis

### Judicial Analysis (`scripts/10-15_judicial_*.py`)
- Rapporteur and chamber effects
- Judge co-occurrence patterns
- Robustness checks for judicial variables

### Temporal Analysis (`scripts/10-14_temporal_*.py`)
- Time trends in ruling direction
- Period decomposition
- Interpretive method evolution

See `../docs/methodology/` for detailed methodology documentation.
See `../docs/findings/ACADEMIC_PAPER.md` for complete results.
