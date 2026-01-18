# GDPR CJEU Case Analyzer

A complete toolkit for parsing, analyzing, and browsing coded CJEU GDPR decisions.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ *_coded.md      │     │                  │     │ cases.json          │
│ (your coded     │ ──► │  parse_coded.py  │ ──► │ holdings.csv        │
│  judgments)     │     │                  │     │ gdpr_cjeu.db        │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────────┐
                                                 │  viewer/index.html  │
                                                 │  (interactive UI)   │
                                                 └─────────────────────┘
```

## Quick Start

### 1. Parse Your Coded Files

```bash
# Parse a single file
python3 parser/parse_coded.py path/to/C-123-45_coded.md -o output/

# Parse all coded files in a directory
python3 parser/parse_coded.py coded_judgments/ -o output/

# JSON only (skip CSV and SQLite)
python3 parser/parse_coded.py coded_judgments/ -o output/ --json-only
```

### 2. Outputs

| File | Purpose | Use For |
|------|---------|---------|
| `cases.json` | Complete hierarchical data | Web viewer, programmatic access |
| `holdings.csv` | Flat denormalized data | R, pandas, Excel, statistical analysis |
| `gdpr_cjeu.db` | SQLite database | Complex queries, aggregations, network analysis |

### 3. Interactive Viewer

1. Open `viewer/index.html` in a browser
2. Click "Load JSON" and select `output/cases.json`
3. Browse, filter, search, and drill down into cases

## Analysis with SQLite

The SQLite database has these tables:

```sql
-- Main tables
cases          -- One row per case
holdings       -- One row per holding (linked to cases)

-- Junction tables for many-to-many relationships
case_citations    -- Citations between cases
article_references -- Which articles each holding references
```

### Example Queries

**Direction breakdown by year:**
```sql
SELECT 
    judgment_year,
    ruling_direction,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY judgment_year), 1) as pct
FROM holdings h
JOIN cases c ON h.case_id = c.case_id
GROUP BY judgment_year, ruling_direction
ORDER BY judgment_year, count DESC;
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

**Concepts by chamber:**
```sql
SELECT 
    c.chamber,
    h.primary_concept,
    COUNT(*) as count
FROM holdings h
JOIN cases c ON h.case_id = c.case_id
GROUP BY c.chamber, h.primary_concept
ORDER BY c.chamber, count DESC;
```

**Correlation: teleological interpretation → pro-data-subject:**
```sql
SELECT 
    dominant_source,
    ruling_direction,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY dominant_source), 1) as pct
FROM holdings
GROUP BY dominant_source, ruling_direction
ORDER BY dominant_source, count DESC;
```

**Level shifting analysis:**
```sql
SELECT 
    case_id,
    holding_id,
    primary_concept,
    level_shifting_explanation
FROM holdings
WHERE level_shifting = 1
ORDER BY case_id;
```

**Holdings involving balancing:**
```sql
SELECT 
    case_id,
    holding_id,
    core_holding,
    necessity_standard,
    interest_prevails,
    other_rights,
    right_prevails
FROM holdings
WHERE necessity_discussed = 1 
   OR controller_ds_balancing = 1 
   OR other_rights_balancing = 1;
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

**Citation network (for visualization):**
```sql
SELECT 
    citing_case as source,
    cited_case as target,
    COUNT(*) as weight
FROM case_citations
GROUP BY citing_case, cited_case;
```

## Analysis with Python/Pandas

```python
import pandas as pd
import json

# Load CSV for flat analysis
df = pd.read_csv('output/holdings.csv')

# Direction breakdown
df['ruling_direction'].value_counts()

# Cross-tabulation
pd.crosstab(df['dominant_source'], df['ruling_direction'], normalize='index')

# Load JSON for hierarchical access
with open('output/cases.json') as f:
    cases = json.load(f)

# Access nested data
for case in cases:
    for h in case['holdings']:
        if h['reasoning']['level_shifting']:
            print(f"{case['case_id']}: {h['reasoning']['level_shifting_explanation']}")
```

## Analysis with R

```r
library(tidyverse)

df <- read_csv("output/holdings.csv")

# Direction by year
df %>%
  mutate(year = year(as.Date(judgment_date))) %>%
  count(year, ruling_direction) %>%
  group_by(year) %>%
  mutate(pct = n / sum(n))

# Interpretation source vs direction
df %>%
  count(dominant_source, ruling_direction) %>%
  ggplot(aes(dominant_source, ruling_direction, fill = n)) +
  geom_tile()
```

## Viewer Features

The interactive HTML viewer provides:

- **Search**: Full-text search across case IDs, holdings, and concepts
- **Filters**: Chamber, ruling direction, dominant source, concept
- **Drill-down**: Expand holdings to see quotes, citations, balancing analysis
- **Statistics**: Aggregate view with breakdowns and progress bars

### Customizing the Viewer

The viewer embeds sample data. To use your own:

1. Load JSON via the "Load JSON" button, or
2. Replace `SAMPLE_DATA` in `viewer/index.html` with your exported JSON

## Schema Reference

See the original questionnaire for full field definitions. Key fields:

| Field | Type | Values |
|-------|------|--------|
| `ruling_direction` | enum | PRO_DATA_SUBJECT, PRO_CONTROLLER, MIXED, NEUTRAL_OR_UNCLEAR |
| `dominant_source` | enum | SEMANTIC, SYSTEMATIC, TELEOLOGICAL, UNCLEAR |
| `dominant_structure` | enum | RULE_BASED, CASE_LAW_BASED, PRINCIPLE_BASED, MIXED |
| `primary_concept` | enum | 40 concepts (see schema) |
| `necessity_standard` | enum | STRICT, REGULAR, NONE |

## Extending the Analyzer

### Adding New Fields

1. Update `parse_coded.py`:
   - Add to dataclass
   - Parse in `_parse_holding()`
   - Export in `export_csv()` and `export_sqlite()`

2. Update `viewer/index.html`:
   - Add to display logic
   - Add filters if needed

### Custom Visualizations

Export data and use your preferred tool:

- **Network graphs**: Export `case_citations` table → Gephi, D3.js
- **Time series**: Query by year → matplotlib, ggplot2
- **Heatmaps**: Cross-tabulations → seaborn, plotly

## Troubleshooting

**Parser errors:**
- Check that your `_coded.md` files match the expected format
- Run with `--strict` to see all validation issues

**Missing data:**
- Ensure all A1-A43 fields are present for each holding
- Use `NULL` for empty optional fields

**Viewer not loading:**
- Check browser console for JavaScript errors
- Verify JSON is valid with `python -m json.tool output/cases.json`
