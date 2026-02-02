#!/usr/bin/env python3
"""
CJEU Ruling-to-Question Matcher

This script matches operative part rulings to their corresponding question
sections in CJEU judgement markdown files. It uses multiple matching strategies:

1. Explicit Markers: Finds "the answer to the X question is that..." patterns
2. Article Reference Matching: Matches GDPR Articles mentioned in rulings to
   Articles discussed in question sections
3. Semantic Similarity: Uses sentence embeddings to find best matching sections
4. GDPR Topic Classification: Classifies rulings by GDPR concept/topic

This enables:
- Automatic section extraction for specific rulings
- Topic-based filtering (e.g., "all legitimate interest rulings")
- Cross-judgement analysis by topic

Author: Claude Code
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

# Try to import optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("Note: sentence-transformers not available. Using heuristic matching only.")

try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False


# GDPR topic taxonomy for classification
GDPR_TOPICS = {
    'LEGITIMATE_INTEREST': {
        'keywords': ['legitimate interest', 'article 6(1)(f)', 'art. 6(1)(f)',
                     'balancing', 'overriding interest'],
        'articles': ['6(1)(f)', '6.1.f']
    },
    'CONSENT': {
        'keywords': ['consent', 'article 6(1)(a)', 'article 7', 'freely given',
                     'explicit consent', 'withdrawal'],
        'articles': ['6(1)(a)', '7']
    },
    'RIGHT_TO_ERASURE': {
        'keywords': ['erasure', 'right to be forgotten', 'article 17',
                     'deletion', 'erase'],
        'articles': ['17']
    },
    'RIGHT_OF_ACCESS': {
        'keywords': ['access', 'article 15', 'copy', 'obtain', 'right of access'],
        'articles': ['15']
    },
    'RIGHT_TO_RECTIFICATION': {
        'keywords': ['rectification', 'article 16', 'correct', 'inaccurate'],
        'articles': ['16']
    },
    'DATA_SUBJECT_RIGHTS': {
        'keywords': ['data subject rights', 'articles 12 to 22', 'exercise of rights'],
        'articles': ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']
    },
    'COMPENSATION': {
        'keywords': ['compensation', 'damages', 'article 82', 'non-material damage',
                     'material damage', 'liability'],
        'articles': ['82']
    },
    'DATA_BREACH': {
        'keywords': ['breach', 'article 33', 'article 34', 'notification',
                     'personal data breach', 'security incident'],
        'articles': ['33', '34']
    },
    'TRANSFERS': {
        'keywords': ['transfer', 'third country', 'article 44', 'article 45',
                     'article 46', 'adequacy', 'standard contractual clauses', 'scc'],
        'articles': ['44', '45', '46', '47', '49']
    },
    'CONTROLLER_PROCESSOR': {
        'keywords': ['controller', 'processor', 'joint controller', 'article 26',
                     'article 28', 'processing on behalf'],
        'articles': ['26', '28', '4(7)', '4(8)']
    },
    'LAWFULNESS': {
        'keywords': ['lawfulness', 'legal basis', 'article 6', 'lawful processing'],
        'articles': ['6']
    },
    'PURPOSE_LIMITATION': {
        'keywords': ['purpose limitation', 'compatible purpose', 'further processing',
                     'article 5(1)(b)'],
        'articles': ['5(1)(b)']
    },
    'DATA_MINIMISATION': {
        'keywords': ['minimisation', 'adequate, relevant', 'article 5(1)(c)'],
        'articles': ['5(1)(c)']
    },
    'SPECIAL_CATEGORIES': {
        'keywords': ['special categories', 'sensitive data', 'article 9',
                     'health data', 'biometric', 'genetic', 'racial', 'ethnic',
                     'political opinions', 'religious', 'sexual orientation'],
        'articles': ['9']
    },
    'DPA_POWERS': {
        'keywords': ['supervisory authority', 'dpa', 'article 51', 'article 58',
                     'corrective powers', 'investigative powers'],
        'articles': ['51', '52', '57', '58']
    },
    'FINES': {
        'keywords': ['administrative fine', 'article 83', 'penalty', 'sanction'],
        'articles': ['83']
    },
    'TERRITORIAL_SCOPE': {
        'keywords': ['territorial scope', 'article 3', 'establishment',
                     'offering goods', 'monitoring behaviour'],
        'articles': ['3']
    },
    'MATERIAL_SCOPE': {
        'keywords': ['material scope', 'article 2', 'household exemption',
                     'law enforcement'],
        'articles': ['2']
    },
    'TRANSPARENCY': {
        'keywords': ['transparency', 'information', 'article 13', 'article 14',
                     'privacy notice', 'fair processing'],
        'articles': ['13', '14']
    },
    'PROFILING': {
        'keywords': ['profiling', 'automated decision', 'article 22',
                     'automated processing'],
        'articles': ['22']
    }
}


@dataclass
class QuestionSection:
    """Represents a question analysis section in the judgement."""
    header: str
    question_numbers: List[str]  # e.g., ['first', 'second'] or ['1', '2']
    start_line: int
    end_line: int
    content: str
    answer_text: Optional[str] = None  # The "answer to X question is that..." text
    articles_mentioned: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)


@dataclass
class OperativeRuling:
    """Represents a single ruling in the operative part."""
    number: int
    article_reference: str  # e.g., "Article 82(1) of Regulation 2016/679"
    ruling_text: str
    full_text: str
    start_line: int
    articles_mentioned: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    matched_questions: List[str] = field(default_factory=list)
    match_confidence: float = 0.0
    match_method: str = ""


@dataclass
class JudgementAnalysis:
    """Complete analysis of a judgement's structure."""
    case_id: str
    questions: List[QuestionSection]
    rulings: List[OperativeRuling]
    ruling_question_mapping: Dict[int, List[str]]  # ruling_num -> question_nums


