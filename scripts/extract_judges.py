#!/usr/bin/env python3
"""
Extract judge names, rapporteur, and advocate general from CJEU decision files.
Updates cases_metadata.json with composition information.
"""

import json
import re
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Composition:
    chamber: Optional[str]
    judges: list[str]
    judgeRapporteur: Optional[str]
    advocateGeneral: Optional[str]


# Known name corrections for OCR/encoding errors in source files
NAME_CORRECTIONS = {
    'M.L. Arasteyx2 Sahún': 'M.L. Arastey Sahún',
}


def normalize_name(name: str) -> str:
    """Normalize judge name by cleaning whitespace and special characters."""
    # Replace various dash types with standard hyphen
    name = name.replace('‑', '-').replace('–', '-').replace('—', '-')
    # Clean whitespace
    name = ' '.join(name.split())
    name = name.strip()

    # Remove leftover role fragments
    role_fragments = [
        r'\s*of the Court$',
        r'\s*Vice-$',
        r'^Vice-\s*',
        r'\s*President of the [\w\s]+ Chamber$',
        r'\s*President of the Chamber$',
        r'\s*Presidents of Chambers$',
        r'\s*President$',
    ]
    for pattern in role_fragments:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    name = name.strip()

    # Apply known name corrections
    if name in NAME_CORRECTIONS:
        name = NAME_CORRECTIONS[name]

    return name


def is_valid_judgment_file(text: str) -> bool:
    """Check if the file contains a proper judgment (not raw HTML)."""
    # Check for signs of raw HTML/JavaScript
    if '<script' in text.lower() or 'function(' in text or 'window.location' in text:
        return False
    # Check for expected judgment markers
    if 'JUDGMENT OF THE COURT' in text or 'THE COURT' in text:
        return True
    return False


def extract_chamber(text: str) -> Optional[str]:
    """Extract chamber name from decision text."""
    # Pattern: THE COURT (Chamber Name),
    match = re.search(r'THE COURT \(([^)]+)\)', text)
    if match:
        chamber = match.group(1)
        # Normalize: "Fourth Chamber" -> "Fourth", "Grand Chamber" -> "Grand"
        chamber = chamber.replace(' Chamber', '')
        return chamber
    return None


def extract_judges_line(text: str) -> Optional[str]:
    """Extract the full 'composed of ... Judges,' line."""
    # The line starts with 'composed of' and ends with 'Judges,'
    # It may span multiple lines in the markdown
    match = re.search(r'composed of\s+(.+?),?\s*Judges,', text, re.DOTALL)
    if match:
        return match.group(1)
    return None


def parse_judges_from_line(judges_line: str) -> tuple[list[str], Optional[str]]:
    """
    Parse judge names and identify rapporteur from the composed-of line.
    Returns (list of judge names, rapporteur name or None).
    """
    judges = []
    rapporteur = None

    # Clean up the line - normalize whitespace
    judges_line = ' '.join(judges_line.split())

    # Find the rapporteur - the name directly before "(Rapporteur)"
    # The rapporteur name is typically: Initial. LastName or Initial.Initial. LastName
    # Pattern: Look for name pattern immediately before (Rapporteur)
    # Split approach: find segment containing (Rapporteur), extract name from it
    rapporteur_match = re.search(r'\(Rapporteur\)', judges_line)
    if rapporteur_match:
        # Get text before "(Rapporteur)"
        before_rapporteur = judges_line[:rapporteur_match.start()].strip()
        # Split by commas and "and" to find the actual name
        # The rapporteur name is the last segment before (Rapporteur)
        segments = re.split(r',\s*|\s+and\s+', before_rapporteur)
        if segments:
            # Get the last non-empty segment
            for seg in reversed(segments):
                seg = seg.strip()
                if seg and re.match(r'^[A-Z]', seg):
                    rapporteur = normalize_name(seg)
                    break

    # Remove role descriptions to isolate names
    # Remove "(Rapporteur)" markers
    cleaned = re.sub(r'\s*\(Rapporteur\)', '', judges_line)

    # Remove role titles
    role_patterns = [
        r',?\s*President of the [\w\s]+ Chamber,?\s*acting as President of the [\w\s]+ Chamber',
        r',?\s*President of the Chamber',
        r',?\s*Presidents of Chambers',
        r',?\s*Vice-President',
        r',?\s*President(?!\s+of)',  # President but not "President of"
        r',?\s*acting as President of the [\w\s]+ Chamber',
    ]
    for pattern in role_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Now split by common delimiters: comma, 'and'
    # Replace 'and' with comma for uniform splitting
    cleaned = re.sub(r'\s+and\s+', ', ', cleaned)

    # Split by comma
    parts = [p.strip() for p in cleaned.split(',')]

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip if it's just a role or empty
        if part.lower() in ['', 'and']:
            continue
        # A valid name should start with a capital letter and have initials or name pattern
        if re.match(r'^[A-Z]', part):
            name = normalize_name(part)
            if name and len(name) > 1:
                judges.append(name)

    return judges, rapporteur


