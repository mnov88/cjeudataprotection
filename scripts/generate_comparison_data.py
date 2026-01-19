#!/usr/bin/env python3
"""
Generate comparison data for the Coder Comparison UI.

This script creates JSON files suitable for the coder-comparison.html interface.
It can:
1. Load coded files from multiple directories (different coders)
2. Generate comparison structures for each case
3. Support single-coder mode (for review/validation)

Usage:
    # Compare two coders
    python generate_comparison_data.py --coder-a data/coded --coder-b data/coded_v2

    # Single coder review mode
    python generate_comparison_data.py --coder-a data/coded --single

    # Specific case
    python generate_comparison_data.py --coder-a data/coded --case C-129-21
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


def parse_coded_file(filepath: Path) -> Dict[str, str]:
    """Parse a coded markdown file into a dictionary of answers."""
    content = filepath.read_text(encoding='utf-8')
    answers = {}
    current_holding = None

    for line in content.split('\n'):
        line = line.strip()

        # Check for holding marker
        holding_match = re.match(r'=== HOLDING (\d+) ===', line)
        if holding_match:
            current_holding = int(holding_match.group(1))
            continue

        # Parse answer lines (A1: value)
        answer_match = re.match(r'^(A\d+):\s*(.*)$', line)
        if answer_match:
            key = answer_match.group(1)
            value = answer_match.group(2).strip()

            # If we're in a holding, prefix the key with holding number
            if current_holding is not None:
                answers[f"H{current_holding}_{key}"] = value
            else:
                answers[key] = value

    return answers


def extract_holdings(answers: Dict[str, str]) -> List[Dict[str, str]]:
    """Extract individual holdings from parsed answers."""
    # Get case metadata
    metadata = {k: v for k, v in answers.items() if not k.startswith('H')}

    # Group by holding
    holdings = {}
    for key, value in answers.items():
        if key.startswith('H'):
            match = re.match(r'H(\d+)_(A\d+)', key)
            if match:
                holding_num = int(match.group(1))
                field_key = match.group(2)
                if holding_num not in holdings:
                    holdings[holding_num] = {}
                holdings[holding_num][field_key] = value

    return metadata, holdings


def generate_comparison_data(
    coder_a_dir: Path,
    coder_b_dir: Optional[Path] = None,
    case_filter: Optional[str] = None,
    coder_a_name: str = "Coder A",
    coder_b_name: str = "Coder B"
) -> List[Dict[str, Any]]:
    """Generate comparison data for all cases."""
    comparison_data = []

    # Find all coded files in coder A directory
    coded_files = list(coder_a_dir.glob('*_coded.md'))

    for coded_file in sorted(coded_files):
        case_id = coded_file.stem.replace('_coded', '')

        # Apply case filter if specified
        if case_filter and case_filter not in case_id:
            continue

        # Parse coder A
        answers_a = parse_coded_file(coded_file)
        metadata_a, holdings_a = extract_holdings(answers_a)

        # Parse coder B if available
        if coder_b_dir:
            coder_b_file = coder_b_dir / coded_file.name
            if coder_b_file.exists():
                answers_b = parse_coded_file(coder_b_file)
                metadata_b, holdings_b = extract_holdings(answers_b)
            else:
                # Create empty structure for missing file
                answers_b = {}
                metadata_b = {}
                holdings_b = {}
        else:
            # Single coder mode - duplicate for self-review
            answers_b = answers_a.copy()
            metadata_b = metadata_a.copy()
            holdings_b = {k: v.copy() for k, v in holdings_a.items()}
            coder_b_name = f"{coder_a_name} (Copy)"

        # Format case ID properly (C-129-21 -> C-129/21)
        formatted_case_id = re.sub(r'^(C)-(\d+)-(\d+)$', r'\1-\2/\3', case_id)

        # Build comparison structure
        case_data = {
            "case_id": formatted_case_id,
            "judgment_date": metadata_a.get('A2', ''),
            "chamber": metadata_a.get('A3', ''),
            "decision_file": f"../data/decisions/{case_id}.md",
            "holdings": []
        }

        # Merge holdings from both coders
        all_holding_ids = sorted(set(holdings_a.keys()) | set(holdings_b.keys()))

        for holding_id in all_holding_ids:
            holding_a = holdings_a.get(holding_id, {})
            holding_b = holdings_b.get(holding_id, {})

            case_data["holdings"].append({
                "holding_id": holding_id,
                "coders": {
                    coder_a_name: holding_a,
                    coder_b_name: holding_b
                },
                "selected": {},
                "customValues": {}
            })

        comparison_data.append(case_data)

    return comparison_data


def main():
    parser = argparse.ArgumentParser(description='Generate coder comparison data')
    parser.add_argument('--coder-a', required=True, help='Directory with first coder\'s files')
    parser.add_argument('--coder-b', help='Directory with second coder\'s files (optional)')
    parser.add_argument('--coder-a-name', default='Coder A', help='Name for first coder')
    parser.add_argument('--coder-b-name', default='Coder B', help='Name for second coder')
    parser.add_argument('--case', help='Filter to specific case (partial match)')
    parser.add_argument('--output', '-o', help='Output file (default: comparison_data.json)')
    parser.add_argument('--single', action='store_true', help='Single coder review mode')
    parser.add_argument('--split', action='store_true', help='Generate separate file per case')

    args = parser.parse_args()

    coder_a_dir = Path(args.coder_a)
    coder_b_dir = Path(args.coder_b) if args.coder_b else None

    if not coder_a_dir.exists():
        print(f"Error: Directory not found: {coder_a_dir}")
        return 1

    if coder_b_dir and not coder_b_dir.exists():
        print(f"Error: Directory not found: {coder_b_dir}")
        return 1

    print(f"Loading coded files from: {coder_a_dir}")
    if coder_b_dir:
        print(f"Comparing with: {coder_b_dir}")

    comparison_data = generate_comparison_data(
        coder_a_dir,
        coder_b_dir,
        case_filter=args.case,
        coder_a_name=args.coder_a_name,
        coder_b_name=args.coder_b_name
    )

    if args.split:
        # Generate separate file per case
        output_dir = Path(args.output) if args.output else Path('comparison_output')
        output_dir.mkdir(exist_ok=True)

        for case_data in comparison_data:
            case_id = case_data['case_id'].replace('/', '-')
            output_file = output_dir / f"{case_id}_comparison.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False)
            print(f"Generated: {output_file}")
    else:
        # Single output file
        output_file = args.output or 'comparison_data.json'

        # If single case, output just that case (not wrapped in array)
        if args.case and len(comparison_data) == 1:
            output_data = comparison_data[0]
        else:
            output_data = comparison_data

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nGenerated comparison data: {output_file}")
        print(f"Total cases: {len(comparison_data)}")
        total_holdings = sum(len(c['holdings']) for c in comparison_data)
        print(f"Total holdings: {total_holdings}")

    return 0


if __name__ == '__main__':
    exit(main())
