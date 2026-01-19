# CJEU GDPR Empirical Analysis: Factors Predicting Pro-Data Subject Rulings

## Executive Summary

This empirical study examines factors associated with pro-data subject versus pro-controller outcomes in 181 holdings from 67 CJEU GDPR decisions (2019-2025). Using bivariate tests with FDR correction and hierarchical logistic regression, we identify robust predictors of ruling direction.

**Key Findings:**

1. **60.8% of holdings favor data subjects** — the CJEU demonstrates a clear pro-protection orientation
2. **Invoking HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS purposes increases pro-DS odds 4.5x** (OR=4.49, p=0.001)
3. **Rights and Scope concept clusters strongly predict pro-DS outcomes** (OR≈7.7, p<0.03)
4. **Grand Chamber more pro-DS** (77.6%) **than Third Chamber** (34.1%)
5. **Balancing analysis does NOT predict fewer pro-DS outcomes** — contrary to expectations

---

## 1. Data Overview

| Metric | Value |
|--------|-------|
| Total holdings analyzed | 181 |
| Total cases | 67 |
| Time period | 2019-2025 |
| Pro-data subject holdings | 110 (60.8%) |
| Pro-controller holdings | 23 (12.7%) |
| Mixed holdings | 28 (15.5%) |
| Neutral/Unclear holdings | 20 (11.0%) |

### Analytical Approach

- **Unit of analysis**: Individual holding (not case)
- **Dependent variable**: Binary (PRO_DATA_SUBJECT=1 vs. OTHER=0)
- **Bivariate tests**: Chi-square/Fisher's exact with Benjamini-Hochberg FDR correction
- **Multivariate**: Hierarchical logistic regression with model comparison via AIC/LR tests
- **Quality check**: Individual case review for each major finding

---

## 2. Bivariate Results

### 2.1 Interpretive Sources

| Variable | % Pro-DS (Yes) | % Pro-DS (No) | Effect Size | p-value |
|----------|----------------|---------------|-------------|---------|
| Teleological present | 59.9% (n=167) | 71.4% (n=14) | Φ=0.042 | 0.572 |
| Pro-DS purpose invoked | **69.6%** (n=138) | **32.6%** (n=43) | **Φ=0.309** | **<0.001** |

**Dominant Source by Pro-DS Rate:**
| Source | Pro-DS Rate | n |
|--------|-------------|---|
| TELEOLOGICAL | **73.3%** | 75 |
| SEMANTIC | 62.5% | 40 |
| SYSTEMATIC | **44.4%** | 63 |

**Finding**: Teleological interpretation is near-ubiquitous (92.3%), limiting variance. However, when the Court explicitly invokes HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS as teleological purposes, pro-DS rates jump from 32.6% to 69.6% (Φ=0.309, p<0.001). This is the strongest bivariate predictor.

### 2.2 Reasoning Structure

| Variable | % Pro-DS (Yes) | % Pro-DS (No) | Effect Size | p-value |
|----------|----------------|---------------|-------------|---------|
| Principle-based present | 64.4% (n=90) | 57.1% (n=91) | Φ=0.063 | 0.393 |
| Level-shifting | **81.8%** (n=22) | 57.9% (n=159) | Φ=0.143 | 0.054 |

**Dominant Structure by Pro-DS Rate:**
| Structure | Pro-DS Rate | n |
|-----------|-------------|---|
| PRINCIPLE_BASED | **77.4%** | 31 |
| MIXED | 72.2% | 18 |
| RULE_BASED | 58.2% | 91 |
| CASE_LAW_BASED | 51.3% | 39 |

**Finding**: Level-shifting (moving from textual rules to principles) shows a strong association with pro-DS outcomes (81.8% vs 57.9%), marginally significant at p=0.054. Principle-based dominant structure has the highest pro-DS rate (77.4%).

### 2.3 Institutional Factors

| Chamber | Pro-DS Rate | n |
|---------|-------------|---|
| **GRAND_CHAMBER** | **77.6%** | 49 |
| FOURTH | 75.0% | 16 |
| FIRST | 61.4% | 44 |
| OTHER | 61.3% | 31 |
| **THIRD** | **34.1%** | 41 |

**Finding**: Grand Chamber is significantly more pro-DS (77.6% vs 54.5%, Φ=0.197, p=0.008). Third Chamber is notably less pro-DS (34.1%), suggesting chamber composition materially affects outcomes.

### 2.4 Conceptual Clusters

