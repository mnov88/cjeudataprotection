# Methodology for Testing the "Judicial Opportunism" Hypothesis in CJEU GDPR Jurisprudence

## Executive Summary

This document proposes a rigorous empirical methodology to test the hypothesis that "the Court is making decisions inconsistently, primarily to expand data subject rights" (colloquially: "making shit up as it goes along, mostly to expand the rights"). This hypothesis contains two distinct empirical claims requiring separate operationalization and testing:

1. **Methodological Opportunism (H1)**: The Court selects interpretive methods and reasoning structures based on desired outcomes rather than applying methods consistently
2. **Systematic Pro-Rights Expansion (H2)**: This opportunism systematically favors data subjects over controllers

Testing these claims requires moving beyond the existing correlational analyses to designs that can identify (a) outcome-dependent method selection, (b) inconsistency across similar cases, and (c) asymmetric reasoning patterns.

---

## 1. Operationalization of the Hypothesis

### 1.1 Component 1: "Making Shit Up" (Methodological Opportunism)

**Theoretical Concept**: The Court does not apply a consistent interpretive methodology but rather selects methods opportunistically to justify predetermined conclusions.

**Observable Implications**:

| Implication | Operationalization | Data Source |
|-------------|-------------------|-------------|
| **O1.1**: Method selection depends on outcome | Interpretive method distribution differs by ruling direction, *controlling for legal question type* | Holdings data |
| **O1.2**: Similar cases receive different treatment | Cases with similar legal questions/facts have different methods leading to different outcomes | Case pairs analysis |
| **O1.3**: Reasoning follows conclusions | Citations, purposes, and arguments show patterns consistent with motivated reasoning | Citation network + text analysis |
| **O1.4**: Temporal inconsistency | The Court's position on the same question changes over time without explicit acknowledgment | Temporal citation analysis |
| **O1.5**: Level-shifting is strategic | Level-shifting from text to principles occurs selectively when textual interpretation would disfavor the preferred outcome | Holdings data |

### 1.2 Component 2: "Mostly to Expand the Rights" (Pro-DS Bias)

**Theoretical Concept**: The opportunism operates asymmetrically, systematically favoring expansion of data subject rights.

**Observable Implications**:

| Implication | Operationalization | Data Source |
|-------------|-------------------|-------------|
| **O2.1**: Baseline pro-DS rate exceeds neutral expectation | Pro-DS rate significantly > 50% | Holdings data |
| **O2.2**: Pro-DS outcomes use "expansive" methods | When ruling pro-DS, Court uses teleological/purposive methods; when ruling pro-controller, Court uses textual/systematic methods | Holdings data |
| **O2.3**: Asymmetric invocation of purposes | "High level of protection" invoked when expanding rights, not when restricting them | Holdings data |
| **O2.4**: Scope expands, remedies contract | Court is pro-DS on who is protected (scope), but pro-controller on how much they can recover (remedies) | Concept cluster analysis |
| **O2.5**: Precedent is selectively followed | Pro-DS precedents are followed more consistently than pro-controller precedents | Citation network |

---

## 2. Bivariate Analysis Framework

### 2.1 Test Suite for Methodological Opportunism (H1)

#### Test 1.1: Outcome-Dependent Method Selection

**Research Question**: Does the distribution of interpretive methods differ by outcome *more than would be expected* based on the legal question type?

**Design**: Stratified chi-square analysis

```
For each concept_cluster c:
    Compute: χ²(dominant_source | ruling_direction) within cluster c

Compare: Observed χ² vs. null distribution from permutation test
```

**Rationale**: If methods are applied consistently, then within a given type of legal question (e.g., SCOPE cases, RIGHTS cases), the method-outcome association should be weak. Strong within-cluster associations suggest method selection depends on desired outcome.

**Statistical Test**:
- Within-cluster chi-square tests with FDR correction
- Cochran-Mantel-Haenszel test for conditional independence
- Breslow-Day test for homogeneity of odds ratios across clusters

#### Test 1.2: Case Similarity Analysis

**Research Question**: Do cases addressing similar legal questions with similar facts reach consistent outcomes using consistent methods?

