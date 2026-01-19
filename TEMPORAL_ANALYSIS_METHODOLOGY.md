# Comprehensive Temporal Analysis Methodology: CJEU GDPR Jurisprudence

## Bivariate and Multivariate Analysis of Temporal Effects

---

## Executive Summary

This document proposes a rigorous methodology for analyzing temporal effects in CJEU GDPR decisions. The analysis addresses the fundamental question: **What has time affected and how?** This encompasses both descriptive temporal trends and analytical decomposition of whether observed changes reflect genuine doctrinal evolution or compositional shifts in the case portfolio.

**Key Research Questions:**
1. How have ruling patterns changed over time?
2. Do the effects of key predictors (interpretation, chamber, concepts) vary across time periods?
3. Are there structural breaks in CJEU GDPR jurisprudence?
4. To what extent are temporal trends explained by changing case composition vs. genuine doctrinal shift?

---

## 1. Data Structure and Temporal Variables

### 1.1 Temporal Scope

| Year | Holdings | Cases | Avg Holdings/Case |
|------|----------|-------|-------------------|
| 2019 | 14 | ~4 | 3.5 |
| 2020 | 14 | ~4 | 3.5 |
| 2021 | 24 | ~8 | 3.0 |
| 2022 | 21 | ~8 | 2.6 |
| 2023 | 45 | ~17 | 2.6 |
| 2024 | 63 | ~22 | 2.9 |
| 2025* | 20* | ~4* | 5.0* |

*Note: 2025 data reflects partial year (January only)*

### 1.2 Primary Temporal Variable Construction

```
judgment_year = YEAR(judgment_date)
judgment_quarter = CONCAT(YEAR, "-Q", QUARTER)
judgment_semester = CONCAT(YEAR, IF(MONTH <= 6, "-H1", "-H2"))
days_since_gdpr = judgment_date - "2018-05-25"
case_sequence = RANK(judgment_date) PARTITION BY case_type
```

### 1.3 Derived Temporal Variables

| Variable | Definition | Purpose |
|----------|------------|---------|
| `year_centered` | year - 2022 | Improve model interpretability |
| `year_scaled` | (year - 2019) / 6 | Standardize for comparison |
| `period_binary` | 1 if year >= 2023 else 0 | Early vs. late period |
| `period_tertile` | Tercile-based period grouping | Three-period analysis |
| `log_days_since_gdpr` | log(days since 25 May 2018) | Non-linear time effect |

---

## 2. Bivariate Temporal Analysis

### 2.1 Framework: Variable × Time Associations

The bivariate temporal analysis systematically examines how each variable in the dataset varies over time. This establishes the empirical foundation for understanding what has changed before investigating how or why.

### 2.2 Analysis Plan for Each Variable Type

#### 2.2.1 Binary Variables × Time

**Variables:** `pro_ds_binary`, `teleological_present`, `semantic_present`, `systematic_present`, `rule_based_present`, `case_law_present`, `principle_based_present`, `level_shifting`, `necessity_discussed`, `controller_ds_balancing`, `other_rights_balancing`

**Analysis Protocol:**

```
For each binary variable Y:
    1. Calculate annual prevalence: P(Y=1|year=t) for t ∈ {2019,...,2025}
    2. Test for trend:
       a. Cochran-Armitage trend test (ordinal time)
       b. Logistic regression: logit(Y) = β₀ + β₁(year_centered)
       c. Report: OR per year, 95% CI, p-value
    3. Test for non-monotonic patterns:
       a. Wald test for year² term: logit(Y) = β₀ + β₁(year) + β₂(year²)
       b. Likelihood ratio test: quadratic vs. linear model
    4. Report: Temporal trend plot with 95% confidence bands
```

**Reporting Template:**

| Variable | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | Trend OR | p | Interpretation |
|----------|------|------|------|------|------|------|----------|---|----------------|
| Pro-DS | 64.3% | 85.7% | 66.7% | 61.9% | 60.0% | 54.0% | 0.83 | 0.103 | Descriptive decline, not significant |

#### 2.2.2 Categorical Variables × Time

