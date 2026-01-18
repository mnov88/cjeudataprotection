#!/usr/bin/env python3
"""
GDPR CJEU Coded Judgment Parser

Parses *_coded.md files into structured JSON and SQLite database.
Validates against the coding schema and provides detailed error reporting.
"""

import re
import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import date
import argparse


# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

CHAMBERS = {
    "GRAND_CHAMBER", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH",
    "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "FULL_COURT"
}

CONCEPTS = {
    "SCOPE_MATERIAL", "SCOPE_TERRITORIAL", "PERSONAL_DATA_SCOPE",
    "HOUSEHOLD_EXEMPTION", "OTHER_EXEMPTION", "CONTROLLER_DEFINITION",
    "JOINT_CONTROLLERS_DEFINITION", "PROCESSOR_OBLIGATIONS",
    "RECIPIENT_DEFINITION", "DATA_PROTECTION_PRINCIPLES", "ACCOUNTABILITY",
    "CONSENT_BASIS", "CONTRACT_BASIS", "LEGAL_OBLIGATION_BASIS",
    "VITAL_INTERESTS_BASIS", "PUBLIC_INTEREST_BASIS", "LEGITIMATE_INTERESTS",
    "SPECIAL_CATEGORIES_DEFINITION", "SPECIAL_CATEGORIES_CONDITIONS",
    "TRANSPARENCY", "RIGHT_OF_ACCESS", "RIGHT_TO_RECTIFICATION",
    "RIGHT_TO_ERASURE", "RIGHT_TO_RESTRICTION", "RIGHT_TO_PORTABILITY",
    "RIGHT_TO_OBJECT", "AUTOMATED_DECISION_MAKING", "SECURITY",
    "INTERNATIONAL_TRANSFER", "OTHER_CONTROLLER_OBLIGATIONS",
    "DPA_INDEPENDENCE", "DPA_POWERS", "DPA_OBLIGATIONS", "ONE_STOP_SHOP",
    "DPA_OTHER", "ADMINISTRATIVE_FINES", "REMEDIES_COMPENSATION",
    "REPRESENTATIVE_ACTIONS", "MEMBER_STATE_DISCRETION", "OTHER"
}

PURPOSES = {
    "HIGH_LEVEL_OF_PROTECTION", "FREE_FLOW_OF_DATA", "HARMONIZATION",
    "LEGAL_CERTAINTY", "FUNDAMENTAL_RIGHTS", "TECHNOLOGY_NEUTRALITY",
    "ACCOUNTABILITY", "EFFECTIVE_ENFORCEMENT", "OTHER"
}

INTERPRETIVE_SOURCES = {"SEMANTIC", "SYSTEMATIC", "TELEOLOGICAL", "UNCLEAR"}
REASONING_STRUCTURES = {"RULE_BASED", "CASE_LAW_BASED", "PRINCIPLE_BASED", "MIXED"}
RULING_DIRECTIONS = {"PRO_DATA_SUBJECT", "PRO_CONTROLLER", "MIXED", "NEUTRAL_OR_UNCLEAR"}
NECESSITY_STANDARDS = {"STRICT", "REGULAR", "NONE"}
INTEREST_PREVAILS = {"DATA_SUBJECT", "CONTROLLER", "NONE"}
RIGHT_PREVAILS = {"DATA_PROTECTION", "OTHER_RIGHT", "NONE"}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Interpretation:
    semantic_present: bool = False
    semantic_quote: Optional[str] = None
    systematic_present: bool = False
    systematic_quote: Optional[str] = None
    teleological_present: bool = False
    teleological_quote: Optional[str] = None
    teleological_purposes: List[str] = field(default_factory=list)
    other_purpose: Optional[str] = None
    dominant_source: str = "UNCLEAR"
    dominant_confident: bool = False


@dataclass
class ReasoningStructure:
    rule_based_present: bool = False
    rule_based_quote: Optional[str] = None
    case_law_present: bool = False
    case_law_quote: Optional[str] = None
    cited_cases: List[str] = field(default_factory=list)
    principle_based_present: bool = False
    principle_based_quote: Optional[str] = None
    dominant_structure: str = "MIXED"
    level_shifting: bool = False
    level_shifting_explanation: Optional[str] = None


