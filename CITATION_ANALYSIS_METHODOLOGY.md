# Methodology: Bivariate and Multivariate Analysis of Judgment Citation Effects in CJEU GDPR Jurisprudence

---

## Executive Summary

This document proposes a rigorous methodology for analyzing how CJEU GDPR judgments influence subsequent rulings through citation networks. Building on the existing empirical analysis of 181 holdings from 67 cases, we develop a comprehensive framework for:

1. **Citation Network Analysis**: Constructing and analyzing the directed acyclic graph (DAG) of case citations
2. **Bivariate Analysis**: Testing associations between cited case characteristics and citing case outcomes
3. **Multivariate Analysis**: Network-informed regression models controlling for case attributes and citation context
4. **Influence Propagation**: Measuring and modeling how judicial interpretation patterns diffuse through the citation network

The methodology adheres to standards of academic rigor appropriate for empirical legal scholarship, including pre-specification of hypotheses, multiple testing corrections, and sensitivity analyses.

---

## 1. Introduction and Research Questions

### 1.1 Motivation

The existing analysis of CJEU GDPR jurisprudence identifies factors associated with pro-data subject outcomes but treats each holding as effectively independent. However, judicial decisions exist within a network of precedent: later cases cite earlier ones, and these citations may carry substantive implications for how law develops.

Understanding citation dynamics addresses several important questions:

- **Doctrinal coherence**: Do later cases citing pro-DS precedents themselves rule pro-DS?
- **Path dependency**: Does early jurisprudence shape subsequent interpretive trajectories?
- **Interpretive diffusion**: Do specific reasoning patterns (e.g., teleological interpretation) propagate through citations?
- **Authority concentration**: Which cases serve as "hub" precedents, and does this affect outcomes?

### 1.2 Primary Research Questions

**RQ1 (Bivariate)**: Are characteristics of cited precedents associated with outcomes in citing cases?
- H1.1: Holdings citing pro-DS precedents are more likely to rule pro-DS
- H1.2: Holdings citing precedents that invoked "high level of protection" purposes are more likely to do so themselves
- H1.3: Citation of Grand Chamber precedents is associated with different outcomes than citation of other chambers

**RQ2 (Multivariate)**: Do citation effects persist after controlling for case-level characteristics?
- H2.1: The association between cited precedent direction and citing case outcome persists after controlling for concept cluster, chamber, and year
- H2.2: Citation network position (centrality) is independently associated with ruling direction

**RQ3 (Network)**: What is the structure of the CJEU GDPR citation network?
- H3.1: The network exhibits preferential attachment (a few cases attract most citations)
- H3.2: Citation clusters correspond to substantive legal domains (concept clusters)
- H3.3: Temporal citation patterns reveal doctrinal development trajectories

**RQ4 (Influence)**: How do interpretive approaches propagate through the network?
- H4.1: Teleological interpretation usage increases in cases citing teleological precedents
- H4.2: The "compensation gap" can be traced to specific early precedents that established restrictive interpretations

---

## 2. Data Description

### 2.1 Available Data Assets

| Dataset | Records | Key Variables | Source |
|---------|---------|---------------|--------|
| `cases.json` | 67 cases | case_id, judgment_date, chamber, holding_count | Parsed from coded decisions |
| `holdings.csv` | 181 holdings | All 47 coded variables per holding | Parsed from coded decisions |
| `case_citations` table | 639 edges | citing_case, citing_holding, cited_case | SQLite database |
| `cases_metadata.json` | 67 cases | judges, rapporteur, advocate_general | EUR-Lex metadata |

### 2.2 Citation Network Composition

Based on preliminary analysis:

- **Total citation edges**: 639 (holding-level citations to cases)
- **Unique cited cases**: 247
  - **Internal** (within GDPR corpus): 53 cases
  - **External** (outside corpus): 194 cases
- **Most-cited internal cases**: C-300/21 (25 citations), C-439/19 (21), C-667/21 (14)
- **Highest-citing cases**: C-313/23 et al. (33 cases cited), C-439/19 (28), C-817/19 (25)

### 2.3 Network Type Classification