| Cluster | Pro-DS Rate | n |
|---------|-------------|---|
| **SCOPE** | **88.2%** | 17 |
| **RIGHTS** | **81.0%** | 21 |
| ACTORS | 70.0% | 10 |
| SPECIAL_CATEGORIES | 66.7% | 12 |
| LAWFULNESS | 64.7% | 17 |
| PRINCIPLES | 64.7% | 17 |
| OTHER | 50.0% | 22 |
| **ENFORCEMENT** | **46.2%** | 65 |

**Finding**: Cases about SCOPE (material/territorial definitions, 88.2%) and individual RIGHTS (access, erasure, etc., 81.0%) are most likely pro-DS. ENFORCEMENT cases (DPA powers, fines, remedies) are least likely pro-DS (46.2%). This suggests the Court expands protective scope but is more cautious about enforcement mechanisms.

### 2.5 Balancing Analysis

| Variable | % Pro-DS (Yes) | % Pro-DS (No) | Effect Size | p-value |
|----------|----------------|---------------|-------------|---------|
| Any balancing | 60.0% (n=55) | 61.1% (n=126) | Φ=0.000 | 1.000 |
| Necessity discussed | 63.4% (n=41) | 60.0% (n=140) | Φ=0.016 | 0.832 |

**Surprising Finding on Necessity Standard** (among necessity-discussed cases, n=41):
| Standard | Pro-DS Rate | n |
|----------|-------------|---|
| **STRICT** | **86.4%** | 22 |
| REGULAR | 36.8% | 19 |

**Finding**: Contrary to hypothesis, explicit balancing does NOT reduce pro-DS outcomes. Even more surprising: STRICT necessity standard is associated with HIGHER pro-DS rates (86.4%) than REGULAR (36.8%). This suggests that when the Court applies strict scrutiny, it typically finds in favor of data subjects.

---

## 3. Multivariate Results

### 3.1 Model Comparison

| Model | K | Log-lik | AIC | BIC | Pseudo-R² |
|-------|---|---------|-----|-----|-----------|
| M0: Null | 1 | -121.22 | 244.4 | 247.6 | 0.000 |
| M1: + Institutional | 6 | -111.18 | 234.4 | 253.6 | 0.083 |
| M2: + Conceptual | 13 | -105.45 | 236.9 | 278.5 | 0.130 |
| **M3: + Interpretive** | 18 | -93.13 | **222.3** | 279.8 | **0.232** |
| M4: + Reasoning | 24 | -90.51 | 229.0 | 305.8 | 0.253 |
| M5: Full | 25 | -87.68 | 225.4 | 305.3 | 0.277 |

**Best Model**: Model 3 (Institutional + Conceptual + Interpretive Sources) by AIC (222.3)

### 3.2 Final Model Coefficients (Model 3)

| Predictor | OR | 95% CI | p | Sig |
|-----------|----:|--------|---:|:---:|
| **Pro-DS purpose invoked** | **4.49** | [1.81, 11.12] | 0.001 | ** |
| **RIGHTS cluster** | **7.78** | [1.43, 42.22] | 0.018 | * |
| **SCOPE cluster** | **7.69** | [1.24, 47.75] | 0.029 | * |
| SYSTEMATIC dominant | 0.40 | [0.15, 1.05] | 0.062 | . |
| GRAND_CHAMBER | 2.07 | [0.65, 6.60] | 0.218 | |
| THIRD chamber | 0.43 | [0.14, 1.34] | 0.146 | |

**Interpretation**:
- Invoking HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS purposes increases odds of pro-DS ruling by 4.5x, controlling for other factors
- Cases about data subject RIGHTS are 7.8x more likely to be pro-DS than OTHER concept cases
- Cases about SCOPE definitions are 7.7x more likely to be pro-DS
- SYSTEMATIC dominant interpretation shows a trend toward fewer pro-DS outcomes (OR=0.40, p=0.062)
- Chamber effects attenuate after controlling for interpretive and conceptual factors

---

## 4. Quality Check: Individual Case Review

Each finding was validated against individual coded decisions:

| Finding | Confirming | Challenging | Confirmation Rate |
|---------|------------|-------------|-------------------|
| Teleological → Pro-DS | 100 | 67 | 59.9% |
| **Pro-DS Purpose → Pro-DS** | **96** | **42** | **69.6%** |
| **Level Shifting → Pro-DS** | **18** | **4** | **81.8%** |
| Balancing → Fewer Pro-DS | 22 | 33 | 40.0% |
| Semantic → Fewer Pro-DS | 15 | 25 | 37.5% |

