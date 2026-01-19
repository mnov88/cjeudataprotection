# Statistical Analysis Methodology: CJEU GDPR Case Outcomes

## A Comprehensive Framework for Bivariate and Multivariate Analysis of Pro-Data Subject vs. Pro-Controller Rulings

---

## 1. Executive Summary

This document proposes a rigorous statistical methodology for analyzing factors associated with ruling direction in CJEU GDPR decisions. The analysis employs the holding as the unit of analysis (N=181) and examines how interpretive methods, reasoning structures, legal concepts, and institutional factors predict whether the Court rules in favor of data subjects or controllers.

---

## 2. Dependent Variable: Ruling Direction

### 2.1 Original Coding (4 Categories)

| Value | N | % |
|-------|---|---|
| PRO_DATA_SUBJECT | 110 | 60.8% |
| MIXED | 28 | 15.5% |
| PRO_CONTROLLER | 23 | 12.7% |
| NEUTRAL_OR_UNCLEAR | 20 | 11.0% |

### 2.2 Recoded Binary Variable (Recommended for Primary Analysis)

For maximum statistical power and interpretability, we recommend creating a binary dependent variable:

```
pro_ds_binary = 1 if ruling_direction == "PRO_DATA_SUBJECT" else 0
```

This yields: **PRO_DATA_SUBJECT (n=110, 60.8%) vs. OTHER (n=71, 39.2%)**

**Justification**:
- The research question centers on identifying factors that predict pro-data subject outcomes
- The "MIXED" and "NEUTRAL_OR_UNCLEAR" categories are conceptually closer to non-pro-DS outcomes
- Binary logistic regression provides superior interpretability (odds ratios)
- Sample size constraints make multinomial models with 4 categories statistically underpowered

### 2.3 Alternative Trichotomous Coding (Sensitivity Analysis)

For robustness checks, consider a 3-category variable:

```
direction_3cat = "PRO_DATA_SUBJECT" | "PRO_CONTROLLER" | "INDETERMINATE" (MIXED + NEUTRAL)
```

This supports multinomial logistic regression with PRO_CONTROLLER as reference category.

---

## 3. Independent Variables

### 3.1 Variable Classification

| Category | Variables | Type | Levels |
|----------|-----------|------|--------|
| **Institutional** | `chamber` | Nominal | 9 levels |
| **Temporal** | `judgment_year` (derived) | Ordinal/Continuous | 2019-2025 |
| **Conceptual** | `primary_concept` | Nominal | 40 levels → grouped |
| | `article_numbers` | Multi-valued | Individual indicators |
| **Interpretive Sources** | `semantic_present` | Binary | TRUE/FALSE |
| | `systematic_present` | Binary | TRUE/FALSE |
| | `teleological_present` | Binary | TRUE/FALSE |
| | `dominant_source` | Nominal | 4 levels |
| | `teleological_purposes` | Multi-valued | 9 possible values |
| **Reasoning Structure** | `rule_based_present` | Binary | TRUE/FALSE |
| | `case_law_present` | Binary | TRUE/FALSE |
| | `principle_based_present` | Binary | TRUE/FALSE |
| | `dominant_structure` | Nominal | 4 levels |
| | `level_shifting` | Binary | TRUE/FALSE |
| | `cited_case_count` | Count | 0+ |
| **Balancing** | `necessity_discussed` | Binary | TRUE/FALSE |
| | `necessity_standard` | Ordinal | NONE < REGULAR < STRICT |
| | `controller_ds_balancing` | Binary | TRUE/FALSE |
| | `other_rights_balancing` | Binary | TRUE/FALSE |

### 3.2 Variable Transformations

#### 3.2.1 Concept Grouping (Reduce 40 → 8 Categories)

Given sample size constraints, aggregate `primary_concept` into theoretically meaningful clusters:

