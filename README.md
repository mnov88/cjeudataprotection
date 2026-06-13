# CJEU GDPR Jurisprudence — Empirical Analysis

An empirical study of how the Court of Justice of the EU (CJEU) decides GDPR cases:
**who wins, and what predicts it.** 67 cases, 181 coded holdings, 2019 – January 2025.

> **New here? Read these two files and nothing else:**
> 1. The headline findings table just below.
> 2. [`docs/KEY_CLAIMS.md`](docs/KEY_CLAIMS.md) — every claim, ranked, grouped, and graded by strength, with the caveats.

---

## The findings in one glance

| # | Finding | The number |
|---|---------|-----------|
| 1 | Most holdings favor data subjects | **60.8%** pro-data-subject |
| 2 | Naming a *protective purpose* ("high level of protection" / "fundamental rights") is the strongest predictor of a win | **≈3.9× odds**, p=0.008 |
| 3 | Strict-necessity scrutiny almost always helps the data subject | **86% vs 37%** win rate |
| 4 | The Third Chamber is far less pro-data-subject than the Grand Chamber | **34% vs 78%** |
| 5 | Compensation (Article 82) cases are the exception — much less pro-data-subject | **36% vs 67%** |
| 6 | Subject-matter matters most: scope/rights cases win, enforcement cases don't | 88% / 81% / **46%** |
| 7 | The "decline" in data-subject wins over time isn't real — it's the rise of compensation cases | non-significant (p=0.19) |
| 8 | Protective reasoning spreads through citation chains | OR=8.29, p<0.0001 |
| 9 | Apparent "judge bias" is mostly which topics a judge handles, not ideology | effects vanish within-topic |
| 10 | When the Court names a balancing "winner," the result is near-automatic (likely post-hoc) | 95% vs 0% |

Full detail, strength grades, and every reconciled discrepancy: **[`docs/KEY_CLAIMS.md`](docs/KEY_CLAIMS.md)**.

---

## Where everything lives

```
.
├── README.md                ← you are here (orientation)
├── docs/
│   ├── KEY_CLAIMS.md         ★ the ranked claim ledger — start here for findings
│   ├── REPOSITORY_MAP.md     ★ full directory + analysis-pipeline map
│   ├── findings/             9 detailed analysis write-ups (see index below)
│   ├── methodology/          how each analysis was done (+ 2 PROPOSED, unexecuted)
│   ├── coding-agent-instructions.md   the 43-question coding schema
│   └── REVISION_PLAN.md      post-peer-review changelog (completed)
├── data/
│   ├── decisions/            69 raw judgment texts (67 coded — see note)
│   ├── coded/                67 coded judgments (43-question schema)
│   ├── parsed/               machine-readable: cases.json · holdings.csv · gdpr_cjeu.db
│   ├── metadata/             EUR-Lex case metadata
│   └── li-case-law/          SECONDARY sub-study: "legitimate interest" cases (18, separate)
├── analysis/
│   ├── ANALYSIS_REPORT.md     core statistical findings
│   ├── scripts/              numbered pipeline, 4 tracks (stats · citation · judicial · temporal)
│   └── output/               all results: JSON, CSV, figures, per-track syntheses
├── scripts/                  data tooling: parser, viewers, judge extractor, heading/parser tools
└── CONSOLIDATION_NOTES.md    what the June-2026 cleanup did + branch status
```

Full navigation, including what each of the ~30 analysis scripts does and how the
parallel pipelines fit together, is in **[`docs/REPOSITORY_MAP.md`](docs/REPOSITORY_MAP.md)**.

### The 9 detailed findings docs

| Document | Focus |
|----------|-------|
| [ACADEMIC_PAPER](docs/findings/ACADEMIC_PAPER.md) | The main paper — full methods + results |
| [JUDICIAL_ANALYSIS_REPORT](docs/findings/JUDICIAL_ANALYSIS_REPORT.md) | Chamber, rapporteur & panel effects |
| [CITATION_ANALYSIS_FINDINGS](docs/findings/CITATION_ANALYSIS_FINDINGS.md) | Precedent network & propagation |
| [CITATION_CONCORDANCE_ANALYSIS](docs/findings/CITATION_CONCORDANCE_ANALYSIS.md) | Directional concordance of citations |
| [COHERENCE_ANALYSIS](docs/findings/COHERENCE_ANALYSIS.md) | How predictable each holding is |
| [PRO_CONTROLLER_ANALYSIS](docs/findings/PRO_CONTROLLER_ANALYSIS.md) | The 23 pro-controller holdings |
| [PRO_CONTROLLER_NARRATIVE_ANALYSIS](docs/findings/PRO_CONTROLLER_NARRATIVE_ANALYSIS.md) | The 11 non-compensation pro-controller rulings |
| [BALANCING_JURISPRUDENCE_ANALYSIS](docs/findings/BALANCING_JURISPRUDENCE_ANALYSIS.md) | Explicit rights-balancing |
| [MEANS_ENDS_PROPORTIONALITY_ANALYSIS](docs/findings/MEANS_ENDS_PROPORTIONALITY_ANALYSIS.md) | The proportionality cascade |

---

## Quick start

**Just want the answers?** → [`docs/KEY_CLAIMS.md`](docs/KEY_CLAIMS.md).

**Explore the data:**
```bash
sqlite3 data/parsed/gdpr_cjeu.db "SELECT ruling_direction, COUNT(*) FROM holdings GROUP BY 1;"
# or open the browser viewer:
open scripts/viewer.html
```

**Re-run the statistical pipeline:**
```bash
pip install pandas numpy scipy statsmodels scikit-learn
cd analysis && python scripts/run_analysis.py        # or run 01_*.py … 17_*.py in order
```

**Re-parse coded decisions into the dataset:**
```bash
python scripts/parser.py data/coded/ -o data/parsed/
```

---

## Three things to know before you cite a number

1. **67 cases / 181 holdings** is the analytic dataset. There are 69 raw judgment files;
   `C-312-23` and `C-560-21` are present as text but **uncoded**, so they are excluded from all statistics.
2. **"Teleological method" does not predict outcomes** — it appears in 92% of holdings. What predicts a
   win is the Court explicitly *naming a protective purpose*. (An earlier version of this README blurred the two.)
3. **Two documents in `methodology/` prefixed `PROPOSED_`** are unexecuted plans (the "is the Court making
   things up?" hypotheses), **not findings.** See [`docs/KEY_CLAIMS.md` §10](docs/KEY_CLAIMS.md#10-proposed-but-not-yet-executed).

---

## Method, in brief

- **Unit of analysis:** the individual holding (N=181), nested within 67 cases (clustering handled via
  cluster-robust SEs; ICC=0.295).
- **Coding:** a 43-question schema (metadata → concept → interpretation → balancing → outcome), single coder,
  no formal inter-coder reliability ([schema](docs/coding-agent-instructions.md)).
- **Tests:** χ²/Fisher with Benjamini-Hochberg FDR correction (bivariate); hierarchical logistic regression
  with 6 nested models, plus mixed-effects, GEE, and inverse-holding-weighted robustness checks.
- Full methods: [`docs/methodology/`](docs/methodology/).

## Citation

> [Author]. (2025). *Factors Associated with Pro-Data-Subject Rulings in CJEU GDPR Jurisprudence:
> Interpretive Methods, Institutional Factors, and the Compensation Gap.*

## License

Academic research use. See individual files for specific terms.