**Variables:** `chamber`, `dominant_source`, `dominant_structure`, `necessity_standard`, `primary_concept`, `concept_cluster`

**Analysis Protocol:**

```
For each categorical variable C with k levels:
    1. Contingency table: C × year
    2. Test for independence:
       a. Chi-square test (if expected counts ≥ 5)
       b. Fisher-Freeman-Halton exact test (if sparse)
    3. Report: Cramér's V for association strength
    4. Visualize: Stacked area plot or heat map of proportions
    5. Post-hoc: Examine which levels show strongest temporal change
```

**Key Hypotheses:**

| Hypothesis | Variable | Expected Pattern |
|------------|----------|------------------|
| H-T1 | `chamber` | Third Chamber increasing representation |
| H-T2 | `dominant_source` | Shift from teleological to systematic |
| H-T3 | `concept_cluster` | ENFORCEMENT increasing (compensation cases) |
| H-T4 | `necessity_standard` | Increasing use of STRICT standard |

#### 2.2.3 Count Variables × Time

**Variables:** `cited_case_count`, `paragraph_count`, `judge_count`

**Analysis Protocol:**

```
For each count variable N:
    1. Calculate annual means and medians
    2. Test for trend:
       a. Jonckheere-Terpstra test (non-parametric ordinal trend)
       b. Negative binomial regression: log(E[N]) = β₀ + β₁(year)
       c. For overdispersed counts: quasi-Poisson or negative binomial
    3. Report: Incidence rate ratio (IRR) per year
    4. Visualize: Time series with LOESS smoothing
```

### 2.3 Multiple Testing Correction

With approximately 25 temporal trend tests:

1. **Primary correction:** Benjamini-Hochberg FDR (q < 0.10)
2. **Family-wise correction:** Report Holm-Bonferroni adjusted p-values
3. **Distinction:** Pre-registered (confirmatory) vs. exploratory analyses

### 2.4 Bivariate Temporal Analysis Outputs

**Table T1:** Temporal Trends in Key Variables
- Columns: Variable, N, 2019-2021 %, 2022-2024 %, Trend OR/IRR, 95% CI, p, FDR-q

**Figure T1:** Time Series of Pro-DS Ruling Rate
- Plot: Annual proportion with 95% Wilson confidence intervals
- Overlay: Linear trend line with confidence band

**Figure T2:** Case Composition Over Time
- Plot: Stacked area chart of concept clusters by year

**Figure T3:** Interpretive Methods Over Time
- Plot: Multi-line chart of proportion invoking each source type

---

## 3. Multivariate Temporal Analysis

### 3.1 Time as Covariate: Does Time Predict Outcomes?

The simplest multivariate temporal question: after controlling for case characteristics, does judgment year independently predict ruling direction?

#### 3.1.1 Model Specification

**Model M-T1: Baseline temporal model**

```
logit(P(PRO_DS = 1)) = β₀ + β₁(year_centered) + u_case
```

**Model M-T2: Temporal model with covariates**

```
logit(P(PRO_DS = 1)) = β₀ + β₁(year_centered) + β₂(concept_cluster) +
                        β₃(chamber_grouped) + β₄(pro_ds_purpose) + u_case
```

**Model M-T3: Temporal model with full controls**

```
logit(P(PRO_DS = 1)) = β₀ + β₁(year_centered) + β₂(concept_cluster) +
                        β₃(chamber_grouped) + β₄(pro_ds_purpose) +
                        β₅(dominant_source) + β₆(level_shifting) + u_case
```

#### 3.1.2 Interpretation Framework

| Scenario | β₁ raw | β₁ adjusted | Interpretation |
|----------|--------|-------------|----------------|
| A | Significant | Significant | Pure temporal effect after controls |
| B | Significant | Not significant | Temporal effect explained by covariates |
| C | Not significant | Not significant | No temporal effect |
| D | Not significant | Significant | Suppression effect (covariates unmask time trend) |

### 3.2 Time as Moderator: Do Effects Change Over Time?

The core analytical question: do the effects of key predictors vary across time periods?

#### 3.2.1 Interaction Model Specification

**Model M-T4: Pro-DS purpose × time interaction**

