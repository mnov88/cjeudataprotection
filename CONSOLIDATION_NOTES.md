# Consolidation Notes — June 2026

This repo had accumulated ~20 parallel `claude/*` working branches, duplicate analyses, and
overlapping summary docs, making it hard to tell what was current. This pass consolidated it
into a single `main` branch with a clean navigation layer. Here is exactly what changed and why.

## What was done

1. **Audited all 20 branches** by timestamp and divergence from `main`. The newest real work
   (the judgment-heading + ruling-question-matcher tools, 2026-02-02) lived on
   `claude/add-judgement-headings-M7Kg5`, which was 4 commits ahead of `main` and 0 behind —
   so it became the canonical state and was folded into `main`.

2. **Identified merged vs. unmerged branches.** 12 branches were fully merged into `main`
   (0 unique commits) and are safe to delete. 6 branches held unmerged commits (see below).

3. **Recovered unmerged content where possible.** Salvaged two genuinely-unique documents from
   `claude/court-decision-analysis-1cd5U` into `docs/methodology/`:
   - `PROPOSED_judicial-opportunism-methodology.md`
   - `PROPOSED_judicial-invention-methodology.md`

   These are **unexecuted research plans** (the "is the Court making things up / opportunistically
   expanding rights?" hypotheses), clearly labelled as such.

4. **Added a navigation layer:**
   - `README.md` — rewritten as an ultra-skimmable orientation hub with the 10 headline findings.
   - `docs/KEY_CLAIMS.md` — a new ranked, strength-graded ledger of **every** claim across all
     findings docs, grouped by theme, with a reconciliation section.
   - `docs/REPOSITORY_MAP.md` — a full directory + analysis-pipeline map (decodes the four
     parallel `10–17` script tracks).
   - `docs/FINDINGS_OVERVIEW.md` — reduced to a stub pointing at `KEY_CLAIMS.md` (its content
     was absorbed there) to remove duplicate overviews.

5. **Reconciled conflicting numbers** (full log in `KEY_CLAIMS.md §9`). Headline corrections:
   - **67 cases / 181 holdings** is the analytic dataset; 69 raw judgments exist but
     `C-312-23` and `C-560-21` are uncoded and excluded.
   - The pro-DS-purpose effect is **OR ≈ 3.9 (cluster-robust)**, not the naive 4.49; and it is
     *purpose invocation*, not "teleological method," that predicts outcomes (the old README
     conflated them).
   - The Third Chamber effect is partly compositional but has a genuine residual (revised view
     in `FINDINGS_OVERVIEW`/`ACADEMIC_PAPER` governs over the older `JUDICIAL_ANALYSIS` passage).

6. **Cleanup:** removed committed `.DS_Store` files; corrected `data/README.md` and `docs/README.md`
   to match actual contents.

## Branch status

### Fully merged into `main` — safe to delete (12)
`analyze-gdpr-holdings-7uunF`, `analyze-judgment-citations-o92fz`, `cjeu-pro-controller-analysis-FTi2c`,
`extract-judge-names-exqy7`, `judicial-analysis-methodology-J6UOg`, `organize-files-update-docs-C0Fk1`,
`organize-structure-docs-87Yks`, `review-docs-outliers-tKfZS`, `review-topic-clustering-gGZAT`,
`statistical-analysis-methodology-cTipf`, `temporal-analysis-planning-K3IuX`, `topic-focus-graphs-ayuok`.

### Unmerged — review before deleting (6)
| Branch | Unique commits | Status |
|--------|---------------|--------|
| `court-decision-analysis-1cd5U` | 2 | ✅ **content recovered** into `docs/methodology/PROPOSED_*` |
| `consolidate-reports-summary-HS9Hx` | 2 | ⚠️ not recovered — see note |
| `coder-comparison-ui-QnqBH` | 2 | ⚠️ not recovered (a coder-comparison web UI tool) |
| `gdpr-cjeu-chapter-E5G9Z` | 1 | ⚠️ not recovered (an "empirical overview chapter") |
| `analyze-judge-specialization-UGH1F` | 1 | ⚠️ not recovered (judge-specialization analysis) |
| `add-printable-reports-g4C1F` | 1 | ⚠️ not recovered (a report-formatting enhancement) |

> **Why "not recovered":** this clone's packfile is partially unreadable in the working
> environment — `git` diff/tree/show operations on those specific branch objects fail with
> bus errors (the original `git clone` also reported "possible repository corruption"). The
> commit metadata is intact, so **the content still exists on GitHub (`origin`)**. None of the
> six are likely to contain irreplaceable findings (they are tooling, a draft chapter, an
> overlapping summary, and one analysis that the merged `JUDICIAL_ANALYSIS_REPORT.md` already
> covers), but they were **kept, not deleted**, so you can recover them from GitHub if wanted:
> `git fetch origin && git checkout origin/claude/<branch>`.

## ⚠️ One manual step is needed to finish

All the **file changes above are already saved** in your working folder. But the git commit and
branch surgery **could not be performed inside the Cowork sandbox**: a stale `.git/index.lock`
(left by a git process that crashed on this environment's flaky filesystem) could not be removed
there, so git refused to write. Everything is staged and ready; you just need to run one script
locally, where git works normally:

```bash
bash finish-consolidation.sh     # commits changes, fast-forwards main, deletes the feature branch
```

Then publish and clean the remote:

```bash
git push origin main
bash cleanup-remote-branches.sh  # prints what it will do, asks before deleting the 12 merged branches
```

`cleanup-remote-branches.sh` deletes **only** the 12 verified-merged branches and leaves the 6
unmerged ones for you to review.

_Consolidated 2026-06-12. (Working-tree changes complete; run `finish-consolidation.sh` to commit.)_
