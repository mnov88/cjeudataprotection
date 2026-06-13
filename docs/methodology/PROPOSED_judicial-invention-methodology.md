# Methodology for Testing the "Judicial Invention" Hypothesis

## The Core Claim

> "The Court invents what the GDPR says despite it not being in the text, mostly to expand the rights."

This hypothesis asserts that the CJEU systematically derives obligations, rights, and rules from the GDPR that are **not explicitly present in the statutory text**, using interpretive mechanisms to justify conclusions that go beyond what the legislature enacted.

---

## 1. Operationalization: What Counts as "Invention"?

### 1.1 Defining Judicial Invention

**Judicial invention** occurs when a court's holding:
1. Asserts a legal rule as derived from a statutory provision
2. Where that rule is **not explicitly stated** in the provision's text
3. And the derivation requires **interpretive bridging** through principles, purposes, or external sources

### 1.2 Observable Indicators in the Dataset

| Indicator | Variable | Definition |
|-----------|----------|------------|
| **Level-Shifting** | `level_shifting` | Court shifts from rule/text to principle/objective to resolve ambiguity |
| **Teleological Dominance** | `dominant_source = TELEOLOGICAL` | Purposive interpretation drives the holding |
| **Purpose Invocation** | `pro_ds_purpose` | Invocation of "high level of protection" or "fundamental rights" |
| **Principle-Based Reasoning** | `principle_based_present` | Normative/balancing reasoning rather than deductive rule application |
| **Low Semantic Reliance** | `semantic_present = False` OR `dominant_source ≠ SEMANTIC` | Textual interpretation absent or not determinative |

### 1.3 Types of Invention (Qualitative Taxonomy)

Based on the coded decisions, invention manifests in several forms:

| Type | Description | Example |
|------|-------------|---------|
| **Charter Bootstrap** | Invoking Charter rights to override or supplement GDPR text | C-247/23: Surgery prohibition derived from "essence" of Articles 3 & 7 Charter |
| **Necessity Escalation** | Converting permissive language into strict necessity requirements | C-817/19: "Necessary and proportionate" becomes "strict necessity" with individualized risk assessment |
| **Obligation Creation** | Deriving affirmative duties not stated in the provision | C-65/23: Full judicial review obligation derived from primacy principle |
| **Scope Expansion** | Interpreting definitions more broadly than text supports | C-252/21: "Revealing" special categories includes indirect revelation through browsing |
| **Balancing Imposition** | Creating balancing requirements where text doesn't require them | C-579/21: Employee identity access requires "essentiality" balancing |

---

## 2. Hypotheses and Predictions

### H1: Invention Prevalence
**Claim**: A substantial proportion of CJEU GDPR holdings involve judicial invention.

**Prediction**: Level-shifting or teleological dominance occurs in >40% of holdings.

### H2: Invention-Outcome Association
**Claim**: Judicial invention is associated with pro-data subject outcomes.

**Predictions**:
- P(pro_DS | level_shifting = True) > P(pro_DS | level_shifting = False)
- P(pro_DS | dominant_source = TELEOLOGICAL) > P(pro_DS | dominant_source = SEMANTIC)
- P(pro_DS | pro_ds_purpose = True) > P(pro_DS | pro_ds_purpose = False)

### H3: Selective Invention
**Claim**: Invention is deployed selectively—more often when expanding rights than when restricting them.

**Predictions**:
- Level-shifting more common in pro-DS holdings than pro-controller holdings
- Teleological dominance more common when expanding scope/rights than when limiting remedies
- The Court uses semantic interpretation to justify pro-controller outcomes

### H4: Textual Constraint Bypassing
**Claim**: When the GDPR text would favor controllers, the Court bypasses it using invention.

**Prediction**: In cases where semantic interpretation is present but outcome is pro-DS, level-shifting or teleological override is also present.

### H5: Asymmetric Citation of Principles
**Claim**: "High level of protection" and "fundamental rights" are invoked to expand rights but not to restrict them.

**Prediction**:
- P(pro_ds_purpose | pro_DS) >> P(pro_ds_purpose | pro_controller)
- The purposes are not invoked symmetrically