The citation network is:
- **Directed**: Citations flow from later (citing) to earlier (cited) cases
- **Acyclic**: By construction (cases cannot cite future cases)
- **Bipartite structure**: Internal citations (within corpus) vs. external citations (to prior case law)
- **Multi-level**: Citations exist at holding level but aggregate to case level

---

## 3. Network Construction

### 3.1 Graph Representations

We construct three complementary graph representations:

#### 3.1.1 Case-Level Citation Graph (G_case)

**Nodes**: 67 CJEU GDPR cases + 194 external cited cases = 261 nodes
**Edges**: Directed edges from citing_case to cited_case (aggregated from holdings)
**Edge weights**: Number of holdings in citing_case that cite the cited_case

```
Node attributes:
- is_gdpr_corpus: Boolean (internal vs external)
- judgment_date: Date (for temporal analysis)
- chamber: Categorical (for internal cases)
- pro_ds_rate: Float (proportion of pro-DS holdings, for internal cases)
- holding_count: Integer (for internal cases)
```

#### 3.1.2 Holding-Level Citation Graph (G_holding)

**Nodes**: 181 holdings (internal only)
**Edges**: Directed edges representing citation relationships (derived from case citations with holding attribution)

```
Node attributes:
- All 47 coded variables from holdings.csv
- case_id: Parent case identifier
```

#### 3.1.3 Internal Citation Subgraph (G_internal)

**Nodes**: 67 CJEU GDPR cases (corpus only)
**Edges**: Citations between cases within the GDPR corpus
**Purpose**: Analyzing within-corpus doctrinal development

### 3.2 Temporal Constraints

All graphs enforce temporal ordering: edges only exist from later cases to earlier cases. This is verified during construction and any violations flagged for manual review (indicating potential data entry errors).

### 3.3 Edge Attribution

For analyses requiring outcome-level information, edges are attributed with:
- **citing_outcome**: ruling_direction of the citing holding
- **citing_concept**: primary_concept of the citing holding
- **citing_interpretation**: dominant_source of the citing holding
- **citing_purpose**: pro_ds_purpose of the citing holding

---

## 4. Bivariate Analysis Framework

### 4.1 Hypotheses and Tests

#### 4.1.1 Citation Direction Effect (H1.1)

**Null hypothesis**: The proportion of pro-DS outcomes in citing holdings is independent of whether cited precedents were pro-DS.

**Analysis**:
1. For each citing holding, compute the **precedent direction score**: proportion of cited internal cases that ruled pro-DS (weighted by citation frequency)
2. Dichotomize: "Predominantly pro-DS precedents cited" vs. "Predominantly pro-controller/mixed precedents cited"
3. Chi-square test of association with citing holding outcome
4. Effect size: Phi coefficient

**Operationalization**:
```
precedent_direction_score = Σ(pro_ds_rate of cited case × citation weight) / Σ(citation weight)
predominantly_pro_ds_precedents = 1 if precedent_direction_score > 0.5 else 0
```

#### 4.1.2 Purpose Propagation (H1.2)

**Null hypothesis**: Invocation of protective purposes (HIGH_LEVEL_OF_PROTECTION, FUNDAMENTAL_RIGHTS) in citing holdings is independent of whether cited precedents invoked these purposes.

**Analysis**:
1. For each cited case within corpus, determine whether any of its holdings invoked pro-DS purposes
2. For each citing holding, compute: does it cite at least one precedent that invoked pro-DS purposes?
3. Chi-square test of association with citing holding's purpose invocation
4. Effect size: Phi coefficient

**Rationale**: Tests whether protective purpose language is "sticky" across citations.

#### 4.1.3 Chamber Authority Effect (H1.3)

**Null hypothesis**: Outcomes in citing holdings are independent of the chamber composition of cited precedents.

**Analysis**:
1. Classify cited internal cases by chamber (Grand Chamber vs. other)
2. For each citing holding: does it cite any Grand Chamber precedent?
3. Chi-square test of association with ruling direction
4. Stratified analysis by citing case chamber

### 4.2 Multiple Testing Correction