@dataclass
class Balancing:
    necessity_discussed: bool = False
    necessity_standard: str = "NONE"
    necessity_summary: Optional[str] = None
    controller_ds_balancing: bool = False
    interest_prevails: str = "NONE"
    balance_summary: Optional[str] = None
    other_rights_balancing: bool = False
    other_rights: List[str] = field(default_factory=list)
    right_prevails: str = "NONE"
    rights_balance_summary: Optional[str] = None


@dataclass
class Holding:
    holding_id: int = 0
    paragraphs: List[int] = field(default_factory=list)
    core_holding: str = ""
    provisions_cited: List[str] = field(default_factory=list)
    article_numbers: List[int] = field(default_factory=list)
    primary_concept: str = "OTHER"
    secondary_concepts: List[str] = field(default_factory=list)
    interpretation: Interpretation = field(default_factory=Interpretation)
    reasoning: ReasoningStructure = field(default_factory=ReasoningStructure)
    ruling_direction: str = "NEUTRAL_OR_UNCLEAR"
    direction_justification: str = ""
    balancing: Balancing = field(default_factory=Balancing)


@dataclass
class Case:
    case_id: str = ""
    judgment_date: str = ""
    chamber: str = ""
    holding_count: int = 0
    holdings: List[Holding] = field(default_factory=list)
    source_file: str = ""
    parse_errors: List[str] = field(default_factory=list)
    parse_warnings: List[str] = field(default_factory=list)


# ============================================================================
# PARSER
# ============================================================================