---

## 3. Bivariate Analysis Plan

### 3.1 Invention Prevalence (H1)

**Test**: Compute proportion of holdings with invention indicators

```
Invention indicators:
1. level_shifting = True
2. dominant_source = TELEOLOGICAL
3. principle_based_present = True AND dominant_source ≠ RULE_BASED
4. pro_ds_purpose = True AND semantic_present = False

Composite measure: Any of (1)-(4) = "Invention Present"
```

**Expected Output**: Table showing invention prevalence overall and by concept cluster

### 3.2 Invention-Outcome Association (H2)

**Test A**: Chi-square for level_shifting × ruling_direction
```
           PRO_DS  PRO_CONTROLLER  MIXED  NEUTRAL
Shifting      ?          ?          ?       ?
No Shift      ?          ?          ?       ?
```

**Test B**: Chi-square for dominant_source × ruling_direction

**Test C**: Odds ratio for pro_ds_purpose predicting pro_DS outcome

**FDR Correction**: Benjamini-Hochberg at q < 0.05

### 3.3 Selective Invention (H3)

**Test**: Conditional probability comparison

```
P(level_shifting = True | ruling_direction = PRO_DS) vs.
P(level_shifting = True | ruling_direction = PRO_CONTROLLER)

If invention is selective: P(invention | pro_DS) >> P(invention | pro_controller)
```

**Visual**: Stacked bar chart of invention indicators by outcome direction

### 3.4 Text Bypassing (H4)

**Test**: Among holdings where semantic interpretation is present, does level-shifting predict pro-DS outcomes?

```
Subset: semantic_present = True
Within subset: χ²(level_shifting × pro_ds)
```

**Interpretation**: If significant, suggests level-shifting is used to override textual constraints

### 3.5 Purpose Invocation Asymmetry (H5)

**Test**: Compare purpose invocation rates across outcomes

```
Rate_pro_DS = P(pro_ds_purpose = True | ruling_direction = PRO_DS)
Rate_pro_Con = P(pro_ds_purpose = True | ruling_direction = PRO_CONTROLLER)

Asymmetry ratio = Rate_pro_DS / Rate_pro_Con
```

**Expected**: Strong asymmetry (ratio >> 1)

---

## 4. Multivariate Analysis Plan

### 4.1 Model 1: Invention Predicts Outcome

**Question**: Does invention predict pro-DS outcomes, controlling for case characteristics?

```
logit(P(pro_DS)) = β₀ + β₁·level_shifting + β₂·teleological_dominant +
                   β₃·pro_ds_purpose + β₄·concept_cluster + β₅·chamber + β₆·year + ε
```

**Key coefficient**: β₁, β₂, β₃ (invention indicators)
- If positive and significant: Invention associated with pro-DS outcomes

### 4.2 Model 2: Outcome Predicts Invention (Reverse Regression)

**Question**: Does the outcome predict whether invention was used, controlling for legal question type?

```
logit(P(level_shifting)) = β₀ + β₁·pro_DS + β₂·concept_cluster +
                           β₃·article_count + β₄·chamber + β₅·year + ε
```

**Key coefficient**: β₁
- If β₁ > 0 and significant: Invention is selectively used for pro-DS outcomes
- This is the critical test for **selective invention**

### 4.3 Model 3: Within-Cluster Analysis

**Question**: Within each concept cluster, does invention predict outcome?

```
For each cluster c:
    Within holdings where concept_cluster = c:
    logit(P(pro_DS)) = β₀ + β₁·level_shifting + β₂·pro_ds_purpose + ε
```

**Interpretation**:
- Consistent β₁ across clusters: Invention universally predicts pro-DS
- β₁ varies by cluster: Invention effects are context-dependent

### 4.4 Model 4: Interaction Effects

**Question**: Is invention more predictive of pro-DS outcomes in certain contexts?

```
logit(P(pro_DS)) = β₀ + β₁·level_shifting + β₂·concept_cluster +
                   β₃·(level_shifting × concept_cluster) + controls + ε
```