```
logit(P(PRO_DS = 1)) = β₀ + β₁(pro_ds_purpose) + β₂(year_centered) +
                        β₃(pro_ds_purpose × year_centered) + controls + u_case
```

**Interpretation of β₃:**
- β₃ > 0: Pro-DS purpose effect strengthens over time
- β₃ < 0: Pro-DS purpose effect weakens over time
- β₃ ≈ 0: Stable effect over time

**Model M-T5: Chamber × time interaction**

```
logit(P(PRO_DS = 1)) = β₀ + β₁(third_chamber) + β₂(year_centered) +
                        β₃(third_chamber × year_centered) + controls + u_case
```

**Research Question:** Is the Third Chamber effect explained by its increasing concentration of certain case types over time?

#### 3.2.2 Period-Based Analysis (Structural Stability)

Given sample size constraints, period-based analysis may have superior power to continuous interactions.

**Period Definition Options:**

| Option | Periods | Rationale |
|--------|---------|-----------|
| Binary | 2019-2022 vs. 2023-2025 | Pre/post caseload increase |
| Tertile | 2019-2021, 2022-2023, 2024-2025 | Equal temporal thirds |
| Compensation | Pre/post Article 82 surge | Conceptual break point |

**Model M-T6: Split-sample analysis**

```
For each period p:
    Fit model: logit(P(PRO_DS = 1)) = β₀ₚ + β₁ₚ(pro_ds_purpose) + controls + u_case
    Compare: β₁_early vs. β₁_late
```

**Statistical Test:** Wald test for coefficient equality across periods

```
H₀: β₁_early = β₁_late
H₁: β₁_early ≠ β₁_late
Test statistic: (β₁_early - β₁_late)² / (SE²_early + SE²_late)
```

### 3.3 Time as Confounder: Temporal Confounding Analysis

#### 3.3.1 Conceptual Framework

Temporal confounding occurs when:
1. Both the predictor and outcome change over time
2. The predictor-outcome association is spuriously inflated/deflated by shared temporal trends

**Key Confounding Pathways:**

```
Time → Case Composition → Ruling Direction
Time → Chamber Assignment → Ruling Direction
Time → Interpretive Style → Ruling Direction
```

#### 3.3.2 Analysis Strategy

**Step 1: Document temporal variation in predictors**
- Which predictors show significant temporal trends? (from Section 2)

**Step 2: Sensitivity analysis with time controls**

| Model | Specification | Purpose |
|-------|--------------|---------|
| A | No time control | Baseline association |
| B | Year as covariate | Control for linear trend |
| C | Year fixed effects | Full temporal adjustment |
| D | Year dummies (2020, 2021, ..., 2025) | Flexible time control |

**Step 3: Compare coefficient stability**

If β(predictor) changes substantially across Models A-D, temporal confounding is present.

**Example from Current Analysis:**
- Third Chamber effect: OR=0.11 (p=0.0002) without year control
- Third Chamber effect: OR=0.21 (p=0.051) with year fixed effects
- **Conclusion:** Temporal confounding partially explains chamber effect

---

## 4. Structural Break Analysis

### 4.1 Rationale

GDPR jurisprudence may exhibit discrete regime changes rather than gradual evolution. Potential break points:

| Candidate Break | Rationale |
|-----------------|-----------|
| 2020 (COVID) | Pandemic may have affected case processing |
| 2022 (Schrems II settled) | Major doctrinal clarification |
| 2023 (compensation surge) | Article 82 cases begin dominating |
| 2024 | Possible doctrinal maturation |

### 4.2 Structural Break Tests

#### 4.2.1 Chow Test (Known Break Point)

For a hypothesized break at time t*:

```
H₀: No structural break at t*
H₁: Parameters differ before and after t*

Test: F = [(RSS_pooled - RSS_early - RSS_late) / k] /
          [(RSS_early + RSS_late) / (n - 2k)]
```

#### 4.2.2 Quandt Likelihood Ratio (Unknown Break Point)

When the break point is unknown:

```
For each candidate break point t ∈ [t_min, t_max]:
    Calculate Chow F-statistic

Sup-F = max{F_t} for t ∈ trimmed range

Critical values: Andrews (1993) or Hansen (1997)
```