| Cluster | Concepts |
|---------|----------|
| **SCOPE** | SCOPE_MATERIAL, SCOPE_TERRITORIAL, PERSONAL_DATA_SCOPE, HOUSEHOLD_EXEMPTION, OTHER_EXEMPTION |
| **ACTORS** | CONTROLLER_DEFINITION, JOINT_CONTROLLERS_DEFINITION, PROCESSOR_OBLIGATIONS, RECIPIENT_DEFINITION |
| **LAWFULNESS** | CONSENT_BASIS, CONTRACT_BASIS, LEGAL_OBLIGATION_BASIS, VITAL_INTERESTS_BASIS, PUBLIC_INTEREST_BASIS, LEGITIMATE_INTERESTS |
| **PRINCIPLES** | DATA_PROTECTION_PRINCIPLES, ACCOUNTABILITY, TRANSPARENCY |
| **RIGHTS** | RIGHT_OF_ACCESS, RIGHT_TO_RECTIFICATION, RIGHT_TO_ERASURE, RIGHT_TO_RESTRICTION, RIGHT_TO_PORTABILITY, RIGHT_TO_OBJECT, AUTOMATED_DECISION_MAKING |
| **SPECIAL** | SPECIAL_CATEGORIES_DEFINITION, SPECIAL_CATEGORIES_CONDITIONS |
| **ENFORCEMENT** | DPA_INDEPENDENCE, DPA_POWERS, DPA_OBLIGATIONS, ONE_STOP_SHOP, DPA_OTHER, ADMINISTRATIVE_FINES, REMEDIES_COMPENSATION, REPRESENTATIVE_ACTIONS |
| **OTHER** | SECURITY, INTERNATIONAL_TRANSFER, OTHER_CONTROLLER_OBLIGATIONS, MEMBER_STATE_DISCRETION, OTHER |

**CRITICAL NOTE ON ENFORCEMENT CLUSTER HETEROGENEITY (v2.0):**

The ENFORCEMENT cluster is heterogeneous:
- **55.4% is REMEDIES_COMPENSATION** (Article 82 damages, n=36)
- Remaining 44.6% is DPA-related (DPA_POWERS, ADMINISTRATIVE_FINES, etc., n=29)

Pro-DS rates differ substantially:
- REMEDIES_COMPENSATION: 36.1% pro-DS
- Non-compensation ENFORCEMENT: ~58.6% pro-DS

This heterogeneity affects:
1. **Third Chamber analysis**: 59% of Third Chamber holdings are compensation
2. **Rapporteur within-topic comparisons**: Jääskinen handles 89% compensation within ENFORCEMENT
3. **Temporal trends**: 97% of compensation cases appear in 2023+

**Recommended approach**: Report analyses both WITH and WITHOUT compensation cases as sensitivity checks. The `is_compensation` flag variable enables this.

#### 3.2.2 Chamber Grouping

Collapse low-frequency chambers:

| Grouped | Original |
|---------|----------|
| GRAND_CHAMBER | GRAND_CHAMBER |
| FIRST | FIRST |
| THIRD | THIRD |
| FOURTH | FOURTH |
| OTHER | FIFTH, SIXTH, EIGHTH, NINTH, SECOND |

#### 3.2.3 Derived Variables

```python
# Interpretive plurality index (count of methods used)
interpretation_count = semantic_present + systematic_present + teleological_present

# Reasoning plurality index
reasoning_count = rule_based_present + case_law_present + principle_based_present

# High protection purpose indicator
high_protection_purpose = "HIGH_LEVEL_OF_PROTECTION" in teleological_purposes

# Fundamental rights purpose indicator
fundamental_rights_purpose = "FUNDAMENTAL_RIGHTS" in teleological_purposes

# Any balancing indicator
any_balancing = necessity_discussed | controller_ds_balancing | other_rights_balancing

# Compensation flag (critical for sensitivity analyses) - v2.0
is_compensation = (primary_concept == 'REMEDIES_COMPENSATION')

# Non-compensation enforcement flag
is_enforcement_non_comp = (concept_cluster == 'ENFORCEMENT') & (~is_compensation)

# Inverse weighting (addresses within-case clustering, ICC=29.5%)
holdings_in_case = groupby(case_id).count()
inverse_weight = 1.0 / holdings_in_case
```