**Interpretation**: Significant β₃ indicates invention has different effects across legal domains

---

## 5. Advanced Analyses

### 5.1 Text-Holding Divergence Score

**Concept**: Quantify how far each holding diverges from what the cited text explicitly states.

**Construction** (requires additional coding):

For each holding, expert coders assess:
1. **Textual Support Score (1-5)**: How directly does the cited provision support the holding?
   - 5 = Holding is explicit restatement of text
   - 4 = Holding follows logically from text
   - 3 = Holding requires reasonable inference
   - 2 = Holding requires significant interpretive extension
   - 1 = Holding cannot be derived from text alone

2. **Interpretive Gap Score (1-5)**: How much interpretive work bridges text to holding?
   - 5 = No gap (text → holding is direct)
   - 1 = Large gap (major principles/purposes invoked)

**Composite**: Divergence Score = 6 - Textual Support Score (so higher = more invention)

### 5.2 Textual Analysis: Automated Text Comparison

**Method**: Compare GDPR article text to holding text using NLP

```
1. Extract cited_article_text (actual GDPR provision text)
2. Extract core_holding text
3. Compute semantic similarity (embedding distance)
4. Identify novel concepts in holding not in article text
```

**Metrics**:
- **Semantic distance**: Low similarity = greater divergence
- **Novel term count**: Terms in holding not in article
- **Obligation expansion**: Count new obligations/rights mentioned

### 5.3 Citation Pattern Analysis

**Question**: Does the Court cite external sources (Charter, general principles) more when inventing?

```
Examine cited_cases and provisions_cited:
- Proportion citing Charter
- Proportion citing general EU law principles
- Proportion citing only GDPR text

Compare by level_shifting and ruling_direction
```

**Prediction**: Invention holdings cite Charter/principles more; non-invention cite GDPR text more

### 5.4 Advocate General Comparison

**Question**: Do AGs propose invention that the Court then adopts, or does the Court invent beyond AG opinions?

```
1. Code AG opinion interpretive method (if available)
2. Compare Court method to AG method
3. Identify cases where Court invents beyond AG recommendation
```

### 5.5 Temporal Evolution of Invention

**Question**: Is the Court inventing more over time?

```
Compute: Annual rate of level_shifting
Test: Cochran-Armitage trend test for increasing invention over time
Model: logit(P(level_shifting)) = β₀ + β₁·year + controls
```

---

## 6. Robustness Checks

### 6.1 Alternative Invention Definitions

| Definition | Variables |
|------------|-----------|
| Narrow | level_shifting = True only |
| Moderate | level_shifting = True OR dominant_source = TELEOLOGICAL |
| Broad | Any non-semantic dominance with principle_based reasoning |

Re-run all analyses under each definition.

### 6.2 Placebo Test

**Logic**: If invention is strategic (not inherent to legal questions), then randomly permuting outcomes should eliminate the invention-outcome association.

```
For b = 1 to 10,000:
    Permute ruling_direction labels
    Compute χ²(level_shifting × ruling_direction)
Compare observed χ² to permutation distribution
```

### 6.3 Concept-Cluster Fixed Effects

**Logic**: Control for the possibility that certain legal questions inherently require more invention.

```
Include concept_cluster dummies in all models
Compare: Does invention effect survive?
```

### 6.4 Excluding Obvious Cases

Remove holdings where:
- Outcome is NEUTRAL_OR_UNCLEAR (no direction to explain)
- The question is purely procedural
- The concept is definitional (may inherently require interpretation)

Re-run analyses on "substantive" holdings only.

---

## 7. Interpretation Framework

### 7.1 Evidence Thresholds

| Finding | Evidence FOR "Judicial Invention" |
|---------|----------------------------------|
| Level-shifting rate > 40% | Invention is prevalent |
| OR(pro_DS \| level_shifting) > 2.0 | Invention predicts pro-DS |
| β₁ > 0 in reverse regression (Model 2) | Invention is selectively deployed |
| Purpose asymmetry ratio > 3.0 | "High protection" invoked one-directionally |
| Text-holding divergence correlates with pro-DS | Invention expands rights |