**Note:** With N=181 and 7 years, power for structural break detection is limited. Consider pooling years into semesters for increased observations per period.

#### 4.2.3 CUSUM Test (Cumulative Sum of Residuals)

```
1. Fit model on full sample: Y = Xβ + ε
2. Calculate recursive residuals: e_t = (y_t - x_t'β̂_{t-1}) / √(1 + x_t'(X'_{t-1}X_{t-1})⁻¹x_t)
3. Compute CUSUM: W_t = Σ_{j=1}^t e_j / σ̂
4. Plot W_t against t; instability indicated if W_t crosses ±(a + 2at/T) bands
```

### 4.3 Practical Implementation

Given sample size constraints:

1. **Primary:** Binary period analysis (pre-2023 vs. 2023+) with Chow test
2. **Secondary:** Visual inspection of rolling window estimates
3. **Tertiary:** Wald test for interaction terms (period × predictors)

---

## 5. Composition vs. Trend Decomposition

### 5.1 The Decomposition Problem

**Observed change** in pro-DS rate from 78.9% (2019-2020) to 56.6% (2024-2025) could reflect:

1. **Genuine doctrinal shift:** Court becomes less protective holding case mix constant
2. **Compositional change:** Different types of cases arrive (e.g., more Article 82)
3. **Both:** Mixture of doctrinal and compositional effects

### 5.2 Kitagawa-Blinder-Oaxaca Decomposition

#### 5.2.1 Two-Period Decomposition

Let t=0 (early period) and t=1 (late period).

**Observed difference:**
```
Δ = Ȳ₁ - Ȳ₀ = P(PRO_DS|late) - P(PRO_DS|early)
```

**Decomposition:**
```
Δ = [E(X₁) - E(X₀)]'β̂₀  +  E(X₁)'(β̂₁ - β̂₀)  +  [E(X₁) - E(X₀)]'(β̂₁ - β̂₀)
    ──────────────────     ────────────────────     ─────────────────────────
    COMPOSITION EFFECT     COEFFICIENT EFFECT       INTERACTION
    (explained by          (doctrinal shift         (composition of
    changing case mix)     holding mix constant)    composition & shift)
```

#### 5.2.2 Implementation

```python
# Step 1: Estimate models for each period
model_early = logit(PRO_DS ~ concept_cluster + chamber + pro_ds_purpose + ...)
model_late = logit(PRO_DS ~ concept_cluster + chamber + pro_ds_purpose + ...)

# Step 2: Calculate mean characteristics by period
X_mean_early = df[df['period'] == 'early'][features].mean()
X_mean_late = df[df['period'] == 'late'][features].mean()

# Step 3: Counterfactual prediction
# What would late period look like with early period characteristics?
P_counterfactual = model_late.predict(X_mean_early)

# Step 4: Decomposition
composition_effect = P_late_actual - P_counterfactual
coefficient_effect = P_counterfactual - P_early_predicted
```

### 5.3 Standardization (Direct vs. Indirect)

#### 5.3.1 Direct Standardization

**Question:** What would the pro-DS rate be in each year if case composition were held constant?

```
For each year t:
    P_standardized(t) = Σᵢ [P(PRO_DS|concept=i, year=t) × P(concept=i|standard)]

Where standard = marginal distribution across all years
```

#### 5.3.2 Implementation Example

```
Concept Cluster       | Marginal % | 2019-2020 Rate | 2024 Rate | Effect
----------------------|------------|----------------|-----------|-------
SCOPE                 | 10%        | 90%            | 85%       | -0.5pp
ENFORCEMENT           | 25%        | 55%            | 40%       | -3.75pp
RIGHTS                | 20%        | 85%            | 80%       | -1.0pp
...                   | ...        | ...            | ...       | ...

Standardized rate 2019-2020: 75%
Standardized rate 2024: 65%
Composition-adjusted decline: 10pp (vs. raw 23pp)
```

### 5.4 Shift-Share Analysis

For each predictor, quantify:

1. **Within effect:** Change in pro-DS rate within categories
2. **Between effect:** Change in distribution across categories
3. **Total effect:** Sum of within and between

```
ΔP = Σⱼ [w̄ⱼ × Δpⱼ]  +  Σⱼ [Δwⱼ × p̄ⱼ]  +  Σⱼ [Δwⱼ × Δpⱼ]
     ──────────────     ──────────────     ─────────────
     WITHIN             BETWEEN            INTERACTION
```

Where:
- wⱼ = weight (proportion) in category j
- pⱼ = pro-DS rate in category j
- Δ = change from early to late period
- bars indicate averages across periods

---

## 6. Advanced Temporal Methods

### 6.1 Sequential Dependence Analysis

#### 6.1.1 Rationale

Are consecutive rulings non-independent? Does a pro-DS ruling increase/decrease probability of next pro-DS ruling?

**Hypothesis:** CJEU may exhibit "doctrinal momentum" or "correction tendencies"

#### 6.1.2 Analysis

**Lag structure test:**
```
logit(P(PRO_DS_t = 1)) = β₀ + β₁(PRO_DS_{t-1}) + controls + ε_t
```

**Autocorrelation function:**
- Calculate ACF for residuals from main model
- Test for significant lag-1 correlation using Durbin-Watson

**Note:** Sorting by date within cases may create artificial serial correlation. Consider case-blocked randomization tests.

### 6.2 Growth Curve / Trajectory Analysis

#### 6.2.1 Random Slopes Model

If there is sufficient within-case variation over time (for multi-judgment cases):

```
logit(P(PRO_DS_ij = 1)) = β₀ + β₁(time_ij) + u₀ⱼ + u₁ⱼ(time_ij) + ε_ij
```

Where:
- i indexes holdings within case
- j indexes cases
- u₀ⱼ = random intercept (case-level)
- u₁ⱼ = random slope (case-specific time trend)

**Limitation:** Most cases have single judgment date; this analysis applies only to multi-date case clusters.

### 6.3 Event Study Design

#### 6.3.1 Application

For discrete events (e.g., landmark rulings like C-252/21 Meta), examine pre/post effects:

```
Y_t = β₀ + Σ_{k=-3}^{+3} β_k × D_{t,k} + controls + ε_t
```

Where D_{t,k} = 1 if observation is k periods from event.

**Candidate Events:**
- C-252/21 Meta (2023-07-04): Major platform data processing ruling
- C-300/21 UI (2023-05-04): First Article 82 damages ruling
- C-340/21 Natsionalna (2023-12-14): Liability without fault ruling

### 6.4 Survival/Duration Analysis

#### 6.4.1 Time-to-First-Ruling by Type

**Question:** How long does it take from GDPR entry into force to first ruling on a given topic?

```
Hazard function: h(t) = P(first ruling in [t, t+dt] | no ruling by t)

Model: h(t) = h₀(t) × exp(β'X)

Where X = concept type, institutional factors
```

**Findings:**
- First SCOPE ruling: 2019 (16 months post-GDPR)
- First ENFORCEMENT/compensation ruling: 2023 (60 months post-GDPR)

---

## 7. Temporal Mediation and Moderation

### 7.1 Does Time Moderate Predictor Effects?

**Framework:**
```
X → Y  [Does this effect vary over time?]

Test: Y = β₀ + β₁X + β₂T + β₃(X×T) + ε
H₀: β₃ = 0 (no moderation)
```

**Key Moderation Hypotheses:**

| Predictor (X) | Moderator (T) | Expected Pattern |
|---------------|---------------|------------------|
| Pro-DS purpose | Year | Effect may weaken as doctrine matures |
| Third Chamber | Year | Effect may strengthen as composition diverges |
| Teleological interpretation | Year | Effect may weaken (becoming baseline) |
| ENFORCEMENT concept | Year | Effect may strengthen (compensation backlash) |

### 7.2 Does Case Composition Mediate Temporal Effects?

**Framework:**
```
Time → Composition → Outcome

Path a: Time predicts composition change
Path b: Composition predicts outcome
Path c: Direct time → outcome effect
Path c': Time → outcome effect controlling for composition
```