**Design**: Matched case-pair analysis

```
1. Identify case pairs with high similarity (same primary_concept, same article_numbers)
2. For each pair, compute:
   - method_concordance: Same dominant_source?
   - outcome_concordance: Same ruling_direction?
3. Test: Is method_concordance associated with outcome_concordance?
```

**Rationale**: If methods determine outcomes, methodologically similar cases should have similar outcomes. If outcomes determine methods, outcome-discordant pairs should also be method-discordant (different methods used to justify different outcomes).

**Statistical Test**:
- McNemar's test for paired data
- Cohen's kappa for method-outcome agreement
- Logistic regression: P(outcome_concordance) ~ method_concordance

#### Test 1.3: Reversal Detection

**Research Question**: Are there instances where the Court reverses position on a legal question, and do such reversals involve methodological shifts?

**Design**: Temporal precedent analysis

```
1. Identify question-outcome pairs (legal question → outcome)
2. Track each question over time
3. Flag "reversals": Same question, different outcome direction
4. Analyze: Do reversals correlate with method changes?
```

**Statistical Test**:
- Descriptive: Number and proportion of reversals
- Fisher's exact: Association between reversal and method change
- Survival analysis: Time to reversal by initial method

#### Test 1.4: Level-Shifting Strategic Use

**Research Question**: Does level-shifting occur selectively when textual interpretation would disfavor the outcome?

**Design**: Conditional probability analysis

```
Define:
- text_favors_DS: Would strict textual interpretation favor data subject?
- level_shifting: Movement from text to principles occurred
- pro_ds: Outcome favors data subject

Test: P(level_shifting | text_favors_DS=0, pro_ds=1) > P(level_shifting | text_favors_DS=1, pro_ds=1)
```

**Challenge**: `text_favors_DS` requires subjective coding. Alternative: Use cases where semantic interpretation is explicitly present but not dominant.

**Statistical Test**:
- Conditional chi-square
- Logistic regression with interaction: level_shifting ~ pro_ds * semantic_present

### 2.2 Test Suite for Pro-Rights Expansion (H2)

#### Test 2.1: Baseline Pro-DS Rate

**Research Question**: Is the pro-DS rate significantly different from 50%?

**Design**: One-sample proportion test

```
H0: π(pro_ds) = 0.50
Ha: π(pro_ds) > 0.50
```

**Statistical Test**:
- Binomial test
- Cluster-adjusted CI using case-level bootstrap

**Known Result**: Pro-DS rate = 60.8% (110/181). The question is whether this significantly exceeds 50% after accounting for clustering.

#### Test 2.2: Asymmetric Method-Outcome Association

**Research Question**: Is the association between teleological interpretation and pro-DS outcomes stronger than the association between semantic interpretation and pro-controller outcomes?

**Design**: Asymmetry test

```
Compute:
- OR_tele_proDS: Odds ratio for teleological → pro_DS
- OR_sem_proCon: Odds ratio for semantic → pro_controller

Test: OR_tele_proDS vs. OR_sem_proCon (are these symmetric?)
```

**Statistical Test**:
- Bootstrap comparison of odds ratios
- Interaction test in logistic regression

#### Test 2.3: Purpose Invocation Asymmetry

**Research Question**: Is "high level of protection" invoked selectively for rights-expanding decisions?

**Design**: Conditional probability comparison

```
P(pro_ds_purpose | pro_ds=1) vs. P(pro_ds_purpose | pro_ds=0)

If symmetric: These should be comparable
If asymmetric: pro_ds_purpose is invoked selectively for pro-DS outcomes
```

**Statistical Test**:
- Chi-square test
- Odds ratio with 95% CI
- NNT (number needed to treat) interpretation

**Known Result**: 69.6% pro-DS when purpose invoked vs. 32.6% when not. This is a 37pp gap (φ = 0.309, p < 0.001).

#### Test 2.4: Scope-Remedies Divergence

**Research Question**: Does the Court expand scope/rights definitions while restricting enforcement/remedies?

**Design**: Cluster comparison

