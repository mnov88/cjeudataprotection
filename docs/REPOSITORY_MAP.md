# Repository Map

A complete tour of what is where and how it connects. For the *findings*, see
[`KEY_CLAIMS.md`](KEY_CLAIMS.md); for orientation, the root [`README.md`](../README.md).

---

## The pipeline at a glance

```
data/decisions/  ──(manual coding, 43-Q schema)──►  data/coded/
        │                                                │
        │                                       (scripts/parser.py)
        │                                                ▼
        │                                         data/parsed/  (cases.json · holdings.csv · gdpr_cjeu.db)
        │                                                │
        │                            ┌───────────────────┼───────────────────┬──────────────────┐
        │                            ▼                   ▼                   ▼                  ▼
        │                    analysis (stats)    citation track      judicial track     temporal track
        │                            │                   │                   │                  │
        │                            └─────────► analysis/output/ ◄──────────┴──────────────────┘
        │                                                │
        └──────────────► docs/findings/  ◄───────(human-written write-ups synthesizing output)
```

---

## `data/` — the corpus and the dataset

| Path | What | Count |
|------|------|-------|
| `data/decisions/` | Raw CJEU judgment texts (Markdown), `C-{num}-{yr}.md` | **69 files** |
| `data/coded/` | Coded holdings, one `*_coded.md` per case (schema A1–A43) | **67 files** |
| `data/parsed/cases.json` | Hierarchical case→holding data (web viewer / programmatic) | 67 cases |
| `data/parsed/holdings.csv` | Flat holding-level table (R / pandas / stats) | 181 holdings |
| `data/parsed/gdpr_cjeu.db` | SQLite of the same, for queries | — |
| `data/parsed/backup/` | Previous versions of the three parsed files (kept for safety) | — |
| `data/metadata/cases_metadata.json` | EUR-Lex metadata (parties, URLs, articles) | — |
| `data/ruling_question_mappings.json` | Output of the heading/ruling-matcher tool (maps operative rulings to questions across the 69-judgment raw corpus) | — |
| `data/planned-features/` | A research note on operative-part extraction tooling (Docling/BERT) — background reading, not part of the analysis | 1 file |