def extract_advocate_general(text: str) -> Optional[str]:
    """Extract Advocate General name from decision text."""
    # Pattern: Advocate General: Name,
    match = re.search(r'Advocate General:\s*([^,\n]+)', text)
    if match:
        return normalize_name(match.group(1))
    return None


def extract_case_number_from_filename(filename: str) -> str:
    """Convert filename like 'C-17-22.md' to case number pattern 'C-17/22'."""
    # Remove .md extension
    base = filename.replace('.md', '')
    # Convert C-17-22 to C-17/22
    parts = base.split('-')
    if len(parts) >= 3:
        # C-17-22 -> C-17/22
        return f"{parts[0]}-{parts[1]}/{parts[2]}"
    return base


def process_decision_file(filepath: Path) -> tuple[str, Optional[Composition], list[str]]:
    """
    Process a single decision file and extract composition.
    Returns (case_identifier, Composition or None, list of warnings).
    """
    warnings = []
    case_id = extract_case_number_from_filename(filepath.name)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        warnings.append(f"Could not read file: {e}")
        return case_id, None, warnings

    # Check if file contains valid judgment content
    if not is_valid_judgment_file(text):
        warnings.append("File contains raw HTML/JavaScript instead of judgment text - skipped")
        return case_id, None, warnings

    # Extract chamber
    chamber = extract_chamber(text)
    if not chamber:
        warnings.append("Could not extract chamber")

    # Extract judges
    judges_line = extract_judges_line(text)
    if judges_line:
        judges, rapporteur = parse_judges_from_line(judges_line)
        if not judges:
            warnings.append("Could not parse any judge names")
        if not rapporteur:
            warnings.append("Could not identify rapporteur")
    else:
        judges = []
        rapporteur = None
        warnings.append("Could not find 'composed of ... Judges' line")

    # Extract Advocate General
    ag = extract_advocate_general(text)
    if not ag:
        warnings.append("No Advocate General found (may be intentional)")

    composition = Composition(
        chamber=chamber,
        judges=judges,
        judgeRapporteur=rapporteur,
        advocateGeneral=ag
    )

    return case_id, composition, warnings


def match_case_to_metadata(case_id: str, metadata_cases: list[dict]) -> Optional[dict]:
    """Find matching case in metadata by case number."""
    # case_id is like "C-17/22"
    for case in metadata_cases:
        case_number = case.get('caseNumber', '')
        # caseNumber is like "Case C-17/22" or "Joined Cases C-17/22 and C-18/22"
        if case_id in case_number:
            return case
    return None


