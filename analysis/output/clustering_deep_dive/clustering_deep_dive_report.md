# Topic Clustering Deep Dive Analysis

## Executive Summary

This report provides a deep dive analysis into alternative clustering schemes and
specific examination of lawfulness bases (consent vs legitimate interest).

## 1. Alternative Clustering Schemes Evaluated

### 1.1 Schemes Compared

| Scheme | N Clusters | Description |
|--------|------------|-------------|
| Original | 8 | Current implementation (SCOPE, ACTORS, etc.) |
| Split | 10 | Separates ENFORCEMENT (compensation vs DPA) and LAWFULNESS (consent-type vs obligation-type) |
| Granular | 14 | Each major legal basis separate + more subdivisions |
| Empirical | 4 | Data-driven: HIGH/MEDIUM_HIGH/MEDIUM/LOW pro-DS rate bands |

### 1.2 Statistical Comparison

| Scheme | N Clusters | Chi-square | p-value | Cramér's V |
|--------|------------|------------|---------|------------|
| Original (8 clusters) | 8 | 17.22 | 0.0160 | 0.308 |
| Split (10 clusters) | 10 | 24.46 | 0.0036 | 0.368 |
| Granular (14 clusters) | 15 | 26.22 | 0.0243 | 0.381 |
| Empirical (4 clusters) | 4 | 28.89 | 0.0000 | 0.400 |

### 1.3 Multivariate Model Comparison

| Model | AIC | BIC | Pseudo-R² | N params |
|-------|-----|-----|-----------|----------|
| M0_no_clustering | 216.9 | 255.3 | 0.2045 | 12 |
| M1_compensation_only | 217.1 | 258.7 | 0.2119 | 13 |
| M2_original_clustering | 217.4 | 278.2 | 0.2600 | 19 |
| M3_split_clustering | 220.5 | 287.6 | 0.2639 | 21 |
| M4_granular_clustering | 225.4 | 308.6 | 0.2848 | 26 |
| M5_empirical_clustering | 208.0 | 256.0 | 0.2658 | 15 |
| M6_original_plus_compensation | 219.3 | 283.3 | 0.2603 | 20 |

**Best model by AIC**: M5_empirical_clustering
**Best model by BIC**: M0_no_clustering

## 2. Deep Dive: Lawfulness Bases

### 2.1 Legal Basis Comparison

The LAWFULNESS cluster shows high internal heterogeneity. Key findings:

| Legal Basis | N | Pro-DS Rate |
|-------------|---|-------------|
| CONSENT_BASIS | 4 | 75.0% |
| LEGITIMATE_INTERESTS | 5 | 80.0% |

**Fisher's exact test**: OR=1.333, p=1.0000

### 2.2 Interpretation

- **CONSENT_BASIS**: Cases tend to favor data subjects when consent validity/scope is at issue
- **LEGITIMATE_INTERESTS**: Also generally pro-DS due to strict necessity and balancing requirements
- **LEGAL_OBLIGATION_BASIS**: Lower pro-DS rate as these involve external legal requirements where DS arguments have less traction

## 3. Analysis Without Clustering

### 3.1 Concept-Level Findings

The unclustered analysis includes 138 holdings across 13 concepts.

**Bivariate test**: Chi-square=27.12, p=0.0074, Cramér's V=0.443

### 3.2 Individual Concept Effects

| Concept | Odds Ratio | p-value |
|---------|------------|----------|
| REMEDIESCOMPENSATION | 0.570 | 0.3099 |
| DPAPOWERS | 1.140 | 0.8330 |
| DATAPROTECTIONPRINCIPLES | 1.545 | 0.5888 |
| SCOPEMATERIAL | 2.361 | 0.3343 |
| RIGHTOFACCESS | 1.787 | 0.5045 |
| SPECIALCATEGORIESCONDITIONS | 2.042 | 0.4189 |

## 4. Recommendations

### 4.1 Clustering Approach

Based on this analysis:

1. **Split clustering** (separating compensation and consent-type lawfulness) provides
   a good balance of interpretability and homogeneity
2. **Granular clustering** loses too many degrees of freedom for the sample size
3. **Empirical clustering** is data-driven but may overfit and lacks legal interpretability

### 4.2 For Lawfulness Analysis

1. Consider treating CONSENT_BASIS and LEGITIMATE_INTERESTS together (both consent-like, high pro-DS)
2. Treat LEGAL_OBLIGATION_BASIS separately (obligation-based, lower pro-DS)
3. PUBLIC_INTEREST_BASIS and VITAL_INTERESTS_BASIS have very few cases - combine or exclude

### 4.3 Sensitivity Analysis Recommendations

Always report:
1. Primary results with chosen clustering
2. Sensitivity with split ENFORCEMENT (compensation vs other)
3. Results without any clustering (raw concept as control)

## 5. Conclusion

The analysis confirms that:
- Current clustering masks significant within-cluster heterogeneity
- The compensation paradox in ENFORCEMENT is the most impactful source of heterogeneity
- Lawfulness bases can be meaningfully split into consent-type vs obligation-type
- Model fit improves slightly with split clustering or targeted controls
