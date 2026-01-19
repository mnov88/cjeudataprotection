# Phase 2: Bivariate Temporal Tests - Findings

**Analysis Date:** January 2026
**Data:** 181 holdings (52 early, 129 late)

---

## Executive Summary

The bivariate temporal tests reveal a crucial insight: **the apparent decline in pro-data subject rulings is NOT statistically significant**, while the **compositional shift toward compensation cases IS highly significant**. This strongly suggests that the observed temporal pattern reflects changing case composition rather than genuine doctrinal evolution.

---

## 1. Pro-DS Rate Decline: Not Statistically Significant

### 1.1 Test Results

| Metric | Value |
|--------|-------|
| Early (2019-2022) | 69.2% pro-DS (N=52) |
| Late (2023-2025) | 57.4% pro-DS (N=129) |
| Difference | -11.8 percentage points |
| Chi-square | χ²=1.720, p=0.190 |
| Fisher's exact | p=0.178 |
| Cochran-Armitage trend | z=-1.64, p=0.101 |
| Logistic trend | OR=0.83/year, p=0.103 |

### 1.2 Interpretation

Despite a descriptively notable 11.8 pp decline, the trend is **not statistically significant** at conventional levels (α=0.05). This is consistent with:
- Random variation in a relatively small sample
- Compositional confounding (see Section 2)
- The decline being explained by case mix changes

**Conclusion:** Cannot reject null hypothesis of no temporal trend in pro-DS rate.

---

## 2. Compensation Case Concentration: Highly Significant

### 2.1 Temporal Distribution

| Period | Compensation Cases | % of Holdings |
|--------|-------------------|---------------|
| Pre-2023 | 1 | 1.9% |
| 2023+ | 35 | 27.1% |

**Concentration:** 97.2% of all compensation cases occurred in 2023+

### 2.2 Statistical Tests

| Test | Result |
|------|--------|
| Chi-square (year × compensation) | χ²=26.32, p<0.0001 |
| Cochran-Armitage trend | z=3.73, p=0.0002 |
| FDR-corrected q-value | q=0.0021 |

**Conclusion:** The temporal concentration of compensation cases is **highly statistically significant**.

---

## 3. Compensation Gap: Strongest Bivariate Effect

### 3.1 Pro-DS Rates by Case Type

| Case Type | N | Pro-DS Rate |
|-----------|---|-------------|
| Compensation | 36 | 36.1% |
| Non-compensation | 145 | 66.9% |
| **Gap** | | **-30.8 pp** |

### 3.2 Statistical Tests

| Test | Result |
|------|--------|
| Chi-square | χ²=10.21, p=0.0014 |
| Fisher's exact | p=0.0011 |

**Conclusion:** Compensation cases are **30.8 percentage points less likely** to be pro-data subject than non-compensation cases. This is the **strongest bivariate effect** in the dataset.

### 3.3 Implication for Temporal Trend

The combination of findings 2 and 3 explains the temporal pattern:
- Compensation cases are much less likely to be pro-DS (-30.8 pp)
- Compensation cases are concentrated in 2023+ (97.2%)
- Therefore, the late period has more cases with low pro-DS probability
- The apparent temporal decline is **compositional, not doctrinal**

---

## 4. Third Chamber Concentration: Significant

### 4.1 Temporal Distribution

| Period | Third Chamber % |
|--------|----------------|
| Early (2019-2022) | 5.8% |
| Late (2023-2025) | 29.5% |
| **Difference** | **+23.7 pp** |

### 4.2 Statistical Tests

| Test | Result |
|------|--------|
| Chi-square | χ²=10.56, p=0.0012 |
| FDR-corrected q-value | q<0.001 |

**Conclusion:** Third Chamber's share of holdings increased significantly over time, coinciding with the compensation case surge.

---

## 5. Chamber Distribution: Major Temporal Shift

### 5.1 Full Chamber Distribution

| Chamber | Early | Late | Change |
|---------|-------|------|--------|
| GRAND_CHAMBER | 55.8% | 15.5% | -40.3 pp |
| THIRD | 5.8% | 29.5% | +23.7 pp |
| FIRST | 7.7% | 31.0% | +23.3 pp |
| FIFTH | 17.3% | 4.7% | -12.6 pp |

### 5.2 Statistical Test

