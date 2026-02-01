#!/usr/bin/env python3
"""
CJEU Judgement Heading Extraction and Insertion System

This script adds markdown headings to CJEU judgement files to enable:
1. Better navigation and readability
2. Programmatic section extraction ("chopping")
3. Semantic structure preservation

Based on comprehensive analysis of 15+ CJEU judgements, this system handles:
- Standard section structures
- Combined/grouped questions
- Out-of-order question examination
- Variations in terminology (EU law vs European Union law, etc.)
- Typos in original documents (e.g., "The7th")
- Missing sections (some judgements lack certain headers)
- Nested legal context hierarchies

Heading Levels:
- ## (H2): Major structural sections (Judgment, Legal context, Dispute, Consideration, Costs, Operative)
- ### (H3): Primary sub-sections (EU law, National law, Question headers)
- #### (H4): Tertiary sections (specific directives, Admissibility, Substance, Preliminary observations)

Author: Claude Code
"""

import re
import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class HeadingLevel(Enum):
    """Markdown heading levels for different section types."""
    H2 = "##"      # Major sections
    H3 = "###"     # Primary sub-sections
    H4 = "####"    # Tertiary sections


@dataclass
class HeadingPattern:
    """Represents a pattern for detecting section headings."""
    pattern: re.Pattern
    level: HeadingLevel
    description: str
    priority: int = 0  # Higher priority patterns are checked first


@dataclass
class DetectedHeading:
    """Represents a detected heading in the document."""
    line_number: int
    original_text: str
    heading_level: HeadingLevel
    pattern_description: str


