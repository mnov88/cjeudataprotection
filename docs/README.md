# Documentation

**Start with [`KEY_CLAIMS.md`](KEY_CLAIMS.md)** (the ranked findings ledger) and
[`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) (navigation). This folder also holds the detailed
write-ups, methods, and the codebook.

```
docs/
├── KEY_CLAIMS.md            ★ ranked/graded ledger of every claim + reconciliations
├── REPOSITORY_MAP.md        ★ full directory + analysis-pipeline map
├── findings/                9 detailed analysis write-ups
├── methodology/             4 method docs + 2 PROPOSED_ (unexecuted plans)
├── coding-agent-instructions.md   the 43-question coding schema (codebook)
├── REVISION_PLAN.md         completed post-peer-review changelog
└── FINDINGS_OVERVIEW.md     stub → redirects to KEY_CLAIMS.md
```

### findings/
| Document | Focus |
|----------|-------|
| `ACADEMIC_PAPER.md` | Main paper — full methods + results |
| `JUDICIAL_ANALYSIS_REPORT.md` | Chamber, rapporteur & panel effects |
| `CITATION_ANALYSIS_FINDINGS.md` | Precedent network & purpose propagation |
| `CITATION_CONCORDANCE_ANALYSIS.md` | Directional concordance of citations |
| `COHERENCE_ANALYSIS.md` | Predictability of holdings; "incoherent" flags |
| `PRO_CONTROLLER_ANALYSIS.md` | The 23 pro-controller holdings |
| `PRO_CONTROLLER_NARRATIVE_ANALYSIS.md` | The 11 non-compensation pro-controller rulings |
| `BALANCING_JURISPRUDENCE_ANALYSIS.md` | Explicit rights-balancing |
| `MEANS_ENDS_PROPORTIONALITY_ANALYSIS.md` | The proportionality cascade |

### methodology/
| Document | Status |
|----------|--------|
| `statistical-analysis-methodology.md` | ✅ implemented |
| `judicial-analysis-methodology.md` | ✅ implemented |
| `citation-analysis-methodology.md` | ✅ implemented |
| `temporal-analysis-methodology.md` | ✅ implemented |
| `PROPOSED_judicial-opportunism-methodology.md` | ⚠️ **proposed plan, not run** |
| `PROPOSED_judicial-invention-methodology.md` | ⚠️ **proposed plan, not run** |

### The coding schema (43 answers per case)
`A1–A4` case metadata · `A5–A11` holding + GDPR concept · `A12–A21` interpretive sources ·
`A22–A31` reasoning structure · `A32–A33` ruling direction · `A34–A43` necessity & balancing.
Full definitions: [`coding-agent-instructions.md`](coding-agent-instructions.md).
