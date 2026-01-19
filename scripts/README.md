# Data Processing Scripts

Utilities for parsing, analyzing, and browsing coded CJEU GDPR decisions.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ data/coded/     │     │                  │     │ data/parsed/        │
│ (*_coded.md)    │ ──► │    parser.py     │ ──► │ - cases.json        │
│                 │     │                  │     │ - holdings.csv      │
└─────────────────┘     └──────────────────┘     │ - gdpr_cjeu.db      │
                                                 └─────────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────────┐
                                                 │    viewer.html      │
                                                 │  (interactive UI)   │
                                                 └─────────────────────┘
```

## Scripts

| Script | Description |
|--------|-------------|
| `parser.py` | Parse coded markdown files → JSON, CSV, SQLite |
| `viewer.html` | Interactive browser for exploring cases |
| `extract_judges.py` | Extract judge information from decisions |
| `analyze_rapporteurs.py` | Analyze judge-rapporteur patterns |
| `analyze_rapporteurs_stats.py` | Statistical analysis of rapporteur data |

## Quick Start

### Parse Coded Decisions

```bash
# Parse all coded files
python parser.py ../data/coded/ -o ../data/parsed/

# Parse a single file
python parser.py ../data/coded/C-311-18_coded.md -o ../data/parsed/

# JSON only (skip CSV and SQLite)
python parser.py ../data/coded/ -o ../data/parsed/ --json-only
```

### Interactive Viewer

1. Open `viewer.html` in a browser
2. Click "Load JSON" and select `data/parsed/cases.json`
3. Browse, filter, and search cases

### Judge Analysis

```bash
# Extract judge information
python extract_judges.py

# Analyze rapporteur patterns
python analyze_rapporteurs.py
python analyze_rapporteurs_stats.py
```

## Output Formats

| File | Purpose | Use For |
|------|---------|---------|
| `cases.json` | Complete hierarchical data | Web viewer, programmatic access |
| `holdings.csv` | Flat denormalized data | R, pandas, Excel, statistics |
| `gdpr_cjeu.db` | SQLite database | Complex queries, network analysis |

## SQLite Schema

```sql
-- Main tables
cases          -- One row per case
holdings       -- One row per holding (linked to cases)

-- Junction tables
case_citations    -- Citations between cases
article_references -- Articles each holding references
```

### Example Queries

**Direction breakdown by year:**
```sql
SELECT
    judgment_year,
    ruling_direction,
    COUNT(*) as count
FROM holdings h
JOIN cases c ON h.case_id = c.case_id
GROUP BY judgment_year, ruling_direction
ORDER BY judgment_year;
```

**Most cited cases:**
```sql
SELECT
    cited_case,
    COUNT(*) as times_cited
FROM case_citations
GROUP BY cited_case
ORDER BY times_cited DESC
LIMIT 20;
```

**Article frequency:**
```sql
SELECT
    article_number,
    COUNT(DISTINCT case_id) as cases,
    COUNT(*) as holdings
FROM article_references
GROUP BY article_number
ORDER BY holdings DESC;
```

## Viewer Features

- **Search**: Full-text search across cases and holdings
- **Filters**: Chamber, ruling direction, interpretation source, concept
- **Drill-down**: Expand holdings to see quotes, citations, balancing analysis
- **Statistics**: Aggregate breakdowns with progress bars

## Extending

### Adding New Fields

1. Update `parser.py`:
   - Add to dataclass
   - Parse in `_parse_holding()`
   - Export in `export_csv()` and `export_sqlite()`

2. Update `viewer.html`:
   - Add to display logic
   - Add filters if needed

## Troubleshooting

**Parser errors:**
- Check that coded files match the expected A1-A43 format
- Run with `--strict` to see validation issues

**Missing data:**
- Ensure all A1-A43 fields are present for each holding
- Use `NULL` for empty optional fields

**Viewer not loading:**
- Check browser console for errors
- Verify JSON: `python -m json.tool ../data/parsed/cases.json`