class CodedMDParser:
    """Parser for coded markdown files following the GDPR CJEU schema."""
    
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse_file(self, filepath: Path) -> Case:
        """Parse a single coded markdown file."""
        self.errors = []
        self.warnings = []
        
        content = filepath.read_text(encoding='utf-8')
        case = self._parse_content(content)
        case.source_file = str(filepath)
        case.parse_errors = self.errors.copy()
        case.parse_warnings = self.warnings.copy()
        
        return case
    
    def _parse_content(self, content: str) -> Case:
        """Parse the content of a coded markdown file."""
        lines = content.strip().split('\n')
        answers: Dict[str, str] = {}
        holdings_data: List[Dict[str, str]] = []
        current_holding: Optional[Dict[str, str]] = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for holding delimiter
            if line.startswith('=== HOLDING'):
                if current_holding:
                    holdings_data.append(current_holding)
                current_holding = {}
                continue
            
            # Parse A#: value format
            match = re.match(r'^A(\d+):\s*(.*)$', line)
            if match:
                key = f"A{match.group(1)}"
                value = match.group(2).strip()
                
                if current_holding is not None:
                    current_holding[key] = value
                else:
                    answers[key] = value
        
        # Don't forget the last holding
        if current_holding:
            holdings_data.append(current_holding)
        
        # Build the Case object
        case = Case()
        case.case_id = answers.get('A1', '')
        case.judgment_date = answers.get('A2', '')
        case.chamber = self._validate_enum(answers.get('A3', ''), CHAMBERS, 'A3 (chamber)')
        case.holding_count = self._parse_int(answers.get('A4', '0'), 'A4 (holding_count)')
        
        # Parse each holding
        for i, h_data in enumerate(holdings_data, 1):
            holding = self._parse_holding(h_data, i)
            case.holdings.append(holding)
        
        # Validate holding count
        if len(case.holdings) != case.holding_count:
            self.warnings.append(
                f"A4 says {case.holding_count} holdings but found {len(case.holdings)}"
            )
        
        return case
    
    def _parse_holding(self, data: Dict[str, str], expected_id: int) -> Holding:
        """Parse a single holding's data."""
        h = Holding()
        
        # Basic fields
        h.holding_id = self._parse_int(data.get('A5', str(expected_id)), 'A5')
        h.paragraphs = self._parse_int_list(data.get('A6', ''), 'A6')
        h.core_holding = data.get('A7', '')
        h.provisions_cited = self._parse_string_list(data.get('A8', ''))
        h.article_numbers = self._parse_int_list(data.get('A9', ''), 'A9')
        h.primary_concept = self._validate_enum(data.get('A10', 'OTHER'), CONCEPTS, 'A10')
        h.secondary_concepts = self._parse_enum_list(data.get('A11', ''), CONCEPTS, 'A11')
        
        # Interpretation
        h.interpretation.semantic_present = self._parse_bool(data.get('A12', 'FALSE'))
        h.interpretation.semantic_quote = self._parse_nullable(data.get('A13', 'NULL'))
        h.interpretation.systematic_present = self._parse_bool(data.get('A14', 'FALSE'))
        h.interpretation.systematic_quote = self._parse_nullable(data.get('A15', 'NULL'))
        h.interpretation.teleological_present = self._parse_bool(data.get('A16', 'FALSE'))
        h.interpretation.teleological_quote = self._parse_nullable(data.get('A17', 'NULL'))
        h.interpretation.teleological_purposes = self._parse_enum_list(
            data.get('A18', ''), PURPOSES, 'A18'
        )
        h.interpretation.other_purpose = self._parse_nullable(data.get('A19', 'NULL'))
        h.interpretation.dominant_source = self._validate_enum(
            data.get('A20', 'UNCLEAR'), INTERPRETIVE_SOURCES, 'A20'
        )
        h.interpretation.dominant_confident = self._parse_bool(data.get('A21', 'FALSE'))
        
        # Reasoning structure
        h.reasoning.rule_based_present = self._parse_bool(data.get('A22', 'FALSE'))
        h.reasoning.rule_based_quote = self._parse_nullable(data.get('A23', 'NULL'))
        h.reasoning.case_law_present = self._parse_bool(data.get('A24', 'FALSE'))
        h.reasoning.case_law_quote = self._parse_nullable(data.get('A25', 'NULL'))
        h.reasoning.cited_cases = self._parse_string_list(data.get('A26', ''))
        h.reasoning.principle_based_present = self._parse_bool(data.get('A27', 'FALSE'))
        h.reasoning.principle_based_quote = self._parse_nullable(data.get('A28', 'NULL'))
        h.reasoning.dominant_structure = self._validate_enum(
            data.get('A29', 'MIXED'), REASONING_STRUCTURES, 'A29'
        )
        h.reasoning.level_shifting = self._parse_bool(data.get('A30', 'FALSE'))
        h.reasoning.level_shifting_explanation = self._parse_nullable(data.get('A31', 'NULL'))
        
        # Ruling direction
        h.ruling_direction = self._validate_enum(
            data.get('A32', 'NEUTRAL_OR_UNCLEAR'), RULING_DIRECTIONS, 'A32'
        )
        h.direction_justification = data.get('A33', '')
        
        # Balancing
        h.balancing.necessity_discussed = self._parse_bool(data.get('A34', 'FALSE'))
        h.balancing.necessity_standard = self._validate_enum(
            data.get('A35', 'NONE'), NECESSITY_STANDARDS, 'A35'
        )
        h.balancing.necessity_summary = self._parse_nullable(data.get('A36', 'NULL'))
        h.balancing.controller_ds_balancing = self._parse_bool(data.get('A37', 'FALSE'))
        h.balancing.interest_prevails = self._validate_enum(
            data.get('A38', 'NONE'), INTEREST_PREVAILS, 'A38'
        )
        h.balancing.balance_summary = self._parse_nullable(data.get('A39', 'NULL'))
        h.balancing.other_rights_balancing = self._parse_bool(data.get('A40', 'FALSE'))
        h.balancing.other_rights = self._parse_string_list(data.get('A41', ''))
        h.balancing.right_prevails = self._validate_enum(
            data.get('A42', 'NONE'), RIGHT_PREVAILS, 'A42'
        )
        h.balancing.rights_balance_summary = self._parse_nullable(data.get('A43', 'NULL'))
        
        return h
    
    def _parse_bool(self, value: str) -> bool:
        return value.upper() == 'TRUE'
    
    def _parse_int(self, value: str, field: str) -> int:
        try:
            return int(value.strip())
        except ValueError:
            self.errors.append(f"{field}: expected integer, got '{value}'")
            return 0
    
    def _parse_int_list(self, value: str, field: str) -> List[int]:
        if not value or value.upper() == 'NULL':
            return []
        result = []
        for item in value.split(','):
            item = item.strip()
            if item:
                try:
                    result.append(int(item))
                except ValueError:
                    self.errors.append(f"{field}: invalid integer '{item}'")
        return result
    
    def _parse_string_list(self, value: str) -> List[str]:
        if not value or value.upper() == 'NULL':
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def _parse_enum_list(self, value: str, valid: set, field: str) -> List[str]:
        if not value or value.upper() == 'NULL':
            return []
        result = []
        for item in value.split(','):
            item = item.strip().upper()
            if item and item != 'NULL':
                if item in valid:
                    result.append(item)
                else:
                    self.warnings.append(f"{field}: unknown value '{item}'")
        return result
    
    def _parse_nullable(self, value: str) -> Optional[str]:
        if not value or value.upper() == 'NULL':
            return None
        return value
    
    def _validate_enum(self, value: str, valid: set, field: str) -> str:
        value = value.upper().strip()
        if value not in valid:
            self.warnings.append(f"{field}: unknown value '{value}', valid: {sorted(valid)[:5]}...")
            return value  # Keep original for inspection
        return value