---

## 4. Bivariate Analysis

### 4.1 Statistical Tests by Variable Type

| DV | IV Type | Test | Effect Size |
|----|---------|------|-------------|
| Binary | Binary | Chi-square / Fisher's exact | Phi (φ) |
| Binary | Nominal (3+) | Chi-square | Cramér's V |
| Binary | Ordinal | Mann-Whitney U | Rank-biserial r |
| Binary | Count | Mann-Whitney U / t-test | Cohen's d |

### 4.2 Planned Bivariate Comparisons

#### 4.2.1 Core Hypotheses

| # | Hypothesis | IV | Expected Direction |
|---|------------|----|--------------------|
| H1 | Teleological interpretation predicts pro-DS outcomes | `teleological_present` | + |
| H2 | Semantic interpretation predicts pro-controller outcomes | `semantic_present` (as dominant) | - |
| H3 | Principle-based reasoning predicts pro-DS outcomes | `principle_based_present` | + |
| H4 | Level-shifting predicts pro-DS outcomes | `level_shifting` | + |
| H5 | Grand Chamber cases more likely pro-DS | `chamber` = GRAND | + |
| H6 | Rights concepts predict pro-DS outcomes | `concept_cluster` = RIGHTS | + |
| H7 | Invocation of HIGH_LEVEL_OF_PROTECTION predicts pro-DS | `high_protection_purpose` | + |
| H8 | Explicit balancing predicts pro-controller outcomes | `any_balancing` | - |
| H9 | Strict necessity standard predicts pro-controller | `necessity_standard` = STRICT | - |

#### 4.2.2 Cross-Tabulation Template

For each bivariate test, report:

```
┌─────────────────────────────────────────────────────────────┐
│ Table X: Ruling Direction by [IV Name]                      │
├─────────────────────┬───────────────┬───────────────┬───────┤
│                     │ PRO_DATA_SUB  │ OTHER         │ Total │
├─────────────────────┼───────────────┼───────────────┼───────┤
│ [IV Category 1]     │ n (row %)     │ n (row %)     │ n     │
│ [IV Category 2]     │ n (row %)     │ n (row %)     │ n     │
├─────────────────────┼───────────────┼───────────────┼───────┤
│ Total               │ n (col %)     │ n (col %)     │ N     │
└─────────────────────┴───────────────┴───────────────┴───────┘

χ²(df) = X.XX, p = .XXX
Cramér's V = X.XX [95% CI: X.XX, X.XX]
```

### 4.3 Multiple Testing Correction

With ~20 planned bivariate tests, apply:

1. **Benjamini-Hochberg FDR correction** (q < 0.05) for all tests
2. Report both unadjusted p-values and FDR-adjusted q-values
3. Distinguish confirmatory (pre-registered) from exploratory analyses

---

## 5. Multivariate Analysis

### 5.1 Model Selection Rationale

| Model | When to Use | Advantages | Disadvantages |
|-------|-------------|------------|---------------|
| **Binary Logistic Regression** | Binary DV (PRO_DS vs. OTHER) | Interpretable ORs, robust | Information loss |
| **Multinomial Logistic Regression** | 3-4 category DV | Retains full information | Lower power, complex interpretation |
| **Mixed-Effects Logistic** | Account for case clustering | Handles non-independence | Requires sufficient clusters |

**Primary recommendation**: Binary logistic regression with case-level random intercepts (mixed-effects model) to account for multiple holdings per case.

### 5.2 Model Building Strategy

#### 5.2.1 Hierarchical (Nested) Model Approach