With multiple bivariate tests, we apply Benjamini-Hochberg FDR correction at q < 0.05, consistent with the existing analysis methodology.

### 4.3 Sensitivity Analyses

1. **Weighted vs. unweighted**: Compare results using citation-weighted vs. unweighted precedent scores
2. **Internal-only vs. all citations**: Test whether effects persist when considering only internal citations
3. **Concept-stratified**: Test within concept clusters to assess heterogeneity
4. **Temporal windows**: Restrict to precedents within 2-year windows to test recency effects

---

## 5. Multivariate Analysis Framework

### 5.1 Model Specification

We extend the existing hierarchical logistic regression framework to incorporate citation network features.

#### 5.1.1 Model 0 (Baseline - Existing)

```
logit(pro_ds) = β₀ + β₁·chamber + β₂·year + β₃·concept_cluster + β₄·pro_ds_purpose + β₅·dominant_source + ε
```

#### 5.1.2 Model 1 (Citation-Augmented)

```
logit(pro_ds) = β₀ + β₁·chamber + β₂·year + β₃·concept_cluster + β₄·pro_ds_purpose + β₅·dominant_source
              + β₆·precedent_direction_score + β₇·citation_count + ε
```

**New variables**:
- `precedent_direction_score`: Continuous [0,1], weighted average pro-DS rate of cited internal precedents
- `citation_count`: Count of cited cases (log-transformed if skewed)

#### 5.1.3 Model 2 (Network Position)

```
logit(pro_ds) = ... + β₈·citing_case_centrality + β₉·avg_cited_centrality + ε
```

**New variables**:
- `citing_case_centrality`: PageRank or degree centrality of citing case in citation network
- `avg_cited_centrality`: Average centrality of cited precedents

#### 5.1.4 Model 3 (Citation Context)

```
logit(pro_ds) = ... + β₁₀·cites_gc_precedent + β₁₁·precedent_purpose_invocation + β₁₂·concept_match + ε
```

**New variables**:
- `cites_gc_precedent`: Binary, cites at least one Grand Chamber case
- `precedent_purpose_invocation`: Proportion of cited cases that invoked pro-DS purposes
- `concept_match`: Proportion of cited cases addressing same concept cluster

### 5.2 Model Comparison

Models are compared using:
- Likelihood ratio tests (nested models)
- AIC/BIC (all models)
- Pseudo-R² (McFadden's, Nagelkerke's)
- Out-of-sample prediction accuracy (k-fold cross-validation)

### 5.3 Addressing Clustering

Holdings are nested within cases, and cases are connected through citations. We address this multi-level dependence through:

1. **Cluster-robust standard errors**: Clustered at case level (existing approach)
2. **Mixed-effects models**: Random intercepts for cases
3. **Spatial regression diagnostics**: Testing for network autocorrelation using Moran's I on citation network

### 5.4 Endogeneity Considerations

Citation choices may be endogenous: judges may selectively cite precedents that support their preferred outcome. We address this through:

1. **Instrumental variables**: Using procedural variables (e.g., number of questions referred) as instruments for citation count
2. **Propensity score matching**: Matching citing holdings on observable characteristics, then comparing those with/without pro-DS precedent citations
3. **Robustness to exclusion**: Testing stability of effects when excluding high-influence observations

---

## 6. Network Metrics and Graph Analysis

### 6.1 Node-Level Metrics

For each case/holding in the internal network, we compute:

| Metric | Definition | Interpretation |
|--------|------------|----------------|
| **In-degree** | Number of cases citing this case | Legal authority/influence |
| **Out-degree** | Number of cases this case cites | Doctrinal embeddedness |
| **PageRank** | Recursive importance score | Authority accounting for citing case importance |
| **Betweenness** | Fraction of shortest paths through node | Bridge between doctrinal areas |
| **Closeness** | Average distance to all other nodes | Accessibility in citation network |
| **Clustering coefficient** | Degree to which neighbors cite each other | Local clustering |

### 6.2 Edge-Level Metrics