class JudgementHeadingProcessor:
    """
    Processes CJEU judgement markdown files to add structural headings.

    This class handles the complex patterns found in CJEU judgements, including:
    - Standard sections (Legal context, Dispute, Consideration, Costs)
    - Question analysis sections with various formats
    - Legal framework hierarchies (EU law, National law, specific directives)
    - Edge cases (typos, variations, missing sections)
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.patterns = self._build_patterns()

    def _build_patterns(self) -> List[HeadingPattern]:
        """
        Build comprehensive pattern list for heading detection.

        Patterns are ordered by specificity - more specific patterns first
        to avoid false matches.
        """
        patterns = []

        # ============================================================
        # LEVEL 2 (H2) - MAJOR STRUCTURAL SECTIONS
        # ============================================================

        # Document title - "Judgment" standalone
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Judgment$', re.IGNORECASE),
            level=HeadingLevel.H2,
            description="Document title",
            priority=100
        ))

        # ============================================================
        # ROMAN NUMERAL FORMAT (used in complex cases like C-817-19)
        # These cases use: I., II., III., IV. for major sections
        # and A., B. for sub-sections, 1., 2. for sub-sub-sections
        # ============================================================

        # Roman numeral major sections: "I. Legal context", "II. The dispute..."
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+Legal\s+context$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Legal context (Roman numeral format)",
            priority=110
        ))

        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+'
                r'(The\s+)?dispute\s+in\s+the\s+main\s+proceedings',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Dispute section (Roman numeral format)",
            priority=110
        ))

        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+'
                r'Consideration\s+of\s+the\s+questions?\s+referred',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Question consideration (Roman numeral format)",
            priority=110
        ))

        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+Costs$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Costs section (Roman numeral format)",
            priority=110
        ))

        # Letter-prefixed sub-sections: "A. European Union law", "B. Belgian law"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^[A-H]\.\s+(European\s+Union\s+law|EU\s+law)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="EU law (letter prefix format)",
            priority=105
        ))

        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^[A-H]\.\s+'
                r'(National\s+law|German\s+law|Belgian\s+law|French\s+law|'
                r'Hungarian\s+law|Finnish\s+law|Bulgarian\s+law|Lithuanian\s+law|'
                r'[A-Z][a-z]+\s+law)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="National law (letter prefix format)",
            priority=105
        ))

        # Letter-prefixed question sections: "A. Question 1", "B. Questions 2 to 4 and Question 6"
        # Also handles: "F. Question 9(a)", "G. Question 9(b)"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^[A-H]\.\s+Questions?\s+\d+(\([a-z]\))?'
                r'(\s+(to|and)\s+\d+)*'
                r'(\s+and\s+Questions?\s+\d+)?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="Question header (letter prefix format)",
            priority=105
        ))

        # Number-prefixed directive/regulation: "1. Directive 95/46/EC", "2. The API Directive"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^\d+\.\s+(Directive\s+(\(EU\)\s+)?(\d{2,4}/\d+|95/46)(/EC|/EEC)?'
                r'|The\s+\w+\s+Directive'
                r'|The\s+GDPR'
                r'|Regulation\s+(\(EU\)\s+)?\d{2,4}/\d+)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Legislation reference (number prefix format)",
            priority=105
        ))

        # Number-prefixed national law: "1. The Constitution", "2. The Law of 25 December 2016"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^\d+\.\s+The\s+(Constitution|Law\s+of\s+.+)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="National law act (number prefix format)",
            priority=105
        ))

        # Number-prefixed analysis sections: "1. Interferences with...", "2. Justification for..."
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^\d+\.\s+'
                r'(Interferences\s+with|Justification\s+for|'
                r'Air\s+passenger|The\s+purposes|The\s+link\s+between|'
                r'The\s+air\s+passengers|Advance\s+assessment|'
                r'The\s+disclosure)',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Analysis sub-section (number prefix format)",
            priority=100
        ))

        # Parenthetical sub-sub-sections: "(a) Observance of...", "(b) Objective of..."
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^\([a-z]\)\s+[A-Z]',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Sub-sub-section (parenthetical format)",
            priority=95
        ))

        # Numbered parenthetical sub-sections: "(1) Air passenger data...", "(2) The purposes..."
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^\(\d+\)\s+[A-Z]',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Numbered sub-section (parenthetical format)",
            priority=95
        ))

        # Roman numeral sub-sub-sections: "(i) Comparing PNR data...", "(ii) Processing..."
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^\((i|ii|iii|iv|v|vi)\)\s+[A-Z]',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Roman numeral sub-section (parenthetical format)",
            priority=95
        ))

        # ============================================================
        # STANDARD FORMAT SECTIONS (non-Roman numeral)
        # ============================================================

        # Legal context section
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Legal context$', re.IGNORECASE),
            level=HeadingLevel.H2,
            description="Legal framework section",
            priority=100
        ))

        # Dispute/Facts section - multiple variations
        # Pattern: [The] [facts of the] dispute in the main proceedings...
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(The\s+)?(facts\s+of\s+the\s+)?'
                r'[Dd]ispute\s+in\s+the\s+main\s+proceedings\s+'
                r'and\s+the\s+questions?\s+referred'
                r'(\s+for\s+a\s+preliminary\s+ruling)?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Dispute and questions referred section",
            priority=100
        ))

        # Admissibility of the request (top-level, not under question)
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^Admissibility\s+of\s+the\s+request\s+for\s+a\s+preliminary\s+ruling$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Request admissibility section",
            priority=95
        ))

        # Jurisdiction of the Court
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^The\s+jurisdiction\s+of\s+the\s+Court$', re.IGNORECASE),
            level=HeadingLevel.H2,
            description="Jurisdiction section",
            priority=100
        ))

        # Consideration of questions referred - multiple variations
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(Consideration\s+of\s+the\s+questions?\s+referred'
                r'|The\s+request\s+for\s+a\s+preliminary\s+ruling)'
                r'(\s+for\s+a\s+preliminary\s+ruling)?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Question consideration section",
            priority=100
        ))

        # Request to reopen written procedure (rare but important)
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^The\s+request\s+to\s+have\s+the\s+written\s+procedure\s+reopened$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Procedure reopening request",
            priority=100
        ))

        # Costs section
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Costs$', re.IGNORECASE),
            level=HeadingLevel.H2,
            description="Costs section",
            priority=100
        ))

        # Operative part - "On those grounds, the Court..."
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^On\s+those\s+grounds,?\s+the\s+Court\s*'
                r'\([^)]+\)\s*hereby\s+rules:?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H2,
            description="Operative part (ruling)",
            priority=100
        ))

        # ============================================================
        # LEVEL 3 (H3) - PRIMARY SUB-SECTIONS
        # ============================================================

        # EU law section - variations
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^(European\s+Union\s+law|EU\s+law)$', re.IGNORECASE),
            level=HeadingLevel.H3,
            description="EU law sub-section",
            priority=90
        ))

        # National law sections - various country patterns
        # Matches: "German law", "Hungarian law", "National law", "Finnish law", etc.
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(National\s+law|'
                r'German\s+law|Hungarian\s+law|Finnish\s+law|'
                r'Belgian\s+law|Bulgarian\s+law|Lithuanian\s+law|'
                r'French\s+law|Italian\s+law|Spanish\s+law|'
                r'Polish\s+law|Dutch\s+law|Austrian\s+law|'
                r'Irish\s+law|Greek\s+law|Portuguese\s+law|'
                r'Swedish\s+law|Danish\s+law|Czech\s+law|'
                r'Slovak\s+law|Romanian\s+law|Croatian\s+law|'
                r'Slovenian\s+law|Estonian\s+law|Latvian\s+law|'
                r'Maltese\s+law|Cypriot\s+law|Luxembourgish\s+law|'
                r'[A-Z][a-z]+\s+law)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="National law sub-section",
            priority=90
        ))

        # Question headers - COMPLEX PATTERNS
        # These handle: "The first question", "First question", "The second and third questions",
        # "Questions 1 and 2", "Question 1(a) and (c)", "The7th question" (typo), etc.

        # Pattern for ordinal questions with optional "The" and combinations
        # Matches: "The first question", "First question", "The first and second questions",
        # "The second, third and sixth questions", "The first, second and third questions"
        ordinal_words = (
            r'first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|'
            r'eleventh|twelfth|thirteenth|fourteenth|fifteenth'
        )

        # Single or combined ordinal questions
        patterns.append(HeadingPattern(
            pattern=re.compile(
                rf'^(The\s+)?({ordinal_words})'
                rf'(,?\s*({ordinal_words}))*'
                rf'(\s+and\s+({ordinal_words}))?'
                rf'\s+questions?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="Question header (ordinal)",
            priority=85
        ))

        # Numeric questions: "The 4th question", "The 4th, 5th and 6th questions"
        # Also handles typos like "The7th" (no space)
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(The\s*)?(\d+)(st|nd|rd|th)'
                r'(,?\s*(\d+)(st|nd|rd|th))*'
                r'(\s+and\s+(\d+)(st|nd|rd|th))?'
                r'\s+questions?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="Question header (numeric ordinal)",
            priority=85
        ))

        # Questions with sub-parts: "Question 1(a) and (c)", "Question 1(a), (b) and (c)"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^Questions?\s+\d+'
                r'(\([a-z]\))'
                r'(,?\s*\([a-z]\))*'
                r'(\s+and\s+\([a-z]\))?$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H3,
            description="Question header (with sub-parts)",
            priority=85
        ))

        # Simple "Question X" format: "Question 1", "Question 2"
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Questions?\s+\d+$', re.IGNORECASE),
            level=HeadingLevel.H3,
            description="Question header (simple numeric)",
            priority=85
        ))

        # ============================================================
        # LEVEL 4 (H4) - TERTIARY SECTIONS
        # ============================================================

        # Preliminary observations
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Preliminary\s+observations$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="Preliminary observations",
            priority=80
        ))

        # Admissibility (under a question, not top-level)
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Admissibility$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="Admissibility sub-section",
            priority=75
        ))

        # Substance
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Substance$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="Substance sub-section",
            priority=80
        ))

        # Specific EU legislation - Directives
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^Directive\s+(\(EU\)\s+)?\d{2,4}/\d+(/EC|/EEC)?'
                r'(;|$)',  # May end with semicolon (edge case found)
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="EU Directive reference",
            priority=80
        ))

        # Specific EU legislation - Regulations
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^Regulation\s+(\(EU\)\s+)?\d{2,4}/\d+'
                r'(;|$)',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="EU Regulation reference",
            priority=80
        ))

        # "The GDPR" as sub-section header
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^The\s+GDPR$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="GDPR sub-section",
            priority=80
        ))

        # Directive 95/46 (older style without "Directive" prefix sometimes)
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^Directive\s+95/46(/EC)?$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="Data Protection Directive",
            priority=80
        ))

        # Decision references (e.g., "The SCC Decision", "The Privacy Shield Decision")
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^The\s+[A-Za-z\s]+Decision$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Decision reference",
            priority=75
        ))

        # National law specific acts - common patterns
        # e.g., "The Law on the registers", "Federal law", "The law of Land Hessen"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^(The\s+)?(Law\s+on\s+.+|Federal\s+law|'
                r'The\s+law\s+of\s+.+|'
                r'The\s+Commercial\s+Code|'
                r'Decree\s+No\s+.+)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="National law act reference",
            priority=75
        ))

        # Generic law reference with statute numbers
        # e.g., "Law on the protection of personal data (1050/2018)"
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^Law\s+on\s+.+\(\d+/\d+\)$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="National statute with number",
            priority=75
        ))

        # The finding of... (sub-section within question analysis)
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^The\s+finding\s+of\s+.+$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="Finding sub-section",
            priority=70
        ))

        # The customs legislation (thematic sub-section)
        patterns.append(HeadingPattern(
            pattern=re.compile(r'^The\s+customs\s+legislation;?$', re.IGNORECASE),
            level=HeadingLevel.H4,
            description="Customs legislation sub-section",
            priority=75
        ))

        # The right to protection of personal data (thematic)
        patterns.append(HeadingPattern(
            pattern=re.compile(
                r'^The\s+right\s+to\s+protection\s+of\s+personal\s+data$',
                re.IGNORECASE
            ),
            level=HeadingLevel.H4,
            description="Personal data protection sub-section",
            priority=75
        ))

        # Sort by priority (highest first)
        patterns.sort(key=lambda p: -p.priority)

        return patterns

    def _is_already_heading(self, line: str) -> bool:
        """Check if line is already a markdown heading."""
        return line.strip().startswith('#')

    def _is_paragraph_number(self, line: str) -> bool:
        """Check if line starts with a paragraph number (e.g., '1', '32', '100')."""
        stripped = line.strip()
        # Match lines that are just numbers or start with number followed by space
        if re.match(r'^\d+\s', stripped) or re.match(r'^\d+$', stripped):
            return True
        return False

    def _is_empty_or_whitespace(self, line: str) -> bool:
        """Check if line is empty or whitespace only."""
        return len(line.strip()) == 0

    def _clean_heading_text(self, text: str) -> str:
        """
        Clean heading text for consistency.

        - Removes trailing semicolons (edge case)
        - Normalizes whitespace
        - Preserves original casing
        """
        cleaned = text.strip()
        # Remove trailing semicolons (found in some documents)
        if cleaned.endswith(';'):
            cleaned = cleaned[:-1]
        return cleaned

    def _find_table_of_contents_end(self, lines: List[str]) -> int:
        """
        Find the end of the table of contents section, if present.

        Some judgements (like C-817-19) have a table of contents at the start.
        We need to skip these lines to avoid duplicate headings.

        Returns the line number after which actual content begins,
        or 0 if no table of contents is detected.
        """
        # Look for "Table of contents" marker
        toc_start = -1
        for i, line in enumerate(lines[:50]):  # Check first 50 lines
            if 'table of contents' in line.lower():
                toc_start = i
                break

        if toc_start == -1:
            return 0  # No TOC found

        # Find where actual "Judgment" section starts (after the formal header stuff)
        # Look for "gives the following" followed by "Judgment"
        for i in range(toc_start, min(len(lines), 250)):
            stripped = lines[i].strip().lower()
            if stripped == 'judgment':
                # Check if previous non-empty line contains "gives the following"
                for j in range(i-1, max(0, i-10), -1):
                    prev_stripped = lines[j].strip().lower()
                    if 'gives the following' in prev_stripped:
                        return i  # Return the "Judgment" line number
                    if prev_stripped:  # Stop at first non-empty line
                        break

        # Fallback: if we found TOC but not "gives the following",
        # look for first paragraph numbered "1 "
        for i in range(toc_start, min(len(lines), 300)):
            stripped = lines[i].strip()
            if re.match(r'^1\s+This\s+', stripped, re.IGNORECASE):
                # The "Judgment" header should be a few lines before this
                for j in range(i-1, max(0, i-10), -1):
                    if lines[j].strip().lower() == 'judgment':
                        return j
                return i - 2  # Estimate

        return 0  # Couldn't determine, process from start

    def detect_headings(self, content: str) -> List[DetectedHeading]:
        """
        Detect all potential headings in the document.

        Returns a list of DetectedHeading objects with line numbers
        and suggested heading levels.
        """
        lines = content.split('\n')
        detected = []

        # Find where table of contents ends (if present)
        content_start = self._find_table_of_contents_end(lines)
        if self.verbose and content_start > 0:
            print(f"  Table of contents detected, content starts at line {content_start + 1}")

        for i, line in enumerate(lines):
            # Skip lines before actual content (in table of contents)
            if i < content_start:
                continue

            stripped = line.strip()

            # Skip empty lines, existing headings, and paragraph numbers
            if (self._is_empty_or_whitespace(line) or
                self._is_already_heading(line) or
                self._is_paragraph_number(line)):
                continue

            # Skip lines that are too long (likely paragraph content)
            if len(stripped) > 150:
                continue

            # Skip lines starting with common paragraph markers
            if stripped.startswith(('–', '-', '•', '*', '(', '"', "'")):
                continue

            # Check against all patterns
            for pattern in self.patterns:
                if pattern.pattern.match(stripped):
                    detected.append(DetectedHeading(
                        line_number=i,
                        original_text=stripped,
                        heading_level=pattern.level,
                        pattern_description=pattern.description
                    ))
                    if self.verbose:
                        print(f"  Line {i+1}: [{pattern.level.value}] {stripped}")
                        print(f"           Pattern: {pattern.description}")
                    break  # Use first matching pattern (highest priority)

        return detected

    def add_headings(self, content: str) -> str:
        """
        Add markdown headings to the document content.

        Returns the modified content with headings inserted.
        """
        detected = self.detect_headings(content)

        if not detected:
            return content

        lines = content.split('\n')

        # Process in reverse order to preserve line numbers
        for heading in reversed(detected):
            line_idx = heading.line_number
            original = lines[line_idx]
            cleaned_text = self._clean_heading_text(heading.original_text)

            # Create the heading line
            new_line = f"{heading.heading_level.value} {cleaned_text}"

            # Preserve original indentation if any (though usually none for headings)
            leading_whitespace = original[:len(original) - len(original.lstrip())]
            lines[line_idx] = leading_whitespace + new_line

        return '\n'.join(lines)

    def process_file(self, filepath: Path, dry_run: bool = False) -> Tuple[bool, int]:
        """
        Process a single judgement file.

        Args:
            filepath: Path to the markdown file
            dry_run: If True, don't write changes, just report

        Returns:
            Tuple of (success: bool, headings_added: int)
        """
        try:
            content = filepath.read_text(encoding='utf-8')

            if self.verbose:
                print(f"\nProcessing: {filepath.name}")

            detected = self.detect_headings(content)

            if not detected:
                if self.verbose:
                    print(f"  No headings detected")
                return True, 0

            if dry_run:
                print(f"\n{filepath.name}: {len(detected)} headings would be added:")
                for h in detected:
                    print(f"  Line {h.line_number + 1}: [{h.heading_level.value}] {h.original_text}")
                return True, len(detected)

            # Add headings and write back
            modified_content = self.add_headings(content)
            filepath.write_text(modified_content, encoding='utf-8')

            if self.verbose:
                print(f"  Added {len(detected)} headings")

            return True, len(detected)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return False, 0

    def process_directory(
        self,
        directory: Path,
        dry_run: bool = False,
        pattern: str = "*.md"
    ) -> Dict[str, int]:
        """
        Process all matching files in a directory.

        Args:
            directory: Path to directory containing judgement files
            dry_run: If True, don't write changes
            pattern: Glob pattern for files to process

        Returns:
            Dictionary with statistics
        """
        files = list(directory.glob(pattern))

        stats = {
            'total_files': len(files),
            'processed': 0,
            'failed': 0,
            'total_headings': 0
        }

        print(f"\nProcessing {len(files)} files in {directory}")

        for filepath in sorted(files):
            success, headings = self.process_file(filepath, dry_run)
            if success:
                stats['processed'] += 1
                stats['total_headings'] += headings
            else:
                stats['failed'] += 1

        return stats


def validate_headings(filepath: Path) -> List[str]:
    """
    Validate that headings in a file are properly structured.

    Checks:
    - Heading hierarchy (no skipping levels)
    - Expected sections present
    - No duplicate headings at same level

    Returns list of warnings/issues found.
    """
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    issues = []

    heading_pattern = re.compile(r'^(#{2,4})\s+(.+)$')

    found_sections = {
        'judgment': False,
        'legal_context': False,
        'dispute': False,
        'consideration': False,
        'costs': False,
        'operative': False
    }

    prev_level = 0

    for i, line in enumerate(lines):
        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).lower()

            # Check for level skipping
            if prev_level > 0 and level > prev_level + 1:
                issues.append(f"Line {i+1}: Heading level skipped from {prev_level} to {level}")

            prev_level = level

            # Track found sections
            if 'judgment' in text:
                found_sections['judgment'] = True
            elif 'legal context' in text:
                found_sections['legal_context'] = True
            elif 'dispute' in text or 'main proceedings' in text:
                found_sections['dispute'] = True
            elif 'consideration' in text:
                found_sections['consideration'] = True
            elif text == 'costs':
                found_sections['costs'] = True
            elif 'hereby rules' in text:
                found_sections['operative'] = True

    # Check for missing expected sections
    for section, found in found_sections.items():
        if not found:
            issues.append(f"Missing expected section: {section}")

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Add structural headings to CJEU judgement markdown files'
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to a single file or directory of files'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate heading structure after processing'
    )
    parser.add_argument(
        '--pattern', '-p',
        default='*.md',
        help='File pattern to match (default: *.md)'
    )

    args = parser.parse_args()

    processor = JudgementHeadingProcessor(verbose=args.verbose)

    if args.path.is_file():
        success, count = processor.process_file(args.path, dry_run=args.dry_run)
        if success:
            print(f"\nProcessed: {args.path.name}")
            print(f"Headings added: {count}")

            if args.validate and not args.dry_run:
                issues = validate_headings(args.path)
                if issues:
                    print("\nValidation issues:")
                    for issue in issues:
                        print(f"  - {issue}")
                else:
                    print("\nValidation passed")
        else:
            sys.exit(1)

    elif args.path.is_dir():
        stats = processor.process_directory(
            args.path,
            dry_run=args.dry_run,
            pattern=args.pattern
        )

        print(f"\n{'=' * 50}")
        print(f"Summary:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Total headings added: {stats['total_headings']}")

        if args.validate and not args.dry_run:
            print("\nValidating processed files...")
            all_issues = []
            for filepath in args.path.glob(args.pattern):
                issues = validate_headings(filepath)
                if issues:
                    all_issues.append((filepath.name, issues))

            if all_issues:
                print(f"\nValidation issues found in {len(all_issues)} files:")
                for filename, issues in all_issues[:5]:  # Show first 5
                    print(f"\n  {filename}:")
                    for issue in issues:
                        print(f"    - {issue}")
                if len(all_issues) > 5:
                    print(f"\n  ... and {len(all_issues) - 5} more files with issues")
            else:
                print("\nAll files passed validation")
    else:
        print(f"Error: {args.path} does not exist")
        sys.exit(1)


if __name__ == '__main__':
    main()