**Analysis:**
1. Fit: Composition = α + a×Time (path a)
2. Fit: Outcome = α + c×Time (total effect)
3. Fit: Outcome = α + c'×Time + b×Composition (direct + mediated)
4. Mediation = c - c' = a×b

**Example Application:**
- Does increasing proportion of Article 82 cases mediate the temporal decline in pro-DS rate?
- Sobel test or bootstrap CIs for mediation effect

---

## 8. Sample Size and Power Considerations

### 8.1 Power Limitations

| Analysis | Required Effect Size | Achievable Power |
|----------|---------------------|------------------|
| Trend test (OR=0.8/year) | Medium | ~50% |
| Period comparison (N=90 vs 91) | Large (OR=2.0) | ~70% |
| Interaction (predictor × year) | Large | ~40% |
| Structural break | Very large | ~30% |

### 8.2 Strategies to Maximize Power

1. **Aggregate time:** Use periods instead of years
2. **Combine predictors:** Test joint hypotheses
3. **One-sided tests:** Where direction is predicted
4. **Focus on largest effects:** Prioritize detection of large effects

### 8.3 Pre-Registration

To avoid underpowered exploratory analyses:

**Primary (confirmatory):**
- H1: Pro-DS rate declines over time (one-sided, α=0.05)
- H2: Third Chamber effect attenuates with year control (two-sided, α=0.05)
- H3: Article 82 case proportion mediates temporal trend (one-sided, α=0.05)

**Secondary (exploratory):**
- All interaction tests
- Structural break analysis
- Detailed decomposition

---

## 9. Robustness and Sensitivity Analyses

### 9.1 Temporal Specification Sensitivity

| Specification | Description | Purpose |
|---------------|-------------|---------|
| Linear year | β(year) | Standard trend |
| Quadratic year | β₁(year) + β₂(year²) | Non-linear trend |
| Log time | β(log(days since GDPR)) | Diminishing effect |
| Year dummies | Σ β_t×D_t | Fully flexible |
| Period dummies | β(early) + β(middle) + β(late) | Discrete periods |

### 9.2 Exclusion Sensitivity

| Exclusion | Rationale |
|-----------|-----------|
| Exclude 2019-2020 | Small N, establishment phase |
| Exclude 2025 | Partial year |
| Exclude Article 82 cases | Test whether compensation cases drive results |
| Exclude Grand Chamber | Test whether major cases drive results |

### 9.3 Alternative Outcome Specifications

| Specification | Description |
|---------------|-------------|
| Binary (PRO_DS vs other) | Primary analysis |
| Trichotomous (PRO_DS/MIXED/PRO_CONTROLLER) | Multinomial sensitivity |
| Ordinal (PRO_CONTROLLER < MIXED < PRO_DS) | Ordered logit |
| Case-level majority | Aggregated to case level |

### 9.4 Cluster Robustness

All temporal analyses should report:
1. **Holding-level:** Standard errors
2. **Cluster-robust SE:** Case-level clustering
3. **Case-level aggregation:** Fully aggregated analysis

---

## 10. Visualization Strategy

### 10.1 Core Temporal Visualizations

**Figure T1: Pro-DS Rate Over Time**
- X: Year
- Y: Proportion pro-DS
- Elements: Point estimates, 95% CI, trend line

**Figure T2: Case Composition Shift**
- X: Year
- Y: Proportion
- Elements: Stacked areas by concept cluster

**Figure T3: Temporal Stability of Key Effects**
- X: Year or period
- Y: Coefficient (OR)
- Elements: Point estimates with CIs, reference line at 1.0

**Figure T4: Decomposition Visualization**
- Bar chart showing composition vs. coefficient contributions to change

**Figure T5: Rolling Window Analysis**
- X: Window midpoint
- Y: Pro-DS rate or key coefficient
- Elements: Rolling 2-year windows with ±1 SE bands

### 10.2 Diagnostic Visualizations

- Residual vs. time plot (check for temporal patterns in residuals)
- ACF/PACF plots (serial correlation diagnosis)
- CUSUM plot (structural stability)

---

## 11. Implementation Workflow