| Metric | Definition | Use |
|--------|------------|-----|
| **Temporal distance** | Days between citing and cited judgment | Recency of precedent |
| **Concept similarity** | Jaccard similarity of primary/secondary concepts | Topical relevance |
| **Outcome concordance** | 1 if same ruling direction, 0 otherwise | Doctrinal consistency |

### 6.3 Network-Level Metrics

| Metric | Description |
|--------|-------------|
| **Density** | Proportion of possible edges that exist |
| **Reciprocity** | N/A (citations are unidirectional by construction) |
| **Transitivity** | Global clustering coefficient |
| **Average path length** | Mean geodesic distance |
| **Degree distribution** | Power-law fit for preferential attachment test |
| **Modularity** | Community structure detection |

### 6.4 Community Detection

We apply multiple community detection algorithms to identify substantively coherent citation clusters:

1. **Louvain method**: Modularity optimization
2. **Label propagation**: Fast semi-supervised clustering
3. **Stochastic block models**: Probabilistic community structure

Detected communities are validated against:
- Concept cluster assignments (expected correspondence)
- Chamber assignments (testing for institutional clustering)
- Temporal periods (testing for era-based clustering)

---

## 7. Influence Propagation Analysis

### 7.1 Interpretive Diffusion Model

We model the diffusion of interpretive approaches through the citation network using a discrete-time contagion framework.

**State variable**: For each holding, whether it invokes pro-DS purposes (binary)

**Diffusion mechanism**:
```
P(pro_ds_purpose_i = 1) = α + β × (fraction of cited precedents invoking pro_ds_purpose)
```

**Estimation**: Logistic regression with citation-lagged predictors

### 7.2 Path-Dependent Doctrinal Development

We trace specific doctrinal lines through the citation network:

1. **Article 82 compensation doctrine**: Identify the earliest cases establishing the "actual damage" requirement and trace forward through citations
2. **Strict necessity standard**: Identify cases applying STRICT vs. REGULAR necessity and trace citation inheritance
3. **Grand Chamber leadership**: Test whether Grand Chamber judgments serve as originating points for doctrinal positions

### 7.3 Counterfactual Analysis

Using the network structure, we simulate counterfactuals:

- **What if C-300/21 had ruled differently?** Propagate hypothetical outcome through citing cases
- **Citation rewiring**: Test sensitivity of aggregate outcomes to changes in citation patterns

---

## 8. Robustness and Sensitivity Analyses

### 8.1 Pre-Specified Robustness Checks

| Check | Description | Purpose |
|-------|-------------|---------|
| **External citations only** | Exclude internal citations | Test external precedent effects |
| **Holding-level vs case-level** | Aggregate citations to case level | Test unit of analysis sensitivity |
| **Alternative outcome coding** | Use 3-category DV (pro-DS, pro-controller, indeterminate) | Test binary coding sensitivity |
| **Temporal restriction** | Exclude cases from 2024-2025 | Test stability over time |
| **Outlier exclusion** | Exclude top 5% most-cited and most-citing cases | Test influence of extreme cases |
| **Alternative weighting** | Holding-weighted (cases with more holdings weighted more) | Test weighting sensitivity |
| **Inverse probability weighting** | Weight by 1/holdings per case | Address case-level clustering |

### 8.2 Placebo Tests

- **Randomized citations**: Shuffle citation edges while preserving degree distribution
- **Temporal placebo**: Replace cited case outcomes with cases from same time period but not cited
- **Concept placebo**: Replace cited cases with cases addressing same concepts but not cited

### 8.3 Reporting Standards

Following Simmons, Nelson & Simonsohn (2011), we commit to reporting:
- All primary outcome specifications
- All robustness checks conducted
- Full results regardless of statistical significance
- Sample sizes for all subgroup analyses

---

## 9. Implementation Plan

### 9.1 Technical Requirements

**Python packages**:
- `networkx`: Graph construction and analysis
- `igraph`: High-performance network metrics
- `pandas`, `numpy`: Data manipulation
- `scipy.stats`: Statistical tests
- `statsmodels`: Regression models
- `sklearn`: Machine learning (cross-validation)

**Optional**:
- `graph-tool`: Stochastic block models
- `pyvis` or `gephi`: Network visualization

### 9.2 Script Structure

