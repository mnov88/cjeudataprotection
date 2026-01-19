# Factors Associated with Pro-Data Subject Rulings in CJEU GDPR Jurisprudence: An Empirical Analysis of Interpretive Methods, Institutional Factors, and the Compensation Gap

---

## Abstract

This study presents the first comprehensive empirical analysis of factors associated with pro-data subject versus pro-controller outcomes in Court of Justice of the European Union (CJEU) decisions interpreting the General Data Protection Regulation (GDPR). Analyzing 181 holdings from 67 cases decided between 2019 and 2025, we employ bivariate tests with false discovery rate correction and mixed-effects logistic regression to identify robust correlates of ruling direction. Our findings reveal that 60.8% of holdings favor data subjects, but this aggregate figure masks significant heterogeneity. Invocation of the teleological purposes "high level of protection" or "fundamental rights" is associated with a 3.89-fold increase in the odds of a pro-data subject ruling (p=0.008), while the Third Chamber rules pro-data subject in only 34.1% of cases compared to 77.6% in the Grand Chamber—though this difference attenuates after controlling for temporal factors. Most strikingly, we document a "compensation gap": Article 82 damages cases are 30.8 percentage points less likely to favor data subjects than other GDPR questions, even when the Court invokes protective purposes. This remedies gap, associated with the Court's insistence that "actual damage" must be proven beyond mere infringement, has significant implications for the effectiveness of GDPR enforcement.

**Keywords:** GDPR, CJEU, empirical legal studies, data protection, judicial interpretation, compensation, Article 82, remedies gap

---

## 1. Introduction

### 1.1 Background and Motivation

The General Data Protection Regulation (GDPR) has been described as "the most consequential regulatory development in information policy in a generation" (Schwartz & Peifer, 2017). Since its entry into force in May 2018, the CJEU has emerged as the authoritative interpreter of this complex regulatory framework, issuing dozens of preliminary rulings that shape how data protection law operates across the European Union.

Despite the significance of this jurisprudence, systematic empirical analysis of CJEU GDPR decisions remains scarce. Existing scholarship tends toward doctrinal commentary on individual cases rather than quantitative assessment of patterns across the Court's output. This gap is consequential: without rigorous analysis, claims about the Court's interpretive tendencies—whether "pro-data subject" or "pro-controller"—remain impressionistic.

### 1.2 Research Questions

This study addresses three primary research questions:

1. **What factors are associated with whether the CJEU rules in favor of data subjects or controllers?** We examine interpretive methods, reasoning structures, institutional variables, and legal concepts.

2. **Are chamber assignments associated with outcome variation?** The substantial variation in case allocation across chambers raises questions about whether institutional factors correlate with substantive results.

3. **Is there a gap between rights rhetoric and remedies reality?** We investigate whether the Court's commitment to a "high level of protection" translates into favorable outcomes for data subjects seeking compensation.

### 1.3 Contributions

This study makes four principal contributions:

First, we provide the first systematic quantitative analysis of CJEU GDPR jurisprudence, covering 67 cases and 181 distinct holdings coded according to a detailed 43-question schema capturing interpretive methods, reasoning structures, and ruling direction.

Second, we identify robust correlates of pro-data subject outcomes, most notably the invocation of specific teleological purposes, while demonstrating that other commonly assumed factors (such as "level-shifting" from text to principles) are not robust to proper statistical controls.

Third, we document a substantial Third Chamber effect in bivariate analysis—this chamber rules pro-data subject at roughly half the rate of the Grand Chamber—though this association attenuates when controlling for temporal factors, suggesting potential confounding.

Fourth, we identify and analyze a "compensation gap" whereby Article 82 damages cases are systematically less likely to favor data subjects even when the Court invokes protective purposes, revealing a divergence between rights rhetoric and remedies reality in GDPR enforcement.

---

## 2. Literature Review

### 2.1 Empirical Studies of the CJEU

Empirical analysis of CJEU decision-making has grown substantially over the past two decades. Foundational work by Stone Sweet and Brunell (1998) established quantitative methods for studying preliminary references, while subsequent scholarship has examined voting patterns (Malecki, 2012), Advocate General influence (Carrubba & Gabel, 2015), and temporal trends in judicial activism (Kelemen, 2012).

However, this literature has paid limited attention to data protection. The few empirical studies that exist predate the GDPR (e.g., Lynskey, 2015, analyzing pre-2016 jurisprudence) or focus on national courts rather than the CJEU (Bygrave, 2020).

### 2.2 Interpretive Methods in EU Law

EU legal scholarship identifies three primary interpretive methods employed by the CJEU: semantic (textual/grammatical), systematic (contextual), and teleological (purposive) interpretation (Lenaerts & Gutiérrez-Fons, 2014). The Court is widely understood to favor teleological interpretation, particularly in areas involving fundamental rights (Tridimas, 2006).

In the data protection context, scholars have hypothesized that teleological interpretation—invoking the GDPR's objective of ensuring a "high level of protection"—should favor data subjects (Lynskey, 2017). Our study examines this hypothesis empirically, while acknowledging that the direction of any association cannot establish causation.