```
Compare pro-DS rates:
- SCOPE cluster vs. ENFORCEMENT cluster
- RIGHTS cluster vs. ENFORCEMENT cluster
```

**Statistical Test**:
- Chi-square tests for cluster pairs
- Logistic regression with cluster as predictor
- Post-hoc pairwise comparisons with Tukey adjustment

**Known Results**: SCOPE (88.2%), RIGHTS (81.0%) vs. ENFORCEMENT (46.2%). This supports O2.4.

---

## 3. Multivariate Analysis Framework

### 3.1 Core Models

#### Model A: Outcome-Dependent Method Selection (Testing H1)

**Question**: Does ruling direction predict interpretive method, controlling for case characteristics?

**Design**: Reverse regression (outcome → method)

```
For Method M ∈ {TELEOLOGICAL, SYSTEMATIC, SEMANTIC}:
    P(dominant_source = M) = logit⁻¹(β₀ + β₁·pro_ds + β₂·concept_cluster +
                                      β₃·year + β₄·chamber + β₅·article_count)
```

**Interpretation**:
- If β₁ ≠ 0 after controlling for case characteristics, method selection depends on outcome
- This is evidence for methodological opportunism

**Important Caveat**: This cannot establish causation (outcome → method). It tests whether method and outcome are associated *beyond what case characteristics predict*.

#### Model B: Method-Mediated Outcome Determination (Path Analysis)

**Question**: Do methods mediate the effect of case characteristics on outcomes?

**Design**: Structural equation model

```
Path 1 (Direct): case_characteristics → ruling_direction
Path 2 (Indirect): case_characteristics → method → ruling_direction

Test: Does including method as mediator reduce direct path coefficient?
```

**Implementation**: Baron-Kenny mediation analysis with bootstrap CIs

#### Model C: Consistency Index Construction

**Question**: Can we quantify the Court's consistency in applying methods?

**Design**: Within-cluster prediction model

```
1. Within each concept_cluster, fit:
   P(pro_ds) ~ dominant_source + reasoning_structure + level_shifting

2. Compute residual variance: How much outcome variation remains unexplained by methods?

3. Consistency Index = 1 - (residual variance / total variance)
```

**Interpretation**: High consistency index suggests methods predict outcomes consistently. Low index suggests outcomes vary independently of stated methods.

### 3.2 Advanced Interaction Models

#### Model D: Asymmetry Test

**Question**: Is the method-outcome relationship asymmetric (stronger for pro-DS)?

```
pro_ds ~ dominant_source * direction_expected + concept_cluster + year + chamber

where direction_expected = 1 if case type typically favors DS, 0 otherwise
```

**Interpretation**: Significant interaction indicates different method-outcome relationships depending on expected direction.

#### Model E: Temporal Evolution of Opportunism

**Question**: Has methodological opportunism increased or decreased over time?

```
pro_ds ~ dominant_source * year + concept_cluster + chamber
```

**Interpretation**: Significant interaction indicates the strength of method-outcome association changes over time.

---

## 4. Advanced Statistical Methods

### 4.1 Instrumental Variables Analysis

**Goal**: Address endogeneity in method-outcome relationship

**Challenge**: Method selection may be endogenous—courts may choose methods based on anticipated outcomes.

**Potential Instruments**:
1. **Advocate General opinion method**: AG's interpretive approach may predict Court's method but not directly cause outcome
2. **Referring court's suggested interpretation**: May influence method but not directly determine outcome
3. **Prior Chamber method preferences**: Chamber's historical method preferences

**Two-Stage Least Squares**:
```
Stage 1: dominant_source ~ AG_method + referring_court_suggestion + chamber_priors
Stage 2: pro_ds ~ dominant_source_hat + concept_cluster + year
```

**Validity Tests**: Sargan/Hansen test for overidentification; weak instrument tests

### 4.2 Latent Class Analysis

**Goal**: Identify unobserved "types" of judicial decision-making

**Model**:
```
Assume K latent classes of holdings
Within each class k:
    P(pro_ds | class=k) = πk
    P(dominant_source | class=k) = λk
    P(level_shifting | class=k) = γk
```