```
analysis/scripts/
├── 10_citation_network_construction.py      # ✓ IMPLEMENTED - Build graphs from data
├── 11_citation_bivariate_analysis.py        # ✓ IMPLEMENTED - Bivariate tests (Section 4)
├── 12_citation_multivariate_analysis.py     # ✓ IMPLEMENTED - Regression models (Section 5)
├── 13_network_metrics.py                    # ⊘ MERGED INTO 10 - Network statistics
├── 14_influence_propagation.py              # ✓ IMPLEMENTED - Diffusion models (Section 7)
├── 15_citation_robustness.py                # ✓ IMPLEMENTED - Robustness checks (Section 8)
└── 16_advanced_deep_dives.py                # ✓ IMPLEMENTED - Extended analyses (chamber anomaly, mediation, cascades)
```

### 9.3 Output Artifacts

1. **Network data files**: Edgelist, node attributes, computed metrics (CSV/JSON)
2. **Statistical results**: Bivariate tests, regression coefficients, model comparisons (JSON)
3. **Figures**: Network visualizations, metric distributions, temporal patterns (PNG/PDF)
4. **Tables**: Summary statistics, regression tables, robustness comparison (Markdown/LaTeX)
5. **Supplementary findings**: Document extending SUPPLEMENTARY_FINDINGS.md

### 9.4 Quality Assurance

- **Unit tests**: Verify network construction integrity
- **Reproducibility**: Random seeds for all stochastic operations
- **Version control**: All scripts tracked in git
- **Documentation**: Docstrings for all functions, README for scripts directory

---

## 10. Limitations and Scope Boundaries

### 10.1 Data Limitations

1. **Single-coder design**: No inter-coder reliability for citation extraction
2. **External citations**: Incomplete coding (only case ID, not outcome/characteristics)
3. **Citation context**: Citations extracted from text without distinguishing positive/negative/distinguishing citations
4. **Unobserved citations**: Implicit influences not captured by explicit citations

### 10.2 Methodological Limitations

1. **Causal inference**: Observational design cannot establish that citations cause outcomes
2. **Selection effects**: Judges choose which cases to cite (endogeneity)
3. **Sparse network**: 67 internal cases limits statistical power for network analysis
4. **Temporal confounding**: Citation patterns may be confounded with time trends

### 10.3 Scope Boundaries

This methodology does NOT address:
- Citation valence (positive vs. negative citations)
- Paragraph-level citation analysis
- External case characteristics (would require coding non-GDPR CJEU cases)
- Advocate General opinion citations (separate from judgment citations)

---

## 11. Expected Contributions

Successful execution of this methodology will yield:

1. **First network analysis of CJEU GDPR jurisprudence**: Novel contribution to empirical legal literature
2. **Quantified precedent effects**: Empirical estimates of how cited case characteristics predict outcomes
3. **Doctrinal map**: Visual and structural representation of GDPR legal development
4. **Methodological template**: Reusable framework for citation analysis in other legal domains
5. **Extended academic paper**: New section on citation dynamics for ACADEMIC_PAPER.md

---

## Appendix A: Variable Definitions

### A.1 Derived Citation Variables

| Variable | Type | Definition | Formula |
|----------|------|------------|---------|
| `precedent_direction_score` | Continuous [0,1] | Weighted average pro-DS rate of cited internal cases | Σ(w_j × pro_ds_rate_j) / Σw_j |
| `predominantly_pro_ds_precedents` | Binary | Majority of cited precedents pro-DS | 1 if precedent_direction_score > 0.5 |
| `citation_count` | Count | Number of cases cited | Count distinct cited_case |
| `internal_citation_count` | Count | Number of internal corpus cases cited | Count distinct cited_case where is_gdpr_corpus=1 |
| `cites_gc_precedent` | Binary | Cites Grand Chamber case | 1 if any cited_case chamber = GRAND_CHAMBER |
| `precedent_purpose_invocation` | Continuous [0,1] | Prop. of cited cases invoking pro-DS purposes | Count(cited cases with pro_ds_purpose) / total cited |
| `concept_match` | Continuous [0,1] | Prop. of cited cases with same concept cluster | Count(same cluster) / total cited |
| `avg_cited_centrality` | Continuous | Mean PageRank of cited cases | Mean(PageRank of cited cases) |