### 7.2 Alternative Explanations to Address

| Alternative | How to Test |
|-------------|-------------|
| "Some questions inherently require teleology" | Within-cluster analysis |
| "GDPR is written to favor DS, Court just applies it" | Compare semantic-dominant outcomes to teleological-dominant |
| "Level-shifting reflects legal complexity, not strategy" | Test association with paragraph_count, article_count |
| "Coder bias toward labeling pro-DS as invention" | Blind re-coding of subset |

### 7.3 What This Analysis Cannot Prove

1. **Intent**: We cannot prove the Court consciously invents to expand rights
2. **Normative wrongness**: Statistical patterns don't mean the Court is wrong
3. **Causation**: We observe correlation between invention and outcome
4. **Alternatives**: We cannot know what a "textually faithful" court would have held

---

## 8. Data Requirements

### 8.1 Existing Variables (No New Coding)

From `holdings.csv`:
- `level_shifting` (Boolean)
- `dominant_source` (SEMANTIC | SYSTEMATIC | TELEOLOGICAL | UNCLEAR)
- `semantic_present`, `systematic_present`, `teleological_present` (Boolean)
- `teleological_purposes` (list)
- `pro_ds_purpose` (derived: TRUE if HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS)
- `principle_based_present` (Boolean)
- `ruling_direction` (PRO_DATA_SUBJECT | PRO_CONTROLLER | MIXED | NEUTRAL_OR_UNCLEAR)
- `concept_cluster`, `primary_concept`
- `provisions_cited`, `article_numbers`
- `core_holding`
- `chamber`, `judgment_date`

### 8.2 Variables to Derive

| Variable | Construction |
|----------|--------------|
| `pro_ds` | Binary: 1 if ruling_direction = PRO_DATA_SUBJECT |
| `invention_narrow` | Binary: level_shifting = True |
| `invention_moderate` | Binary: level_shifting = True OR dominant_source = TELEOLOGICAL |
| `invention_broad` | Binary: Any invention indicator |
| `purpose_invoked` | Binary: pro_ds_purpose = True |
| `year` | Extracted from judgment_date |
| `article_count` | Count of articles in article_numbers |

### 8.3 Additional Coding Needed (Optional)

For deeper analysis:
- **Textual Support Score (1-5)**: Expert assessment of text-holding fit
- **AG opinion method**: Interpretive approach in Advocate General opinion
- **Actual GDPR article text**: For NLP comparison

---

## 9. Expected Findings (Based on Preliminary Data)

### 9.1 Known Results from Existing Analysis

| Variable | Rate / Effect |
|----------|---------------|
| Pro-DS overall rate | 60.8% |
| pro_ds_purpose → pro_DS | OR ≈ 4.5, p < 0.001 |
| SCOPE cluster pro-DS rate | 88.2% |
| ENFORCEMENT cluster pro-DS rate | 46.2% |
| Level-shifting pro-DS rate (bivariate) | ~82% (marginally significant) |

### 9.2 Predicted New Findings

| Hypothesis | Predicted Result |
|------------|------------------|
| H1 (Prevalence) | 40-50% of holdings show invention indicators |
| H2 (Association) | Strong: OR > 3 for level_shifting → pro_DS |
| H3 (Selectivity) | P(invention \| pro_DS) ≈ 2× P(invention \| pro_controller) |
| H4 (Bypassing) | Among semantic-present holdings, level-shifting strongly predicts pro-DS |
| H5 (Asymmetry) | Purpose invocation ratio > 5:1 (pro_DS vs. pro_controller) |

---

## 10. Presentation of Results

### 10.1 Main Table: Invention Indicators by Outcome

| Invention Indicator | PRO_DS (N=110) | PRO_CONTROLLER (N=23) | PRO_DS Rate | OR (95% CI) | p |
|--------------------|----|----|----|----|----|
| Level-shifting = True | ? | ? | ? | ? | ? |
| Dominant = TELEOLOGICAL | ? | ? | ? | ? | ? |
| pro_ds_purpose = True | ? | ? | ? | ? | ? |
| Principle-based present | ? | ? | ? | ? | ? |
| Any invention indicator | ? | ? | ? | ? | ? |