def run_extraction(decisions_dir: Path, preview_only: bool = True) -> dict:
    """
    Run extraction on all decision files.
    Returns a report dict with results and statistics.
    """
    report = {
        'total_files': 0,
        'successful': 0,
        'with_warnings': 0,
        'failed': 0,
        'results': [],
        'all_warnings': []
    }

    decision_files = sorted(decisions_dir.glob('*.md'))
    report['total_files'] = len(decision_files)

    for filepath in decision_files:
        case_id, composition, warnings = process_decision_file(filepath)

        result = {
            'file': filepath.name,
            'case_id': case_id,
            'composition': asdict(composition) if composition else None,
            'warnings': warnings
        }
        report['results'].append(result)

        if composition and composition.judges:
            report['successful'] += 1
            if warnings:
                report['with_warnings'] += 1
        else:
            report['failed'] += 1

        if warnings:
            for w in warnings:
                report['all_warnings'].append(f"{filepath.name}: {w}")

    return report


def print_report(report: dict, verbose: bool = False):
    """Print extraction report."""
    print("=" * 60)
    print("JUDGE EXTRACTION REPORT")
    print("=" * 60)
    print(f"Total files processed: {report['total_files']}")
    print(f"Successful extractions: {report['successful']}")
    print(f"  - With warnings: {report['with_warnings']}")
    print(f"Failed extractions: {report['failed']}")
    print()

    if verbose:
        print("-" * 60)
        print("DETAILED RESULTS:")
        print("-" * 60)
        for result in report['results']:
            print(f"\n{result['file']} ({result['case_id']}):")
            if result['composition']:
                comp = result['composition']
                print(f"  Chamber: {comp['chamber']}")
                print(f"  Judges: {', '.join(comp['judges']) if comp['judges'] else 'NONE'}")
                print(f"  Rapporteur: {comp['judgeRapporteur']}")
                print(f"  Advocate General: {comp['advocateGeneral']}")
            if result['warnings']:
                for w in result['warnings']:
                    print(f"  ⚠️  {w}")

    if report['all_warnings']:
        print("-" * 60)
        print("ALL WARNINGS:")
        print("-" * 60)
        for w in report['all_warnings']:
            print(f"  - {w}")


def update_metadata(metadata_path: Path, decisions_dir: Path) -> tuple[int, int, list[str]]:
    """
    Update cases_metadata.json with composition data.
    Returns (updated_count, not_found_count, errors).
    """
    # Load existing metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    cases = metadata.get('cases', [])
    updated = 0
    not_found = 0
    errors = []

    # Process each decision file
    decision_files = sorted(decisions_dir.glob('*.md'))

    for filepath in decision_files:
        case_id, composition, warnings = process_decision_file(filepath)

        if not composition or not composition.judges:
            errors.append(f"{filepath.name}: Failed to extract composition")
            continue

        # Find matching case in metadata
        matched_case = match_case_to_metadata(case_id, cases)

        if matched_case:
            matched_case['composition'] = asdict(composition)
            updated += 1
        else:
            not_found += 1
            errors.append(f"{filepath.name}: No matching case in metadata for {case_id}")

    # Save updated metadata
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return updated, not_found, errors


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Extract judge information from CJEU decisions')
    parser.add_argument('--preview', action='store_true', default=True,
                        help='Preview extraction without updating metadata (default)')
    parser.add_argument('--update', action='store_true',
                        help='Update cases_metadata.json with extracted data')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed results for each file')
    parser.add_argument('--decisions-dir', type=Path,
                        default=Path(__file__).parent.parent / 'decisions',
                        help='Path to decisions directory')
    parser.add_argument('--metadata', type=Path,
                        default=Path(__file__).parent.parent / 'cases-metadata' / 'cases_metadata.json',
                        help='Path to cases_metadata.json')

    args = parser.parse_args()

    if args.update:
        print("Updating cases_metadata.json...")
        updated, not_found, errors = update_metadata(args.metadata, args.decisions_dir)
        print(f"\nResults:")
        print(f"  Cases updated: {updated}")
        print(f"  Cases not found in metadata: {not_found}")
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for e in errors:
                print(f"  - {e}")
        print(f"\nMetadata file updated: {args.metadata}")
    else:
        # Preview mode
        report = run_extraction(args.decisions_dir, preview_only=True)
        print_report(report, verbose=args.verbose)
        print("\nTo update metadata, run with --update flag")


if __name__ == '__main__':
    main()