> **69 vs 67:** `C-312-23` and `C-560-21` exist as raw text but were never coded, so all
> statistics use **67 cases / 181 holdings**. See [`KEY_CLAIMS.md` §9](KEY_CLAIMS.md#9-reconciliation--contested-points).

### `data/li-case-law/` — secondary "legitimate interest" sub-study
A **separate, smaller** dataset focused on Article 6(1)(f) legitimate-interest case law:
18 judgments, 16 coded (`coded/`), parsed to `parsed/li_cases.{json,csv}`. It is **not** part
of the 181-holding main analysis. Browse it with `scripts/li-viewer.html`.

---

## `analysis/` — statistics and results

Top-level write-ups: [`ANALYSIS_REPORT.md`](../analysis/ANALYSIS_REPORT.md) (core findings) and
[`SUPPLEMENTARY_FINDINGS.md`](../analysis/SUPPLEMENTARY_FINDINGS.md) (older, exploratory).

### `analysis/scripts/` — four pipelines sharing a number space
The scripts are numbered, but **four parallel tracks reuse the same `10–17` prefixes**, which is the
single most confusing thing in the repo. Here is the decoder. Run everything via
`run_analysis.py`, or each track in order.

**Core statistics (run first):**
`01_data_preparation` → `02_bivariate_analysis` → `03_multivariate_analysis` →
`04_quality_check` → `05_third_chamber_investigation` → `06_mixed_effects_models` →
`07_compensation_paradox` → `08_reviewer_response_analysis` → `09_advanced_topic_analysis`

**Citation track:** `10_citation_network_construction` → `11_citation_bivariate_analysis` →
`12_citation_multivariate_analysis` → `14_influence_propagation` → `15_citation_robustness` →
`15_method_selfcitation_analysis` → `16_advanced_deep_dives` → `17_citation_concordance_analysis`

**Judicial track:** `10_judicial_data_preparation` → `11_judicial_descriptive_analysis` →
`12_judicial_bivariate_analysis` → `13_judicial_multivariate_analysis` →
`14_judicial_robustness_checks` → `15_supplementary_judicial_analysis`

**Temporal track:** `10_temporal_phase1_descriptive` → `11_temporal_phase2_bivariate` →
`12_temporal_phase3_multivariate` → `13_temporal_phase4_decomposition` → `14_temporal_deep_dive`

**Topic / coherence (standalone):** `12_topic_focus_graphs`, `16_coherence_residual_analysis`

### `analysis/output/` — every result file
| Subdir / file | Track | Contents |
|---|---|---|
| `*.json`, `*.csv` at top level | core stats | bivariate/multivariate results, model comparison, final coefficients, compensation paradox, third-chamber investigation, mixed-effects, quality checks |
| `citation_network/` | citation | edges, node centralities, network metrics, mediation/influence, robustness |
| `citation_concordance/` | citation | concordance analysis + citation pairs |
| `coherence/` | coherence | model results + per-holding residuals (which holdings are "incoherent") |
| `temporal/` | temporal | **7 synthesis `.md` files** (PHASE1–4, DEEP_DIVE, METHOD_SELFCITATION, and `TEMPORAL_ANALYSIS_SYNTHESIS.md` — the readable summary) plus JSON results |
| `topic_focus/` | topic | the figures (PNG+PDF): concept clusters, articles over time, heatmaps |

---

## `docs/` — documentation

| Path | What |
|------|------|
| [`KEY_CLAIMS.md`](KEY_CLAIMS.md) | ★ Ranked, graded ledger of every claim + reconciliations |
| `REPOSITORY_MAP.md` | ★ This file |
| `findings/` | 9 detailed write-ups (indexed in the README) |
| `methodology/` | 4 method docs (statistical, judicial, citation, temporal) + 2 `PROPOSED_*` |
| `coding-agent-instructions.md` | The 43-question coding schema (the codebook) |
| `REVISION_PLAN.md` | Completed post-peer-review changelog |

> `docs/methodology/PROPOSED_*.md` are **unexecuted research plans**, not results
> (the "judicial opportunism" / "judicial invention" hypotheses). See [`KEY_CLAIMS.md` §10](KEY_CLAIMS.md#10-proposed-but-not-yet-executed).
> `docs/FINDINGS_OVERVIEW.md` is retained as a stub pointing here — its content was absorbed into `KEY_CLAIMS.md`.

---

## `scripts/` — tooling (not analysis)

| File | Purpose |
|------|---------|
| `parser.py` | Coded decisions (`data/coded/`) → `cases.json` / `holdings.csv` / `gdpr_cjeu.db` |
| `viewer.html` | Interactive browser for the main coded dataset |
| `li-viewer.html` | Browser for the legitimate-interest sub-study |
| `parse_li_cases.py` | Parser for the LI sub-study |
| `extract_judges.py` | Extract judge/rapporteur names from judgments |
| `analyze_rapporteurs.py`, `analyze_rapporteurs_stats.py` | Rapporteur tabulations feeding the judicial track |
| `add_judgement_headings.py` | Inserts Markdown section headings into raw judgment texts |
| `match_rulings_to_questions.py` | Maps operative rulings to referred questions (→ `data/ruling_question_mappings.json`) |
| `cjeu-judgement-parser.js` + `cjeu-parser-demo.html` | Standalone browser JS parser for CJEU judgments |

---

## Provenance

This layout is the result of a June 2026 consolidation that merged ~20 parallel working
branches into a single `main`, recovered unmerged content, reconciled conflicting numbers,
and added this navigation layer. Details and the branch-cleanup script:
[`../CONSOLIDATION_NOTES.md`](../CONSOLIDATION_NOTES.md).
