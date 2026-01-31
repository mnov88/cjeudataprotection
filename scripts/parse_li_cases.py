#!/usr/bin/env python3
"""
Parser for li-case-law coded files.

Reads all *_coded.md files in data/li-case-law/, extracts the 27 structured
fields (A0.1 through A5.2), and outputs JSON + CSV.

Usage:
    python3 scripts/parse_li_cases.py
"""

import csv
import json
import re
from pathlib import Path

# ============================================================================
# Schema: field ID -> (label, type)
# Types: string, date, text, bool, list, nested, enum, bool_or_text
# ============================================================================

SCHEMA = {
    "A0.1": ("case_number", "string"),
    "A0.2": ("case_date", "date"),
    "A0.3": ("factual_summary", "text"),
    "A1.1": ("li_discussed", "bool"),
    "A1.2": ("controller_interests", "list"),
    "A1.3": ("interest_findings", "nested:interest>finding"),
    "A1.4": ("factual_assumptions_interest", "bool_or_text"),
    "A1.5": ("case_law_interest", "nested:case>quote>conclusion"),
    "A2.1": ("necessity_discussed", "bool_or_text"),
    "A2.2": ("necessity_found", "bool"),
    "A2.3": ("strict_necessity", "bool"),
    "A2.4": ("less_effective_means", "bool"),
    "A2.5": ("factual_assumptions_necessity", "bool_or_text"),
    "A2.6": ("data_minimisation", "bool_or_text"),
    "A2.7": ("case_law_necessity", "nested:case>quote>conclusion"),
    "A3.1": ("balancing_discussed", "bool"),
    "A3.2": ("controller_side_interests", "list"),
    "A3.3": ("ds_side_interests", "list"),
    "A3.4": ("prevailing_side", "enum"),
    "A3.5": ("factual_assumptions_balancing", "bool_or_text"),
    "A3.6": ("case_law_balancing", "nested:case>quote>conclusion"),
    "A4.1": ("charter_invoked", "bool"),
    "A4.2": ("charter_articles", "list"),
    "A4.3": ("reasonable_expectations", "bool"),
    "A4.4": ("expectations_detail", "nested:expectation>conclusion"),
    "A5.1": ("li_valid_basis", "enum"),
    "A5.2": ("key_holdings_summary", "text"),
}

FIELD_IDS = list(SCHEMA.keys())


# ============================================================================
# Parsing helpers
# ============================================================================

def pipe_list(val: str) -> list[str]:
    """Split a pipe-separated value into a list of stripped strings."""
    if not val or val.strip().upper() in ("N", "NA"):
        return []
    return [item.strip() for item in val.split("|") if item.strip()]


def nested(val: str, keys: list[str]) -> list[dict]:
    """
    Parse nested structures separated by | (items) and > (levels).
    E.g. "case > quote > conclusion | case > quote > conclusion"
    Returns list of dicts with named keys.
    """
    if not val or val.strip().upper() in ("N", "NA"):
        return []
    items = []
    for entry in val.split("|"):
        entry = entry.strip()
        if not entry:
            continue
        parts = [p.strip() for p in entry.split(">")]
        obj = {}
        for i, key in enumerate(keys):
            obj[key] = parts[i] if i < len(parts) else ""
        # If there are extra parts beyond the keys, append to last key
        if len(parts) > len(keys):
            obj[keys[-1]] = " > ".join(parts[len(keys) - 1 :])
        items.append(obj)
    return items


def extract_case_number(text: str) -> str:
    """
    Extract the C-number from a case citation string.
    E.g. "Case C-275/06 Promusicae" -> "C-275/06"
         "C-92/09 and C-93/09 Volker..." -> "C-92/09 and C-93/09"
         "C-17/22 and C-18/22 HTB..." -> "C-17/22 and C-18/22"
    Returns original text if no C-number found.
    """
    # Find all C-number patterns
    numbers = re.findall(r"C-\d+/\d+", text)
    if numbers:
        return " and ".join(numbers)
    return text


def parse_nested_keys(type_str: str) -> list[str]:
    """Extract key names from a type like 'nested:case>quote>conclusion'."""
    _, _, keys_part = type_str.partition(":")
    return [k.strip() for k in keys_part.split(">")]


# ============================================================================
# File parser
# ============================================================================

