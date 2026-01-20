# CJEU GDPR Jurisprudence Analysis

Empirical analysis of CJEU (Court of Justice of the European Union) decisions interpreting the GDPR, examining factors associated with pro-data subject vs. pro-controller outcomes.

## Overview

This repository contains:
- **67 CJEU GDPR decisions** (2019-2025) with full judgment texts
- **181 coded holdings** analyzed using a 43-question coding schema
- **Statistical analysis** identifying predictors of ruling direction
- **Citation network analysis** of inter-case references
- **Temporal analysis** of jurisprudential evolution

## Key Findings

- **60.8% of holdings favor data subjects**
- **Teleological interpretation** (invoking "high level of protection" or "fundamental rights") increases pro-data subject odds by 3.89x
- **Third Chamber** rules pro-data subject at ~34% vs. Grand Chamber at ~78%
- **Compensation gap**: Article 82 damages cases are 30.8pp less likely to favor data subjects

## Repository Structure

```
├── data/
│   ├── decisions/          # Raw CJEU judgment texts (Markdown)
│   ├── coded/              # Coded holdings per judgment
│   ├── parsed/             # Processed data (JSON, CSV, SQLite)
│   └── metadata/           # Case metadata from EUR-Lex
│
├── scripts/                # Data processing utilities
│   ├── parser.py           # Parse coded decisions → JSON/CSV/DB
│   ├── viewer.html         # Interactive data browser
│   ├── extract_judges.py   # Judge/rapporteur extraction
│   └── README.md           # Scripts documentation
│
├── analysis/               # Statistical analysis
│   ├── scripts/            # Analysis pipeline (Python)
│   ├── output/             # Results, models, figures
│   └── README.md           # Analysis documentation
│
├── docs/                   # Documentation
│   ├── methodology/        # Statistical & analytical methods
│   ├── findings/           # Research papers & reports
│   ├── coding-agent-instructions.md  # 43-question coding schema
│   └── REVISION_PLAN.md    # Planned improvements
│
└── README.md               # This file
```

## Quick Start

### 1. Explore the Data

```bash
# Open interactive viewer
open scripts/viewer.html

# Or query the SQLite database
sqlite3 data/parsed/gdpr_cjeu.db "SELECT * FROM holdings LIMIT 5;"
```

### 2. Run Statistical Analysis

```bash
cd analysis
pip install pandas numpy scipy statsmodels scikit-learn

# Run analysis pipeline
python scripts/01_data_preparation.py
python scripts/02_bivariate_analysis.py
python scripts/03_multivariate_analysis.py
```

### 3. Parse New Coded Decisions

```bash
python scripts/parser.py data/coded/ -o data/parsed/
```

## Data Formats

| File | Description | Use Case |
|------|-------------|----------|
| `data/parsed/cases.json` | Hierarchical case data | Web viewer, programmatic access |
| `data/parsed/holdings.csv` | Flat holding-level data | R, pandas, Excel, statistics |
| `data/parsed/gdpr_cjeu.db` | SQLite database | Complex queries, aggregations |

## Coding Schema

Each holding is coded with 43 questions covering:

- **Metadata**: Case ID, date, chamber (Q1-Q4)
- **Concepts**: Primary GDPR concept, articles referenced (Q5-Q9)
- **Interpretation**: Dominant source (semantic/teleological), structure (Q10-Q20)
- **Balancing**: Necessity tests, rights weighting (Q21-Q32)
- **Outcome**: Ruling direction, remedies (Q33-Q43)

See [`docs/coding-agent-instructions.md`](docs/coding-agent-instructions.md) for the full schema.

## Documentation

### Methodology
- [Statistical Analysis Methodology](docs/methodology/statistical-analysis-methodology.md)
- [Judicial Analysis Methodology](docs/methodology/judicial-analysis-methodology.md)
- [Citation Analysis Methodology](docs/methodology/citation-analysis-methodology.md)
- [Temporal Analysis Methodology](docs/methodology/temporal-analysis-methodology.md)

### Findings
- [Academic Paper](docs/findings/ACADEMIC_PAPER.md) - Main research paper
- [Judicial Analysis Report](docs/findings/JUDICIAL_ANALYSIS_REPORT.md)
- [Citation Analysis Findings](docs/findings/CITATION_ANALYSIS_FINDINGS.md)
- [Pro-Controller Analysis](docs/findings/PRO_CONTROLLER_ANALYSIS.md)
- [Pro-Controller Narrative Analysis](docs/findings/PRO_CONTROLLER_NARRATIVE_ANALYSIS.md)
- [Balancing Jurisprudence Analysis](docs/findings/BALANCING_JURISPRUDENCE_ANALYSIS.md)
- [Means-Ends Proportionality Analysis](docs/findings/MEANS_ENDS_PROPORTIONALITY_ANALYSIS.md)
- [Findings Overview](docs/FINDINGS_OVERVIEW.md) - Summary of all findings

## Dependencies

**Python 3.8+** with:
```
pandas >= 2.0
numpy >= 1.24
scipy >= 1.10
statsmodels >= 0.14
scikit-learn >= 1.3
```

Install: `pip install pandas numpy scipy statsmodels scikit-learn`

## Methodology

- **Unit of analysis**: Individual holding (N=181 from 67 cases)
- **Dependent variable**: Binary ruling direction (PRO_DATA_SUBJECT vs. other)
- **Bivariate tests**: Chi-square/Fisher's exact with Benjamini-Hochberg FDR correction
- **Multivariate**: Hierarchical logistic regression with 6 nested models
- **Validation**: Individual case review for robustness

## Citation

If using this dataset or analysis, please cite:

> [Author]. (2025). Factors Associated with Pro-Data Subject Rulings in CJEU GDPR Jurisprudence: An Empirical Analysis of Interpretive Methods, Institutional Factors, and the Compensation Gap.

## License

Academic research use. See individual files for specific terms.
