# Key Claims Ledger

**The complete, ranked, and grouped inventory of every substantive claim in this repository.**
Use this as the single place to find what the project actually argues, how strong each
claim is, and where to verify it. For a 2-minute orientation, read the root
[`README.md`](../README.md) instead.

- **Dataset:** 181 coded holdings from 67 CJEU GDPR cases (judgments 2019 – Jan 2025).
- **Outcome variable:** ruling direction — `PRO_DATA_SUBJECT` vs. `PRO_CONTROLLER` / `MIXED` / `NEUTRAL`.
- **Strength legend:** 🟢 **Strong** (regression / significant / robust across specifications) ·
  🟡 **Moderate** (significant but attenuates under controls, or modest N) ·
  🟠 **Weak** (small subgroup / exploratory / anecdotal) · ⚪ **Descriptive** (a count or rate, no test).

> Where a number is quoted differently across source documents, the value here is the most
> defensible one and the discrepancy is logged in [§9 Reconciliation](#9-reconciliation--contested-points).

---

## 1. The ten headline findings (ranked)

| # | Claim | Numbers | Strength | Where |
|---|-------|---------|----------|-------|
| 1 | **Most GDPR holdings favor data subjects** | 60.8% pro-DS (110/181); 12.7% pro-controller, 15.5% mixed, 11.0% neutral | ⚪ | base rate |
| 2 | **Invoking a protective *purpose* is the single strongest predictor of a pro-DS ruling** — i.e. when the Court explicitly names "high level of protection" or "fundamental rights" | 69.6% pro-DS when invoked vs. 32.6% when not; cluster-robust **OR ≈ 3.9** (p=0.008); robust across 5 model specifications | 🟢 | `ACADEMIC_PAPER`, `ANALYSIS_REPORT` |
| 3 | **Strict-necessity scrutiny almost always helps the data subject** (counterintuitive) | Data subjects win **86%** under strict necessity (19/22) vs. **37%** under regular necessity; OR=10.86 (p=0.001) | 🟢 | `ANALYSIS_REPORT`, `MEANS_ENDS` |
| 4 | **The Third Chamber is markedly less pro-DS than the Grand Chamber** | 34% vs. 78% pro-DS — a 43.5pp gap (p<0.001). **Persists** after removing compensation cases (OR=0.21, p=0.014) | 🟢 | `JUDICIAL_ANALYSIS`, `ACADEMIC_PAPER` |
| 5 | **The "compensation gap": Article 82 damages cases are far less pro-DS** | 36% pro-DS vs. 67% for everything else — 30.8pp gap (p<0.001). Doctrine crystallized fast: 97% of comp. holdings are from 2023–24 | 🟢 | `ANALYSIS_REPORT`, `PRO_CONTROLLER` |
| 6 | **Outcome depends heavily on subject-matter** | SCOPE cluster 88% pro-DS, RIGHTS 81%, ENFORCEMENT only 46%. Multivariate OR ≈ 7.7 for both SCOPE and RIGHTS vs. baseline | 🟢 | `ACADEMIC_PAPER` |
| 7 | **The apparent decline in pro-DS rulings over time is compositional, not a real doctrinal shift** | Drop from ~86% (2020) to ~54% (2024) is non-significant (p=0.19) and disappears once the Article 82 surge is removed | 🟢 | `FINDINGS_OVERVIEW`, `ACADEMIC_PAPER` |
| 8 | **Protective reasoning propagates through citation chains** | Holdings citing high-purpose precedents invoke protective purposes 90.7% vs. 54.1% (Φ=0.396, OR=8.29, p<0.0001); purpose mediates ~26% of the citation→outcome effect | 🟡 | `CITATION_ANALYSIS` |
| 9 | **Apparent "judge effects" are mostly topic allocation, not bias** | Rapporteur effects (Rossi +25pp, Jääskinen −25pp) vanish within-topic once compensation cases are excluded (p>0.3); 86% of comp. cases went to one rapporteur | 🟢 | `JUDICIAL_ANALYSIS` |
| 10 | **When the Court names a "winner" in explicit balancing, the outcome is near-deterministic** — suggesting balancing language is often post-hoc justification | Data-subject named winner → 95% pro-DS (N=20); controller named winner → 0% pro-DS (N=3) | 🟠 | `SUPPLEMENTARY`, `ACADEMIC_PAPER` |

---

## 2. Outcomes & base rates

- ⚪ 181 holdings: **60.8% pro-DS** (110), 12.7% pro-controller (23), 15.5% mixed (28), 11.0% neutral (20).
- 🟢 **Concept cluster drives outcomes** (multivariate, Model 3, AIC=222.3, pseudo-R²=0.232):
  SCOPE 88.2% (N=17), RIGHTS 81.0% (N=21), LAWFULNESS mid, **ENFORCEMENT 46.2%** (N=65, the largest and least pro-DS cluster). RIGHTS OR≈7.78 (p=0.018), SCOPE OR≈7.69 (p=0.029) vs. the OTHER cluster.
- 🟠 **Secondary concept** swings are large but small-N: TRANSPARENCY 100% pro-DS (N=6), DATA_PROTECTION_PRINCIPLES 84.6% (N=13), **MEMBER_STATE_DISCRETION only 12.5%** (N=8) — a 72pp spread (largest raw effect in the data, but underpowered).
- ⚪ 66% of multi-holding cases are directionally **split** (mixed within a single case); only 34% unanimous.

## 3. Interpretive method

- 🟢 **Naming a protective purpose** (high-level-of-protection / fundamental-rights) → cluster-robust OR≈3.9 (p=0.008); naive OR=4.49, GEE 3.91, inverse-weighted 4.95. **This is the project's most robust predictor.**
- 🟢 **Caveat — "teleological method" itself does NOT predict outcome.** Teleological interpretation appears in 92.3% of holdings (near-ubiquitous), so it has no discriminating power (Φ=0.042, p=0.572). It is the *content* of the purpose, not the presence of teleology, that matters. *(The old README phrasing "teleological interpretation increases odds 3.89x" was imprecise; corrected here.)*
- 🟢 **Systematic-dominant** interpretation is *negatively* associated with pro-DS outcomes (OR=0.36, p=0.037). Teleological-dominant 73.7% pro-DS; semantic-dominant 61.9%; systematic-dominant 44.4%.
- 🟡 **Level-shifting** (jumping from text to principle to resolve ambiguity) looks pro-DS in naive analysis (81.8% vs. 57.9%, p=0.054) but **becomes non-significant after clustering** (OR=1.62, p=0.486) — it co-occurs with purpose invocation 91% of the time, so it adds nothing independently.
- ⚪ Principle-based reasoning structure: 77.4% pro-DS (highest); case-law-based: 51.3% (lowest).

## 4. Institutional, chamber & judge effects

- 🟢 **Grand Chamber 77.6%** pro-DS (N=49) vs. **Third Chamber 34.1%** (N=41). Bivariate Cramér's V=0.327 (p=0.0007). Robust across all six specification-curve variants and to single-case removal.
- 🟢 **The Third Chamber effect is partly compositional but not only compositional.** The Third Chamber gets 63% of ENFORCEMENT cases and 59% of all compensation holdings (Grand Chamber: 2%). Removing compensation shrinks the gap from 43pp to 36pp but it remains significant (OR=0.21, p=0.014) — compensation explains only ~17% of it. *(This reconciles a tension between earlier `JUDICIAL_ANALYSIS` text and the revised `FINDINGS_OVERVIEW`; see §9.)*
- 🟡 Third Chamber effect **attenuates to marginal** (OR=0.21, p=0.051) once year fixed effects are added — temporal confounding is real but doesn't erase it.
- 🟢 **Rapporteur effects are real bivariately** (χ²(13)=26.24, p=0.016; Rossi 81.2% pro-DS N=32, Jääskinen 43.1% N=51) **but disappear within-topic** once compensation is excluded (Jääskinen p=0.865, Rossi p=0.318). Rossi retains a small unexplained positive residual (+18pp). **Read as specialization, not ideology.**
- 🟢 **Individual judge / panel effects are not identifiable** — the panel co-occurrence network is too dense (density 0.670, clustering 0.878); no individual judge effect survives FDR correction.
- ⚪ Only 1 of 23 pro-controller holdings came from the Grand Chamber (C-807/21, the fault-for-fines ruling).

## 5. Balancing & proportionality

- ⚪ Of 41 holdings with explicit balancing, **data protection prevails 68.3%**, a competing interest 9.8%, mixed 22.0%.
- ⚪ **The Court never rejects a claimed objective as illegitimate** — advertising, road safety, anti-corruption, national security, law enforcement all pass the "legitimacy filter." The real work happens at the **necessity / proportionality** stage (the "proportionality cascade": legitimacy → necessity → less-restrictive-means → proportionality *stricto sensu*).
- ⚪ Competing interests almost only win in **judicial-independence / open-justice** cases (the one category where data protection reliably yields). Commercial interests never beat data protection outright (0/5 economic-interest cases).
- 🟠 Strict-necessity result (headline #3) is presented as a **key finding** in `MEANS_ENDS` but flagged as **exploratory / hypothesis-generating** in `ACADEMIC_PAPER` (small subgroups N=22/19); multivariate OR reduces to 4.06 (p=0.061). Treat as strong-but-not-confirmatory.
- Illustrative Grand Chamber proportionality cases: C-184/20 (anti-corruption declarations), C-439/19 (penalty-point publication), C-311/18 (Schrems II), C-252/21 (Meta cross-platform tracking), C-205/21 (blanket biometrics).

## 6. The compensation (Article 82) story

- 🟢 36 compensation holdings (19.9% of data), only **36.1% pro-DS** vs. 66.9% elsewhere (30.8pp gap). Most-contested domain: 33% pro-controller, 25% mixed.
- ⚪ Settled restrictive doctrine: **mere infringement ≠ compensation; actual damage must be proven** (C-300/21, C-507/23, C-687/21, C-741/21); Article 82 is **purely compensatory, not punitive** (C-590/22, C-667/21, C-655/23); **fear of future misuse** without access is not damage (C-687/21).
- ⚪ Two-track enforcement design: **public** (DPA fines, deterrent — but fault required, C-807/21) vs. **private** (Article 82 damages, compensatory only).
- 🟠 **The "compensation paradox":** 10 comp. holdings (27.8%) invoke protective purposes yet still rule against the data subject. Two framings coexist in the repo — a *normative deficiency* (`ACADEMIC_PAPER`) vs. *deliberate enforcement-channeling policy* (`PRO_CONTROLLER`). Unresolved; see §9.

## 7. Citation network

- ⚪ Network: 639 citation edges (276 internal, 363 external) over 67 cases; internal density 0.050.
- 🟢 **Citations are directionally concordant above chance** — 59.4% over all 276 internal pairs (p=0.001), or 66.8% over the 238 classifiable pairs (p<10⁻⁶). Both numbers are correct on different denominators (see §9).
- 🟢 **Purpose propagation** (headline #8): high-purpose precedents → 90.7% purpose invocation downstream (OR=8.29, p<0.0001); Baron–Kenny mediation: purpose carries ~26% of the citation→outcome effect (Sobel z=2.196, p=0.028).
- 🟡 The **direct** citation-direction→outcome link (r=0.286, p=0.001) **attenuates to non-significance under full controls** and is **chamber-specific**: it lives in the Third Chamber (r=0.320) and vanishes in the Grand Chamber (r=−0.039). It only emerged in 2023–24, tracking the compensation surge.
- ⚪ **C-300/21** is the restrictive-compensation anchor: most-cited (11 internal / 25 total), influence reaches 22 cases; its citers average just 37% pro-DS. **C-175/20** is the most coherently applied anchor (92% concordance); **C-340/21** is the biggest doctrinal pivot (only 33% concordance).

## 8. Temporal evolution

- 🟢 **No genuine doctrinal drift.** Apparent pro-DS decline (86%→54%) is non-significant (χ² p=0.19; trend p=0.10) and ~67% explained by the compensation surge (counterfactual without comp.: 65% vs. 57% actual).
- 🟢 **Method is stable over time** — purpose effect identical early vs. late (OR=4.82 both; interaction p=0.999); the three interpretive methods each appear in >90% of holdings throughout.
- 🟢 **What *did* change is composition:** Grand Chamber's share of holdings fell 56%→16% while the Third Chamber's rose 6%→30% (p=0.001); GDPR self-citation rose 31%→83% (p<0.0001); case-law-based reasoning rose 10%→26% (p=0.014) — i.e. the field is consolidating and self-referencing.

---

## 9. Reconciliation & contested points

Read this before quoting any single number.

**Dataset counts (67 vs 69).** There are **69 raw judgment files** in `data/decisions/` but only **67 are coded** — `C-312-23` and `C-560-21` are present as text but were never coded into the schema, so they are **excluded** from all 181-holding statistics. Quote **67 cases / 181 holdings** for any analytic claim. (Scripts that say "69 judgements," e.g. the heading/parser tools, operate on the raw-text corpus, not the coded dataset.)

**The pro-DS-purpose odds ratio** appears as 4.49 (naive Model 3), **3.89 (cluster-robust — use this one)**, 4.21 (coherence model), and 7.15 (citation model). All are the same predictor under different control sets. Headline value: **≈ 3.9** (cluster-robust is the methodologically preferred estimate given ICC=0.295).

**Third Chamber effect — "real or artifact?"** `JUDICIAL_ANALYSIS_REPORT.md` contains an earlier passage attributing the gap "largely" to case allocation; `FINDINGS_OVERVIEW.md` and `ACADEMIC_PAPER.md` carry the revised, better-supported conclusion that a genuine residual effect persists after excluding compensation (OR=0.21, p=0.014). **The revised view governs.** Honest summary: partly compositional, partly genuine, partly temporal.

**Citation concordance 59.4% vs 66.8%.** Same analysis, different denominator: 59.4% counts all 276 internal pairs; 66.8% drops 38 "mixed-direction" cited cases (238 classifiable). Neither is wrong.

**C-300/21 citation count 11 vs 25.** 11 = internal-corpus citations; 25 = all citations including external/aggregated. Both appear in the citation docs.

**Strict-necessity finding** is a confirmed "key finding" in `MEANS_ENDS_PROPORTIONALITY_ANALYSIS.md` but an "exploratory / hypothesis-generating" result in `ACADEMIC_PAPER.md` (subgroups of 22 and 19). Treat as strong signal, not settled.

**`analysis/SUPPLEMENTARY_FINDINGS.md` is older** (dated Jan 2025, before the other 2026 outputs) and exploratory — its small-subgroup numbers may rest on a smaller sample. Use it for hypotheses, not headline claims.

**Coder reliability.** All coding was done by a single coder/agent with **no formal inter-coder reliability** assessment — a stated limitation. The ruling-direction tie-breaker heuristic is literally "if Google's General Counsel would be annoyed, it's PRO_DATA_SUBJECT."

---

## 10. Proposed but NOT YET executed

These read like findings but are **unexecuted research plans** — do not cite them as results:

- **`docs/methodology/PROPOSED_judicial-opportunism-methodology.md`** — a design to test whether "the Court picks interpretive methods to fit desired outcomes, mostly to expand rights" (H1 methodological opportunism, H2 systematic pro-rights skew). All result cells are blank; only outline code exists.
- **`docs/methodology/PROPOSED_judicial-invention-methodology.md`** — a design to test whether "the Court invents GDPR content not in the text, mostly to expand rights." Result table is all `?`; requires new text-vs-holding coding not yet done.
- **`docs/REVISION_PLAN.md`** — by contrast, this is *completed* work: a post-peer-review log marking 8/9 reviewer items DONE (inverse-weighted regression, year-FE robustness, temporal decomposition). Only inter-coder reliability and AG-opinion analysis remain open (both need new data).

*(These two PROPOSED docs were recovered from an unmerged branch during consolidation — see [`../CONSOLIDATION_NOTES.md`](../CONSOLIDATION_NOTES.md).)*

---

## Source documents

| Code used above | File |
|---|---|
| `ACADEMIC_PAPER` | `docs/findings/ACADEMIC_PAPER.md` — main paper |
| `ANALYSIS_REPORT` | `analysis/ANALYSIS_REPORT.md` — core statistics |
| `JUDICIAL_ANALYSIS` | `docs/findings/JUDICIAL_ANALYSIS_REPORT.md` |
| `CITATION_ANALYSIS` | `docs/findings/CITATION_ANALYSIS_FINDINGS.md` (+ `CITATION_CONCORDANCE_ANALYSIS.md`) |
| `COHERENCE` | `docs/findings/COHERENCE_ANALYSIS.md` |
| `PRO_CONTROLLER` | `docs/findings/PRO_CONTROLLER_ANALYSIS.md` (+ `_NARRATIVE_`) |
| `BALANCING` | `docs/findings/BALANCING_JURISPRUDENCE_ANALYSIS.md` |
| `MEANS_ENDS` | `docs/findings/MEANS_ENDS_PROPORTIONALITY_ANALYSIS.md` |
| `SUPPLEMENTARY` | `analysis/SUPPLEMENTARY_FINDINGS.md` |
| `FINDINGS_OVERVIEW` | `analysis/output/temporal/TEMPORAL_ANALYSIS_SYNTHESIS.md` + cross-cutting synthesis |

_Last consolidated: 2026-06-12._