**Interpretation**:
- Class 1: "Principled textualism" (high semantic, consistent outcomes)
- Class 2: "Strategic purposivism" (high teleological, pro-DS outcomes)
- Class 3: "Remedial restraint" (mixed methods, pro-controller outcomes)

**Model Selection**: BIC, entropy, Lo-Mendell-Rubin test

### 4.3 Network-Based Consistency Analysis

**Goal**: Test whether citations are used consistently or selectively

**Method**:
```
1. For each cited precedent P, determine:
   - P's method (M_P) and outcome (O_P)
   - Citing case's method (M_C) and outcome (O_C)

2. Compute concordance rates:
   - method_concordance: P(M_C = M_P)
   - outcome_concordance: P(O_C = O_P)

3. Test: Is outcome_concordance > method_concordance?
   (i.e., does Court cite based on outcomes rather than methods?)
```

**Statistical Test**: McNemar's test for paired proportions

### 4.4 Causal Discovery Analysis

**Goal**: Infer causal structure from observational data

**Method**: PC Algorithm / FCI Algorithm

```
Variables: {concept_cluster, dominant_source, level_shifting, pro_ds_purpose,
            chamber, year, ruling_direction}

Algorithm discovers directed acyclic graph (DAG) from conditional independencies
```

**Output**: Inferred causal graph showing which variables cause others

**Limitation**: Assumes causal sufficiency and faithfulness

---

## 5. Robustness and Sensitivity Analyses

### 5.1 Alternative Outcome Definitions

1. **Trichotomous outcome**: PRO_DS / MIXED / PRO_CONTROLLER (multinomial logit)
2. **Strength-weighted outcome**: Code degree of pro-DS orientation (ordinal logit)
3. **Excluding NEUTRAL**: Remove neutral/unclear holdings

### 5.2 Alternative Unit of Analysis

1. **Case-level**: Aggregate holdings to case majority
2. **Article-level**: Disaggregate by GDPR article addressed
3. **Paragraph-level**: Unit is reasoning paragraph (if coded)

### 5.3 Subset Analyses

1. **By time period**: Pre-2023 vs. post-2023
2. **By concept cluster**: Separate analyses for each cluster
3. **By chamber**: Grand Chamber vs. numbered chambers
4. **Excluding compensation**: Remove Article 82 holdings

### 5.4 Permutation Tests

```
For each test statistic T:
1. Compute observed T_obs
2. For b = 1 to B (e.g., 10,000):
   - Randomly permute ruling_direction labels
   - Compute T_b
3. p-value = (1 + Σ I(|T_b| ≥ |T_obs|)) / (B + 1)
```

### 5.5 Leave-One-Out Sensitivity

For each case c:
1. Exclude case c
2. Re-estimate models
3. Check: Do conclusions change?

---

## 6. Addressing Potential Confounds

### 6.1 Case Selection Effects

**Problem**: Cases reaching the CJEU are non-random; difficult cases may be systematically different.

**Mitigation**:
- Control for case complexity (paragraph_count, article_count)
- Stratify by referral type (if available)
- Discuss limitations explicitly

### 6.2 Coder Subjectivity

**Problem**: Single-coder design introduces potential bias in classification.

**Mitigation**:
- Sensitivity analysis with alternative coding rules
- Publish codebook for replication
- Report marginal cases explicitly

### 6.3 Temporal Confounding

**Problem**: Both methods and outcomes may evolve over time due to external factors.

**Mitigation**:
- Include year fixed effects
- Test for structural breaks
- Control for legal context changes (e.g., new Advocate Generals)

### 6.4 Legal Domain Confounding

**Problem**: Different legal questions may inherently call for different methods.

**Mitigation**:
- Control for concept_cluster
- Within-cluster analyses
- Cochran-Mantel-Haenszel stratified tests

---

## 7. Implementation Plan

### Phase 1: Data Preparation (Week 1)

1. **Variable Construction**
   - Create `text_favors_DS` variable (requires legal expertise)
   - Create case similarity matrix
   - Create reversal indicators for temporal analysis