class RulingQuestionMatcher:
    """
    Matches operative rulings to question sections using multiple strategies.
    """

    def __init__(self, use_semantic: bool = True, model_name: str = 'all-MiniLM-L6-v2'):
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE
        self.model = None
        self.model_name = model_name

        if self.use_semantic:
            print(f"Loading semantic model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            print("Model loaded.")

    def extract_articles(self, text: str) -> List[str]:
        """Extract GDPR article references from text."""
        articles = []

        # Pattern for "Article X" or "Article X(Y)"
        pattern = r'Article\s+(\d+)(?:\((\d+)\))?(?:\([a-z]\))?'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            article = match.group(1)
            paragraph = match.group(2)
            if paragraph:
                articles.append(f"{article}({paragraph})")
            else:
                articles.append(article)

        # Pattern for "Art. X" shorthand
        pattern = r'Art\.\s*(\d+)(?:\((\d+)\))?'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            article = match.group(1)
            paragraph = match.group(2)
            if paragraph:
                articles.append(f"{article}({paragraph})")
            else:
                articles.append(article)

        return list(set(articles))

    def classify_topics(self, text: str) -> List[str]:
        """Classify text by GDPR topics based on keywords and articles."""
        text_lower = text.lower()
        topics = []

        for topic, config in GDPR_TOPICS.items():
            # Check keywords
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    if topic not in topics:
                        topics.append(topic)
                    break

            # Check article references
            for article in config['articles']:
                if re.search(rf'article\s*{re.escape(article)}', text_lower):
                    if topic not in topics:
                        topics.append(topic)
                    break

        return topics

    def parse_question_header(self, header: str) -> List[str]:
        """Parse question header to extract question numbers."""
        questions = []
        header_lower = header.lower()

        # Ordinal words
        ordinals = {
            'first': '1', 'second': '2', 'third': '3', 'fourth': '4',
            'fifth': '5', 'sixth': '6', 'seventh': '7', 'eighth': '8',
            'ninth': '9', 'tenth': '10', 'eleventh': '11', 'twelfth': '12'
        }

        # Check for ordinal words
        for word, num in ordinals.items():
            if word in header_lower:
                questions.append(num)

        # Check for numeric patterns like "4th", "5th", "7th" etc.
        # Also handles typos like "The7th" (no space before number)
        for match in re.finditer(r'(\d+)(?:st|nd|rd|th)', header_lower):
            num = match.group(1)
            if num not in questions:
                questions.append(num)

        # Check for "Question X" patterns
        for match in re.finditer(r'questions?\s+(\d+)', header_lower):
            num = match.group(1)
            if num not in questions:
                questions.append(num)

        # Handle sub-questions like "9(a)", "9(b)"
        for match in re.finditer(r'(\d+)\s*\([a-z]\)', header_lower):
            num = match.group(1)
            if num not in questions:
                questions.append(num)

        return sorted(questions, key=lambda x: int(re.match(r'\d+', x).group())) if questions else []

    def extract_question_sections(self, content: str, lines: List[str]) -> List[QuestionSection]:
        """Extract all question analysis sections from judgement."""
        sections = []

        # Find question headers (### level in our markdown)
        # Note: handles typos like "The7th" (no space before number)
        question_pattern = re.compile(
            r'^###\s+(The\s*)?'  # "The " or "The" (no space for typos like "The7th")
            r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|'
            r'eleventh|twelfth|\d+(?:st|nd|rd|th)|'
            r'[A-H]\.\s+Questions?\s+\d+)',
            re.IGNORECASE | re.MULTILINE
        )

        # Find all question headers with their positions
        headers = []
        for i, line in enumerate(lines):
            if question_pattern.match(line.strip()):
                headers.append((i, line.strip()))

        # If no individual question headers found, check for unified consideration section
        if not headers:
            consideration_start = None
            consideration_end = None

            for i, line in enumerate(lines):
                # Look for either "Consideration of the questions" or "The request for a preliminary ruling"
                if ('## Consideration' in line or
                    '## The request for a preliminary ruling' in line):
                    consideration_start = i
                elif consideration_start and (line.strip().startswith('## Costs') or
                                               line.strip().startswith('## On those grounds')):
                    consideration_end = i
                    break

            if consideration_start:
                consideration_end = consideration_end or len(lines)
                section_content = '\n'.join(lines[consideration_start:consideration_end])

                # Try to extract the question numbers from the reformulated question
                # Pattern: "by its questions... asks..." or "the questions... ask..."
                question_nums = []
                reform_match = re.search(
                    r'by\s+its\s+questions?,?\s+which\s+it\s+is\s+appropriate\s+to\s+examine\s+together',
                    section_content,
                    re.IGNORECASE
                )
                if reform_match:
                    question_nums = ['combined']

                sections.append(QuestionSection(
                    header='## Consideration of the questions referred (combined)',
                    question_numbers=question_nums or ['1'],
                    start_line=consideration_start,
                    end_line=consideration_end,
                    content=section_content,
                    answer_text=None,  # Will try to extract later
                    articles_mentioned=self.extract_articles(section_content),
                    topics=self.classify_topics(section_content)
                ))

            return sections

        # Extract sections between headers
        for idx, (line_num, header) in enumerate(headers):
            # Determine end line (next header or end of consideration section)
            if idx + 1 < len(headers):
                end_line = headers[idx + 1][0]
            else:
                # Find end of Consideration section (## Costs or ## On those grounds)
                end_line = len(lines)
                for i in range(line_num, len(lines)):
                    if lines[i].strip().startswith('## Costs') or \
                       lines[i].strip().startswith('## On those grounds'):
                        end_line = i
                        break

            section_content = '\n'.join(lines[line_num:end_line])

            # Extract answer text - try multiple patterns
            # Pattern 1: Standard "the answer to the X question is that..."
            answer_match = re.search(
                r'(?:the\s+)?answer\s+to\s+(?:the\s+)?'
                r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|'
                r'\d+(?:st|nd|rd|th))'
                r'(?:\s*(?:,|and)\s*(?:the\s+)?'
                r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|'
                r'\d+(?:st|nd|rd|th)))*'
                r'\s+questions?\s+is\s+that\s+(.+?)(?:\.|$)',
                section_content,
                re.IGNORECASE | re.DOTALL
            )

            answer_text = None
            if answer_match:
                answer_text = answer_match.group(0)

            # Pattern 2: Alternative conclusion patterns
            # "it is to be concluded that...", "it follows that...", "it must be held that..."
            if not answer_text:
                alt_patterns = [
                    r'it\s+is\s+to\s+be\s+concluded\s+that\s+(.{50,500})',
                    r'it\s+follows\s+that\s+(.{50,500})',
                    r'it\s+must\s+be\s+(?:held|concluded)\s+that\s+(.{50,500})',
                    r'the\s+court\s+(?:therefore\s+)?(?:holds|finds|concludes)\s+that\s+(.{50,500})',
                ]
                for pattern in alt_patterns:
                    alt_match = re.search(pattern, section_content, re.IGNORECASE | re.DOTALL)
                    if alt_match:
                        answer_text = alt_match.group(0)
                        break

            # Pattern 3: Look for the last paragraph that contains key conclusions
            # This handles cases where the conclusion is implicit
            if not answer_text and 'invalid' in section_content.lower():
                # For validity challenges, extract the invalidity conclusion
                invalid_match = re.search(
                    r'(?:is\s+invalid|is\s+incompatible|must\s+be\s+annulled)(.{0,200})',
                    section_content,
                    re.IGNORECASE | re.DOTALL
                )
                if invalid_match:
                    # Get some context before the match
                    start = max(0, section_content.lower().find(invalid_match.group(0).lower()) - 100)
                    answer_text = section_content[start:start + 300]

            section = QuestionSection(
                header=header,
                question_numbers=self.parse_question_header(header),
                start_line=line_num,
                end_line=end_line,
                content=section_content,
                answer_text=answer_text,
                articles_mentioned=self.extract_articles(section_content),
                topics=self.classify_topics(section_content)
            )
            sections.append(section)

        return sections

    def extract_operative_rulings(self, content: str, lines: List[str]) -> List[OperativeRuling]:
        """Extract all rulings from the operative part."""
        rulings = []

        # Find operative part start
        operative_start = None
        for i, line in enumerate(lines):
            if 'On those grounds' in line and 'hereby rules' in line:
                operative_start = i
                break

        if operative_start is None:
            return rulings

        # Find rulings (numbered 1., 2., 3., etc.)
        current_ruling_num = None
        current_ruling_lines = []
        current_start_line = None

        for i in range(operative_start + 1, len(lines)):
            line = lines[i].strip()

            # Check for new ruling number
            ruling_match = re.match(r'^(\d+)\.\s*(.*)$', line)

            if ruling_match:
                # Save previous ruling if exists
                if current_ruling_num is not None:
                    ruling_text = '\n'.join(current_ruling_lines)
                    rulings.append(self._create_ruling(
                        current_ruling_num, ruling_text, current_start_line
                    ))

                # Start new ruling
                current_ruling_num = int(ruling_match.group(1))
                current_start_line = i
                remaining = ruling_match.group(2)
                current_ruling_lines = [remaining] if remaining else []

            elif current_ruling_num is not None:
                # Check for end markers
                if line.startswith('[Signatures]') or line == '* * *':
                    break
                current_ruling_lines.append(line)

        # Don't forget last ruling
        if current_ruling_num is not None and current_ruling_lines:
            ruling_text = '\n'.join(current_ruling_lines)
            rulings.append(self._create_ruling(
                current_ruling_num, ruling_text, current_start_line
            ))

        # Handle case of single unnumbered ruling
        # (Some judgements have just one ruling without a number)
        if not rulings and operative_start:
            # Collect all text between operative header and signatures
            ruling_lines = []
            for i in range(operative_start + 1, len(lines)):
                line = lines[i].strip()
                if line.startswith('[Signatures]') or line == '* * *' or line == 'Signatures':
                    break
                if line:  # Skip empty lines at start
                    ruling_lines.append(line)

            if ruling_lines:
                ruling_text = '\n'.join(ruling_lines)
                # Check if this looks like a ruling (contains "must be interpreted" or similar)
                if ('must be interpreted' in ruling_text.lower() or
                    'is to be interpreted' in ruling_text.lower() or
                    'precludes' in ruling_text.lower() or
                    'does not preclude' in ruling_text.lower()):
                    rulings.append(self._create_ruling(1, ruling_text, operative_start + 1))

        return rulings

    def _create_ruling(self, number: int, text: str, start_line: int) -> OperativeRuling:
        """Create an OperativeRuling object from parsed text."""
        # Extract article reference (usually first line)
        lines = text.strip().split('\n')
        article_ref = lines[0] if lines else ""

        # The actual ruling usually starts with "must be interpreted"
        ruling_text = text
        for i, line in enumerate(lines):
            if 'must be interpreted' in line.lower():
                ruling_text = '\n'.join(lines[i:])
                break

        return OperativeRuling(
            number=number,
            article_reference=article_ref,
            ruling_text=ruling_text.strip(),
            full_text=text.strip(),
            start_line=start_line,
            articles_mentioned=self.extract_articles(text),
            topics=self.classify_topics(text)
        )

    def match_by_explicit_answer(
        self,
        ruling: OperativeRuling,
        questions: List[QuestionSection]
    ) -> Optional[Tuple[List[str], float]]:
        """Match ruling to question using explicit 'answer to X question' text."""
        ruling_text_lower = ruling.ruling_text.lower()

        # Extract key interpretive phrase from ruling
        # The ruling typically says "must be interpreted as meaning that..."
        ruling_key = ""
        if 'must be interpreted as' in ruling_text_lower:
            parts = ruling_text_lower.split('must be interpreted as')
            if len(parts) > 1:
                # Get the interpretation part (first 200 chars)
                ruling_key = parts[1][:200].strip()

        best_match = None
        best_score = 0.0

        for question in questions:
            if question.answer_text:
                answer_lower = question.answer_text.lower()

                # Extract the interpretation from the answer
                answer_key = ""
                if 'must be interpreted as' in answer_lower:
                    parts = answer_lower.split('must be interpreted as')
                    if len(parts) > 1:
                        answer_key = parts[1][:200].strip()

                # Compare the key interpretive phrases
                if ruling_key and answer_key:
                    if FUZZY_AVAILABLE:
                        similarity = fuzz.ratio(ruling_key, answer_key) / 100
                    else:
                        # Count matching words
                        ruling_words = set(ruling_key.split())
                        answer_words = set(answer_key.split())
                        if ruling_words and answer_words:
                            intersection = ruling_words & answer_words
                            similarity = len(intersection) / max(len(ruling_words), len(answer_words))
                        else:
                            similarity = 0.0

                    if similarity > best_score:
                        best_score = similarity
                        best_match = question.question_numbers

                # Also try full text comparison as fallback
                elif FUZZY_AVAILABLE:
                    similarity = fuzz.partial_ratio(ruling_text_lower, answer_lower) / 100
                    if similarity > best_score:
                        best_score = similarity
                        best_match = question.question_numbers

        if best_match and best_score > 0.6:
            return (best_match, best_score)

        return None

    def match_by_article_reference(
        self,
        ruling: OperativeRuling,
        questions: List[QuestionSection]
    ) -> Optional[Tuple[List[str], float]]:
        """Match ruling to question based on Article references."""
        ruling_articles = set(ruling.articles_mentioned)

        if not ruling_articles:
            return None

        best_match = None
        best_score = 0.0

        for question in questions:
            question_articles = set(question.articles_mentioned)

            if not question_articles:
                continue

            # Calculate Jaccard similarity
            intersection = ruling_articles & question_articles
            union = ruling_articles | question_articles

            if union:
                score = len(intersection) / len(union)

                # Boost score if main ruling article is in question
                main_article = ruling.articles_mentioned[0] if ruling.articles_mentioned else None
                if main_article and main_article in question_articles:
                    score = min(1.0, score + 0.3)

                if score > best_score:
                    best_score = score
                    best_match = question.question_numbers

        if best_score > 0.3:
            return (best_match, best_score)

        return None

    def match_by_semantic_similarity(
        self,
        ruling: OperativeRuling,
        questions: List[QuestionSection]
    ) -> Optional[Tuple[List[str], float]]:
        """Match ruling to question using semantic similarity."""
        if not self.use_semantic or self.model is None:
            return None

        # Encode ruling
        ruling_embedding = self.model.encode(ruling.ruling_text, convert_to_tensor=True)

        best_match = None
        best_score = 0.0

        for question in questions:
            # Use answer text if available, otherwise use full content
            text_to_compare = question.answer_text or question.content[:2000]

            question_embedding = self.model.encode(text_to_compare, convert_to_tensor=True)

            similarity = float(cos_sim(ruling_embedding, question_embedding)[0][0])

            if similarity > best_score:
                best_score = similarity
                best_match = question.question_numbers

        if best_score > 0.5:
            return (best_match, best_score)

        return None

    def match_by_topic(
        self,
        ruling: OperativeRuling,
        questions: List[QuestionSection]
    ) -> Optional[Tuple[List[str], float]]:
        """Match ruling to question based on GDPR topics."""
        ruling_topics = set(ruling.topics)

        if not ruling_topics:
            return None

        best_match = None
        best_score = 0.0

        for question in questions:
            question_topics = set(question.topics)

            if not question_topics:
                continue

            # Calculate topic overlap
            intersection = ruling_topics & question_topics

            if intersection:
                score = len(intersection) / len(ruling_topics)

                if score > best_score:
                    best_score = score
                    best_match = question.question_numbers

        if best_score > 0.3:
            return (best_match, best_score)

        return None

    def match_ruling_to_questions(
        self,
        ruling: OperativeRuling,
        questions: List[QuestionSection]
    ) -> Tuple[List[str], float, str]:
        """
        Match a ruling to question sections using multiple strategies.

        Returns: (matched_question_numbers, confidence_score, method_used)
        """
        # Strategy 1: Explicit answer text matching
        result = self.match_by_explicit_answer(ruling, questions)
        if result and result[1] > 0.8:
            return (result[0], result[1], 'explicit_answer')

        # Strategy 2: Article reference matching
        article_result = self.match_by_article_reference(ruling, questions)

        # Strategy 3: Semantic similarity
        semantic_result = self.match_by_semantic_similarity(ruling, questions)

        # Strategy 4: Topic matching
        topic_result = self.match_by_topic(ruling, questions)

        # Combine results with weighted scoring
        candidates = []

        if result:
            candidates.append(('explicit_answer', result[0], result[1] * 1.0))
        if article_result:
            candidates.append(('article_match', article_result[0], article_result[1] * 0.9))
        if semantic_result:
            candidates.append(('semantic', semantic_result[0], semantic_result[1] * 0.8))
        if topic_result:
            candidates.append(('topic', topic_result[0], topic_result[1] * 0.7))

        if not candidates:
            # Fallback: use ruling order (ruling N often matches question N)
            if ruling.number <= len(questions):
                return (questions[ruling.number - 1].question_numbers, 0.3, 'order_fallback')
            return ([], 0.0, 'no_match')

        # Sort by score and return best
        candidates.sort(key=lambda x: x[2], reverse=True)
        best = candidates[0]

        return (best[1], best[2], best[0])

    def analyze_judgement(self, filepath: Path) -> JudgementAnalysis:
        """Perform complete analysis of a judgement file."""
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Extract case ID
        case_id = filepath.stem

        # Extract question sections
        questions = self.extract_question_sections(content, lines)

        # Extract operative rulings
        rulings = self.extract_operative_rulings(content, lines)

        # Match rulings to questions
        mapping = {}

        for ruling in rulings:
            matched_qs, confidence, method = self.match_ruling_to_questions(ruling, questions)
            ruling.matched_questions = matched_qs
            ruling.match_confidence = confidence
            ruling.match_method = method
            mapping[ruling.number] = matched_qs

        return JudgementAnalysis(
            case_id=case_id,
            questions=questions,
            rulings=rulings,
            ruling_question_mapping=mapping
        )

    def to_dict(self, analysis: JudgementAnalysis) -> Dict[str, Any]:
        """Convert analysis to dictionary for JSON serialization."""
        return {
            'case_id': analysis.case_id,
            'questions': [
                {
                    'header': q.header,
                    'question_numbers': q.question_numbers,
                    'start_line': q.start_line,
                    'end_line': q.end_line,
                    'articles_mentioned': q.articles_mentioned,
                    'topics': q.topics,
                    'has_answer_text': q.answer_text is not None
                }
                for q in analysis.questions
            ],
            'rulings': [
                {
                    'number': r.number,
                    'article_reference': r.article_reference,
                    'ruling_text': r.ruling_text[:500] + '...' if len(r.ruling_text) > 500 else r.ruling_text,
                    'articles_mentioned': r.articles_mentioned,
                    'topics': r.topics,
                    'matched_questions': r.matched_questions,
                    'match_confidence': round(r.match_confidence, 3),
                    'match_method': r.match_method
                }
                for r in analysis.rulings
            ],
            'ruling_question_mapping': {
                str(k): v for k, v in analysis.ruling_question_mapping.items()
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='Match CJEU operative rulings to question sections'
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to judgement file or directory'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output JSON file for results'
    )
    parser.add_argument(
        '--no-semantic',
        action='store_true',
        help='Disable semantic similarity matching'
    )
    parser.add_argument(
        '--topic',
        type=str,
        help='Filter by GDPR topic (e.g., LEGITIMATE_INTEREST, CONSENT)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    # Initialize matcher
    matcher = RulingQuestionMatcher(use_semantic=not args.no_semantic)

    # Process files
    if args.path.is_file():
        files = [args.path]
    else:
        files = list(args.path.glob('*.md'))

    all_results = []

    for filepath in sorted(files):
        print(f"\nAnalyzing: {filepath.name}")

        analysis = matcher.analyze_judgement(filepath)
        result_dict = matcher.to_dict(analysis)

        # Filter by topic if specified
        if args.topic:
            topic_upper = args.topic.upper()
            relevant_rulings = [
                r for r in result_dict['rulings']
                if topic_upper in r['topics']
            ]
            if not relevant_rulings:
                continue
            result_dict['rulings'] = relevant_rulings

        all_results.append(result_dict)

        if args.verbose:
            print(f"  Questions found: {len(analysis.questions)}")
            for q in analysis.questions:
                print(f"    - {q.header} (Q{', Q'.join(q.question_numbers)})")
                if q.topics:
                    print(f"      Topics: {', '.join(q.topics)}")

            print(f"  Rulings found: {len(analysis.rulings)}")
            for r in analysis.rulings:
                print(f"    - Ruling {r.number}: → Q{', Q'.join(r.matched_questions)}")
                print(f"      Confidence: {r.match_confidence:.2f} ({r.match_method})")
                if r.topics:
                    print(f"      Topics: {', '.join(r.topics)}")
        else:
            # Compact output
            print(f"  Mapping: ", end='')
            mappings = [f"R{r['number']}→Q{','.join(r['matched_questions'])}"
                       for r in result_dict['rulings']]
            print(' | '.join(mappings))

    # Write output if specified
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults written to: {args.output}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Processed {len(all_results)} judgements")
    if args.topic:
        print(f"Filtered by topic: {args.topic}")
        total_rulings = sum(len(r['rulings']) for r in all_results)
        print(f"Total matching rulings: {total_rulings}")


if __name__ == '__main__':
    main()