**Overall Confirmation Rate**: 57.8%

### 4.1 Strongest Confirmed Finding: Level Shifting

When the Court shifts from textual rules to normative principles, 81.8% of outcomes favor data subjects. Example confirming case:

> **C-200/23, Holding 3**: "A Member State cannot refuse erasure requests for non-required personal data solely because redacted forms would require additional effort."

### 4.2 Strongest Confirmed Finding: Pro-DS Purpose Invocation

Invoking HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS correlates with 69.6% pro-DS outcomes. Example:

> **C-673/17, Holding 1**: "Consent for cookie storage is not valid when obtained through a pre-checked checkbox."
> Direction: PRO_DATA_SUBJECT. Purposes: HIGH_LEVEL_OF_PROTECTION, FUNDAMENTAL_RIGHTS.

### 4.3 Non-Confirmed Finding: Balancing

Contrary to hypothesis, balancing analysis does not predict fewer pro-DS outcomes (confirmation rate only 40.0%). Many "MIXED" outcomes explain this:

> **C-456/22, Holding 1**: "Article 82(1) GDPR precludes a de minimis threshold for non-material damage but data subjects must prove actual damage."
> Ruling: MIXED — balancing yields nuanced outcomes, not pro-controller ones.

### 4.4 Surprising Cases

27 holdings expected to be pro-DS (teleological + pro-DS purpose + no balancing) ruled otherwise. Common pattern: **compensation threshold cases** where the Court limits damages despite protective rhetoric.

> **C-507/23, Holding 1**: "A GDPR infringement alone does not constitute damage; actual damage must be separately established."
> Despite invoking HIGH_LEVEL_OF_PROTECTION, ruling is PRO_CONTROLLER.

---

## 5. Key Conclusions

### 5.1 Confirmed Hypotheses

1. **H2b: Pro-DS teleological purposes predict pro-DS outcomes** ✓
   - Invocation of HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS is the strongest predictor (OR=4.49)

2. **H4: Level-shifting predicts pro-DS outcomes** ✓ (marginally)
   - 81.8% confirmation rate in quality check; p=0.054 in bivariate

3. **H5: Grand Chamber is more pro-DS** ✓
   - 77.6% vs 54.5% (p=0.008)

4. **H6: Rights concepts predict pro-DS outcomes** ✓
   - OR=7.78 in multivariate model

### 5.2 Rejected/Revised Hypotheses

1. **H1: Teleological interpretation predicts pro-DS** ✗
   - Teleological is ubiquitous (92%); insufficient variance

2. **H7-H8: Balancing predicts fewer pro-DS outcomes** ✗
   - No effect found; balancing produces MIXED outcomes, not pro-controller ones

3. **H9: Strict necessity predicts fewer pro-DS** ✗ (REVERSED)
   - STRICT standard actually correlates with MORE pro-DS outcomes (86.4%)

### 5.3 Novel Insights

1. **Third Chamber Effect**: The Third Chamber rules pro-DS only 34.1% of the time vs 77.6% for Grand Chamber. This 43-percentage-point gap warrants further investigation into chamber composition, case allocation, or subject matter specialization.

2. **ENFORCEMENT vs RIGHTS Divergence**: The Court is protective about defining scope and rights (88%/81% pro-DS) but cautious about enforcement mechanisms like damages and fines (46% pro-DS). This suggests a gap between theoretical protection and practical remedies.

3. **Compensation Paradox**: Many cases invoking HIGH_LEVEL_OF_PROTECTION still rule against data subjects on compensation questions. The Court's compensatory (not punitive) interpretation of Article 82 creates a tension between rhetorical protection and material recovery.

---

## 6. Limitations

1. **Non-independence**: Holdings within cases are not independent; mixed-effects specification recommended for future work

2. **Sample size**: N=181 holdings limits power for detecting small effects and creates instability in full models (convergence warnings observed)

3. **Coding reliability**: Single-coder design; inter-rater reliability not assessed

4. **Causal inference**: Associations only; interpretive methods may be chosen to support predetermined conclusions

5. **Generalizability**: Limited to GDPR cases in CJEU; may not generalize to national courts or other data protection regimes

---

## 7. Implications for Practice

### For Data Protection Practitioners