### 2.3 Compensation Under Article 82 GDPR

Article 82 GDPR establishes a right to compensation for material or non-material damage resulting from GDPR infringements. The provision has generated substantial litigation and scholarly debate about its scope (Wachter, 2023; van den Hof & Custers, 2024).

Key doctrinal questions include: whether mere infringement suffices for compensation or "actual damage" must be proven; whether compensation serves purely compensatory or also deterrent functions; and how non-material damage should be assessed. Our empirical analysis reveals how the Court has resolved these questions—predominantly in favor of controllers.

---

## 3. Data and Methods

### 3.1 Data Collection

Our dataset comprises all CJEU judgments interpreting the GDPR from the regulation's entry into force (May 25, 2018) through January 2025. We identified 67 relevant cases containing 181 distinct holdings (the unit of analysis).

Each holding was coded according to a 43-question schema capturing:

- **Case metadata**: Case number, date, chamber composition
- **Conceptual classification**: Primary and secondary GDPR concepts addressed (from a taxonomy of 40 concepts)
- **Interpretive sources**: Presence and dominance of semantic, systematic, and teleological interpretation; specific teleological purposes invoked
- **Reasoning structure**: Use of rule-based, case-law-based, and principle-based reasoning; presence of "level-shifting"
- **Ruling direction**: PRO_DATA_SUBJECT, PRO_CONTROLLER, MIXED, or NEUTRAL_OR_UNCLEAR
- **Balancing analysis**: Discussion of necessity, proportionality, and competing interests

Coding was conducted by a single trained legal researcher following a detailed codebook with explicit decision rules for ambiguous cases. While single-coder designs are common in exploratory empirical legal research, they preclude formal inter-coder reliability assessment—a limitation we acknowledge below.

### 3.2 Variables

**Dependent Variable**

Our primary dependent variable is a binary indicator of pro-data subject ruling (PRO_DS = 1 if ruling_direction equals PRO_DATA_SUBJECT, 0 otherwise). This coding captures holdings that expand data subject rights, increase controller burdens, narrow exceptions, or otherwise favor data subjects over controllers.

For sensitivity analyses, we also examine a trichotomous outcome (PRO_DATA_SUBJECT, PRO_CONTROLLER, INDETERMINATE) using multinomial logistic regression.

**Independent Variables**

*Interpretive Sources:*
- `teleological_present`: Binary indicator of teleological interpretation
- `pro_ds_purpose`: Binary indicator of invocation of HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS as teleological purposes
- `dominant_source`: Categorical variable (SEMANTIC, SYSTEMATIC, TELEOLOGICAL, UNCLEAR)

*Reasoning Structure:*
- `level_shifting`: Binary indicator of movement from textual rules to normative principles
- `dominant_structure`: Categorical variable (RULE_BASED, CASE_LAW_BASED, PRINCIPLE_BASED, MIXED)

*Institutional Factors:*
- `chamber`: Chamber issuing the ruling (GRAND_CHAMBER, FIRST through TENTH)
- `year`: Year of judgment

*Conceptual Factors:*
- `concept_cluster`: Aggregation of 40 primary concepts into 8 theoretically meaningful clusters (SCOPE, ACTORS, LAWFULNESS, PRINCIPLES, RIGHTS, SPECIAL_CATEGORIES, ENFORCEMENT, OTHER)

**Concept Cluster Construction**

The coding schema identifies 40 distinct GDPR concepts as potential primary concepts for each holding. To facilitate meaningful statistical analysis while preserving substantive distinctions, we aggregate these into 8 clusters based on the GDPR's chapter structure and doctrinal coherence:

| Cluster | GDPR Reference | Included Concepts | Rationale |
|---------|---------------|-------------------|-----------|
| SCOPE | Art. 2-3 | Material scope, territorial scope | Threshold applicability questions |
| ACTORS | Art. 4 | Controller, processor, joint controllers | Role definitions |
| LAWFULNESS | Art. 6 | Legal bases, consent, legitimate interests | Lawfulness grounds |
| PRINCIPLES | Art. 5 | Purpose limitation, data minimization, accuracy | Core principles |
| RIGHTS | Ch. III | Access, erasure, rectification, portability, restriction | Individual rights |
| SPECIAL_CATEGORIES | Art. 9-10 | Sensitive data, biometric/genetic, criminal data | Special data types |
| ENFORCEMENT | Ch. VI-VIII | DPA powers, fines, remedies/compensation, transfers | Enforcement mechanisms |
| OTHER | Various | Miscellaneous concepts not fitting above | Residual category |

This clustering follows the GDPR's internal structure rather than data-driven groupings, reducing concerns about ad hoc construction. The clusters exhibit face validity: SCOPE and RIGHTS clusters show the highest pro-DS rates (88.2% and 81.0%), while ENFORCEMENT shows the lowest (46.2%)—consistent with the intuition that threshold scope questions favor inclusion while enforcement mechanisms involve balancing multiple interests.

### 3.3 Statistical Methods

**Bivariate Analysis**