### A.2 Network Centrality Metrics

| Metric | Interpretation in Legal Context |
|--------|--------------------------------|
| **In-degree** | How often this case is cited as precedent |
| **PageRank** | Importance weighted by citing case importance |
| **Hub score** | Case that cites many authoritative cases |
| **Authority score** | Case cited by many hub cases |
| **Betweenness** | Bridge case connecting different legal domains |

---

## Appendix B: Hypotheses Summary

| ID | Hypothesis | Test | Variables |
|----|-----------|------|-----------|
| H1.1 | Holdings citing pro-DS precedents more likely pro-DS | Chi-square | predominantly_pro_ds_precedents × pro_ds |
| H1.2 | Purpose invocation propagates through citations | Chi-square | cited_purpose × citing_purpose |
| H1.3 | Grand Chamber citation associated with outcomes | Chi-square | cites_gc_precedent × pro_ds |
| H2.1 | Precedent effect persists in multivariate model | Logistic regression | precedent_direction_score (controlling for other vars) |
| H2.2 | Centrality independently associated with outcomes | Logistic regression | centrality metrics |
| H3.1 | Network exhibits preferential attachment | Power-law fit | In-degree distribution |
| H3.2 | Citation clusters match concept clusters | Modularity/NMI | Detected vs. concept clusters |
| H3.3 | Temporal citation patterns reveal trajectories | Network visualization | Time-ordered citation flow |
| H4.1 | Teleological interpretation propagates | Logistic diffusion | cited_teleological × citing_teleological |
| H4.2 | Compensation gap traceable to early cases | Path analysis | Article 82 citation lineage |

---

## References

- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate.
- Freeman, L. C. (1979). Centrality in social networks.
- Fowler, J. H., et al. (2007). Network analysis and the law.
- Landes, W. M., & Posner, R. A. (1976). Legal precedent: A theoretical and empirical analysis.
- Newman, M. E. (2003). The structure and function of complex networks.
- Page, L., et al. (1999). The PageRank citation ranking.
- Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology.

---

## 12. Implementation Status

This methodology has been **fully implemented** with results documented in `CITATION_ANALYSIS_FINDINGS.md`.

### Implemented Analyses

| Section | Status | Key Findings |
|---------|--------|--------------|
| §4 Bivariate | ✓ Complete | H1.2 (purpose propagation) strongly supported (Φ=0.396, p<0.0001) |
| §5 Multivariate | ✓ Complete | Pro-DS purpose OR=7.15 robust; precedent effect attenuates |
| §6 Network Metrics | ✓ Complete | Density 0.050, PageRank computed, centralities analyzed |
| §7 Influence Propagation | ✓ Complete | 59.4% direction concordance, C-300/21 cascade traced |
| §8 Robustness | ✓ Complete | Permutation p<0.0001; Third Chamber exclusion eliminates effect |

### Extended Analyses (Beyond Proposal)

1. **Third Chamber Anomaly**: Deep dive revealing chamber-specific citation dynamics
2. **Formal Mediation Analysis**: Baron-Kenny procedure confirming 25.9% mediated effect
3. **C-300/21 Influence Cascade**: Traced 22-case influence chain
4. **Temporal Structural Breaks**: Identified effect emergence in 2023-2024
5. **Counter-Citation Analysis**: 26.8% rate, concentrated in PRINCIPLES/ENFORCEMENT

### Output Files Generated

```
analysis/output/citation_network/
├── citation_edges.csv
├── case_attributes.csv
├── holding_citation_vars.csv
├── network_metrics.json
├── bivariate_citation_results.json
├── multivariate_citation_results.json
├── influence_propagation_results.json
├── robustness_results.json
└── advanced_deep_dives.json
```

---

*Document version: 2.0*
*Created: 2025-01-19*
*Updated: 2026-01-19*
*Status: FULLY IMPLEMENTED - See CITATION_ANALYSIS_FINDINGS.md for results*