2. **Data Quality Checks**
   - Verify coding consistency
   - Check for missing data patterns
   - Identify influential observations

### Phase 2: Bivariate Analysis (Week 2)

3. **H1 Bivariate Tests**
   - Test 1.1: Within-cluster method-outcome associations
   - Test 1.2: Matched case pair analysis
   - Test 1.3: Reversal detection
   - Test 1.4: Level-shifting conditional analysis

4. **H2 Bivariate Tests**
   - Test 2.1: Pro-DS rate vs. 50%
   - Test 2.2: Method-outcome asymmetry
   - Test 2.3: Purpose invocation asymmetry
   - Test 2.4: Scope-remedies divergence

### Phase 3: Multivariate Analysis (Week 3)

5. **Core Regression Models**
   - Model A: Reverse regression (outcome → method)
   - Model B: Mediation analysis
   - Model C: Consistency index

6. **Interaction Models**
   - Model D: Asymmetry test
   - Model E: Temporal evolution

### Phase 4: Advanced Methods (Week 4)

7. **Instrumental Variables**
   - Identify and validate instruments
   - 2SLS estimation

8. **Latent Class Analysis**
   - Model selection (2-5 classes)
   - Class interpretation

9. **Network Analysis**
   - Citation concordance analysis
   - Selective citation tests

### Phase 5: Robustness & Synthesis (Week 5)

10. **Sensitivity Analyses**
    - Alternative definitions
    - Alternative units
    - Subset analyses
    - Permutation tests

11. **Synthesis**
    - Integration of findings
    - Causal interpretation discussion
    - Limitations and caveats

---

## 8. Interpretation Framework

### 8.1 Evidence Standards

| Strength | Criteria |
|----------|----------|
| **Strong Evidence FOR H1** | Multiple bivariate tests significant + Model A shows β₁ ≠ 0 + Latent classes show strategic patterns |
| **Moderate Evidence FOR H1** | Some bivariate tests significant + Model A suggestive + Some consistency in advanced analyses |
| **Weak/No Evidence FOR H1** | Bivariate tests non-significant + Model A shows β₁ ≈ 0 + Methods predict outcomes consistently |
| **Strong Evidence FOR H2** | Pro-DS rate significantly > 50% + Asymmetric method use + Scope/remedies divergence confirmed |
| **Moderate Evidence FOR H2** | Pro-DS rate > 50% + Some asymmetry + Some divergence |
| **Weak/No Evidence FOR H2** | Pro-DS rate ≈ 50% + Symmetric patterns + No divergence |

### 8.2 Alternative Explanations to Address

1. **Legitimate Legal Reasoning**: Methods may be appropriately matched to questions
2. **Inherent Pro-DS Bias in GDPR**: The regulation itself may be pro-DS
3. **Selection Effects**: Only certain types of cases reach the CJEU
4. **Coding Artifacts**: Apparent patterns may reflect coder interpretation
5. **Small Sample Issues**: N=181 may be insufficient for complex models

### 8.3 What Cannot Be Concluded

- **Causation**: Observational data cannot establish whether methods *cause* outcomes
- **Intentionality**: We cannot determine whether opportunism (if found) is conscious or unconscious
- **Normative Assessment**: Statistical patterns do not imply the Court is acting improperly

---

## 9. Expected Findings Based on Existing Data

### 9.1 Preliminary Indicators (from existing analyses)

| Observable | Existing Evidence | Implication |
|------------|-------------------|-------------|
| Pro-DS rate | 60.8% | Supports O2.1 (above 50%) |
| Purpose-outcome association | OR = 4.49, p < 0.001 | Strong purpose invocation asymmetry |
| Scope vs. Enforcement | 88.2% vs. 46.2% | Supports O2.4 (scope-remedies divergence) |
| Level-shifting | p = 0.054 bivariate, NS multivariate | Unclear support for O1.5 |
| Third Chamber effect | 34.1% vs. 77.6% (Grand) | Institutional variation exists |

### 9.2 Key Unknowns Requiring New Analysis