### 10.2 Key Figure: Invention Selectivity

```
[Stacked bar chart]
X-axis: Ruling Direction (PRO_DS, MIXED, PRO_CONTROLLER, NEUTRAL)
Y-axis: Proportion
Colors: Invention Present (dark) vs. Invention Absent (light)
```

### 10.3 Regression Table

| Model | β(level_shifting) | β(pro_ds_purpose) | Pseudo-R² |
|-------|-------------------|-------------------|-----------|
| Bivariate | ? | ? | ? |
| + Concept cluster | ? | ? | ? |
| + Chamber + Year | ? | ? | ? |
| + Interactions | ? | ? | ? |

---

## 11. Limitations

1. **Circular Coding Risk**: `level_shifting` may be coded based on outcome direction
2. **Single Coder**: No inter-rater reliability for subjective judgments
3. **Small N for Some Cells**: PRO_CONTROLLER only 23 holdings
4. **Cannot Measure True Textual Meaning**: Legal interpretation is inherently contested
5. **Observational Design**: Cannot prove causation or intent

---

## 12. Conclusion

This methodology provides a rigorous framework for testing whether the CJEU systematically "invents" GDPR meaning not found in the text, and whether this invention serves to expand data subject rights. The key insight is that **selective deployment** of invention—using teleological/principle-based reasoning more when expanding rights than when restricting them—is the strongest evidence for strategic judicial invention.

The combination of bivariate tests (invention-outcome association), reverse regression (outcome predicting invention), within-cluster analysis (controlling for legal question type), and asymmetry analysis (one-directional purpose invocation) will provide robust evidence to evaluate the hypothesis.

---

## Appendix: Python Analysis Script Outline

```python
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

# Load data
df = pd.read_csv('parsed-coded/holdings.csv')

# Derive variables
df['pro_ds'] = (df['ruling_direction'] == 'PRO_DATA_SUBJECT').astype(int)
df['year'] = pd.to_datetime(df['judgment_date']).dt.year
df['tele_dominant'] = (df['dominant_source'] == 'TELEOLOGICAL').astype(int)
df['invention_narrow'] = df['level_shifting'].astype(int)
df['invention_moderate'] = ((df['level_shifting']) | (df['dominant_source'] == 'TELEOLOGICAL')).astype(int)

# H1: Prevalence
print("=== H1: Invention Prevalence ===")
print(f"Level-shifting rate: {df['level_shifting'].mean():.1%}")
print(f"Teleological dominant rate: {df['tele_dominant'].mean():.1%}")

# H2: Invention-Outcome Association
print("\n=== H2: Invention-Outcome Association ===")
ct = pd.crosstab(df['level_shifting'], df['pro_ds'])
chi2, p, dof, expected = chi2_contingency(ct)
print(f"Level-shifting × Pro-DS: χ² = {chi2:.2f}, p = {p:.4f}")

# H3: Selective Invention (Reverse Regression)
print("\n=== H3: Reverse Regression ===")
X = df[['pro_ds', 'tele_dominant', 'year']].copy()
X = sm.add_constant(X)
y = df['level_shifting']
model = sm.Logit(y, X).fit(disp=0)
print(model.summary2().tables[1])

# H5: Purpose Asymmetry
print("\n=== H5: Purpose Invocation Asymmetry ===")
rate_prods = df[df['pro_ds']==1]['pro_ds_purpose'].mean()
rate_procon = df[df['ruling_direction']=='PRO_CONTROLLER']['pro_ds_purpose'].mean()
print(f"Purpose rate when pro-DS: {rate_prods:.1%}")
print(f"Purpose rate when pro-controller: {rate_procon:.1%}")
print(f"Asymmetry ratio: {rate_prods/rate_procon:.1f}x")
```

---

*Document Version: 2.0 (Refined for Judicial Invention Hypothesis)*
*Date: January 2026*