### Phase 1: Descriptive Temporal Analysis (Week 1)

```
1.1 Calculate annual statistics for all variables
1.2 Construct temporal trend tables
1.3 Generate time series plots
1.4 Identify candidate break points
```

### Phase 2: Bivariate Temporal Tests (Week 2)

```
2.1 Cochran-Armitage trend tests for binary variables
2.2 Chi-square/Fisher tests for categorical × time
2.3 Apply FDR correction
2.4 Document significant temporal trends
```

### Phase 3: Multivariate Temporal Models (Week 3)

```
3.1 Fit baseline temporal models (M-T1 through M-T3)
3.2 Fit interaction models (M-T4, M-T5)
3.3 Conduct period-based split-sample analysis
3.4 Test coefficient stability across periods
```

### Phase 4: Decomposition Analysis (Week 4)

```
4.1 Implement Kitagawa-Blinder-Oaxaca decomposition
4.2 Direct standardization of annual rates
4.3 Shift-share analysis
4.4 Quantify composition vs. coefficient contributions
```

### Phase 5: Advanced Methods (If Warranted)

```
5.1 Structural break tests
5.2 Serial correlation tests
5.3 Mediation analysis
5.4 Event study (if sufficient post-event observations)
```

### Phase 6: Robustness and Reporting

```
6.1 Sensitivity analyses
6.2 Visualization generation
6.3 Results synthesis
6.4 Manuscript integration
```

---

## 12. Expected Outputs

### 12.1 Primary Results Tables

| Table | Content |
|-------|---------|
| Table T1 | Descriptive temporal trends in all variables |
| Table T2 | Bivariate temporal tests with FDR correction |
| Table T3 | Multivariate temporal models (M-T1 to M-T6) |
| Table T4 | Decomposition results: composition vs. coefficient |
| Table T5 | Temporal robustness checks |

### 12.2 Primary Figures

| Figure | Content |
|--------|---------|
| Figure T1 | Pro-DS rate time series with trend |
| Figure T2 | Case composition evolution |
| Figure T3 | Key coefficients over time |
| Figure T4 | Decomposition bar chart |
| Figure T5 | Rolling window analysis |

### 12.3 Supplementary Materials

- Full trend test results for all variables
- Alternative temporal specifications
- Structural break test details
- Mediation analysis path coefficients

---

## 13. Limitations and Caveats

### 13.1 Fundamental Limitations

1. **Short time span:** 7 years provides limited temporal variation
2. **Small sample:** 181 holdings / 67 cases limits power for complex temporal models
3. **Non-random case arrival:** CJEU does not control which cases it receives
4. **Doctrine still developing:** GDPR jurisprudence may not have reached equilibrium

### 13.2 Interpretive Cautions

1. **Correlation ≠ causation:** Temporal associations do not establish causal time effects
2. **Ecological fallacy:** Aggregate trends may not reflect within-case dynamics
3. **Multiple testing:** Many temporal comparisons increase Type I error risk
4. **Selection bias:** Litigated cases may systematically differ from settled cases

### 13.3 What Temporal Analysis Cannot Answer

- **Why** the Court's approach may have changed
- Whether changes reflect **strategic** vs. **doctrinal** factors
- How the Court **will** rule in future cases
- **Causal** effect of time on rulings

---

## 14. Integration with Existing Analysis

### 14.1 Building on Current Findings

The current analysis established:
- Pro-DS purpose: OR=3.89-4.49 (robust to cluster correction)
- Third Chamber: OR=0.21 with year control (attenuated)
- Temporal trend: OR=0.83/year (p=0.103, not significant)
- Article 82 concentration: 97% in 2023-2024

### 14.2 Key Questions for Temporal Analysis

1. **Is the Third Chamber effect fully explained by temporal factors?**
   - Analysis: Compare chamber effect with/without year fixed effects

2. **Does the pro-DS purpose effect vary over time?**
   - Analysis: Purpose × year interaction

3. **How much of the pro-DS decline is compositional?**
   - Analysis: Decomposition separating Article 82 case surge

4. **Are there structural breaks in CJEU doctrine?**
   - Analysis: Chow test at 2023 (Article 82 surge)