χ²(5) = 47.71, p < 0.0001, Cramér's V = 0.513

**Conclusion:** The chamber distribution has shifted dramatically, with Grand Chamber declining and Third/First Chambers increasing.

---

## 6. Concept Cluster Evolution: Significant

### 6.1 Distribution Changes

| Cluster | Early | Late | Change |
|---------|-------|------|--------|
| ENFORCEMENT | 23.1% | 41.1% | +18.0 pp |
| PRINCIPLES | 23.1% | 3.9% | -19.2 pp |
| RIGHTS | 7.7% | 13.2% | +5.5 pp |
| SCOPE | 15.4% | 7.0% | -8.4 pp |

### 6.2 Statistical Test

χ²(7) = 24.67, p = 0.0009, Cramér's V = 0.369

**Conclusion:** The concept cluster distribution has shifted significantly, with ENFORCEMENT (including compensation) increasing dramatically.

---

## 7. FDR-Corrected Significant Trends

Seven variables showed significant temporal trends after Benjamini-Hochberg FDR correction (q < 0.10):

| Variable | Change | q-value | Direction |
|----------|--------|---------|-----------|
| Compensation Case | +25.2 pp | 0.002 | ↑ Increasing |
| Judge Count | -3.6 (mean) | <0.001 | ↓ Decreasing |
| Chamber (Grouped) | — | <0.001 | Restructuring |
| Concept Cluster | — | 0.005 | ENFORCEMENT↑ |
| Dominant Structure | — | 0.053 | CASE_LAW↑ |
| Paragraphs | -6.3 (mean) | 0.053 | ↓ Shorter |
| Case Law Reasoning | +5.3 pp | 0.098 | ↑ Increasing |

---

## 8. Non-Significant Trends

The following variables showed **no significant temporal trend**:

| Variable | Early | Late | Diff | p-value |
|----------|-------|------|------|---------|
| Pro-DS Ruling | 69.2% | 57.4% | -11.8 | 0.103 |
| Pro-DS Purpose | 76.9% | 76.0% | -0.9 | 0.427 |
| Teleological | 90.4% | 93.0% | +2.6 | 0.086 |
| Systematic | 98.1% | 89.9% | -8.2 | 0.154 |
| Level Shifting | 17.3% | 10.1% | -7.2 | 0.843 |
| Principle-Based | 59.6% | 45.7% | -13.9 | 0.459 |

**Key Finding:** Pro-DS purpose invocation remains stable (~76-77%) across periods, suggesting the Court's rights-protective rhetoric has not declined even as case composition shifted.

---

## 9. Key Implications

### For Multivariate Analysis (Phase 3):
1. Test whether temporal effect disappears when controlling for compensation cases
2. Test whether Third Chamber effect is fully explained by compensation concentration
3. Model time × compensation interaction

### For Decomposition Analysis (Phase 4):
1. Quantify how much of the -11.8 pp decline is explained by composition vs. coefficients
2. Hypothesis: >75% of decline is compositional

### For Interpretation:
1. **No evidence of doctrinal shift** - pro-DS rate decline not significant
2. **Strong evidence of compositional shift** - compensation surge is highly significant
3. **Rights rhetoric stable** - pro-DS purpose invocation unchanged
4. **Institutional shift** - chamber distribution dramatically changed

---

## 10. Summary Table: All Bivariate Tests

| Variable | Early | Late | Diff | p-value | FDR-q | Significant |
|----------|-------|------|------|---------|-------|-------------|
| Pro-DS Ruling | 69.2% | 57.4% | -11.8 | 0.103 | 0.217 | No |
| Compensation | 1.9% | 27.1% | +25.2 | 0.0003 | 0.002 | **Yes** |
| Third Chamber | 5.8% | 29.5% | +23.7 | 0.001 | <0.01 | **Yes** |
| Case Law | 84.6% | 89.9% | +5.3 | 0.033 | 0.098 | **Yes** |
| Pro-DS Purpose | 76.9% | 76.0% | -0.9 | 0.427 | 0.560 | No |
| Level Shifting | 17.3% | 10.1% | -7.2 | 0.843 | 0.932 | No |

---

*Phase 2 Complete. The null hypothesis of no temporal trend in pro-DS rulings cannot be rejected, while the compositional shift toward compensation cases is highly significant. Proceed to Phase 3: Multivariate Temporal Models.*