1. **Within-cluster method-outcome associations** (Test 1.1)
2. **Case similarity analysis** (Test 1.2)
3. **Reversal detection** (Test 1.3)
4. **Reverse regression coefficients** (Model A)
5. **Latent class structure** (LCA)
6. **Citation selectivity** (Network analysis)

---

## 10. Limitations and Caveats

### 10.1 Fundamental Limitations

1. **Observational Design**: Cannot establish causation
2. **Single Coder**: No inter-rater reliability assessment
3. **Small N**: 181 holdings, 67 cases limits power for complex models
4. **Sparse Cells**: Some method-outcome combinations rare
5. **Non-Representative**: CJEU cases are non-random sample of disputes

### 10.2 Interpretive Cautions

1. Finding an association between methods and outcomes does not prove opportunism
2. Legal reasoning may legitimately select methods appropriate to the question
3. "Pro-DS" does not equal "legally incorrect"
4. Statistical patterns may not reflect judicial intent

### 10.3 Generalizability Concerns

1. Results specific to GDPR jurisprudence 2019-2025
2. May not generalize to other legal domains
3. May not reflect future CJEU behavior

---

## 11. Conclusion

This methodology provides a rigorous framework for testing whether the CJEU's GDPR jurisprudence exhibits methodological opportunism in service of rights expansion. By combining bivariate tests, multivariate regression, and advanced statistical methods, we can systematically examine the evidence for each component of the hypothesis.

The key insight is that testing "making shit up" requires examining *consistency*—whether similar cases receive similar treatment—rather than simply whether methods correlate with outcomes. The existing strong correlation between protective purpose invocation and pro-DS outcomes is consistent with opportunism but also with legitimate purposive interpretation.

The proposed analysis framework will generate evidence to evaluate both components of the hypothesis with appropriate statistical rigor while acknowledging the fundamental limitations of observational legal empirical research.

---

## Appendix A: Variable Definitions for New Analyses

### A.1 Variables to Construct

| Variable | Definition | Construction Method |
|----------|------------|---------------------|
| `text_favors_DS` | Would strict textual interpretation favor DS? | Expert legal coding |
| `case_similarity` | Similarity score between case pairs | Jaccard index on concept + article |
| `is_reversal` | Does this holding reverse prior position? | Temporal comparison within concept |
| `method_concordance` | Does method match cited precedent's method? | Citation network analysis |
| `outcome_concordance` | Does outcome match cited precedent's outcome? | Citation network analysis |
| `consistency_residual` | Unexplained variation after method controls | Model residuals |

### A.2 Existing Variables to Use

From `holdings.csv`:
- `ruling_direction`, `pro_ds` (derived)
- `dominant_source`, `dominant_structure`
- `teleological_present`, `pro_ds_purpose`
- `level_shifting`
- `concept_cluster`, `primary_concept`
- `chamber`, `year`
- `cited_cases`, `cited_case_count`

---

## Appendix B: Statistical Power Considerations

### B.1 Detectable Effect Sizes

With N=181, α=0.05, power=0.80:

| Test | Detectable Effect |
|------|-------------------|
| Chi-square (2×2) | φ = 0.21 (medium) |
| Chi-square (4×2) | V = 0.24 (medium) |
| Logistic OR | OR = 2.1 |
| Correlation | r = 0.21 |

### B.2 Implications

- Can detect medium effects
- May miss small but meaningful associations
- Complex models (many predictors) may be underpowered
- Some cell combinations will be sparse

---

## Appendix C: Python Implementation Outline

```python
# Key analyses to implement

# 1. Within-cluster method-outcome test (CMH test)
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import StratifiedTable

# 2. Matched case pair analysis
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import mcnemar

# 3. Reverse regression
import statsmodels.api as sm
# P(method | outcome, controls)

# 4. Mediation analysis
from pingouin import mediation_analysis

# 5. Latent Class Analysis
# Use R's poLCA via rpy2, or Python's lca package

# 6. Permutation tests
from scipy.stats import permutation_test

# 7. Network concordance analysis
import networkx as nx
```

---

*Document Version: 1.0*
*Date: January 2026*
*Authors: Empirical Legal Research Team*