# ============================================================================
# DATA EXPORT
# ============================================================================

def dataclass_to_dict(obj) -> Any:
    """Convert dataclass to dict, handling nested dataclasses."""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: dataclass_to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    else:
        return obj


def export_json(cases: List[Case], output_path: Path):
    """Export cases to JSON."""
    data = [dataclass_to_dict(c) for c in cases]
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def export_csv(cases: List[Case], output_path: Path):
    """Export cases to flattened CSV (one row per holding)."""
    import csv
    
    rows = []
    for case in cases:
        for h in case.holdings:
            row = {
                # Case metadata
                'case_id': case.case_id,
                'judgment_date': case.judgment_date,
                'chamber': case.chamber,
                'case_holding_count': case.holding_count,
                
                # Holding basics
                'holding_id': h.holding_id,
                'paragraphs': ';'.join(map(str, h.paragraphs)),
                'paragraph_count': len(h.paragraphs),
                'core_holding': h.core_holding,
                'provisions_cited': ';'.join(h.provisions_cited),
                'article_numbers': ';'.join(map(str, h.article_numbers)),
                'primary_concept': h.primary_concept,
                'secondary_concepts': ';'.join(h.secondary_concepts),
                
                # Interpretation
                'semantic_present': h.interpretation.semantic_present,
                'semantic_quote': h.interpretation.semantic_quote or '',
                'systematic_present': h.interpretation.systematic_present,
                'systematic_quote': h.interpretation.systematic_quote or '',
                'teleological_present': h.interpretation.teleological_present,
                'teleological_quote': h.interpretation.teleological_quote or '',
                'teleological_purposes': ';'.join(h.interpretation.teleological_purposes),
                'other_purpose': h.interpretation.other_purpose or '',
                'dominant_source': h.interpretation.dominant_source,
                'dominant_confident': h.interpretation.dominant_confident,
                
                # Reasoning
                'rule_based_present': h.reasoning.rule_based_present,
                'case_law_present': h.reasoning.case_law_present,
                'cited_cases': ';'.join(h.reasoning.cited_cases),
                'cited_case_count': len(h.reasoning.cited_cases),
                'principle_based_present': h.reasoning.principle_based_present,
                'dominant_structure': h.reasoning.dominant_structure,
                'level_shifting': h.reasoning.level_shifting,
                
                # Direction
                'ruling_direction': h.ruling_direction,
                'direction_justification': h.direction_justification,
                
                # Balancing
                'necessity_discussed': h.balancing.necessity_discussed,
                'necessity_standard': h.balancing.necessity_standard,
                'controller_ds_balancing': h.balancing.controller_ds_balancing,
                'interest_prevails': h.balancing.interest_prevails,
                'other_rights_balancing': h.balancing.other_rights_balancing,
                'other_rights': ';'.join(h.balancing.other_rights),
                'right_prevails': h.balancing.right_prevails,
            }
            rows.append(row)
    
    if rows:
        fieldnames = list(rows[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def create_sqlite_schema(conn: sqlite3.Connection):
    """Create the SQLite database schema."""
    conn.executescript('''
        -- Cases table
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            judgment_date TEXT,
            judgment_year INTEGER,
            chamber TEXT,
            holding_count INTEGER,
            source_file TEXT
        );
        
        -- Holdings table
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            holding_id INTEGER,
            paragraphs TEXT,
            paragraph_count INTEGER,
            core_holding TEXT,
            provisions_cited TEXT,
            article_numbers TEXT,
            primary_concept TEXT,
            secondary_concepts TEXT,
            
            -- Interpretation
            semantic_present INTEGER,
            semantic_quote TEXT,
            systematic_present INTEGER,
            systematic_quote TEXT,
            teleological_present INTEGER,
            teleological_quote TEXT,
            teleological_purposes TEXT,
            other_purpose TEXT,
            dominant_source TEXT,
            dominant_confident INTEGER,
            
            -- Reasoning
            rule_based_present INTEGER,
            rule_based_quote TEXT,
            case_law_present INTEGER,
            case_law_quote TEXT,
            cited_cases TEXT,
            cited_case_count INTEGER,
            principle_based_present INTEGER,
            principle_based_quote TEXT,
            dominant_structure TEXT,
            level_shifting INTEGER,
            level_shifting_explanation TEXT,
            
            -- Direction
            ruling_direction TEXT,
            direction_justification TEXT,
            
            -- Balancing
            necessity_discussed INTEGER,
            necessity_standard TEXT,
            necessity_summary TEXT,
            controller_ds_balancing INTEGER,
            interest_prevails TEXT,
            balance_summary TEXT,
            other_rights_balancing INTEGER,
            other_rights TEXT,
            right_prevails TEXT,
            rights_balance_summary TEXT,
            
            FOREIGN KEY (case_id) REFERENCES cases(case_id)
        );
        
        -- Indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_holdings_case ON holdings(case_id);
        CREATE INDEX IF NOT EXISTS idx_holdings_concept ON holdings(primary_concept);
        CREATE INDEX IF NOT EXISTS idx_holdings_direction ON holdings(ruling_direction);
        CREATE INDEX IF NOT EXISTS idx_holdings_dominant_source ON holdings(dominant_source);
        CREATE INDEX IF NOT EXISTS idx_holdings_chamber ON holdings(case_id);
        CREATE INDEX IF NOT EXISTS idx_cases_year ON cases(judgment_year);
        CREATE INDEX IF NOT EXISTS idx_cases_chamber ON cases(chamber);
        
        -- Cited cases junction table for network analysis
        CREATE TABLE IF NOT EXISTS case_citations (
            citing_case TEXT,
            citing_holding INTEGER,
            cited_case TEXT,
            FOREIGN KEY (citing_case) REFERENCES cases(case_id)
        );
        CREATE INDEX IF NOT EXISTS idx_citations_citing ON case_citations(citing_case);
        CREATE INDEX IF NOT EXISTS idx_citations_cited ON case_citations(cited_case);
        
        -- Article references for analysis
        CREATE TABLE IF NOT EXISTS article_references (
            case_id TEXT,
            holding_id INTEGER,
            article_number INTEGER,
            FOREIGN KEY (case_id) REFERENCES cases(case_id)
        );
        CREATE INDEX IF NOT EXISTS idx_articles_number ON article_references(article_number);
    ''')


def export_sqlite(cases: List[Case], output_path: Path):
    """Export cases to SQLite database."""
    conn = sqlite3.connect(output_path)
    create_sqlite_schema(conn)
    
    for case in cases:
        # Extract year from date
        year = None
        if case.judgment_date:
            try:
                year = int(case.judgment_date.split('-')[0])
            except (ValueError, IndexError):
                pass
        
        # Insert case
        conn.execute('''
            INSERT OR REPLACE INTO cases 
            (case_id, judgment_date, judgment_year, chamber, holding_count, source_file)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (case.case_id, case.judgment_date, year, case.chamber, 
              case.holding_count, case.source_file))
        
        # Insert holdings
        for h in case.holdings:
            conn.execute('''
                INSERT INTO holdings (
                    case_id, holding_id, paragraphs, paragraph_count, core_holding,
                    provisions_cited, article_numbers, primary_concept, secondary_concepts,
                    semantic_present, semantic_quote, systematic_present, systematic_quote,
                    teleological_present, teleological_quote, teleological_purposes,
                    other_purpose, dominant_source, dominant_confident,
                    rule_based_present, rule_based_quote, case_law_present, case_law_quote,
                    cited_cases, cited_case_count, principle_based_present, principle_based_quote,
                    dominant_structure, level_shifting, level_shifting_explanation,
                    ruling_direction, direction_justification,
                    necessity_discussed, necessity_standard, necessity_summary,
                    controller_ds_balancing, interest_prevails, balance_summary,
                    other_rights_balancing, other_rights, right_prevails, rights_balance_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case.case_id, h.holding_id,
                ','.join(map(str, h.paragraphs)), len(h.paragraphs),
                h.core_holding, ','.join(h.provisions_cited),
                ','.join(map(str, h.article_numbers)), h.primary_concept,
                ','.join(h.secondary_concepts),
                int(h.interpretation.semantic_present), h.interpretation.semantic_quote,
                int(h.interpretation.systematic_present), h.interpretation.systematic_quote,
                int(h.interpretation.teleological_present), h.interpretation.teleological_quote,
                ','.join(h.interpretation.teleological_purposes),
                h.interpretation.other_purpose, h.interpretation.dominant_source,
                int(h.interpretation.dominant_confident),
                int(h.reasoning.rule_based_present), h.reasoning.rule_based_quote,
                int(h.reasoning.case_law_present), h.reasoning.case_law_quote,
                ','.join(h.reasoning.cited_cases), len(h.reasoning.cited_cases),
                int(h.reasoning.principle_based_present), h.reasoning.principle_based_quote,
                h.reasoning.dominant_structure, int(h.reasoning.level_shifting),
                h.reasoning.level_shifting_explanation,
                h.ruling_direction, h.direction_justification,
                int(h.balancing.necessity_discussed), h.balancing.necessity_standard,
                h.balancing.necessity_summary,
                int(h.balancing.controller_ds_balancing), h.balancing.interest_prevails,
                h.balancing.balance_summary,
                int(h.balancing.other_rights_balancing), ','.join(h.balancing.other_rights),
                h.balancing.right_prevails, h.balancing.rights_balance_summary
            ))
            
            # Insert citations
            for cited in h.reasoning.cited_cases:
                cited = cited.strip()
                if cited:
                    conn.execute('''
                        INSERT INTO case_citations (citing_case, citing_holding, cited_case)
                        VALUES (?, ?, ?)
                    ''', (case.case_id, h.holding_id, cited))
            
            # Insert article references
            for art in h.article_numbers:
                conn.execute('''
                    INSERT INTO article_references (case_id, holding_id, article_number)
                    VALUES (?, ?, ?)
                ''', (case.case_id, h.holding_id, art))
    
    conn.commit()
    conn.close()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Parse coded GDPR CJEU judgment files'
    )
    parser.add_argument(
        'input',
        nargs='+',
        help='Input file(s) or directory containing *_coded.md files'
    )
    parser.add_argument(
        '-o', '--output',
        default='./output',
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='Export only JSON'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: fail on validation errors'
    )
    
    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect input files
    input_files: List[Path] = []
    for inp in args.input:
        p = Path(inp)
        if p.is_dir():
            input_files.extend(p.glob('*_coded.md'))
        elif p.is_file():
            input_files.append(p)
        else:
            print(f"Warning: {inp} not found")
    
    if not input_files:
        print("No input files found")
        return 1
    
    print(f"Processing {len(input_files)} file(s)...")
    
    # Parse all files
    parser_inst = CodedMDParser(strict=args.strict)
    cases: List[Case] = []
    
    for filepath in sorted(input_files):
        print(f"  Parsing {filepath.name}...")
        case = parser_inst.parse_file(filepath)
        cases.append(case)
        
        if case.parse_errors:
            for err in case.parse_errors:
                print(f"    ERROR: {err}")
        if case.parse_warnings:
            for warn in case.parse_warnings:
                print(f"    WARNING: {warn}")
    
    print(f"\nParsed {len(cases)} cases with {sum(len(c.holdings) for c in cases)} holdings")
    
    # Export
    json_path = output_dir / 'cases.json'
    export_json(cases, json_path)
    print(f"Exported JSON: {json_path}")
    
    if not args.json_only:
        csv_path = output_dir / 'holdings.csv'
        export_csv(cases, csv_path)
        print(f"Exported CSV: {csv_path}")
        
        sqlite_path = output_dir / 'gdpr_cjeu.db'
        export_sqlite(cases, sqlite_path)
        print(f"Exported SQLite: {sqlite_path}")
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total cases: {len(cases)}")
    print(f"Total holdings: {sum(len(c.holdings) for c in cases)}")
    
    # Quick stats
    directions = {}
    concepts = {}
    sources = {}
    for case in cases:
        for h in case.holdings:
            directions[h.ruling_direction] = directions.get(h.ruling_direction, 0) + 1
            concepts[h.primary_concept] = concepts.get(h.primary_concept, 0) + 1
            sources[h.interpretation.dominant_source] = sources.get(h.interpretation.dominant_source, 0) + 1
    
    print("\nRuling directions:")
    for k, v in sorted(directions.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    
    print("\nTop concepts:")
    for k, v in sorted(concepts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k}: {v}")
    
    print("\nDominant interpretation sources:")
    for k, v in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    
    return 0


if __name__ == '__main__':
    exit(main())
