# Clustering Impact Assessment: Findings at Risk

## Executive Summary

This document identifies which specific findings in the CJEU data protection analysis are dependent on the current topic clustering approach and how they might change with alternative clustering.

---

## 1. HIGH-RISK FINDINGS (Would Substantially Change)

### 1.1 The RIGHTS and SCOPE Cluster Effects

**Current finding:** RIGHTS and SCOPE clusters show significantly higher pro-DS rates
- RIGHTS: OR=7.40, p=0.023 (Model 5)
- SCOPE: OR=5.93, p=0.066 (Model 5, borderline)

**Why at risk:**
- RIGHTS cluster contains 7 concepts with 30pp internal range (70%-100%)
- SCOPE cluster contains 5 concepts with 17pp internal range (83%-100%)
- Effect may be driven by specific concepts (RIGHT_TO_ERASURE at 86%, PERSONAL_DATA_SCOPE at 100%)

**With alternative clustering:**
| Approach | Impact on RIGHTS Effect | Impact on SCOPE Effect |
|----------|------------------------|----------------------|
| Split clustering | Effect persists but magnitude changes | Effect persists |
| Granular (separate concepts) | Splits into ACCESS (70%) vs ERASURE (86%) | Persists |
| Empirical | Absorbed into HIGH_PRO_DS band | Absorbed into HIGH_PRO_DS band |
| No clustering | Individual concept ORs not significant (sparse) | Same |

**Recommendation:** Report sensitivity with split (RIGHTS_ACCESS vs RIGHTS_ERASURE)

---

### 1.2 The ENFORCEMENT Cluster Finding

**Current finding:** ENFORCEMENT has lowest pro-DS rate (46.2%)

**Why at risk:**
- Contains REMEDIES_COMPENSATION (36.1% pro-DS) which drives the low rate
- Non-compensation ENFORCEMENT concepts average 58.6% pro-DS
- 100pp internal range (ONE_STOP_SHOP at 0% to REPRESENTATIVE_ACTIONS at 100%)

**With alternative clustering:**
| Approach | New ENFORCEMENT Rate | New COMPENSATION Rate |
|----------|---------------------|----------------------|
| Split | DPA cluster: 58.6% | Separate: 36.1% |
| Granular | DPA: 58.6% | Compensation: 36.1% |
| Empirical | DPA → MEDIUM_HIGH | Compensation → LOW_PRO_DS |

**Impact on conclusions:**
- Current: "ENFORCEMENT topics favor controllers"
- Revised: "Compensation cases favor controllers; DPA cases are balanced"

---

### 1.3 Temporal Decline Attribution

**Current finding:** Pro-DS rate declined from 69.2% (early) to 57.4% (late)
- Attributed partly to composition shift toward ENFORCEMENT cluster

**Why at risk:**
- Shift-share decomposition uses cluster weights
- ENFORCEMENT weight increased +18pp over time
- But this is driven specifically by compensation cases increasing

**With alternative clustering:**
| Approach | Within-Cluster Shift | Between-Cluster Shift |
|----------|---------------------|----------------------|
| Current | -13.6pp | +1.8pp |
| Split (compensation separate) | Different attribution | Compensation-specific effect isolated |

**Impact on conclusions:**
- Current: "Topic composition shifted toward ENFORCEMENT"
- Revised: "Compensation cases specifically increased, driving decline"

---

### 1.4 Model Explanatory Power

**Current finding:** Concept_cluster contributes ~15% of model pseudo-R²
- Model with clustering: R²=0.268
- Model without clustering: R²=0.119 (55% reduction)

**Why at risk:**
- This comparison depends on how "without clustering" is operationalized
- Empirical clustering achieves better fit (AIC=208) than current (AIC=217)

**With alternative clustering:**
| Approach | AIC | Pseudo-R² | Interpretation |
|----------|-----|-----------|---------------|
| Current 8-cluster | 217.4 | 0.260 | Baseline |
| Split 10-cluster | 220.5 | 0.264 | Marginal improvement |
| Empirical 4-cluster | **208.0** | **0.266** | Better fit, less interpretable |
| No clustering | 216.9 | 0.204 | Worse fit |

---

## 2. MEDIUM-RISK FINDINGS (Would Change Moderately)

### 2.1 LAWFULNESS Cluster Heterogeneity

**Current finding:** LAWFULNESS cluster shows 64.7% pro-DS rate

**Actual breakdown:**
| Legal Basis | Pro-DS Rate | N |
|-------------|-------------|---|
| CONTRACT_BASIS | 100% | 2 |
| VITAL_INTERESTS | 100% | 1 |
| LEGITIMATE_INTERESTS | 80% | 5 |
| CONSENT_BASIS | 75% | 4 |
| LEGAL_OBLIGATION | 25% | 4 |
| PUBLIC_INTEREST | 0% | 1 |

