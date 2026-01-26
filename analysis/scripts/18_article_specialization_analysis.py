#!/usr/bin/env python3
"""
18_article_specialization_analysis.py
======================================
Granular analysis of judge/rapporteur/chamber specialization at the
GDPR article level (e.g. Article 6) and sub-provision level (e.g.
Article 6(1)(a)).

Complements 15_supplementary_judicial_analysis.py which operates at the
topic-cluster level.

Outputs:
  - article_specialization_analysis.json  (full results)
  - Console report
"""

import json
import csv
import math
import re
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HOLDINGS_JUDICIAL = PROJECT_ROOT / "analysis" / "output" / "holdings_judicial.csv"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

# =============================================================================
# DATA LOADING
# =============================================================================

def load_holdings():
    """Load enhanced holdings data."""
    holdings = []
    with open(HOLDINGS_JUDICIAL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['pro_ds'] = int(row.get('pro_ds', 0))
            try:
                row['year'] = int(row.get('year', 0))
            except (ValueError, TypeError):
                row['year'] = 0
            holdings.append(row)
    return holdings

# =============================================================================
# PROVISION PARSING
# =============================================================================

def parse_provisions(provisions_str):
    """
    Parse provisions_cited string into structured list.

    Input:  "Article 6(1)(a) GDPR;Article 82(1);Article 5(1)(c) GDPR"
    Output: [
        {'full': 'Article 6(1)(a)', 'article': 6, 'sub': '6(1)(a)'},
        {'full': 'Article 82(1)',   'article': 82, 'sub': '82(1)'},
        {'full': 'Article 5(1)(c)', 'article': 5,  'sub': '5(1)(c)'},
    ]

    Only GDPR articles are included (Directive 2002/58, Charter, etc. excluded).
    """
    if not provisions_str or not provisions_str.strip():
        return []

    results = []
    parts = [p.strip() for p in provisions_str.split(';') if p.strip()]

    for part in parts:
        # Skip non-GDPR provisions
        lower = part.lower()
        if 'directive' in lower or 'charter' in lower or 'regulation' in lower:
            if 'gdpr' not in lower:
                continue

        # Extract article number and sub-provision
        # Pattern: "Article NN" optionally followed by "(X)", "(X)(Y)", etc.
        match = re.match(r'Article\s+(\d+)((?:\([^)]+\))*)', part)
        if match:
            article_num = int(match.group(1))
            sub_parts = match.group(2)  # e.g. "(1)(a)" or ""

            full = f"Article {article_num}{sub_parts}"
            sub = f"{article_num}{sub_parts}" if sub_parts else None

            results.append({
                'full': full,
                'article': article_num,
                'sub': sub
            })

    return results


def parse_article_numbers(article_str):
    """Parse article_numbers column (semicolon-separated integers)."""
    if not article_str or not article_str.strip():
        return []
    nums = []
    for part in article_str.split(';'):
        part = part.strip()
        try:
            nums.append(int(part))
        except ValueError:
            pass
    return nums

# =============================================================================
# STATISTICAL HELPERS
# =============================================================================

def wilson_ci(successes, n, z=1.96):
    """Wilson score confidence interval."""
    if n == 0:
        return 0, 0, 0
    p = successes / n
    denom = 1 + z**2/n
    center = (p + z**2/(2*n)) / denom
    spread = z * math.sqrt((p*(1-p) + z**2/(4*n))/n) / denom
    return p, max(0, center-spread), min(1, center+spread)


def chi_square_2x2(a, b, c, d):
    """2x2 chi-square test with Yates correction."""
    n = a + b + c + d
    if n == 0:
        return 0, 1.0

    e_a = (a+b)*(a+c)/n
    e_b = (a+b)*(b+d)/n
    e_c = (c+d)*(a+c)/n
    e_d = (c+d)*(b+d)/n

    chi2 = 0
    for obs, exp in [(a, e_a), (b, e_b), (c, e_c), (d, e_d)]:
        if exp > 0:
            chi2 += (abs(obs - exp) - 0.5)**2 / exp

    if chi2 <= 0:
        return 0, 1.0
    z = math.sqrt(chi2)
    p = 2 * 0.5 * math.erfc(z / math.sqrt(2))
    return chi2, p


def fisher_exact_2x2(a, b, c, d):
    """
    Fisher exact test for small samples.
    Returns two-sided p-value using the hypergeometric distribution.
    """
    n = a + b + c + d
    if n == 0:
        return 1.0

    def log_factorial(x):
        return sum(math.log(i) for i in range(1, x+1))

    def log_hyper(a, b, c, d):
        n = a + b + c + d
        return (log_factorial(a+b) + log_factorial(c+d) +
                log_factorial(a+c) + log_factorial(b+d) -
                log_factorial(n) - log_factorial(a) -
                log_factorial(b) - log_factorial(c) - log_factorial(d))

    # Calculate p-value of observed table
    p_observed = math.exp(log_hyper(a, b, c, d))

    # Enumerate all tables with same marginals
    row1 = a + b
    row2 = c + d
    col1 = a + c

    p_value = 0
    for i in range(max(0, col1 - row2), min(row1, col1) + 1):
        j = row1 - i
        k = col1 - i
        l = row2 - k
        if j >= 0 and k >= 0 and l >= 0:
            p_table = math.exp(log_hyper(i, j, k, l))
            if p_table <= p_observed + 1e-10:
                p_value += p_table

    return min(1.0, p_value)


def chi_square_rxc(contingency, row_labels, col_labels):
    """
    R×C chi-square test.
    contingency: dict of {row: {col: count}}
    Returns chi2, df, p-value.
    """
    row_totals = {r: sum(contingency[r].get(c, 0) for c in col_labels) for r in row_labels}
    col_totals = {c: sum(contingency[r].get(c, 0) for r in row_labels) for c in col_labels}
    grand_total = sum(row_totals.values())

    if grand_total == 0:
        return 0, 1, 1.0

    chi2 = 0
    for r in row_labels:
        for c in col_labels:
            observed = contingency[r].get(c, 0)
            expected = row_totals[r] * col_totals[c] / grand_total if grand_total > 0 else 0
            if expected > 0:
                chi2 += (observed - expected)**2 / expected

    df = (len(row_labels) - 1) * (len(col_labels) - 1)
    if df <= 0:
        return chi2, 1, 1.0

    # Wilson-Hilferty approximation for p-value
    k = df
    z = ((chi2/k)**(1/3) - (1 - 2/(9*k))) / math.sqrt(2/(9*k))
    p_value = 0.5 * math.erfc(z / math.sqrt(2))

    return chi2, df, p_value


def hhi(counts_dict, total):
    """Herfindahl-Hirschman Index from counts dict."""
    if total == 0:
        return 0
    return sum((c/total)**2 for c in counts_dict.values())

# =============================================================================
# PART 1: ARTICLE-LEVEL FREQUENCY AND DISTRIBUTION
# =============================================================================

def article_frequency_analysis(holdings):
    """Map out which articles appear, how often, and their outcome rates."""
    print("=" * 80)
    print("PART 1: GDPR ARTICLE FREQUENCY AND OUTCOME RATES")
    print("=" * 80)

    # Parse provisions for each holding
    article_counts = defaultdict(int)      # article -> count of holdings citing it
    sub_counts = defaultdict(int)          # sub-provision -> count
    article_pro_ds = defaultdict(int)      # article -> pro-DS count
    sub_pro_ds = defaultdict(int)

    for h in holdings:
        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen_articles = set()
        seen_subs = set()

        for prov in provisions:
            art = prov['article']
            if art not in seen_articles:
                article_counts[art] += 1
                article_pro_ds[art] += h['pro_ds']
                seen_articles.add(art)

            sub = prov['sub']
            if sub and sub not in seen_subs:
                sub_counts[sub] += 1
                sub_pro_ds[sub] += h['pro_ds']
                seen_subs.add(sub)

    # Top articles by frequency
    print(f"\n  TOP GDPR ARTICLES (cited in ≥5 holdings):")
    print(f"  {'Article':>10} {'Holdings':>10} {'Pro-DS':>10} {'Rate':>8}")
    print("  " + "-" * 42)

    top_articles = sorted(article_counts.items(), key=lambda x: -x[1])
    article_summary = {}
    for art, count in top_articles:
        if count < 5:
            continue
        rate = article_pro_ds[art] / count
        p, ci_lo, ci_hi = wilson_ci(article_pro_ds[art], count)
        article_summary[art] = {
            'n': count,
            'pro_ds': article_pro_ds[art],
            'rate': rate,
            'ci_lo': ci_lo,
            'ci_hi': ci_hi
        }
        print(f"  Art. {art:>4} {count:>10} {article_pro_ds[art]:>10} {rate:>7.1%}")

    # Top sub-provisions
    print(f"\n  TOP SUB-PROVISIONS (cited in ≥3 holdings):")
    print(f"  {'Provision':<20} {'Holdings':>10} {'Pro-DS':>10} {'Rate':>8}")
    print("  " + "-" * 52)

    top_subs = sorted(sub_counts.items(), key=lambda x: -x[1])
    sub_summary = {}
    for sub, count in top_subs:
        if count < 3:
            continue
        rate = sub_pro_ds[sub] / count
        sub_summary[sub] = {
            'n': count,
            'pro_ds': sub_pro_ds[sub],
            'rate': rate
        }
        print(f"  {sub:<20} {count:>10} {sub_pro_ds[sub]:>10} {rate:>7.1%}")

    return article_summary, sub_summary

# =============================================================================
# PART 2: RAPPORTEUR × ARTICLE CROSS-TABULATION
# =============================================================================

def rapporteur_article_analysis(holdings):
    """Cross-tabulate rapporteurs against specific GDPR articles."""
    print("\n" + "=" * 80)
    print("PART 2: RAPPORTEUR × GDPR ARTICLE SPECIALIZATION")
    print("=" * 80)

    # Build rapporteur × article matrix
    rap_article = defaultdict(lambda: defaultdict(int))
    rap_sub = defaultdict(lambda: defaultdict(int))
    rap_totals = defaultdict(int)
    rap_article_pro_ds = defaultdict(lambda: defaultdict(int))
    rap_sub_pro_ds = defaultdict(lambda: defaultdict(int))

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        if not rap:
            continue

        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen_articles = set()
        seen_subs = set()

        rap_totals[rap] += 1

        for prov in provisions:
            art = prov['article']
            if art not in seen_articles:
                rap_article[rap][art] += 1
                rap_article_pro_ds[rap][art] += h['pro_ds']
                seen_articles.add(art)

            sub = prov['sub']
            if sub and sub not in seen_subs:
                rap_sub[rap][sub] += 1
                rap_sub_pro_ds[rap][sub] += h['pro_ds']
                seen_subs.add(sub)

    # Filter to rapporteurs with ≥10 holdings
    active_raps = sorted(
        [r for r, t in rap_totals.items() if t >= 10],
        key=lambda r: -rap_totals[r]
    )

    # Identify articles with enough data (≥5 holdings overall)
    overall_article_counts = defaultdict(int)
    for h in holdings:
        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen = set()
        for prov in provisions:
            if prov['article'] not in seen:
                overall_article_counts[prov['article']] += 1
                seen.add(prov['article'])

    frequent_articles = sorted(
        [a for a, c in overall_article_counts.items() if c >= 5],
        key=lambda a: -overall_article_counts[a]
    )

    # --- 2A: RAPPORTEUR × ARTICLE HEATMAP ---
    print(f"\n  RAPPORTEUR × ARTICLE CROSS-TABULATION")
    print(f"  (Holdings mentioning each article, by rapporteur)")
    print(f"  {len(active_raps)} rapporteurs × {len(frequent_articles)} articles")

    # Print header
    art_labels = [f"Art.{a}" for a in frequent_articles[:12]]
    header = f"  {'Rapporteur':<20} {'N':>4} " + " ".join(f"{l:>7}" for l in art_labels)
    print(f"\n{header}")
    print("  " + "-" * (25 + 8 * len(art_labels)))

    rap_article_results = {}

    for rap in active_raps:
        n = rap_totals[rap]
        cells = []
        for art in frequent_articles[:12]:
            count = rap_article[rap].get(art, 0)
            pct = count / n * 100 if n > 0 else 0
            cells.append(f"{count:>3}({pct:>2.0f}%)")

        rap_article_results[rap] = {
            'n': n,
            'articles': {str(a): rap_article[rap].get(a, 0) for a in frequent_articles}
        }

        print(f"  {rap:<20} {n:>4} " + " ".join(cells))

    # Overall row
    cells = []
    n_total = len(holdings)
    for art in frequent_articles[:12]:
        count = overall_article_counts[art]
        pct = count / n_total * 100
        cells.append(f"{count:>3}({pct:>2.0f}%)")
    print(f"  {'OVERALL':<20} {n_total:>4} " + " ".join(cells))

    # --- 2B: ARTICLE CONCENTRATION PER RAPPORTEUR ---
    print(f"\n  ARTICLE CONCENTRATION (HHI) PER RAPPORTEUR")
    print(f"  {'Rapporteur':<20} {'N':>5} {'Top Art.':>10} {'%':>7} {'HHI':>7} {'Spec?':<6}")
    print("  " + "-" * 60)

    rap_concentration = {}
    # Expected HHI under overall distribution
    total_article_mentions = sum(overall_article_counts.values())
    expected_hhi = sum((c/total_article_mentions)**2
                       for c in overall_article_counts.values()) if total_article_mentions > 0 else 0

    for rap in active_raps:
        articles = rap_article[rap]
        n_mentions = sum(articles.values())
        if n_mentions == 0:
            continue

        top_art = max(articles, key=articles.get)
        top_pct = articles[top_art] / n_mentions

        rap_hhi = hhi(articles, n_mentions)
        spec_ratio = rap_hhi / expected_hhi if expected_hhi > 0 else 1
        is_spec = spec_ratio > 1.5 or top_pct > 0.30

        rap_concentration[rap] = {
            'n_mentions': n_mentions,
            'top_article': top_art,
            'top_pct': top_pct,
            'hhi': rap_hhi,
            'spec_ratio': spec_ratio,
            'is_specialized': is_spec
        }

        spec_str = "YES" if is_spec else "no"
        print(f"  {rap:<20} {n_mentions:>5} Art.{top_art:>4}  {top_pct:>6.1%} {rap_hhi:>6.3f} {spec_str:<6}")

    print(f"\n  Expected HHI (overall distribution): {expected_hhi:.3f}")

    # --- 2C: RAPPORTEUR × SUB-PROVISION ---
    print(f"\n  RAPPORTEUR × SUB-PROVISION (top sub-provisions)")

    # Find sub-provisions with ≥3 overall mentions
    overall_sub_counts = defaultdict(int)
    for h in holdings:
        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen = set()
        for prov in provisions:
            if prov['sub'] and prov['sub'] not in seen:
                overall_sub_counts[prov['sub']] += 1
                seen.add(prov['sub'])

    frequent_subs = sorted(
        [s for s, c in overall_sub_counts.items() if c >= 4],
        key=lambda s: -overall_sub_counts[s]
    )

    print(f"  {len(frequent_subs)} sub-provisions with ≥4 citations")

    rap_sub_results = {}

    for rap in active_raps:
        subs = rap_sub[rap]
        n = rap_totals[rap]
        rap_sub_results[rap] = {
            'n': n,
            'subs': {}
        }

        top_subs_for_rap = sorted(subs.items(), key=lambda x: -x[1])[:5]
        top_strs = [f"{s}({c})" for s, c in top_subs_for_rap if c >= 2]
        if top_strs:
            print(f"  {rap:<20} (n={n:>3}): {', '.join(top_strs)}")
            for s, c in top_subs_for_rap:
                rap_sub_results[rap]['subs'][s] = c

    # --- 2D: STATISTICAL TESTS ---
    print(f"\n  STATISTICAL TESTS")
    print("  " + "-" * 60)

    # Chi-square: rapporteur × article (top 5 raps × top 8 articles)
    test_raps = active_raps[:5]
    test_articles = frequent_articles[:8]

    contingency = {}
    for rap in test_raps:
        contingency[rap] = {}
        for art in test_articles:
            contingency[rap][str(art)] = rap_article[rap].get(art, 0)

    test_art_labels = [str(a) for a in test_articles]
    chi2, df, p = chi_square_rxc(contingency, test_raps, test_art_labels)

    print(f"\n  Chi-square test ({len(test_raps)} rapporteurs × {len(test_articles)} articles):")
    print(f"    χ²({df}) = {chi2:.2f}")
    print(f"    p-value ≈ {p:.6f}")
    if p < 0.001:
        print(f"    → HIGHLY SIGNIFICANT: Non-random article distribution across rapporteurs")
    elif p < 0.05:
        print(f"    → SIGNIFICANT: Evidence of article specialization patterns")
    else:
        print(f"    → Not significant at α=0.05")

    # Per-article tests: is any rapporteur over-represented?
    print(f"\n  PER-ARTICLE RAPPORTEUR OVER-REPRESENTATION:")
    print(f"  {'Article':>10} {'Rapporteur':<20} {'Obs':>5} {'Exp':>7} {'p-value':>10} {'Sig':>5}")
    print("  " + "-" * 62)

    article_overrep = []

    for art in frequent_articles[:10]:
        art_total = overall_article_counts[art]
        for rap in active_raps:
            rap_art_count = rap_article[rap].get(art, 0)
            rap_n = rap_totals[rap]

            # Expected under independence
            expected = rap_n * art_total / n_total if n_total > 0 else 0

            if rap_art_count <= expected or rap_art_count < 3:
                continue

            # Fisher test: rapporteur has this article vs not
            a = rap_art_count
            b = rap_n - a
            c = art_total - a
            d = (n_total - rap_n) - c

            if c < 0:
                c = 0
                d = n_total - rap_n

            p_val = fisher_exact_2x2(a, b, c, d)

            if p_val < 0.10:
                sig = "*" if p_val < 0.05 else "~"
                print(f"  Art. {art:>4} {rap:<20} {rap_art_count:>5} {expected:>6.1f} {p_val:>9.4f} {sig:>5}")
                article_overrep.append({
                    'article': art,
                    'rapporteur': rap,
                    'observed': rap_art_count,
                    'expected': round(expected, 1),
                    'p_value': round(p_val, 4)
                })

    return {
        'rapporteur_article_matrix': rap_article_results,
        'rapporteur_concentration': rap_concentration,
        'rapporteur_sub_provisions': rap_sub_results,
        'chi_square_test': {'chi2': chi2, 'df': df, 'p_value': p},
        'article_overrepresentation': article_overrep
    }

# =============================================================================
# PART 3: CHAMBER × ARTICLE CROSS-TABULATION
# =============================================================================

def chamber_article_analysis(holdings):
    """Cross-tabulate chambers against specific GDPR articles."""
    print("\n" + "=" * 80)
    print("PART 3: CHAMBER × GDPR ARTICLE SPECIALIZATION")
    print("=" * 80)

    chamber_article = defaultdict(lambda: defaultdict(int))
    chamber_sub = defaultdict(lambda: defaultdict(int))
    chamber_totals = defaultdict(int)
    chamber_article_pro_ds = defaultdict(lambda: defaultdict(int))

    for h in holdings:
        chamber = h.get('chamber', '')
        if not chamber:
            continue

        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen_articles = set()
        seen_subs = set()

        chamber_totals[chamber] += 1

        for prov in provisions:
            art = prov['article']
            if art not in seen_articles:
                chamber_article[chamber][art] += 1
                chamber_article_pro_ds[chamber][art] += h['pro_ds']
                seen_articles.add(art)

            sub = prov['sub']
            if sub and sub not in seen_subs:
                chamber_sub[chamber][sub] += 1
                seen_subs.add(sub)

    # Filter chambers with ≥8 holdings
    active_chambers = sorted(
        [c for c, t in chamber_totals.items() if t >= 8],
        key=lambda c: -chamber_totals[c]
    )

    # Overall article counts
    overall_article_counts = defaultdict(int)
    for h in holdings:
        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen = set()
        for prov in provisions:
            if prov['article'] not in seen:
                overall_article_counts[prov['article']] += 1
                seen.add(prov['article'])

    frequent_articles = sorted(
        [a for a, c in overall_article_counts.items() if c >= 5],
        key=lambda a: -overall_article_counts[a]
    )

    n_total = len(holdings)

    # --- 3A: CHAMBER × ARTICLE TABLE ---
    print(f"\n  CHAMBER × ARTICLE CROSS-TABULATION")
    art_labels = [f"Art.{a}" for a in frequent_articles[:12]]
    header = f"  {'Chamber':<16} {'N':>4} " + " ".join(f"{l:>7}" for l in art_labels)
    print(f"\n{header}")
    print("  " + "-" * (21 + 8 * len(art_labels)))

    chamber_results = {}

    for chamber in active_chambers:
        n = chamber_totals[chamber]
        cells = []
        for art in frequent_articles[:12]:
            count = chamber_article[chamber].get(art, 0)
            pct = count / n * 100 if n > 0 else 0
            cells.append(f"{count:>3}({pct:>2.0f}%)")

        chamber_results[chamber] = {
            'n': n,
            'articles': {str(a): chamber_article[chamber].get(a, 0) for a in frequent_articles}
        }

        print(f"  {chamber:<16} {n:>4} " + " ".join(cells))

    # Overall
    cells = []
    for art in frequent_articles[:12]:
        count = overall_article_counts[art]
        pct = count / n_total * 100
        cells.append(f"{count:>3}({pct:>2.0f}%)")
    print(f"  {'OVERALL':<16} {n_total:>4} " + " ".join(cells))

    # --- 3B: CHAMBER ARTICLE CONCENTRATION ---
    print(f"\n  CHAMBER ARTICLE CONCENTRATION (HHI)")
    print(f"  {'Chamber':<16} {'Top Art.':>10} {'%':>7} {'HHI':>7}")
    print("  " + "-" * 44)

    total_mentions = sum(overall_article_counts.values())
    expected_hhi_val = sum((c/total_mentions)**2 for c in overall_article_counts.values()) if total_mentions > 0 else 0

    chamber_concentration = {}

    for chamber in active_chambers:
        articles = chamber_article[chamber]
        n_mentions = sum(articles.values())
        if n_mentions == 0:
            continue

        top_art = max(articles, key=articles.get)
        top_pct = articles[top_art] / n_mentions

        c_hhi = hhi(articles, n_mentions)

        chamber_concentration[chamber] = {
            'n_mentions': n_mentions,
            'top_article': top_art,
            'top_pct': top_pct,
            'hhi': c_hhi
        }

        print(f"  {chamber:<16} Art.{top_art:>4}  {top_pct:>6.1%} {c_hhi:>6.3f}")

    # --- 3C: CHAMBER × ARTICLE OUTCOME RATES ---
    print(f"\n  CHAMBER × ARTICLE PRO-DS RATES")
    print(f"  (For articles with ≥3 holdings in a given chamber)")

    key_articles = frequent_articles[:8]
    print(f"\n  {'Chamber':<16} " + " ".join(f"{'Art.'+str(a):>12}" for a in key_articles))
    print("  " + "-" * (17 + 13 * len(key_articles)))

    for chamber in active_chambers:
        cells = []
        for art in key_articles:
            count = chamber_article[chamber].get(art, 0)
            pro_ds = chamber_article_pro_ds[chamber].get(art, 0)
            if count >= 3:
                rate = pro_ds / count
                cells.append(f"{rate:>5.0%}(n={count:>2})")
            else:
                cells.append(f"{'':>12}")
        print(f"  {chamber:<16} " + " ".join(cells))

    # --- 3D: CHI-SQUARE TEST ---
    print(f"\n  STATISTICAL TEST: CHAMBER × ARTICLE")
    test_chambers = [c for c in active_chambers if chamber_totals[c] >= 10]
    test_articles = frequent_articles[:8]

    contingency = {}
    for chamber in test_chambers:
        contingency[chamber] = {}
        for art in test_articles:
            contingency[chamber][str(art)] = chamber_article[chamber].get(art, 0)

    test_art_labels = [str(a) for a in test_articles]
    chi2, df, p = chi_square_rxc(contingency, test_chambers, test_art_labels)

    print(f"\n  Chi-square test ({len(test_chambers)} chambers × {len(test_articles)} articles):")
    print(f"    χ²({df}) = {chi2:.2f}")
    print(f"    p-value ≈ {p:.6f}")
    if p < 0.001:
        print(f"    → HIGHLY SIGNIFICANT: Chambers differ in article coverage")
    elif p < 0.05:
        print(f"    → SIGNIFICANT: Evidence of chamber-article association")
    else:
        print(f"    → Not significant at α=0.05")

    # --- 3E: TOP SUB-PROVISIONS PER CHAMBER ---
    print(f"\n  TOP SUB-PROVISIONS PER CHAMBER:")

    chamber_sub_results = {}

    for chamber in active_chambers:
        subs = chamber_sub[chamber]
        top_subs = sorted(subs.items(), key=lambda x: -x[1])[:5]
        top_strs = [f"{s}({c})" for s, c in top_subs if c >= 2]
        if top_strs:
            print(f"  {chamber:<16}: {', '.join(top_strs)}")
            chamber_sub_results[chamber] = {s: c for s, c in top_subs if c >= 2}

    return {
        'chamber_article_matrix': chamber_results,
        'chamber_concentration': chamber_concentration,
        'chi_square_test': {'chi2': chi2, 'df': df, 'p_value': p},
        'chamber_sub_provisions': chamber_sub_results
    }

# =============================================================================
# PART 4: ARTICLE-LEVEL OUTCOME ANALYSIS BY RAPPORTEUR
# =============================================================================

def article_outcome_by_rapporteur(holdings):
    """For key articles, compare outcome rates across rapporteurs."""
    print("\n" + "=" * 80)
    print("PART 4: ARTICLE-SPECIFIC OUTCOME RATES BY RAPPORTEUR")
    print("=" * 80)
    print("  Do rapporteurs rule differently on the SAME article?")

    # Build per-article, per-rapporteur outcome data
    art_rap_data = defaultdict(lambda: defaultdict(lambda: {'pro_ds': 0, 'total': 0}))
    article_overall = defaultdict(lambda: {'pro_ds': 0, 'total': 0})

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        if not rap:
            continue

        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen = set()

        for prov in provisions:
            art = prov['article']
            if art not in seen:
                art_rap_data[art][rap]['total'] += 1
                art_rap_data[art][rap]['pro_ds'] += h['pro_ds']
                article_overall[art]['total'] += 1
                article_overall[art]['pro_ds'] += h['pro_ds']
                seen.add(art)

    # Key articles (enough data)
    key_articles = sorted(
        [a for a, d in article_overall.items() if d['total'] >= 8],
        key=lambda a: -article_overall[a]['total']
    )

    results = {}

    for art in key_articles:
        baseline_n = article_overall[art]['total']
        baseline_rate = article_overall[art]['pro_ds'] / baseline_n if baseline_n > 0 else 0

        # Rapporteurs with ≥3 holdings for this article
        raps_with_data = sorted(
            [(r, d) for r, d in art_rap_data[art].items() if d['total'] >= 3],
            key=lambda x: -x[1]['total']
        )

        if len(raps_with_data) < 2:
            continue

        print(f"\n  Article {art} (n={baseline_n}, baseline={baseline_rate:.1%}):")
        print(f"  {'Rapporteur':<20} {'N':>5} {'Pro-DS':>8} {'Rate':>8} {'vs Base':>10}")
        print("  " + "-" * 55)

        art_results = {
            'baseline_n': baseline_n,
            'baseline_rate': baseline_rate,
            'rapporteurs': {}
        }

        for rap, data in raps_with_data:
            rate = data['pro_ds'] / data['total']
            diff = rate - baseline_rate

            art_results['rapporteurs'][rap] = {
                'n': data['total'],
                'pro_ds': data['pro_ds'],
                'rate': rate,
                'diff_from_baseline': diff
            }

            print(f"  {rap:<20} {data['total']:>5} {data['pro_ds']:>8} {rate:>7.1%} {diff:>+9.1%}")

        # Within-article chi-square (all rapporteurs with data vs rest)
        if len(raps_with_data) >= 2:
            # Test: most extreme rapporteur vs rest
            rates = [(r, d['pro_ds']/d['total'], d) for r, d in raps_with_data]
            rates.sort(key=lambda x: x[1])

            # Test lowest vs highest
            low_rap, low_rate, low_data = rates[0]
            high_rap, high_rate, high_data = rates[-1]

            if abs(high_rate - low_rate) > 0.15:
                a = high_data['pro_ds']
                b = high_data['total'] - a
                c = low_data['pro_ds']
                d = low_data['total'] - c

                if min(a, b, c, d) < 5:
                    p_val = fisher_exact_2x2(a, b, c, d)
                    test_type = "Fisher"
                else:
                    _, p_val = chi_square_2x2(a, b, c, d)
                    test_type = "χ²"

                sig = "*" if p_val < 0.05 else ""
                print(f"  → {test_type} test ({high_rap} vs {low_rap}): p={p_val:.3f}{sig}")
                art_results['test'] = {
                    'type': test_type,
                    'high_rap': high_rap,
                    'low_rap': low_rap,
                    'p_value': p_val
                }

        results[str(art)] = art_results

    return results

# =============================================================================
# PART 5: SUB-PROVISION SPECIALIZATION DEEP DIVE
# =============================================================================

def sub_provision_deep_dive(holdings):
    """Detailed analysis at the sub-provision level (e.g. 6(1)(a) vs 6(1)(f))."""
    print("\n" + "=" * 80)
    print("PART 5: SUB-PROVISION SPECIALIZATION DEEP DIVE")
    print("=" * 80)

    # Group sub-provisions by parent article
    article_subs = defaultdict(lambda: defaultdict(int))
    article_sub_rap = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    article_sub_chamber = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    article_sub_pro_ds = defaultdict(lambda: defaultdict(int))

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        chamber = h.get('chamber', '')
        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen = set()

        for prov in provisions:
            sub = prov['sub']
            art = prov['article']
            if sub and sub not in seen:
                article_subs[art][sub] += 1
                article_sub_pro_ds[art][sub] += h['pro_ds']
                if rap:
                    article_sub_rap[art][sub][rap] += 1
                if chamber:
                    article_sub_chamber[art][sub][chamber] += 1
                seen.add(sub)

    # Focus on articles with multiple sub-provisions
    results = {}

    for art in sorted(article_subs.keys()):
        subs = article_subs[art]
        # Need at least 2 sub-provisions each with ≥2 mentions
        qualifying_subs = {s: c for s, c in subs.items() if c >= 2}
        if len(qualifying_subs) < 2:
            continue

        print(f"\n  ARTICLE {art} — SUB-PROVISION BREAKDOWN")
        print("  " + "-" * 60)

        total_art_subs = sum(qualifying_subs.values())
        art_result = {'sub_provisions': {}}

        print(f"  {'Sub-provision':<20} {'N':>5} {'Pro-DS':>8} {'Rate':>8} {'Rapporteurs':<30}")
        print("  " + "-" * 75)

        for sub, count in sorted(qualifying_subs.items(), key=lambda x: -x[1]):
            pro_ds = article_sub_pro_ds[art].get(sub, 0)
            rate = pro_ds / count if count > 0 else 0

            # Top rapporteurs for this sub-provision
            rap_counts = article_sub_rap[art].get(sub, {})
            top_raps = sorted(rap_counts.items(), key=lambda x: -x[1])[:3]
            rap_str = ", ".join(f"{r}({c})" for r, c in top_raps)

            art_result['sub_provisions'][sub] = {
                'n': count,
                'pro_ds': pro_ds,
                'rate': rate,
                'rapporteurs': dict(rap_counts),
                'chambers': dict(article_sub_chamber[art].get(sub, {}))
            }

            print(f"  {sub:<20} {count:>5} {pro_ds:>8} {rate:>7.1%} {rap_str:<30}")

        results[str(art)] = art_result

    return results

# =============================================================================
# PART 6: SUMMARY SPECIALIZATION PROFILES
# =============================================================================

def build_specialization_profiles(holdings, rap_results, chamber_results):
    """Build concise specialization profiles per rapporteur and chamber."""
    print("\n" + "=" * 80)
    print("PART 6: SPECIALIZATION PROFILES")
    print("=" * 80)

    # --- RAPPORTEUR PROFILES ---
    print(f"\n  RAPPORTEUR ARTICLE PROFILES:")
    print("  " + "-" * 70)

    rap_totals = defaultdict(int)
    rap_article_data = defaultdict(lambda: defaultdict(int))
    rap_sub_data = defaultdict(lambda: defaultdict(int))

    for h in holdings:
        rap = h.get('judge_rapporteur', '')
        if not rap:
            continue
        rap_totals[rap] += 1

        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen_art = set()
        seen_sub = set()
        for prov in provisions:
            if prov['article'] not in seen_art:
                rap_article_data[rap][prov['article']] += 1
                seen_art.add(prov['article'])
            if prov['sub'] and prov['sub'] not in seen_sub:
                rap_sub_data[rap][prov['sub']] += 1
                seen_sub.add(prov['sub'])

    active_raps = sorted(
        [r for r, t in rap_totals.items() if t >= 10],
        key=lambda r: -rap_totals[r]
    )

    profiles = {}

    for rap in active_raps:
        n = rap_totals[rap]
        articles = rap_article_data[rap]
        subs = rap_sub_data[rap]

        # Top 3 articles (by % of holdings)
        top_arts = sorted(articles.items(), key=lambda x: -x[1])[:3]
        top_art_strs = [f"Art.{a}({c}/{n}={c/n:.0%})" for a, c in top_arts]

        # Top 3 sub-provisions
        top_subs = sorted(subs.items(), key=lambda x: -x[1])[:3]
        top_sub_strs = [f"{s}({c})" for s, c in top_subs]

        profiles[rap] = {
            'n_holdings': n,
            'top_articles': {str(a): {'count': c, 'pct': c/n} for a, c in top_arts},
            'top_sub_provisions': {s: c for s, c in top_subs}
        }

        print(f"\n  {rap} (n={n}):")
        print(f"    Articles: {', '.join(top_art_strs)}")
        print(f"    Sub-provisions: {', '.join(top_sub_strs)}")

    # --- CHAMBER PROFILES ---
    print(f"\n  CHAMBER ARTICLE PROFILES:")
    print("  " + "-" * 70)

    chamber_totals = defaultdict(int)
    chamber_article_data = defaultdict(lambda: defaultdict(int))

    for h in holdings:
        chamber = h.get('chamber', '')
        if not chamber:
            continue
        chamber_totals[chamber] += 1

        provisions = parse_provisions(h.get('provisions_cited', ''))
        seen = set()
        for prov in provisions:
            if prov['article'] not in seen:
                chamber_article_data[chamber][prov['article']] += 1
                seen.add(prov['article'])

    active_chambers = sorted(
        [c for c, t in chamber_totals.items() if t >= 8],
        key=lambda c: -chamber_totals[c]
    )

    chamber_profiles = {}

    for chamber in active_chambers:
        n = chamber_totals[chamber]
        articles = chamber_article_data[chamber]

        top_arts = sorted(articles.items(), key=lambda x: -x[1])[:4]
        top_art_strs = [f"Art.{a}({c}/{n}={c/n:.0%})" for a, c in top_arts]

        chamber_profiles[chamber] = {
            'n_holdings': n,
            'top_articles': {str(a): {'count': c, 'pct': c/n} for a, c in top_arts}
        }

        print(f"  {chamber:<16} (n={n}): {', '.join(top_art_strs)}")

    return {
        'rapporteur_profiles': profiles,
        'chamber_profiles': chamber_profiles
    }

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Loading data...")
    holdings = load_holdings()
    print(f"Loaded {len(holdings)} holdings")

    print("\n" + "=" * 80)
    print("ARTICLE-LEVEL SPECIALIZATION ANALYSIS")
    print("=" * 80)
    print("  Granular analysis at GDPR article and sub-provision level")
    print("  (complements topic-cluster analysis in 15_supplementary)")

    # Part 1: Article frequency
    article_summary, sub_summary = article_frequency_analysis(holdings)

    # Part 2: Rapporteur × article
    rap_results = rapporteur_article_analysis(holdings)

    # Part 3: Chamber × article
    chamber_results = chamber_article_analysis(holdings)

    # Part 4: Article-level outcomes by rapporteur
    outcome_results = article_outcome_by_rapporteur(holdings)

    # Part 5: Sub-provision deep dive
    sub_results = sub_provision_deep_dive(holdings)

    # Part 6: Specialization profiles
    profiles = build_specialization_profiles(holdings, rap_results, chamber_results)

    # Save all results
    all_results = {
        'article_frequency': {str(k): v for k, v in article_summary.items()},
        'sub_provision_frequency': sub_summary,
        'rapporteur_article_analysis': rap_results,
        'chamber_article_analysis': chamber_results,
        'article_outcome_by_rapporteur': outcome_results,
        'sub_provision_deep_dive': sub_results,
        'specialization_profiles': profiles
    }

    output_file = OUTPUT_PATH / "article_specialization_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # --- FINAL SUMMARY ---
    print("\n" + "=" * 80)
    print("SUMMARY OF ARTICLE-LEVEL SPECIALIZATION FINDINGS")
    print("=" * 80)

    # Rapporteur specialization
    rap_conc = rap_results.get('rapporteur_concentration', {})
    specialized_raps = [r for r, d in rap_conc.items() if d.get('is_specialized')]
    print(f"\n1. RAPPORTEUR ARTICLE SPECIALIZATION:")
    if specialized_raps:
        for rap in specialized_raps:
            d = rap_conc[rap]
            print(f"   - {rap}: concentrated on Art.{d['top_article']} ({d['top_pct']:.0%} of mentions)")
    else:
        print(f"   - No rapporteur shows strong article-level concentration")

    # Rapporteur × article association test
    rap_chi = rap_results.get('chi_square_test', {})
    print(f"\n2. RAPPORTEUR × ARTICLE ASSOCIATION:")
    print(f"   χ²({rap_chi.get('df', '?')}) = {rap_chi.get('chi2', 0):.2f}, p = {rap_chi.get('p_value', 1):.6f}")

    # Chamber differences
    ch_chi = chamber_results.get('chi_square_test', {})
    print(f"\n3. CHAMBER × ARTICLE ASSOCIATION:")
    print(f"   χ²({ch_chi.get('df', '?')}) = {ch_chi.get('chi2', 0):.2f}, p = {ch_chi.get('p_value', 1):.6f}")

    # Notable within-article rapporteur differences
    print(f"\n4. WITHIN-ARTICLE RAPPORTEUR DIFFERENCES:")
    for art, data in outcome_results.items():
        test = data.get('test')
        if test and test.get('p_value', 1) < 0.10:
            print(f"   - Art.{art}: {test['high_rap']} vs {test['low_rap']}, p={test['p_value']:.3f}")

    # Over-represented rapporteur-article pairs
    overrep = rap_results.get('article_overrepresentation', [])
    if overrep:
        print(f"\n5. OVER-REPRESENTED RAPPORTEUR-ARTICLE PAIRS (p<0.10):")
        for entry in overrep[:10]:
            print(f"   - {entry['rapporteur']}: Art.{entry['article']} "
                  f"(obs={entry['observed']}, exp={entry['expected']}, p={entry['p_value']:.4f})")

    return all_results


if __name__ == "__main__":
    results = main()