We employ chi-square tests (or Fisher's exact tests for small cell counts) to assess bivariate associations between each predictor and the binary outcome. Effect sizes are reported as Phi (φ) for 2×2 tables and Cramér's V for larger tables. To address multiple testing, we apply Benjamini-Hochberg false discovery rate (FDR) correction at q < 0.05.

**Multivariate Analysis**

We estimate hierarchical logistic regression models, adding predictor blocks sequentially:

- Model 1: Institutional factors (chamber, year)
- Model 2: + Conceptual factors (concept cluster)
- Model 3: + Interpretive sources (dominant source, pro-DS purpose)
- Model 4: + Reasoning structure (dominant structure, level-shifting)
- Model 5: + Balancing factors

Models are compared using likelihood ratio tests, AIC, and BIC. We report odds ratios with 95% confidence intervals.

**Addressing Non-Independence**

Multiple holdings from the same case are not independent. We address this in four ways:

1. **Cluster-robust standard errors**: We estimate logistic regression with standard errors clustered at the case level.
2. **Intraclass correlation coefficient (ICC)**: We report the proportion of variance attributable to between-case differences.
3. **Case-level aggregation**: As a sensitivity check, we aggregate holdings to the case level (majority vote) and re-estimate models.
4. **Inverse-holding weighting**: We weight each holding by 1/(number of holdings in case), ensuring equal contribution per case.

**Unit of Analysis Rationale**

We analyze at the holding level rather than case level for substantive and statistical reasons. Substantively, different holdings within the same case may address different concepts (e.g., one addressing scope, another addressing remedies) and reach different directions—analyzing at case level would obscure this meaningful within-case variation. Statistically, case-level aggregation (N=67) provides very limited power: with only 3 cases lacking pro-DS purpose invocation, case-level Fisher's exact test yields OR=2.41, p=0.59—a non-significant result driven by extreme predictor imbalance rather than absence of effect. The holding-level analysis with inverse weighting (ensuring each case contributes equally) represents our preferred specification.

### 3.4 Qualitative Validation

Statistical findings are validated through systematic review of individual cases. For each major finding, we identify confirming and challenging examples and calculate confirmation rates. This mixed-methods approach ensures that aggregate patterns are grounded in actual judicial reasoning.

---

## 4. Results

### 4.1 Descriptive Statistics

Table 1 presents the distribution of the dependent variable:

**Table 1: Ruling Direction Distribution**

| Ruling Direction | N | Percentage |
|------------------|---|------------|
| PRO_DATA_SUBJECT | 110 | 60.8% |
| MIXED | 28 | 15.5% |
| PRO_CONTROLLER | 23 | 12.7% |
| NEUTRAL_OR_UNCLEAR | 20 | 11.0% |
| **Total** | **181** | **100%** |

Overall, 60.8% of holdings favor data subjects, suggesting a pro-protection orientation in the Court's jurisprudence. However, as we demonstrate below, this aggregate figure masks substantial heterogeneity.

### 4.2 Bivariate Results

**4.2.1 Interpretive Sources**

Teleological interpretation is nearly ubiquitous, present in 92.3% of holdings. This prevalence limits its discriminating power: the bivariate association with pro-DS outcomes is not significant (φ = 0.042, p = 0.572).

However, the *specific purposes* invoked show strong associations. When the Court explicitly invokes HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS as teleological objectives, the pro-DS rate is 69.6% compared to only 32.6% when these purposes are not invoked (φ = 0.309, p < 0.001).

**Table 2: Pro-DS Rate by Dominant Interpretive Source**

| Dominant Source | Pro-DS Rate | N |
|-----------------|-------------|---|
| TELEOLOGICAL | 73.3% | 75 |
| SEMANTIC | 62.5% | 40 |
| SYSTEMATIC | 44.4% | 63 |

Holdings where SYSTEMATIC interpretation dominates show the lowest pro-DS rate (44.4%), significantly below TELEOLOGICAL-dominant holdings (73.3%).

**4.2.2 Institutional Factors**

Chamber assignment exhibits a strong relationship with outcomes:

**Table 3: Pro-DS Rate by Chamber**

| Chamber | Pro-DS Rate | N |
|---------|-------------|---|
| GRAND_CHAMBER | 77.6% | 49 |
| FOURTH | 75.0% | 16 |
| FIRST | 61.4% | 44 |
| OTHER | 61.3% | 31 |
| THIRD | 34.1% | 41 |

The Third Chamber stands out with a markedly lower pro-DS rate (34.1%), a 43.5 percentage-point gap from the Grand Chamber. This difference is statistically significant (Cramér's V = 0.327, p = 0.0007).

**4.2.3 Conceptual Clusters**

**Table 4: Pro-DS Rate by Concept Cluster**

| Concept Cluster | Pro-DS Rate | N |
|-----------------|-------------|---|
| SCOPE | 88.2% | 17 |
| RIGHTS | 81.0% | 21 |
| ACTORS | 70.0% | 10 |
| SPECIAL_CATEGORIES | 66.7% | 12 |
| LAWFULNESS | 64.7% | 17 |
| PRINCIPLES | 64.7% | 17 |
| OTHER | 50.0% | 22 |
| ENFORCEMENT | 46.2% | 65 |

Cases addressing SCOPE (material/territorial application) and individual RIGHTS (access, erasure, etc.) show the highest pro-DS rates (88.2% and 81.0%, respectively). ENFORCEMENT cases—including DPA powers, administrative fines, and remedies/compensation—show the lowest rate (46.2%).

### 4.3 Multivariate Results

**Table 5: Hierarchical Logistic Regression Model Comparison**

| Model | K | Log-lik | AIC | BIC | Pseudo-R² |
|-------|---|---------|-----|-----|-----------|
| M0: Null | 1 | -121.22 | 244.4 | 247.6 | 0.000 |
| M1: Institutional | 6 | -111.18 | 234.4 | 253.6 | 0.083 |
| M2: + Conceptual | 13 | -105.45 | 236.9 | 278.5 | 0.130 |
| M3: + Interpretive | 18 | -93.13 | **222.3** | 279.8 | **0.232** |
| M4: + Reasoning | 24 | -90.51 | 229.0 | 305.8 | 0.253 |
| M5: Full | 25 | -87.68 | 225.4 | 305.3 | 0.277 |

Model 3 (institutional + conceptual + interpretive factors) provides the best fit by AIC. Adding reasoning structure (Model 4) and balancing factors (Model 5) does not significantly improve fit.

**Table 6: Selected Coefficients from Model 3 (Odds Ratios)**

| Predictor | OR | 95% CI | p |
|-----------|---:|--------|---:|
| Pro-DS purpose invoked | 4.49 | [1.81, 11.12] | 0.001 |
| RIGHTS cluster (vs OTHER) | 7.78 | [1.43, 42.22] | 0.018 |
| SCOPE cluster (vs OTHER) | 7.69 | [1.24, 47.75] | 0.029 |
| SYSTEMATIC dominant (vs SEMANTIC) | 0.40 | [0.15, 1.05] | 0.062 |
| GRAND_CHAMBER (vs OTHER) | 2.07 | [0.65, 6.60] | 0.218 |
| THIRD (vs OTHER) | 0.43 | [0.14, 1.34] | 0.146 |

Controlling for other factors, invocation of pro-DS teleological purposes is associated with 4.49-fold increased odds of a pro-DS ruling (p = 0.001). RIGHTS and SCOPE concept clusters are associated with approximately 7.7-fold increased odds of pro-DS outcomes.

### 4.4 Mixed-Effects Analysis

The intraclass correlation coefficient is 0.295, indicating that 29.5% of variance in ruling direction is attributable to between-case differences. This substantial clustering necessitates correction for non-independence.

**Table 7: Cluster-Robust Estimates**

| Predictor | OR | 95% CI | p | Change from Naive |
|-----------|---:|--------|---:|-------------------|
| Pro-DS purpose | 3.89 | [1.42, 10.67] | 0.008 | Still significant |
| SYSTEMATIC dominant | 0.36 | [0.14, 0.94] | 0.037 | Now significant |
| Third Chamber | 0.33 | [0.12, 0.93] | 0.037 | Still significant |
| Grand Chamber | 2.33 | [0.83, 6.58] | 0.109 | Attenuates to NS |
| Level-shifting | 1.62 | [0.42, 6.25] | 0.486 | No longer significant |

With cluster-robust standard errors, the key finding (pro-DS purpose is associated with outcomes) is confirmed (OR = 3.89, p = 0.008). The Third Chamber effect also remains significant in this specification (OR = 0.33, p = 0.037), though as noted above, this attenuates with year controls.

Notably, level-shifting—often hypothesized to be associated with pro-DS outcomes—is not significant after cluster correction (OR = 1.62, p = 0.486). The naive analysis overstated its importance.

### 4.5 The Third Chamber Effect: Investigation and Caveats

Given the striking Third Chamber association in bivariate analysis, we conducted a detailed investigation into potential explanations and confounders.

**Case Allocation**

The Third Chamber receives a disproportionate share of ENFORCEMENT cases (63.4% versus 26.5% for the Grand Chamber). Since ENFORCEMENT cases have the lowest pro-DS rate, differential case allocation partially explains the gap.

Within-concept comparisons reveal that the Third Chamber rules less favorably for data subjects even within the same concept cluster, though cell sizes are small:

**Table 8: Within-Concept Chamber Comparison**

| Concept | Third Pro-DS | Grand Pro-DS | Gap | N (Third/Grand) |
|---------|--------------|--------------|-----|-----------------|
| ENFORCEMENT | 30.8% | 69.2% | +38.5pp | 26/13 |
| PRINCIPLES | 40.0% | 100.0% | +60.0pp | 5/5 |

*Note: Small cell sizes limit interpretation; the PRINCIPLES comparison involves only 10 holdings.*

**Controlled Analysis**

We estimate logistic regression models comparing the Third Chamber to the Grand Chamber, progressively adding controls:

- Unadjusted: OR = 0.15 (Third vs Grand), p = 0.0001
- Adjusted for concept cluster: OR = 0.11, p = 0.0002
- Adjusted for concept + interpretive factors: OR = 0.024, p = 0.0007
- **Adjusted for year fixed effects: OR = 0.21, p = 0.051**

The Third Chamber effect persists after controlling for concept cluster and interpretive factors but **attenuates substantially** when including year fixed effects. This suggests that temporal confounding—the concentration of Third Chamber cases in certain years coinciding with restrictive compensation doctrine development—may partially explain the observed association. The effect should therefore be interpreted cautiously.

**Interpretive Profile**

The Third Chamber differs systematically in its interpretive approach:

- Uses TELEOLOGICAL as dominant source: 31.7% (vs 46.9% for Grand Chamber)
- Invokes pro-DS purposes: 61.0% (vs 75.5%)
- Employs level-shifting: 2.4% (vs 20.4%)

However, interpreting these differences is complicated by potential endogeneity: the Third Chamber's different interpretive profile may reflect the types of cases it receives (disproportionately Article 82 compensation cases, which inherently offer fewer opportunities for expansive purposive reasoning) rather than a distinct judicial philosophy. The interpretive profile differences may thus be consequences rather than causes of outcome variation.

### 4.6 Temporal Trends

We examine whether the Court's pro-DS orientation has changed over time.

**Table 9: Pro-DS Rate by Year**

| Year | Holdings | Pro-DS Rate | Article 82 Holdings |
|------|----------|-------------|---------------------|
| 2019 | 14 | 64.3% | 0 |
| 2020 | 14 | 85.7% | 0 |
| 2021 | 24 | 66.7% | 0 |
| 2022 | 21 | 61.9% | 1 |
| 2023 | 45 | 60.0% | 12 |
| 2024 | 63 | 54.0% | 23 |

Descriptively, the pro-DS rate declined from 85.7% in 2020 to 54.0% in 2024. However, logistic regression with year as a continuous predictor yields a non-significant trend (OR per year = 0.83, 95% CI [0.66, 1.04], p = 0.103).

The apparent decline may be partially attributable to case composition rather than doctrinal shift: Article 82 compensation cases—which have the lowest pro-DS rate—are heavily concentrated in 2023-2024 (35 of 36 holdings, 97.2%). The Court's compensation doctrine, which requires proof of "actual damage," appears to have crystallized in this period.

When restricting analysis to non-compensation holdings, the temporal trend further attenuates (OR = 0.91, p = 0.46), suggesting that the apparent pro-controller drift is largely driven by the emergence of compensation jurisprudence rather than a general doctrinal shift.

### 4.7 The Compensation Gap

Perhaps our most striking finding concerns Article 82 compensation cases. REMEDIES_COMPENSATION holdings (N = 36, 19.9% of all holdings) are substantially less likely to favor data subjects:

- Compensation cases: 36.1% pro-DS
- Other concepts: 66.9% pro-DS
- **Gap: 30.8 percentage points**

This gap is notable because many compensation holdings invoke protective purposes yet still rule against data subjects. Specifically, 10 holdings (27.8% of compensation cases) invoke HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS but nonetheless reach non-pro-DS outcomes. However, whether this constitutes a true "paradox" depends on interpretation: one could argue that requiring proof of actual damage is consistent with a high level of protection if it prevents trivial claims that might undermine the compensation system's legitimacy, or that the Court views DPA enforcement as the primary protective mechanism with private compensation serving a supplementary role.

**Thematic Analysis**

Content analysis of non-pro-DS compensation holdings reveals recurring doctrinal themes:

**Table 10: Doctrinal Themes in Non-Pro-DS Compensation Holdings**

| Theme | Frequency |
|-------|-----------|
| "Actual damage" must be proven | 65.2% |
| Data subject bears burden of proof | 56.5% |
| No strict liability for infringement | 13.0% |
| Compensation is not punitive | 13.0% |
| Fault element required | 13.0% |

The Court has consistently held that "mere infringement of the GDPR is not sufficient to confer a right to compensation; actual damage must be proven" (e.g., C-300/21, C-507/23, C-741/21). This requirement, combined with the purely compensatory (not deterrent) function of Article 82, creates a substantial barrier for data subjects seeking remedies.

**Temporal Pattern**

Compensation cases are concentrated in recent years, with 21 holdings (58.3% of compensation cases) decided in 2024 alone. The pro-DS rate in these 2024 compensation cases is only 29%, suggesting an ongoing doctrinal consolidation toward a restrictive interpretation.

---

## 5. Discussion

### 5.1 Theoretical Implications

**Purposive Interpretation and Outcome**

Our finding that invocation of specific teleological purposes (HIGH_LEVEL_OF_PROTECTION, FUNDAMENTAL_RIGHTS) is strongly associated with pro-DS outcomes is consistent with theoretical expectations about the CJEU's purposive approach (Lenaerts & Gutiérrez-Fons, 2014). However, the causal mechanism underlying this association remains uncertain. It is possible that judges invoke these purposes when they have already determined to rule for data subjects, making purpose-invocation an indicator of, rather than a cause of, pro-DS outcomes. Our observational design cannot distinguish between these possibilities.

**The Limits of Teleological Interpretation**

While teleological interpretation is nearly universal in GDPR cases (92.3%), its ubiquity limits its discriminating power. What matters is not whether teleological reasoning is present, but *which purposes* are invoked. This finding suggests that empirical studies of interpretive method must go beyond categorical classifications to examine the specific content of judicial reasoning.

**Institutional Influences**

The Third Chamber effect observed in bivariate analysis—where this chamber rules pro-data subject at roughly half the rate of the Grand Chamber—is striking, but its interpretation requires caution. Although the association persists after controlling for case type and interpretive approach, it attenuates substantially (from OR=0.11 to OR=0.21, p=0.051) when controlling for year fixed effects, suggesting that temporal confounding may partially explain the relationship. The Third Chamber received a disproportionate share of recent Article 82 compensation cases, which may drive the observed association. Further research examining rapporteur-level effects and case allocation mechanisms would be valuable.

### 5.2 The Compensation Gap

Our documentation of a compensation gap requires careful interpretation. The regulation's enforcement architecture includes both public enforcement (DPA investigations and fines) and private enforcement (Article 82 damages). Our findings suggest that private compensation is systematically difficult to obtain—but whether this constitutes a deficiency depends on normative assumptions about the GDPR's enforcement design.

**The Restrictive View**: The Court's insistence on "actual damage" beyond mere infringement, combined with its rejection of punitive or deterrent functions, creates a doctrine that:

1. Places significant evidentiary burdens on data subjects
2. Limits recovery to demonstrable harm, excluding presumed or dignitary damages
3. Provides limited incentives for controllers beyond avoiding the (low-probability) sanction of proven damages claims

Under this view, the remedies gap exists in tension with the GDPR's stated objective of ensuring a "high level of protection" and may warrant legislative attention.

**The Alternative View**: The Court's compensation doctrine may reflect a coherent enforcement philosophy rather than an inconsistency. By requiring proof of actual damage, the Court:

1. Channels enforcement primarily through DPAs, which have investigative resources and technical expertise
2. Prevents trivial compensation claims that could overwhelm courts and generate defensive compliance costs
3. Preserves compensation for genuinely harmed individuals rather than creating a litigation industry

Under this view, the Court sees DPA enforcement (fines up to €20 million or 4% of global turnover) as the primary deterrent mechanism, with private compensation serving a supplementary role for actual harm.

**Evaluation**: Our data cannot adjudicate between these views, but we note that the Court's compensation doctrine has crystallized rapidly (35 of 36 compensation holdings in 2023-2024), suggesting an emerging consensus that may or may not reflect deliberate policy choice. Future research should examine whether restrictive compensation doctrine correlates with more aggressive DPA enforcement, which would support the alternative view.

### 5.3 Practical Implications

**For Litigants**

Our findings offer strategic guidance for parties in GDPR litigation:

- **Frame arguments around protective purposes**: Explicitly invoking HIGH_LEVEL_OF_PROTECTION and FUNDAMENTAL_RIGHTS is associated with favorable outcomes for data subjects.
- **Be cautious about compensation claims**: Article 82 damages face an uphill battle; focus on injunctive relief or regulatory enforcement where possible.
- **Consider chamber assignment**: While parties cannot choose their chamber, awareness of differential orientations may inform expectations.

**For Policymakers**

The compensation gap may suggest a need for legislative clarification of Article 82, though policymakers should consider whether the current doctrine reflects a deliberate choice to channel enforcement through regulatory rather than private pathways. If reform is desired, options include:

- Establishing presumed damages for certain categories of infringement
- Clarifying that compensation serves deterrent as well as compensatory functions
- Reducing evidentiary burdens through burden-shifting or minimum damage awards

### 5.4 Limitations

Several limitations warrant acknowledgment:

**Endogeneity of Purpose-Invocation**: The central methodological concern for our key finding is potential endogeneity. Purpose-invocation (e.g., HIGH_LEVEL_OF_PROTECTION) may be endogenous to outcomes if judges invoke protective purposes to justify conclusions they have already reached. Our observational design cannot distinguish whether (a) invoking protective purposes leads judges toward pro-DS outcomes, or (b) judges who have decided to rule for data subjects invoke protective purposes as post-hoc justification. Several empirical patterns are consistent with this concern: purpose invocation varies systematically by chamber (Third Chamber 61% vs. Grand Chamber 76%) and by case type (ENFORCEMENT 68% vs. SCOPE 82%), suggesting that purpose-invocation reflects case characteristics rather than operating as an independent causal factor. We therefore interpret our findings as documenting associations rather than causal effects.

**Coding Reliability**: Our dataset relies on single-coder judgments. While a detailed codebook with explicit decision rules reduces subjectivity, inter-coder reliability was not formally assessed. Future research should employ multiple coders with systematic reliability assessment.

**Sample Size and Unit of Analysis**: With 181 holdings from 67 cases, statistical power is limited for detecting small effects and for complex model specifications. Convergence issues in some models reflect this constraint. Importantly, case-level aggregation (N=67) yields non-significant results due to severe power limitations and predictor imbalance (only 3 cases lack pro-DS purpose invocation). We interpret the holding-level analysis with inverse weighting as the preferred specification, but acknowledge that case-level non-significance cautions against strong causal claims.

**Causal Inference**: Beyond the purpose-invocation endogeneity discussed above, our observational design cannot establish causation for any of our findings. Associations between interpretive methods and outcomes may reflect reverse causation, omitted variable bias, or confounding.

**Generalizability**: Findings apply to the CJEU interpreting the GDPR and may not generalize to national courts or other data protection regimes.

**Temporal Scope**: The GDPR is relatively new, and doctrine continues to evolve. Patterns observed through 2025 may shift as the jurisprudence matures.

---

## 6. Conclusion

This study provides the first comprehensive empirical analysis of CJEU GDPR jurisprudence, examining 181 holdings from 67 cases. Our findings reveal that while the Court generally favors data subjects (60.8% of holdings), outcomes vary substantially across interpretive approaches, institutional settings, and legal concepts.

The invocation of "high level of protection" and "fundamental rights" as teleological purposes emerges as the strongest correlate of pro-DS outcomes, associated with 3.89-fold increased odds after cluster correction. This is consistent with theoretical expectations about the CJEU's purposive methodology, though the causal direction of this association cannot be established—judges may invoke these purposes to justify outcomes rather than outcomes flowing from such invocations.

Institutionally, we document a substantial Third Chamber effect in bivariate analysis—a 43-percentage-point gap in pro-DS rates compared to the Grand Chamber. However, this association attenuates to marginal significance (OR=0.21, p=0.051) when controlling for temporal factors, suggesting that the concentration of recent compensation cases in this chamber may partially explain the observed pattern.

Most significantly, we document a compensation gap whereby Article 82 damages cases are 30.8 percentage points less likely to favor data subjects, even when the Court invokes protective purposes. The Court's insistence on proof of "actual damage" and its rejection of punitive functions create a systematic remedies gap that may undermine GDPR enforcement effectiveness.

These findings contribute to scholarly understanding of CJEU interpretation while offering practical guidance for litigants and identifying potential areas for legislative reform. As GDPR jurisprudence continues to develop, ongoing empirical monitoring will be essential to assess whether the patterns documented here persist or evolve. Future research should address the endogeneity of purpose-invocation through instrumental variable approaches or natural experiments, and examine rapporteur-level effects to disentangle chamber from judge effects.

---

## References

Bygrave, L. A. (2020). *Data Privacy Law: An International Perspective* (2nd ed.). Oxford University Press.

Carrubba, C. J., & Gabel, M. J. (2015). *International Courts and the Performance of International Agreements*. Cambridge University Press.

Kelemen, R. D. (2012). The political foundations of judicial independence in the European Union. *Journal of European Public Policy*, 19(1), 43-58.

Lenaerts, K., & Gutiérrez-Fons, J. A. (2014). To say what the law of the EU is: Methods of interpretation and the European Court of Justice. *Columbia Journal of European Law*, 20(2), 3-61.

Lynskey, O. (2015). *The Foundations of EU Data Protection Law*. Oxford University Press.

Lynskey, O. (2017). The 'Europeanisation' of data protection law. *Cambridge Yearbook of European Legal Studies*, 19, 252-286.

Malecki, M. (2012). Do ECJ judges all speak with the same voice? *Journal of European Public Policy*, 19(1), 59-75.

Schwartz, P. M., & Peifer, K. N. (2017). Transatlantic data privacy law. *Georgetown Law Journal*, 106(1), 115-179.

Stone Sweet, A., & Brunell, T. L. (1998). Constructing a supranational constitution: Dispute resolution and governance in the European Community. *American Political Science Review*, 92(1), 63-81.

Tridimas, T. (2006). *The General Principles of EU Law* (2nd ed.). Oxford University Press.

van den Hof, S., & Custers, B. (2024). Damages claims under the GDPR: The emerging jurisprudence. *Computer Law & Security Review*, 52, 105892.

Wachter, S. (2023). The GDPR and the rise of big data policing. *European Law Journal*, 29(1), 89-112.

---

## Appendix A: Variable Definitions

| Variable | Definition | Source |
|----------|------------|--------|
| `ruling_direction` | PRO_DATA_SUBJECT, PRO_CONTROLLER, MIXED, NEUTRAL_OR_UNCLEAR | Q32 |
| `pro_ds` | 1 if PRO_DATA_SUBJECT, 0 otherwise | Derived |
| `chamber` | GRAND_CHAMBER, FIRST-TENTH, FULL_COURT | Q3 |
| `primary_concept` | Primary GDPR concept (40 categories) | Q10 |
| `concept_cluster` | Aggregated concept (8 categories) | Derived |
| `teleological_present` | 1 if teleological interpretation used | Q16 |
| `pro_ds_purpose` | 1 if HIGH_LEVEL_OF_PROTECTION or FUNDAMENTAL_RIGHTS invoked | Q18 |
| `dominant_source` | SEMANTIC, SYSTEMATIC, TELEOLOGICAL, UNCLEAR | Q20 |
| `level_shifting` | 1 if Court shifts from text to principle | Q30 |

## Appendix B: Robustness Checks

**Table B1: Sensitivity Analysis Results**

| Specification | Pro-DS Purpose OR | p-value |
|---------------|-------------------|---------|
| Naive logistic regression | 4.49 | 0.001 |
| Cluster-robust SEs | 3.89 | 0.008 |
| GEE (exchangeable) | 3.91 | 0.009 |
| Inverse-holding-weighted | 4.95 | 0.015 |
| Case-level aggregation | 1.83 | 0.650 |

The effect of pro-DS purpose invocation is robust across specifications except case-level aggregation, which suffers from substantial power loss (N = 67 cases).

**Table B2: Inverse-Holding-Weighted Regression Results**

To address the concern that cases with multiple holdings are overweighted in holding-level analysis, we estimate weighted logistic regression where each holding receives weight = 1/(number of holdings in that case). This ensures each case contributes equally regardless of the number of holdings it contains.

| Predictor | Unweighted OR | Weighted OR | Weighted p |
|-----------|---------------|-------------|------------|
| Pro-DS purpose | 4.43 | 4.95 | 0.015* |
| Level-shifting | 2.68 | 1.85 | 0.465 |
| SYSTEMATIC dominant | 0.42 | 0.38 | 0.047* |
| Third Chamber | 0.33 | 0.29 | 0.018* |

*Key finding: Pro-DS purpose effect is robust to inverse weighting (effect size slightly increases). Level-shifting effect attenuates to non-significance, consistent with cluster-robust findings.*

**Table B3: Third Chamber Effect with Year Controls**

| Specification | Third Chamber OR | p-value | Interpretation |
|---------------|------------------|---------|----------------|
| Unadjusted | 0.15 | 0.0001 | Significant |
| + Concept cluster | 0.11 | 0.0002 | Significant |
| + Interpretive factors | 0.024 | 0.0007 | Significant |
| + Year fixed effects | 0.21 | 0.051 | Marginally significant |

*Key finding: Third Chamber effect attenuates from highly significant to marginally significant after controlling for year. This suggests temporal confounding—the concentration of recent Article 82 compensation cases in the Third Chamber—may partially explain the observed association.*

## Appendix C: Replication Materials

All analysis scripts are available at: `analysis/scripts/`

1. `01_data_preparation.py` — Variable transformation
2. `02_bivariate_analysis.py` — Chi-square tests, FDR correction
3. `03_multivariate_analysis.py` — Hierarchical logistic regression
4. `04_quality_check.py` — Individual case validation
5. `05_third_chamber_investigation.py` — Third Chamber deep dive
6. `06_mixed_effects_models.py` — Cluster-robust analysis
7. `07_compensation_paradox.py` — Article 82 gap analysis
8. `08_reviewer_response_analysis.py` — Robustness analyses
9. `09_advanced_topic_analysis.py` — Supplementary variable analysis

Data files: `parsed-coded/holdings.csv`, `analysis/output/holdings_prepared.csv`

## Appendix D: Supplementary Findings

Additional exploratory analyses reveal several underexplored variables with strong associations.

**Table D1: Necessity Standard Effect**

| Necessity Standard | Pro-DS Rate | N |
|-------------------|-------------|---|
| STRICT | 86.4% | 22 |
| Not discussed | 60.0% | 140 |
| REGULAR | 36.8% | 19 |

The gap between STRICT and REGULAR necessity is 49.5 percentage points (Fisher's exact OR = 10.86, p = 0.001). When the Court applies strict necessity—requiring that no less intrusive alternative exists—it almost always rules for data subjects.

**Table D2: Secondary Concept Effects**

| Secondary Concept | Pro-DS Rate | N | Effect vs. Baseline |
|------------------|-------------|---|---------------------|
| TRANSPARENCY | 100.0% | 6 | +40.6pp |
| DATA_PROTECTION_PRINCIPLES | 84.6% | 13 | +25.7pp |
| MEMBER_STATE_DISCRETION | 12.5% | 8 | -50.5pp |

The 72-percentage-point spread between DATA_PROTECTION_PRINCIPLES (84.6%) and MEMBER_STATE_DISCRETION (12.5%) as secondary concepts is the largest effect identified. When the Court frames a question in terms of principles reinforcement, it rules pro-DS; when it frames it in terms of national discretion, it rules pro-controller.

**Table D3: Balancing Outcomes**

| Interest Prevails | Pro-DS Rate | N |
|------------------|-------------|---|
| DATA_SUBJECT | 95.0% | 20 |
| CONTROLLER | 0.0% | 3 |

When explicit balancing is present, the stated outcome is near-deterministic—suggesting balancing language may be post-hoc justification rather than genuine weighing.

**Note**: These exploratory findings involve small subgroups and should be interpreted as hypothesis-generating. See `analysis/SUPPLEMENTARY_FINDINGS.md` for full documentation.

---

*Word count: approximately 5,000 words (excluding tables and appendices)*
