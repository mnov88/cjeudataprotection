/**
 * CJEU Judgement Parser
 *
 * Standalone JavaScript module for parsing CJEU judgements:
 * - Detects and adds structural headings
 * - Extracts question sections and operative rulings
 * - Matches rulings to questions
 * - Classifies content by GDPR topic
 *
 * Usage:
 *   const parser = new CJEUJudgementParser();
 *   const result = parser.parse(judgementText);
 *
 *   // Result contains:
 *   // - headings: detected headings with levels
 *   // - questions: question sections with metadata
 *   // - rulings: operative rulings with matched questions
 *   // - structuredText: text with markdown headings inserted
 *
 * @author Claude Code
 * @license MIT
 */

(function(root, factory) {
  // UMD pattern for browser/Node/AMD compatibility
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.CJEUJudgementParser = factory();
  }
}(typeof self !== 'undefined' ? self : this, function() {

  // ============================================================
  // GDPR TOPIC TAXONOMY
  // ============================================================

  const GDPR_TOPICS = {
    LEGITIMATE_INTEREST: {
      keywords: ['legitimate interest', 'article 6(1)(f)', 'art. 6(1)(f)', 'balancing', 'overriding interest'],
      articles: ['6(1)(f)', '6.1.f']
    },
    CONSENT: {
      keywords: ['consent', 'article 6(1)(a)', 'article 7', 'freely given', 'explicit consent', 'withdrawal'],
      articles: ['6(1)(a)', '7']
    },
    RIGHT_TO_ERASURE: {
      keywords: ['erasure', 'right to be forgotten', 'article 17', 'deletion', 'erase'],
      articles: ['17']
    },
    RIGHT_OF_ACCESS: {
      keywords: ['access', 'article 15', 'copy', 'right of access'],
      articles: ['15']
    },
    RIGHT_TO_RECTIFICATION: {
      keywords: ['rectification', 'article 16', 'correct', 'inaccurate'],
      articles: ['16']
    },
    DATA_SUBJECT_RIGHTS: {
      keywords: ['data subject rights', 'articles 12 to 22', 'exercise of rights'],
      articles: ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']
    },
    COMPENSATION: {
      keywords: ['compensation', 'damages', 'article 82', 'non-material damage', 'material damage', 'liability'],
      articles: ['82']
    },
    DATA_BREACH: {
      keywords: ['breach', 'article 33', 'article 34', 'notification', 'personal data breach'],
      articles: ['33', '34']
    },
    TRANSFERS: {
      keywords: ['transfer', 'third country', 'article 44', 'article 45', 'article 46', 'adequacy', 'standard contractual clauses', 'scc'],
      articles: ['44', '45', '46', '47', '49']
    },
    CONTROLLER_PROCESSOR: {
      keywords: ['controller', 'processor', 'joint controller', 'article 26', 'article 28'],
      articles: ['26', '28', '4(7)', '4(8)']
    },
    LAWFULNESS: {
      keywords: ['lawfulness', 'legal basis', 'article 6', 'lawful processing'],
      articles: ['6']
    },
    PURPOSE_LIMITATION: {
      keywords: ['purpose limitation', 'compatible purpose', 'further processing', 'article 5(1)(b)'],
      articles: ['5(1)(b)']
    },
    DATA_MINIMISATION: {
      keywords: ['minimisation', 'adequate, relevant', 'article 5(1)(c)'],
      articles: ['5(1)(c)']
    },
    SPECIAL_CATEGORIES: {
      keywords: ['special categories', 'sensitive data', 'article 9', 'health data', 'biometric', 'genetic', 'racial', 'ethnic', 'political opinions', 'religious', 'sexual orientation'],
      articles: ['9']
    },
    DPA_POWERS: {
      keywords: ['supervisory authority', 'dpa', 'article 51', 'article 58', 'corrective powers', 'investigative powers'],
      articles: ['51', '52', '57', '58']
    },
    FINES: {
      keywords: ['administrative fine', 'article 83', 'penalty', 'sanction'],
      articles: ['83']
    },
    TERRITORIAL_SCOPE: {
      keywords: ['territorial scope', 'article 3', 'establishment', 'offering goods', 'monitoring behaviour'],
      articles: ['3']
    },
    MATERIAL_SCOPE: {
      keywords: ['material scope', 'article 2', 'household exemption', 'law enforcement'],
      articles: ['2']
    },
    TRANSPARENCY: {
      keywords: ['transparency', 'information', 'article 13', 'article 14', 'privacy notice', 'fair processing'],
      articles: ['13', '14']
    },
    PROFILING: {
      keywords: ['profiling', 'automated decision', 'article 22', 'automated processing'],
      articles: ['22']
    }
  };

  // ============================================================
  // HEADING PATTERNS
  // ============================================================

  const HEADING_PATTERNS = [
    // H2 - Major structural sections
    { pattern: /^Judgment$/i, level: 2, type: 'document_title' },
    { pattern: /^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+Legal\s+context$/i, level: 2, type: 'legal_context_roman' },
    { pattern: /^Legal context$/i, level: 2, type: 'legal_context' },
    { pattern: /^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+(The\s+)?dispute\s+in\s+the\s+main\s+proceedings/i, level: 2, type: 'dispute_roman' },
    { pattern: /^(The\s+)?(facts\s+of\s+the\s+)?[Dd]ispute\s+in\s+the\s+main\s+proceedings\s+and\s+the\s+questions?\s+referred(\s+for\s+a\s+preliminary\s+ruling)?$/i, level: 2, type: 'dispute' },
    { pattern: /^Admissibility\s+of\s+the\s+request\s+for\s+a\s+preliminary\s+ruling$/i, level: 2, type: 'admissibility_request' },
    { pattern: /^The\s+jurisdiction\s+of\s+the\s+Court$/i, level: 2, type: 'jurisdiction' },
    { pattern: /^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+Consideration\s+of\s+the\s+questions?\s+referred/i, level: 2, type: 'consideration_roman' },
    { pattern: /^(Consideration\s+of\s+the\s+questions?\s+referred|The\s+request\s+for\s+a\s+preliminary\s+ruling)(\s+for\s+a\s+preliminary\s+ruling)?$/i, level: 2, type: 'consideration' },
    { pattern: /^The\s+request\s+to\s+have\s+the\s+written\s+procedure\s+reopened$/i, level: 2, type: 'reopen_procedure' },
    { pattern: /^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.\s+Costs$/i, level: 2, type: 'costs_roman' },
    { pattern: /^Costs$/i, level: 2, type: 'costs' },
    { pattern: /^On\s+those\s+grounds,?\s+the\s+Court\s*\([^)]+\)\s*hereby\s+rules:?$/i, level: 2, type: 'operative' },

    // H3 - Primary sub-sections
    { pattern: /^[A-H]\.\s+(European\s+Union\s+law|EU\s+law)$/i, level: 3, type: 'eu_law_letter' },
    { pattern: /^(European\s+Union\s+law|EU\s+law)$/i, level: 3, type: 'eu_law' },
    { pattern: /^[A-H]\.\s+(National\s+law|[A-Z][a-z]+\s+law)$/i, level: 3, type: 'national_law_letter' },
    { pattern: /^(National\s+law|German\s+law|Hungarian\s+law|Finnish\s+law|Belgian\s+law|Bulgarian\s+law|Lithuanian\s+law|French\s+law|Italian\s+law|Spanish\s+law|Polish\s+law|Dutch\s+law|Austrian\s+law|Irish\s+law|Greek\s+law|Portuguese\s+law|Swedish\s+law|Danish\s+law|Czech\s+law|Slovak\s+law|Romanian\s+law|Croatian\s+law|Slovenian\s+law|Estonian\s+law|Latvian\s+law|Maltese\s+law|Cypriot\s+law|Luxembourgish\s+law|[A-Z][a-z]+\s+law)$/i, level: 3, type: 'national_law' },

    // Question headers - multiple formats
    { pattern: /^[A-H]\.\s+Questions?\s+\d+(\([a-z]\))?(\s+(to|and)\s+\d+)*(\s+and\s+Questions?\s+\d+)?$/i, level: 3, type: 'question_letter' },
    { pattern: /^(The\s*)?(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)(,?\s*(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth))*(\s+and\s+(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth))?\s+questions?$/i, level: 3, type: 'question_ordinal' },
    { pattern: /^(The\s*)?(\d+)(st|nd|rd|th)(,?\s*(\d+)(st|nd|rd|th))*(\s+and\s+(\d+)(st|nd|rd|th))?\s+questions?$/i, level: 3, type: 'question_numeric' },
    { pattern: /^Questions?\s+\d+(\([a-z]\))?(,?\s*\([a-z]\))*(\s+and\s+\([a-z]\))?$/i, level: 3, type: 'question_subpart' },
    { pattern: /^Questions?\s+\d+$/i, level: 3, type: 'question_simple' },

    // H4 - Tertiary sections
    { pattern: /^Preliminary\s+observations$/i, level: 4, type: 'preliminary' },
    { pattern: /^Admissibility$/i, level: 4, type: 'admissibility' },
    { pattern: /^Substance$/i, level: 4, type: 'substance' },
    { pattern: /^\d+\.\s+(Directive\s+(\(EU\)\s+)?(\d{2,4}\/\d+|95\/46)(\/EC|\/EEC)?|The\s+\w+\s+Directive|The\s+GDPR|Regulation\s+(\(EU\)\s+)?\d{2,4}\/\d+)$/i, level: 4, type: 'legislation_numbered' },
    { pattern: /^Directive\s+(\(EU\)\s+)?\d{2,4}\/\d+(\/EC|\/EEC)?;?$/i, level: 4, type: 'directive' },
    { pattern: /^Regulation\s+(\(EU\)\s+)?\d{2,4}\/\d+;?$/i, level: 4, type: 'regulation' },
    { pattern: /^The\s+GDPR$/i, level: 4, type: 'gdpr' },
    { pattern: /^Directive\s+95\/46(\/EC)?$/i, level: 4, type: 'directive_95_46' },
    { pattern: /^\d+\.\s+The\s+(Constitution|Law\s+of\s+.+)$/i, level: 4, type: 'national_act_numbered' },
    { pattern: /^(The\s+)?(Law\s+on\s+.+|Federal\s+law|The\s+law\s+of\s+.+|The\s+Commercial\s+Code|Decree\s+No\s+.+)$/i, level: 4, type: 'national_act' },
    { pattern: /^The\s+[A-Za-z\s]+Decision$/i, level: 4, type: 'decision' },
    { pattern: /^\d+\.\s+(Interferences\s+with|Justification\s+for|Air\s+passenger|The\s+purposes|The\s+link\s+between|The\s+air\s+passengers|Advance\s+assessment|The\s+disclosure)/i, level: 4, type: 'analysis_numbered' },
    { pattern: /^\([a-z]\)\s+[A-Z]/i, level: 4, type: 'subsubsection_letter' },
    { pattern: /^\(\d+\)\s+[A-Z]/i, level: 4, type: 'subsubsection_number' },
    { pattern: /^\((i|ii|iii|iv|v|vi)\)\s+[A-Z]/i, level: 4, type: 'subsubsection_roman' }
  ];

  // ============================================================
  // ORDINAL MAPPING
  // ============================================================

  const ORDINALS = {
    'first': '1', 'second': '2', 'third': '3', 'fourth': '4',
    'fifth': '5', 'sixth': '6', 'seventh': '7', 'eighth': '8',
    'ninth': '9', 'tenth': '10', 'eleventh': '11', 'twelfth': '12',
    'thirteenth': '13', 'fourteenth': '14', 'fifteenth': '15'
  };

  // ============================================================
  // MAIN PARSER CLASS
  // ============================================================

  class CJEUJudgementParser {
    constructor(options = {}) {
      this.options = {
        addHeadings: true,
        extractQuestions: true,
        extractRulings: true,
        matchRulingsToQuestions: true,
        classifyTopics: true,
        ...options
      };
    }

    /**
     * Parse a CJEU judgement text
     * @param {string} text - The judgement text (plain text or markdown)
     * @returns {Object} Parsed result with headings, questions, rulings, etc.
     */
    parse(text) {
      const lines = text.split('\n');

      // Find table of contents end (if present)
      const contentStart = this._findContentStart(lines);

      // Detect headings
      const headings = this._detectHeadings(lines, contentStart);

      // Extract questions
      const questions = this.options.extractQuestions
        ? this._extractQuestions(lines, headings)
        : [];

      // Extract rulings
      const rulings = this.options.extractRulings
        ? this._extractRulings(lines, headings)
        : [];

      // Match rulings to questions
      if (this.options.matchRulingsToQuestions && rulings.length && questions.length) {
        this._matchRulingsToQuestions(rulings, questions);
      }

      // Generate structured text with headings
      const structuredText = this.options.addHeadings
        ? this._insertHeadings(lines, headings)
        : text;

      return {
        headings,
        questions,
        rulings,
        structuredText,
        stats: {
          totalHeadings: headings.length,
          h2Count: headings.filter(h => h.level === 2).length,
          h3Count: headings.filter(h => h.level === 3).length,
          h4Count: headings.filter(h => h.level === 4).length,
          questionCount: questions.length,
          rulingCount: rulings.length
        }
      };
    }

    // --------------------------------------------------------
    // HEADING DETECTION
    // --------------------------------------------------------

    _findContentStart(lines) {
      // Look for "Table of contents" marker
      let tocStart = -1;
      for (let i = 0; i < Math.min(lines.length, 50); i++) {
        if (lines[i].toLowerCase().includes('table of contents')) {
          tocStart = i;
          break;
        }
      }

      if (tocStart === -1) return 0;

      // Find "gives the following" + "Judgment"
      for (let i = tocStart; i < Math.min(lines.length, 250); i++) {
        if (lines[i].trim().toLowerCase() === 'judgment') {
          for (let j = i - 1; j >= Math.max(0, i - 10); j--) {
            if (lines[j].toLowerCase().includes('gives the following')) {
              return i;
            }
            if (lines[j].trim()) break;
          }
        }
      }

      return 0;
    }

    _detectHeadings(lines, contentStart) {
      const headings = [];

      for (let i = contentStart; i < lines.length; i++) {
        const line = lines[i];
        const stripped = line.trim();

        // Skip empty lines, existing headings, paragraph numbers
        if (!stripped || stripped.startsWith('#') || /^\d+\s/.test(stripped) || /^\d+$/.test(stripped)) {
          continue;
        }

        // Skip lines too long (paragraph content)
        if (stripped.length > 150) continue;

        // Skip common paragraph markers
        if (/^[–\-•*("']/.test(stripped)) continue;

        // Check against patterns
        for (const { pattern, level, type } of HEADING_PATTERNS) {
          if (pattern.test(stripped)) {
            headings.push({
              line: i,
              text: stripped,
              level,
              type,
              markdown: '#'.repeat(level) + ' ' + stripped
            });
            break;
          }
        }
      }

      return headings;
    }

    _insertHeadings(lines, headings) {
      const result = [...lines];

      // Process in reverse to preserve line numbers
      for (let i = headings.length - 1; i >= 0; i--) {
        const h = headings[i];
        result[h.line] = h.markdown;
      }

      return result.join('\n');
    }

    // --------------------------------------------------------
    // QUESTION EXTRACTION
    // --------------------------------------------------------

    _extractQuestions(lines, headings) {
      const questions = [];

      // Find question headings (H3 level, question types)
      const questionHeadings = headings.filter(h =>
        h.level === 3 && h.type.startsWith('question')
      );

      // If no individual question headers, check for unified consideration
      if (questionHeadings.length === 0) {
        const consideration = headings.find(h =>
          h.type === 'consideration' || h.type === 'consideration_roman'
        );

        if (consideration) {
          const endLine = this._findSectionEnd(lines, consideration.line, headings);
          const content = lines.slice(consideration.line, endLine).join('\n');

          questions.push({
            header: consideration.text,
            questionNumbers: ['combined'],
            startLine: consideration.line,
            endLine,
            content,
            answerText: this._extractAnswerText(content),
            articles: this._extractArticles(content),
            topics: this.options.classifyTopics ? this._classifyTopics(content) : []
          });
        }

        return questions;
      }

      // Extract each question section
      for (let i = 0; i < questionHeadings.length; i++) {
        const h = questionHeadings[i];
        const endLine = i + 1 < questionHeadings.length
          ? questionHeadings[i + 1].line
          : this._findSectionEnd(lines, h.line, headings);

        const content = lines.slice(h.line, endLine).join('\n');

        questions.push({
          header: h.text,
          questionNumbers: this._parseQuestionNumbers(h.text),
          startLine: h.line,
          endLine,
          content,
          answerText: this._extractAnswerText(content),
          articles: this._extractArticles(content),
          topics: this.options.classifyTopics ? this._classifyTopics(content) : []
        });
      }

      return questions;
    }

    _parseQuestionNumbers(header) {
      const numbers = [];
      const headerLower = header.toLowerCase();

      // Check ordinal words
      for (const [word, num] of Object.entries(ORDINALS)) {
        if (headerLower.includes(word)) {
          numbers.push(num);
        }
      }

      // Check numeric ordinals (4th, 5th, etc.) - handles typos like "The7th"
      const numericMatches = headerLower.matchAll(/(\d+)(?:st|nd|rd|th)/g);
      for (const match of numericMatches) {
        if (!numbers.includes(match[1])) {
          numbers.push(match[1]);
        }
      }

      // Check "Question X" format
      const questionMatches = headerLower.matchAll(/questions?\s+(\d+)/g);
      for (const match of questionMatches) {
        if (!numbers.includes(match[1])) {
          numbers.push(match[1]);
        }
      }

      // Sort numerically
      return numbers.sort((a, b) => parseInt(a) - parseInt(b));
    }

    _extractAnswerText(content) {
      // Pattern 1: Standard "the answer to the X question is that..."
      const standardMatch = content.match(
        /(?:the\s+)?answer\s+to\s+(?:the\s+)?(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\d+(?:st|nd|rd|th))(?:\s*(?:,|and)\s*(?:the\s+)?(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\d+(?:st|nd|rd|th)))*\s+questions?\s+is\s+that\s+.{50,500}/i
      );
      if (standardMatch) return standardMatch[0];

      // Pattern 2: Alternative conclusions
      const altPatterns = [
        /it\s+is\s+to\s+be\s+concluded\s+that\s+.{50,500}/i,
        /it\s+follows\s+that\s+.{50,500}/i,
        /it\s+must\s+be\s+(?:held|concluded)\s+that\s+.{50,500}/i,
        /the\s+court\s+(?:therefore\s+)?(?:holds|finds|concludes)\s+that\s+.{50,500}/i
      ];

      for (const pattern of altPatterns) {
        const match = content.match(pattern);
        if (match) return match[0];
      }

      // Pattern 3: Invalidity conclusions
      if (content.toLowerCase().includes('invalid')) {
        const invalidMatch = content.match(/(?:is\s+invalid|is\s+incompatible|must\s+be\s+annulled).{0,200}/i);
        if (invalidMatch) {
          const idx = content.toLowerCase().indexOf(invalidMatch[0].toLowerCase());
          return content.substring(Math.max(0, idx - 100), idx + 300);
        }
      }

      return null;
    }

    _findSectionEnd(lines, startLine, headings) {
      // Find next H2 section (Costs or Operative)
      for (let i = startLine + 1; i < lines.length; i++) {
        const stripped = lines[i].trim();
        if (/^##?\s*Costs$/i.test(stripped) ||
            /^##?\s*On\s+those\s+grounds/i.test(stripped) ||
            stripped === 'Costs' ||
            stripped.startsWith('On those grounds')) {
          return i;
        }
      }
      return lines.length;
    }

    // --------------------------------------------------------
    // RULING EXTRACTION
    // --------------------------------------------------------

    _extractRulings(lines, headings) {
      const rulings = [];

      // Find operative part
      const operativeHeading = headings.find(h => h.type === 'operative');
      if (!operativeHeading) return rulings;

      const startLine = operativeHeading.line;
      let currentRulingNum = null;
      let currentRulingLines = [];
      let currentStartLine = null;

      for (let i = startLine + 1; i < lines.length; i++) {
        const line = lines[i].trim();

        // Check for end markers
        if (line.startsWith('[Signatures]') || line === '* * *' || line === 'Signatures') {
          break;
        }

        // Check for new ruling number
        const rulingMatch = line.match(/^(\d+)\.\s*(.*)$/);

        if (rulingMatch) {
          // Save previous ruling
          if (currentRulingNum !== null) {
            rulings.push(this._createRuling(
              currentRulingNum,
              currentRulingLines.join('\n'),
              currentStartLine
            ));
          }

          // Start new ruling
          currentRulingNum = parseInt(rulingMatch[1]);
          currentStartLine = i;
          currentRulingLines = rulingMatch[2] ? [rulingMatch[2]] : [];
        } else if (currentRulingNum !== null) {
          currentRulingLines.push(line);
        }
      }

      // Don't forget last ruling
      if (currentRulingNum !== null && currentRulingLines.length) {
        rulings.push(this._createRuling(
          currentRulingNum,
          currentRulingLines.join('\n'),
          currentStartLine
        ));
      }

      // Handle single unnumbered ruling
      if (rulings.length === 0) {
        const rulingLines = [];
        for (let i = startLine + 1; i < lines.length; i++) {
          const line = lines[i].trim();
          if (line.startsWith('[Signatures]') || line === '* * *' || line === 'Signatures') break;
          if (line) rulingLines.push(line);
        }

        if (rulingLines.length) {
          const text = rulingLines.join('\n');
          if (/must be interpreted|is to be interpreted|precludes|does not preclude/i.test(text)) {
            rulings.push(this._createRuling(1, text, startLine + 1));
          }
        }
      }

      return rulings;
    }

    _createRuling(number, text, startLine) {
      const lines = text.trim().split('\n');
      const articleRef = lines[0] || '';

      // Find ruling text (after "must be interpreted")
      let rulingText = text;
      for (let i = 0; i < lines.length; i++) {
        if (/must be interpreted/i.test(lines[i])) {
          rulingText = lines.slice(i).join('\n');
          break;
        }
      }

      return {
        number,
        articleReference: articleRef,
        rulingText: rulingText.trim(),
        fullText: text.trim(),
        startLine,
        articles: this._extractArticles(text),
        topics: this.options.classifyTopics ? this._classifyTopics(text) : [],
        matchedQuestions: [],
        matchConfidence: 0,
        matchMethod: ''
      };
    }

    // --------------------------------------------------------
    // RULING-QUESTION MATCHING
    // --------------------------------------------------------

    _matchRulingsToQuestions(rulings, questions) {
      for (const ruling of rulings) {
        const match = this._findBestMatch(ruling, questions);
        ruling.matchedQuestions = match.questions;
        ruling.matchConfidence = match.confidence;
        ruling.matchMethod = match.method;
      }
    }

    _findBestMatch(ruling, questions) {
      // Strategy 1: Explicit answer matching
      const explicitMatch = this._matchByExplicitAnswer(ruling, questions);
      if (explicitMatch && explicitMatch.confidence > 0.7) {
        return explicitMatch;
      }

      // Strategy 2: Article reference matching
      const articleMatch = this._matchByArticles(ruling, questions);

      // Strategy 3: Topic matching
      const topicMatch = this._matchByTopics(ruling, questions);

      // Combine and return best
      const candidates = [
        explicitMatch,
        articleMatch,
        topicMatch
      ].filter(Boolean);

      if (candidates.length === 0) {
        // Fallback: use order
        if (ruling.number <= questions.length) {
          return {
            questions: questions[ruling.number - 1].questionNumbers,
            confidence: 0.3,
            method: 'order_fallback'
          };
        }
        return { questions: [], confidence: 0, method: 'no_match' };
      }

      // Weight and sort
      candidates.sort((a, b) => {
        const weights = { explicit_answer: 1.0, article_match: 0.9, topic_match: 0.7 };
        return (b.confidence * (weights[b.method] || 0.5)) -
               (a.confidence * (weights[a.method] || 0.5));
      });

      return candidates[0];
    }

    _matchByExplicitAnswer(ruling, questions) {
      const rulingLower = ruling.rulingText.toLowerCase();

      // Extract key interpretive phrase
      let rulingKey = '';
      if (rulingLower.includes('must be interpreted as')) {
        const parts = rulingLower.split('must be interpreted as');
        if (parts[1]) rulingKey = parts[1].substring(0, 200).trim();
      }

      let bestMatch = null;
      let bestScore = 0;

      for (const question of questions) {
        if (!question.answerText) continue;

        const answerLower = question.answerText.toLowerCase();
        let answerKey = '';

        if (answerLower.includes('must be interpreted as')) {
          const parts = answerLower.split('must be interpreted as');
          if (parts[1]) answerKey = parts[1].substring(0, 200).trim();
        }

        if (rulingKey && answerKey) {
          const similarity = this._calculateSimilarity(rulingKey, answerKey);
          if (similarity > bestScore) {
            bestScore = similarity;
            bestMatch = question.questionNumbers;
          }
        }
      }

      if (bestMatch && bestScore > 0.6) {
        return { questions: bestMatch, confidence: bestScore, method: 'explicit_answer' };
      }

      return null;
    }

    _matchByArticles(ruling, questions) {
      const rulingArticles = new Set(ruling.articles);
      if (rulingArticles.size === 0) return null;

      let bestMatch = null;
      let bestScore = 0;

      for (const question of questions) {
        const questionArticles = new Set(question.articles);
        if (questionArticles.size === 0) continue;

        // Jaccard similarity
        const intersection = [...rulingArticles].filter(a => questionArticles.has(a));
        const union = new Set([...rulingArticles, ...questionArticles]);
        let score = intersection.length / union.size;

        // Boost if main ruling article is in question
        if (ruling.articles[0] && questionArticles.has(ruling.articles[0])) {
          score = Math.min(1.0, score + 0.3);
        }

        if (score > bestScore) {
          bestScore = score;
          bestMatch = question.questionNumbers;
        }
      }

      if (bestMatch && bestScore > 0.3) {
        return { questions: bestMatch, confidence: bestScore, method: 'article_match' };
      }

      return null;
    }

    _matchByTopics(ruling, questions) {
      const rulingTopics = new Set(ruling.topics);
      if (rulingTopics.size === 0) return null;

      let bestMatch = null;
      let bestScore = 0;

      for (const question of questions) {
        const questionTopics = new Set(question.topics);
        if (questionTopics.size === 0) continue;

        const intersection = [...rulingTopics].filter(t => questionTopics.has(t));
        const score = intersection.length / rulingTopics.size;

        if (score > bestScore) {
          bestScore = score;
          bestMatch = question.questionNumbers;
        }
      }

      if (bestMatch && bestScore > 0.3) {
        return { questions: bestMatch, confidence: bestScore, method: 'topic_match' };
      }

      return null;
    }

    // --------------------------------------------------------
    // UTILITY FUNCTIONS
    // --------------------------------------------------------

    _extractArticles(text) {
      const articles = new Set();

      // "Article X" or "Article X(Y)"
      const matches = text.matchAll(/Article\s+(\d+)(?:\((\d+)\))?(?:\([a-z]\))?/gi);
      for (const match of matches) {
        const article = match[1];
        const paragraph = match[2];
        articles.add(paragraph ? `${article}(${paragraph})` : article);
      }

      // "Art. X" shorthand
      const shortMatches = text.matchAll(/Art\.\s*(\d+)(?:\((\d+)\))?/gi);
      for (const match of shortMatches) {
        const article = match[1];
        const paragraph = match[2];
        articles.add(paragraph ? `${article}(${paragraph})` : article);
      }

      return [...articles];
    }

    _classifyTopics(text) {
      const textLower = text.toLowerCase();
      const topics = [];

      for (const [topic, config] of Object.entries(GDPR_TOPICS)) {
        // Check keywords
        for (const keyword of config.keywords) {
          if (textLower.includes(keyword.toLowerCase())) {
            if (!topics.includes(topic)) topics.push(topic);
            break;
          }
        }

        // Check article references
        for (const article of config.articles) {
          const pattern = new RegExp(`article\\s*${article.replace(/[()]/g, '\\$&')}`, 'i');
          if (pattern.test(textLower)) {
            if (!topics.includes(topic)) topics.push(topic);
            break;
          }
        }
      }

      return topics;
    }

    _calculateSimilarity(str1, str2) {
      // Simple word-based Jaccard similarity
      const words1 = new Set(str1.split(/\s+/).filter(w => w.length > 2));
      const words2 = new Set(str2.split(/\s+/).filter(w => w.length > 2));

      const intersection = [...words1].filter(w => words2.has(w));
      const union = new Set([...words1, ...words2]);

      return union.size > 0 ? intersection.length / union.size : 0;
    }

    // --------------------------------------------------------
    // STATIC UTILITIES
    // --------------------------------------------------------

    static get GDPR_TOPICS() {
      return GDPR_TOPICS;
    }

    static get HEADING_PATTERNS() {
      return HEADING_PATTERNS;
    }
  }

  return CJEUJudgementParser;

}));