Build models in theoretically motivated blocks:

```
Model 0: Null model (intercept only)
Model 1: + Institutional factors (chamber, year)
Model 2: + Conceptual factors (concept_cluster)
Model 3: + Interpretive sources (dominant_source, teleological_purposes)
Model 4: + Reasoning structure (dominant_structure, level_shifting)
Model 5: + Balancing factors (necessity_standard, any_balancing)
```

Compare models using:
- Likelihood ratio tests (nested models)
- AIC/BIC (all models)
- McFadden's pseudo-R²
- Area Under ROC Curve (AUC)

#### 5.2.2 Final Model Specification

```
logit(P(PRO_DS = 1)) = β₀ + β₁(chamber) + β₂(year) + β₃(concept_cluster)
                      + β₄(dominant_source) + β₅(high_protection_purpose)
                      + β₆(dominant_structure) + β₇(level_shifting)
                      + β₈(necessity_standard) + β₉(any_balancing)
                      + u_case
```

Where `u_case ~ N(0, σ²)` is a case-level random intercept.

### 5.3 Model Diagnostics

1. **Multicollinearity**: Variance Inflation Factors (VIF < 5)
2. **Influential observations**: Cook's distance, DFBETAs
3. **Goodness of fit**: Hosmer-Lemeshow test (for non-mixed models)
4. **Discrimination**: ROC curve and AUC
5. **Calibration**: Calibration plot (predicted vs. observed probabilities)
6. **Residual analysis**: Pearson residuals, deviance residuals

### 5.4 Reporting Standards

For the final model, report:

| Predictor | OR | 95% CI | p | Interpretation |
|-----------|----|----|---|----------------|
| [Variable] | X.XX | [X.XX, X.XX] | .XXX | [Substantive meaning] |

Include:
- Sample size (N observations, n cases)
- Number of events (PRO_DS = 1)
- Model fit statistics (AIC, BIC, pseudo-R², AUC)
- Variance of random intercept (ICC)

---

## 6. Sensitivity Analyses

### 6.1 Alternative Model Specifications

| Analysis | Purpose |
|----------|---------|
| Exclude NEUTRAL_OR_UNCLEAR holdings | Test whether ambiguous cases drive results |
| Multinomial logistic (4-category DV) | Assess information loss from binarization |
| Separate models by time period (pre-2022 vs. 2022+) | Test temporal stability |
| Exclude single-holding cases | Test robustness to case structure |

### 6.2 Robustness Checks

1. **Bootstrap confidence intervals** (1000 resamples)
2. **Leave-one-case-out cross-validation**
3. **Firth's penalized logistic regression** (for rare events/separation)
4. **Exact logistic regression** (for small cell counts)

---

## 7. Sample Size Considerations

### 7.1 Events Per Variable (EPV) Rule

With N=181 holdings and ~110 "events" (PRO_DS), the effective sample size for regression is limited.

| EPV Guideline | Max Predictors | Recommendation |
|---------------|----------------|----------------|
| EPV ≥ 10 | 11 | Minimum standard |
| EPV ≥ 20 | 5 | Preferred for stable estimates |

**Recommendation**: Limit final model to 5-8 predictors maximum.

### 7.2 Statistical Power

For bivariate chi-square tests with N=181:
- Medium effect (w=0.3): Power = 0.95
- Small effect (w=0.1): Power = 0.20

For logistic regression (OR=2.0, 50% exposure):
- N=181 provides ~75% power at α=0.05

**Implication**: The study is well-powered to detect medium-to-large effects but may miss small effects.

---

## 8. Implementation Plan

### 8.1 Software Requirements

```python
# Python
pandas >= 2.0
numpy >= 1.24
scipy >= 1.10
statsmodels >= 0.14
scikit-learn >= 1.3
```

```r
# R
tidyverse
lme4        # Mixed-effects models
car         # VIF, diagnostics
broom       # Tidy model output
pROC        # ROC curves
ggeffects   # Marginal effects plots
```