5. **Is the apparent temporal trend spurious?**
   - Analysis: Standardized rates holding composition constant

---

## 15. Software Implementation

### 15.1 Python Implementation

```python
# Required packages
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns

# Cochran-Armitage trend test
from scipy.stats import chi2_contingency
def cochran_armitage_trend(table):
    """
    Cochran-Armitage test for trend in proportions
    table: 2 × k contingency table (binary × ordinal)
    """
    # Implementation details...
    pass

# Decomposition
def blinder_oaxaca(model_early, model_late, X_early, X_late):
    """
    Blinder-Oaxaca decomposition for logistic models
    """
    # Implementation details...
    pass
```

### 15.2 R Implementation

```r
# Required packages
library(tidyverse)
library(lme4)       # Mixed effects
library(emmeans)    # Marginal means
library(DescTools)  # Cochran-Armitage
library(oaxaca)     # Decomposition
library(strucchange) # Structural breaks

# Cochran-Armitage trend test
CochranArmitageTest(table, alternative = "two.sided")

# Structural break test
bp <- breakpoints(pro_ds ~ year, data = df)
summary(bp)
```

---

## Appendix A: Statistical Formulas

### A.1 Cochran-Armitage Trend Test

For a 2 × k table with binary outcome Y and ordinal predictor X:

```
Z = Σᵢ(xᵢ - x̄)(rᵢ - np̂) / √[np̂q̂ × Σᵢnᵢ(xᵢ - x̄)²]
```

Where:
- xᵢ = score for column i
- rᵢ = count of successes in column i
- nᵢ = total count in column i
- p̂ = overall proportion of successes
- q̂ = 1 - p̂

### A.2 Blinder-Oaxaca Decomposition

```
Δ = (Ȳ₁ - Ȳ₀) = (X̄₁ - X̄₀)'β* + X̄₁'(β₁ - β*) + X̄₀'(β* - β₀)
                 ─────────────   ────────────────   ─────────────
                 ENDOWMENTS      COEFF (Group 1)    COEFF (Group 0)
```

Where β* is a reference coefficient vector (e.g., pooled estimate).

### A.3 Chow Test Statistic

```
F = [(RSS_pooled - RSS₁ - RSS₂) / k] / [(RSS₁ + RSS₂) / (n₁ + n₂ - 2k)]

df₁ = k, df₂ = n₁ + n₂ - 2k
```

---

## Appendix B: Code Template

### B.1 Temporal Trend Analysis Script

```python
#!/usr/bin/env python3
"""
Temporal Analysis of CJEU GDPR Rulings
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf

def load_and_prepare_data():
    """Load holdings data and create temporal variables."""
    df = pd.read_csv('parsed-coded/holdings.csv')
    df['judgment_date'] = pd.to_datetime(df['judgment_date'])
    df['year'] = df['judgment_date'].dt.year
    df['year_centered'] = df['year'] - 2022
    df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)
    df['period'] = np.where(df['year'] < 2023, 'early', 'late')
    return df

def bivariate_trend_tests(df, variable):
    """Run trend test for binary variable."""
    contingency = pd.crosstab(df['year'], df[variable])
    # Cochran-Armitage trend test implementation
    # ...
    return results

def multivariate_temporal_model(df):
    """Fit temporal logistic regression with random effects."""
    model = smf.mixedlm(
        "pro_ds ~ year_centered + concept_cluster + pro_ds_purpose",
        df, groups=df["case_id"]
    )
    return model.fit()

def decomposition_analysis(df):
    """Blinder-Oaxaca style decomposition."""
    df_early = df[df['period'] == 'early']
    df_late = df[df['period'] == 'late']
    # Decomposition implementation
    # ...
    return composition_effect, coefficient_effect

if __name__ == "__main__":
    df = load_and_prepare_data()
    # Run analyses...
```

---

*Document version: 1.0*
*Author: Prepared for CJEU GDPR Empirical Legal Research Project*
*Methodology aligned with: Econometric time series analysis, epidemiological trend analysis, and empirical legal studies best practices*
*Date: January 2026*