- **Framing matters**: Arguments explicitly invoking HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS purposes are associated with favorable outcomes
- **Scope cases favorable**: Challenges to the scope/territorial reach of GDPR are likely to expand protection
- **Damages are harder**: Even when infringement is established, proving compensable damage remains a significant hurdle

### For Academics

- **Interpretive plurality**: The Court uses multiple methods simultaneously; dominant source categorization captures meaningful variation
- **Chamber composition**: Institutional factors may be as important as doctrinal ones in predicting outcomes
- **Purpose-driven adjudication**: Teleological interpretation with explicit pro-protection purposes is the strongest predictor — supporting purposivist theories of CJEU interpretation

---

## 8. Technical Appendix

### Files Generated

| File | Description |
|------|-------------|
| `holdings_prepared.csv` | Analysis-ready dataset with derived variables |
| `bivariate_summary.csv` | All bivariate test results with effect sizes |
| `bivariate_results.json` | Detailed bivariate output |
| `model_comparison.csv` | Logistic regression model fit statistics |
| `final_model_coefficients.csv` | Best model coefficients |
| `quality_check_summary.csv` | Case review confirmation rates |
| `quality_check_details.json` | Surprising cases detail |

### Reproducibility

All analysis scripts are in `analysis/scripts/`:
1. `01_data_preparation.py` — Variable transformation
2. `02_bivariate_analysis.py` — Chi-square tests, FDR correction
3. `03_multivariate_analysis.py` — Hierarchical logistic regression
4. `04_quality_check.py` — Individual case validation

Run sequence:
```bash
python3 analysis/scripts/01_data_preparation.py
python3 analysis/scripts/02_bivariate_analysis.py
python3 analysis/scripts/03_multivariate_analysis.py
python3 analysis/scripts/04_quality_check.py
```

---

## 9. Advanced Analysis: Priority Investigations

### 9.1 Third Chamber Investigation

The 43-percentage-point gap between Third Chamber (34.1% pro-DS) and Grand Chamber (77.6%) was investigated in depth.

**Case Allocation Hypothesis:**
- Third Chamber receives 63.4% ENFORCEMENT cases vs Grand's 26.5%
- ENFORCEMENT has lowest pro-DS rate (46.2%), so allocation partially explains gap
- Chi-square confirms concept distribution differs significantly by chamber (p=0.008)

**Within-Concept Comparison:**
| Concept | Third Pro-DS | Grand Pro-DS | Gap |
|---------|-------------|--------------|-----|
| ENFORCEMENT | 30.8% | 69.2% | +38.5pp |
| PRINCIPLES | 40.0% | 100.0% | +60.0pp |
| OTHER | 25.0% | 66.7% | +41.7pp |

**Interpretive Differences:**
- Third uses TELEOLOGICAL dominant: 31.7% vs Grand's 46.9%
- Pro-DS purpose invocation: 61.0% vs 75.5%
- Level-shifting: 2.4% vs 20.4%

**Controlled Analysis:**
- Unadjusted OR = 0.15 (Third vs Grand)
- After controlling for concept + interpretation: OR = 0.024, p = 0.0007
- **Conclusion: Third Chamber effect PERSISTS after controls — genuine interpretive difference**

**Key Finding:** Third Chamber is dominated by REMEDIES_COMPENSATION cases (24 of 41 holdings, 58.5%), and rules pro-DS in only 29% of these. The Court's compensatory approach to Article 82 systematically disadvantages data subjects.

### 9.2 Mixed-Effects Analysis

Holdings within cases are not independent. ICC = 0.295 (29.5% of variance is between-case), confirming need for cluster correction.

**Cluster-Robust Standard Errors:**
| Predictor | OR | 95% CI | p | Change from Naive |
|-----------|---:|--------|---:|-------------------|
| Pro-DS purpose | 3.89 | [1.42, 10.67] | 0.008 | Still significant |
| SYSTEMATIC dominant | 0.36 | [0.14, 0.94] | 0.037 | Now significant |
| Third Chamber | 0.33 | [0.12, 0.93] | 0.037 | Still significant |
| Grand Chamber | 2.33 | [0.83, 6.58] | 0.109 | Attenuates to NS |
| Level-shifting | 1.62 | [0.42, 6.25] | 0.486 | **No longer significant** |

**Key Revision:** Level-shifting, previously marginally significant (p=0.054), is NOT significant after cluster correction. The naive analysis overstated its importance.

### 9.3 Article 82 Compensation Paradox

Compensation cases (REMEDIES_COMPENSATION) show a systematic gap between rights rhetoric and remedies outcomes.