### 8.2 Analysis Workflow

```
1. Data Preparation
   ├── Load holdings.csv
   ├── Create derived variables
   ├── Recode categorical variables
   └── Validate completeness

2. Descriptive Statistics
   ├── Univariate distributions
   ├── Missing data patterns
   └── Outlier identification

3. Bivariate Analysis
   ├── Chi-square / Fisher tests
   ├── Effect sizes (Cramér's V)
   ├── FDR correction
   └── Visualization (mosaic plots)

4. Multivariate Modeling
   ├── Collinearity diagnostics
   ├── Model building (hierarchical)
   ├── Model comparison (LRT, AIC)
   ├── Final model selection
   └── Diagnostics and validation

5. Sensitivity Analyses
   ├── Alternative specifications
   ├── Robustness checks
   └── Bootstrap CIs

6. Results Synthesis
   ├── Summary tables
   ├── Forest plots (ORs)
   ├── Predicted probability plots
   └── Narrative interpretation
```

---

## 9. Reporting Checklist (STROBE-inspired)

- [ ] State research objectives and hypotheses
- [ ] Describe data source and coding methodology
- [ ] Define all variables with valid values
- [ ] Report sample sizes at each stage
- [ ] Present descriptive statistics for all variables
- [ ] Report unadjusted (bivariate) associations
- [ ] Present model-building process
- [ ] Report adjusted associations with CIs
- [ ] Discuss confounding and mediation
- [ ] Present sensitivity analyses
- [ ] Discuss limitations (esp. causality, generalizability)

---

## 10. Ethical and Methodological Notes

### 10.1 Unit of Analysis Considerations

Holdings within the same case are **not independent**. The mixed-effects specification addresses this, but researchers should:
- Report the intraclass correlation (ICC)
- Consider case-level aggregation as a sensitivity analysis
- Interpret holding-level effects cautiously

### 10.2 Causal Inference Limitations

This is an **observational study** of judicial reasoning. Associations between interpretive methods and outcomes may reflect:
- Judges selecting methods that support desired outcomes (reverse causation)
- Confounding by case type or legal question
- Coding artifacts

**Do not interpret coefficients as causal effects.**

### 10.3 Reproducibility

- Pre-register the analysis plan before examining DV-IV relationships
- Archive analysis code alongside the manuscript
- Report all analyses conducted, including null findings
- Provide supplementary materials with full model outputs

---

## 11. Expected Outputs

### 11.1 Tables

1. **Table 1**: Descriptive statistics (all variables)
2. **Table 2**: Bivariate associations (chi-square tests, effect sizes)
3. **Table 3**: Logistic regression model comparison
4. **Table 4**: Final model coefficients (ORs, 95% CIs)
5. **Table S1**: Full correlation matrix (appendix)
6. **Table S2**: Sensitivity analysis results (appendix)

### 11.2 Figures

1. **Figure 1**: Ruling direction distribution (bar chart)
2. **Figure 2**: Mosaic plot of key bivariate associations
3. **Figure 3**: Forest plot of adjusted ORs
4. **Figure 4**: Predicted probabilities by dominant source
5. **Figure 5**: ROC curve with AUC

---

## 12. Key Research Questions Addressable

This methodology enables rigorous answers to:

1. **Does the Court's interpretive approach predict outcomes?**
   - Is teleological interpretation associated with pro-data subject rulings?
   - Does semantic interpretation favor controllers?

2. **Does reasoning structure matter?**
   - Is principle-based reasoning more pro-data subject than rule-based?
   - Does level-shifting predict expansive interpretations?

3. **Do institutional factors influence outcomes?**
   - Does the Grand Chamber rule differently than smaller chambers?
   - Are there temporal trends in ruling direction?

4. **How does balancing analysis affect outcomes?**
   - Does explicit necessity analysis favor controllers?
   - When rights conflict, which typically prevails?