def parse_file(filepath: Path) -> dict:
    """
    Parse a single _coded.md file into a dict with raw + parsed values.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()

    raw = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip note lines
        if line.lower().startswith("note:"):
            continue
        # Match field pattern: A{section}.{question}: {value}
        m = re.match(r"^A(\d+\.\d+):\s*(.+)$", line)
        if m:
            field_id = f"A{m.group(1)}"
            raw[field_id] = m.group(2).strip()

    # Build structured case object
    case = {"_source_file": filepath.name}

    for field_id, (label, ftype) in SCHEMA.items():
        val = raw.get(field_id, "")
        case[label] = val  # always store raw string

        # Add parsed sub-field based on type
        if ftype == "list":
            case[f"{label}_parsed"] = pipe_list(val)
        elif ftype.startswith("nested:"):
            keys = parse_nested_keys(ftype)
            parsed = nested(val, keys)
            # Normalize "case" key to C-number only for citation network use
            if "case" in keys:
                for obj in parsed:
                    obj["case"] = extract_case_number(obj["case"])
            case[f"{label}_parsed"] = parsed

    return case


# ============================================================================
# CSV flattening
# ============================================================================

def flatten_for_csv(case: dict) -> dict:
    """
    Produce a flat dict with 27 columns for CSV output.
    Lists joined with ';', nested structures flattened to string.
    """
    row = {}
    for field_id, (label, ftype) in SCHEMA.items():
        val = case.get(label, "")
        if ftype == "list":
            parsed = case.get(f"{label}_parsed", [])
            row[label] = "; ".join(parsed) if parsed else val
        elif ftype.startswith("nested:"):
            parsed = case.get(f"{label}_parsed", [])
            if parsed:
                keys = parse_nested_keys(ftype)
                parts = []
                for obj in parsed:
                    parts.append(" > ".join(obj.get(k, "") for k in keys))
                row[label] = " | ".join(parts)
            else:
                row[label] = val
        else:
            row[label] = val
    return row


# ============================================================================
# Main
# ============================================================================

def main():
    base = Path(__file__).resolve().parent.parent
    input_dir = base / "data" / "li-case-law"
    output_dir = input_dir / "parsed"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all coded files
    coded_files = sorted(input_dir.glob("*_coded.md"))
    if not coded_files:
        print("No *_coded.md files found in", input_dir)
        return 1

    print(f"Found {len(coded_files)} coded files")

    # Parse all files
    cases = []
    for f in coded_files:
        print(f"  Parsing: {f.name}")
        case = parse_file(f)
        cases.append(case)

    # Validate: check each case has all 27 fields
    labels = [label for _, (label, _) in SCHEMA.items()]
    missing_report = []
    for case in cases:
        src = case.get("_source_file", "?")
        missing = [l for l in labels if not case.get(l)]
        if missing:
            missing_report.append(f"  {src}: missing {missing}")

    if missing_report:
        print(f"\nWarnings ({len(missing_report)} files with missing fields):")
        for line in missing_report:
            print(line)

    # Normalize cited case references to match dataset case_number values.
    # Build index: individual C-number -> case_number in dataset
    # e.g. "C-17/22" -> "C-17/22", "C-93/09" -> "C-92/09 and C-93/09"
    cn_index: dict[str, str] = {}
    for case in cases:
        cn = case["case_number"]
        for num in re.findall(r"C-\d+/\d+", cn):
            cn_index[num] = cn

    citation_fields = [
        "case_law_interest_parsed",
        "case_law_necessity_parsed",
        "case_law_balancing_parsed",
    ]
    for case in cases:
        for field in citation_fields:
            for obj in case.get(field, []):
                raw_cite = obj["case"]
                # Already an exact match?
                if raw_cite in cn_index.values():
                    continue
                # Check if any individual C-number in the citation maps to a dataset entry
                nums = re.findall(r"C-\d+/\d+", raw_cite)
                for num in nums:
                    if num in cn_index:
                        obj["case"] = cn_index[num]
                        break

    # Sort by case_date ascending
    cases.sort(key=lambda c: c.get("case_date", ""))

    # Write JSON
    json_path = output_dir / "li_cases.json"
    with open(json_path, "w", encoding="utf-8") as fout:
        json.dump(cases, fout, indent=2, ensure_ascii=False)
    print(f"\nJSON written: {json_path} ({len(cases)} entries)")

    # Write CSV
    csv_path = output_dir / "li_cases.csv"
    csv_labels = [label for _, (label, _) in SCHEMA.items()]
    rows = [flatten_for_csv(c) for c in cases]
    with open(csv_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=csv_labels)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV written: {csv_path} ({len(rows)} rows + header)")

    # Summary
    print(f"\nDone. {len(cases)} cases parsed with {len(SCHEMA)} fields each.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