**With split clustering:**
- LAWFULNESS_CONSENT (consent, contract, legit int): 81.8% pro-DS
- LAWFULNESS_OBLIGATION (legal oblig, public int, vital): 33.3% pro-DS

**Impact:** The "LAWFULNESS is moderately pro-DS" finding would become:
- "Consent-type bases strongly favor data subjects (82%)"
- "Obligation-type bases favor controllers (33%)"

---

### 2.2 Citation Network RIGHTS Effect

**Current finding:** RIGHTS cluster citation effect OR=8.38, p=0.015

**Why at risk:**
- Based on same RIGHTS cluster definition
- May be driven by specific high-citation concepts (RIGHT_OF_ACCESS, RIGHT_TO_ERASURE)

**With alternative clustering:**
- Granular: Separate ACCESS vs ERASURE effects
- Impact: Effect likely persists but splits across concepts

---

## 3. LOW-RISK FINDINGS (Would Not Substantially Change)

### 3.1 Pro-DS Purpose Effect

**Current finding:** pro_ds_purpose OR=5.06, p=0.0009

**Why robust:**
- Remains significant with AND without concept_cluster control
- Model 6 (no clustering): OR=4.21, p=0.0004
- Effect is independent of topic clustering

---

### 3.2 Chamber Effects

**Current finding:** Third Chamber shows lower pro-DS rates

**Why robust:**
- Chamber assignment is orthogonal to concept clustering
- Effect persists across all model specifications

---

### 3.3 Balancing Effects

**Current finding:** any_balancing associated with pro-DS outcomes

**Why robust:**
- Measured independently of concept topic
- Persists across models with/without clustering

---

## 4. SPECIFIC STATISTICAL CHANGES EXPECTED

### Bivariate Analysis

| Metric | Current (8 clusters) | Split (10) | Empirical (4) | No Clustering |
|--------|---------------------|------------|---------------|---------------|
| Chi-square | 17.22 | 24.46 | 28.89 | 27.12 |
| p-value | 0.016 | 0.004 | <0.001 | 0.007 |
| Cramér's V | 0.308 | 0.368 | 0.400 | 0.443 |
| Interpretation | Moderate | Better | Best | Best (but sparse) |

### Multivariate Model Coefficients

| Predictor | Current Model | Split Model | No Cluster Model |
|-----------|--------------|-------------|------------------|
| RIGHTS | OR=7.40* | OR≈7.5* (persists) | N/A |
| SCOPE | OR=5.93 | OR≈6.0* (persists) | N/A |
| ENFORCEMENT | OR=1.09 | DPA: OR≈1.5, COMP: OR≈0.5* | N/A |
| is_compensation | Not included | OR≈0.49, p≈0.18 | OR≈0.49 |

*Estimated based on deep dive analysis

---

## 5. RECOMMENDATIONS FOR REPORTING

### Primary Analysis
1. Use **current 8-cluster approach** for main results (interpretability)
2. **Add is_compensation control** to all models (AIC improves, captures key heterogeneity)

### Sensitivity Analyses
Report in appendix:
1. **Split clustering** results (10 clusters with ENFORCEMENT and LAWFULNESS split)
2. **No clustering** bivariate results (concept-level chi-square)
3. **Coefficient stability table** across clustering approaches

### Specific Finding Revisions
Consider revising these statements:

| Current Statement | Revised Statement |
|-------------------|-------------------|
| "ENFORCEMENT topics favor controllers" | "Compensation cases favor controllers; other enforcement topics are balanced" |
| "LAWFULNESS moderately favors data subjects" | "Consent-type bases strongly favor DS; obligation bases favor controllers" |
| "Temporal decline driven by topic composition shift" | "Temporal decline driven specifically by compensation case increase" |

---

## 6. SUMMARY TABLE

| Finding | Risk Level | Current Value | Would Change To |
|---------|-----------|---------------|-----------------|
| ENFORCEMENT low pro-DS | HIGH | 46.2% | Split: 58.6% (DPA) / 36.1% (comp) |
| RIGHTS high pro-DS | MEDIUM | OR=7.40 | Persists but magnitude may vary |
| SCOPE high pro-DS | MEDIUM | OR=5.93 | Persists |
| Temporal attribution | HIGH | Cluster composition | Compensation-specific |
| Model R² | HIGH | 0.268 | Empirical: 0.266 (similar) |
| LAWFULNESS moderate | HIGH | 64.7% | Split: 82% / 33% |
| Pro-DS purpose | LOW | OR=5.06 | Persists (OR=4.21) |
| Chamber effects | LOW | Varies | Persists |