5. **Which legal concepts drive pro-data subject outcomes?**
   - Are rights provisions (access, erasure) interpreted more protectively?
   - Do enforcement provisions favor data subjects?

---

## Appendix A: Variable Codebook

| Variable | Source | Type | Valid Values | Missing |
|----------|--------|------|--------------|---------|
| `ruling_direction` | A32 | Nominal | PRO_DATA_SUBJECT, PRO_CONTROLLER, MIXED, NEUTRAL_OR_UNCLEAR | Not permitted |
| `chamber` | A3 | Nominal | GRAND_CHAMBER, FIRST-TENTH, FULL_COURT | Not permitted |
| `judgment_date` | A2 | Date | YYYY-MM-DD | Not permitted |
| `primary_concept` | A10 | Nominal | 40 values (see codebook) | Not permitted |
| `semantic_present` | A12 | Binary | TRUE, FALSE | Not permitted |
| `systematic_present` | A14 | Binary | TRUE, FALSE | Not permitted |
| `teleological_present` | A16 | Binary | TRUE, FALSE | Not permitted |
| `teleological_purposes` | A18 | Multi-select | Up to 9 values | NULL if A16=FALSE |
| `dominant_source` | A20 | Nominal | SEMANTIC, SYSTEMATIC, TELEOLOGICAL, UNCLEAR | Not permitted |
| `rule_based_present` | A22 | Binary | TRUE, FALSE | Not permitted |
| `case_law_present` | A24 | Binary | TRUE, FALSE | Not permitted |
| `principle_based_present` | A27 | Binary | TRUE, FALSE | Not permitted |
| `dominant_structure` | A29 | Nominal | RULE_BASED, CASE_LAW_BASED, PRINCIPLE_BASED, MIXED | Not permitted |
| `level_shifting` | A30 | Binary | TRUE, FALSE | Not permitted |
| `necessity_discussed` | A34 | Binary | TRUE, FALSE | Not permitted |
| `necessity_standard` | A35 | Ordinal | STRICT, REGULAR, NONE | Not permitted |
| `controller_ds_balancing` | A37 | Binary | TRUE, FALSE | Not permitted |
| `other_rights_balancing` | A40 | Binary | TRUE, FALSE | Not permitted |

---

## Appendix B: Sample Analysis Code (Python)

```python
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score, roc_curve

# Load data
df = pd.read_csv('data/parsed/holdings.csv')

# Create binary DV
df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)

# Extract year
df['year'] = pd.to_datetime(df['judgment_date']).dt.year

# Create concept clusters (example)
scope_concepts = ['SCOPE_MATERIAL', 'SCOPE_TERRITORIAL', 'PERSONAL_DATA_SCOPE']
df['concept_cluster'] = df['primary_concept'].apply(
    lambda x: 'SCOPE' if x in scope_concepts else 'OTHER'
)

# Bivariate: Chi-square test
contingency = pd.crosstab(df['dominant_source'], df['pro_ds'])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
cramers_v = np.sqrt(chi2 / (len(df) * (min(contingency.shape) - 1)))
print(f"χ²({dof}) = {chi2:.2f}, p = {p:.4f}, Cramér's V = {cramers_v:.3f}")

# Multivariate: Mixed-effects logistic regression
model = smf.mixedlm(
    "pro_ds ~ C(dominant_source) + teleological_present + level_shifting",
    df,
    groups=df["case_id"],
    family=sm.families.Binomial()
)
result = model.fit()
print(result.summary())

# ROC AUC
y_pred = result.predict()
auc = roc_auc_score(df['pro_ds'], y_pred)
print(f"AUC = {auc:.3f}")
```

---

*Document version: 1.0*
*Prepared for: CJEU GDPR Empirical Legal Research Project*
*Methodology aligned with: APA, STROBE, and empirical legal studies best practices*
