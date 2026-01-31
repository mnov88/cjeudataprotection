# Legitimate Interest Case Law Parser

Parses `*_coded.md` files in `data/li-case-law/` and outputs structured JSON and CSV to `data/li-case-law/parsed/`.

## Usage

```
python3 scripts/parse_li_cases.py
```

Outputs:
- `data/li-case-law/parsed/li_cases.json`
- `data/li-case-law/parsed/li_cases.csv`

## Source format

Each `_coded.md` file contains 27 line-based fields using the pattern `A{section}.{question}: {value}`. Blank lines and lines starting with `Note:` are ignored. See `data-schema-legitimate-interest.md` for the full coding schema.

### Delimiters

| Delimiter | Meaning | Example |
|-----------|---------|---------|
| `\|` | separates list items | `interest A \| interest B` |
| `>` | separates nested levels | `case > quote > conclusion` |

### Value types

| Type | Values |
|------|--------|
| bool | `Y`, `N` |
| enum | `Y`, `N`, `NA`, `mixed`, `unclear`, `DC`, `DS` |
| text | free-form string |
| list | pipe-separated items |
| nested | pipe-separated items, each with `>`-separated levels |
| bool_or_text | `Y`, `Y > quote`, `N`, or free text |

## JSON schema

Cases are sorted by `case_date` ascending. Each entry is an object with the following structure.

### Metadata fields

| Key | Source | Type | Description |
|-----|--------|------|-------------|
| `_source_file` | — | string | Filename of the source `_coded.md` file |
| `case_number` | A0.1 | string | Case number, e.g. `"C-252/21"` or `"C-92/09 and C-93/09"` |
| `case_date` | A0.2 | string | Judgment date as `YYYY-MM-DD` |
| `factual_summary` | A0.3 | string | Factual summary of the dispute |

### Section 1: Legitimate interest

| Key | Source | Type | Description |
|-----|--------|------|-------------|
| `li_discussed` | A1.1 | string | `"Y"` or `"N"` |
| `controller_interests` | A1.2 | string | Raw pipe-separated interests |
| `controller_interests_parsed` | A1.2 | `string[]` | Split list of interests |
| `interest_findings` | A1.3 | string | Raw nested string |
| `interest_findings_parsed` | A1.3 | `InterestFinding[]` | See nested type below |
| `factual_assumptions_interest` | A1.4 | string | `"N"` or free text |
| `case_law_interest` | A1.5 | string | Raw nested string |
| `case_law_interest_parsed` | A1.5 | `CaseCitation[]` | See nested type below |

### Section 2: Necessity

| Key | Source | Type | Description |
|-----|--------|------|-------------|
| `necessity_discussed` | A2.1 | string | `"Y > quote"` or `"N"` |
| `necessity_found` | A2.2 | string | `"Y"`, `"N"`, or `"NA"` |
| `strict_necessity` | A2.3 | string | `"Y"` or `"N"` |
| `less_effective_means` | A2.4 | string | `"Y"` or `"N"` |
| `factual_assumptions_necessity` | A2.5 | string | `"N"` or free text |
| `data_minimisation` | A2.6 | string | `"N"` or `"summary > quote"` |
| `case_law_necessity` | A2.7 | string | Raw nested string |
| `case_law_necessity_parsed` | A2.7 | `CaseCitation[]` | See nested type below |

### Section 3: Balancing of interests

| Key | Source | Type | Description |
|-----|--------|------|-------------|
| `balancing_discussed` | A3.1 | string | `"Y"` or `"N"` |
| `controller_side_interests` | A3.2 | string | Raw pipe-separated interests |
| `controller_side_interests_parsed` | A3.2 | `string[]` | Split list of interests |
| `ds_side_interests` | A3.3 | string | Raw pipe-separated interests |
| `ds_side_interests_parsed` | A3.3 | `string[]` | Split list of interests |
| `prevailing_side` | A3.4 | string | `"DC"`, `"DS"`, `"mixed"`, or `"NA"` |
| `factual_assumptions_balancing` | A3.5 | string | `"N"` or free text |
| `case_law_balancing` | A3.6 | string | Raw nested string |
| `case_law_balancing_parsed` | A3.6 | `CaseCitation[]` | See nested type below |

### Section 4: Charter & reasonable expectations

| Key | Source | Type | Description |
|-----|--------|------|-------------|
| `charter_invoked` | A4.1 | string | `"Y"` or `"N"` |
| `charter_articles` | A4.2 | string | Raw pipe-separated articles or `"NA"` |
| `charter_articles_parsed` | A4.2 | `string[]` | Split list, e.g. `["Art. 7", "Art. 8"]` |
| `reasonable_expectations` | A4.3 | string | `"Y"` or `"N"` |
| `expectations_detail` | A4.4 | string | Raw nested string or `"NA"` |
| `expectations_detail_parsed` | A4.4 | `ExpectationDetail[]` | See nested type below |

### Section 5: Conclusion

| Key | Source | Type | Description |
|-----|--------|------|-------------|
| `li_valid_basis` | A5.1 | string | `"Y"`, `"N"`, or `"unclear"` |
| `key_holdings_summary` | A5.2 | string | Summary of key holdings |

## Nested types

### `InterestFinding`

Parsed from `A1.3`. Each item is an object with:

```json
{
  "interest": "personalised advertising",
  "finding": "may be regarded as carried out for a legitimate interest"
}
```

### `CaseCitation`

Parsed from `A1.5`, `A2.7`, `A3.6`. Each item is an object with:

```json
{
  "case": "C-252/21",
  "quote": "verbatim quote from the judgment",
  "conclusion": "conclusion drawn from the citation"
}
```

The `case` field contains only the C-number (e.g. `"C-252/21"`, not `"Case C-252/21 Meta Platforms"`). When a citation refers to a case in the dataset, the value is normalized to match the dataset's `case_number` exactly. For example, a source string `"C-468/10 and C-469/10"` becomes `"C-468/10"` because the dataset entry uses that form.

### `ExpectationDetail`

Parsed from `A4.4`. Each item is an object with:

```json
{
  "expectation": "Users of a free social network cannot reasonably expect ...",
  "conclusion": "The interests of the data subject override those of the controller"
}
```

## CSV format

The CSV file (`li_cases.csv`) has one row per case and 27 columns corresponding to the raw field labels (no `_parsed` or `_source_file` columns). Lists are joined with `; ` and nested structures are flattened back to `>` / `|` notation.

## Citation network

The parsed JSON is designed for citation network analysis. To build edges:

1. Each case is a node, identified by `case_number`.
2. For each case, iterate over `case_law_interest_parsed`, `case_law_necessity_parsed`, and `case_law_balancing_parsed`.
3. Each citation object's `case` field gives the cited C-number. If it matches a `case_number` in the dataset, it is an internal edge; otherwise it is an external citation.