**The Gap:**
- Compensation cases: 36.1% pro-DS
- Other concepts: 66.9% pro-DS
- **Difference: 30.8 percentage points**

**The Paradox:**
10 compensation holdings (27.8%) invoke HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS but still rule against data subjects.

**Key Doctrinal Themes in Non-Pro-DS Compensation Cases:**
| Theme | Frequency |
|-------|-----------|
| Actual damage threshold required | 65.2% |
| Damage proof required | 56.5% |
| No strict liability | 13.0% |
| Compensatory not punitive | 13.0% |
| Fault element required | 13.0% |

**Representative Paradox Case:**
> **C-507/23**: "A GDPR infringement alone does not constitute damage; actual damage must be separately established."
> Despite invoking FUNDAMENTAL_RIGHTS and HIGH_LEVEL_OF_PROTECTION, ruling is PRO_CONTROLLER.

**Temporal Pattern:**
- 2024: 21 compensation holdings, only 29% pro-DS
- This wave of Article 82 cases is establishing a restrictive damages doctrine

**Practical Implications:**
1. Data subjects must prove "actual damage" beyond mere infringement
2. Compensation is purely compensatory, not punitive or deterrent
3. Fear of misuse alone may not suffice unless unauthorized access occurred
4. Controller fault severity does not increase damages

---

## 10. Revised Conclusions

After advanced analysis, the key predictors are:

| Predictor | Status | Evidence |
|-----------|--------|----------|
| **Pro-DS purpose invocation** | **CONFIRMED** | OR=3.89, p=0.008 (cluster-robust) |
| **Third Chamber** | **CONFIRMED** | OR=0.33, p=0.037; effect persists after controls |
| **SYSTEMATIC dominant** | **NEW** | OR=0.36, p=0.037; contextual reasoning less pro-DS |
| Grand Chamber | ATTENUATED | OR=2.33, p=0.109; NS with clustering |
| Level-shifting | **REVISED** | OR=1.62, p=0.486; NS with clustering |
| RIGHTS/SCOPE concepts | CONFIRMED | OR≈7.7 in naive models |

**Novel Insights:**

1. **Compensation creates a systematic remedies gap**: 30.8pp lower pro-DS rate, driven by "actual damage" requirement

2. **Third Chamber effect is genuine**: Not just case allocation; interpretive difference persists after controlling for concept and interpretive factors

3. **ICC = 29.5%**: Substantial clustering means naive analyses overstate significance

4. **Temporal shift**: 2023-2024 compensation case wave is establishing restrictive Article 82 doctrine, primarily in Third Chamber

---

## 8. Technical Appendix

### Files Generated

| File | Description |
|------|-------------|
| `holdings_prepared.csv` | Analysis-ready dataset with derived variables |
| `bivariate_summary.csv` | All bivariate test results with effect sizes |
| `bivariate_results.json` | Detailed bivariate output |
| `model_comparison.csv` | Logistic regression model fit statistics |
| `final_model_coefficients.csv` | Best model coefficients |
| `quality_check_summary.csv` | Case review confirmation rates |
| `quality_check_details.json` | Surprising cases detail |
| `third_chamber_investigation.json` | Third Chamber analysis |
| `mixed_effects_results.json` | Cluster-robust results |
| `compensation_paradox.json` | Article 82 analysis |

### Reproducibility

All analysis scripts are in `analysis/scripts/`:
1. `01_data_preparation.py` — Variable transformation
2. `02_bivariate_analysis.py` — Chi-square tests, FDR correction
3. `03_multivariate_analysis.py` — Hierarchical logistic regression
4. `04_quality_check.py` — Individual case validation
5. `05_third_chamber_investigation.py` — Third Chamber deep dive
6. `06_mixed_effects_models.py` — Cluster-robust analysis
7. `07_compensation_paradox.py` — Article 82 paradox

Run sequence:
```bash
python3 analysis/scripts/01_data_preparation.py
python3 analysis/scripts/02_bivariate_analysis.py
python3 analysis/scripts/03_multivariate_analysis.py
python3 analysis/scripts/04_quality_check.py
python3 analysis/scripts/05_third_chamber_investigation.py
python3 analysis/scripts/06_mixed_effects_models.py
python3 analysis/scripts/07_compensation_paradox.py
```

---

*Report updated: 2026-01-19*
*N=181 holdings from 67 CJEU GDPR decisions (2019-2025)*
